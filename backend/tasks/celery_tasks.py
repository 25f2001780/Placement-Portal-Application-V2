import csv
import io
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab

celery_app = Celery('ppa_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

celery_app.conf.beat_schedule = {
    'minutely-schedule-check': {
        'task': 'tasks.celery_tasks.check_schedules',
        'schedule': crontab(minute='*'), # runs every minute
    }
}
celery_app.conf.timezone = 'UTC'

@celery_app.task
def check_schedules():
    import json
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    settings_path = os.path.join(BASE_DIR, 'settings.json')
    
    if not os.path.exists(settings_path):
        return "No settings file found."
        
    with open(settings_path, 'r') as f:
        settings = json.load(f)
        
    now = datetime.now()
    current_day = now.day
    current_time_str = now.strftime('%H:%M')
    current_month_str = now.strftime('%Y-%m')
    current_day_str = now.strftime('%Y-%m-%d')
    
    updates_made = False
    
    # Check Reminders
    reminder_time = settings.get('reminder_time', '09:00')
    if current_time_str == reminder_time:
        if settings.get('last_reminder_day') != current_day_str:
            daily_reminders.delay(force=True)
            settings['last_reminder_day'] = current_day_str
            updates_made = True
            
    # Check Monthly Report
    report_day = int(settings.get('report_day', 1))
    report_time = settings.get('report_time', '10:00')
    if current_day == report_day and current_time_str == report_time:
        if settings.get('last_report_month') != current_month_str:
            monthly_report.delay()
            settings['last_report_month'] = current_month_str
            updates_made = True
            
    if updates_made:
        with open(settings_path, 'w') as f:
            json.dump(settings, f)
            
    return "Schedules checked and tasks triggered if applicable."

@celery_app.task
def export_student_history_csv(student_profile_id):
    # export student apps to csv and return content directly in result
    sys.path.insert(0, BASE_DIR)
    from app import create_app
    app = create_app()
    with app.app_context():
        from models.models import Application, StudentProfile
        student = StudentProfile.query.get(student_profile_id)
        if not student:
            return {"error": "Student not found"}

        apps = Application.query.filter_by(student_id=student_profile_id).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Application ID', 'Company Name', 'Job Title',
            'Package (LPA)', 'Location', 'Status', 'Application Date'
        ])

        for a in apps:
            writer.writerow([
                a.id,
                a.drive.company.name,
                a.drive.job_title,
                a.drive.package_lpa or 'N/A',
                a.drive.location or 'N/A',
                a.status,
                a.application_date.strftime('%Y-%m-%d')
            ])

        filename = f"applications_{student.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
        # return csv content directly — frontend builds the blob
        return {"csv_content": output.getvalue(), "filename": filename}


@celery_app.task
def daily_reminders(force=False):
    # send reminders for drives closing soon
    sys.path.insert(0, BASE_DIR)
    from app import create_app
    app = create_app()
    with app.app_context():
        from models.models import PlacementDrive, StudentProfile, Application
        
        if force:
            # Force sends reminders for ALL approved drives with future deadlines (useful for viva demonstration)
            upcoming_drives = PlacementDrive.query.filter(
                PlacementDrive.status == 'Approved',
                PlacementDrive.application_deadline >= datetime.now().date()
            ).all()
        else:
            day_after = datetime.now().date() + timedelta(days=2)
            upcoming_drives = PlacementDrive.query.filter(
                PlacementDrive.status == 'Approved',
                PlacementDrive.application_deadline >= datetime.now().date(),
                PlacementDrive.application_deadline <= day_after
            ).all()

        reminder_log = []
        emails_to_send = []  # list of (student_email, student_name, drive info)

        # Filter out drives from companies that are blocked or unapproved
        upcoming_drives = [
            d for d in upcoming_drives
            if d.company.approved and d.company.user.active
        ]

        for drive in upcoming_drives:
            applied_student_ids = {a.student_id for a in drive.applications}
            all_students = StudentProfile.query.all()
            for student in all_students:
                if student.id not in applied_student_ids:
                    eligible = True
                    if drive.cgpa_cutoff and drive.cgpa_cutoff > (student.cgpa or 0):
                        eligible = False
                    if drive.branch_eligibility:
                        branches = [b.strip() for b in drive.branch_eligibility.split(',')]
                        if student.branch not in branches:
                            eligible = False
                    if eligible:
                        reminder_log.append(
                            f"[REMINDER] Student '{student.name}' (ID:{student.id}) - "
                            f"Drive '{drive.job_title}' at '{drive.company.name}' "
                            f"deadline: {drive.application_deadline}"
                        )
                        # get student email from their user account
                        student_email = student.user.email if student.user else None
                        if student_email:
                            emails_to_send.append({
                                "to": student_email,
                                "name": student.name,
                                "job_title": drive.job_title,
                                "company": drive.company.name,
                                "deadline": drive.application_deadline,
                                "package": drive.package_lpa or "N/A",
                                "location": drive.location or "N/A",
                            })

        # send reminder emails via SMTP
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        smtp_server = app.config.get('SMTP_SERVER')
        smtp_port = app.config.get('SMTP_PORT')
        smtp_user = app.config.get('SMTP_USERNAME')
        smtp_pass = app.config.get('SMTP_PASSWORD')
        from_email = app.config.get('SMTP_FROM_EMAIL')

        if smtp_user and smtp_pass:
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_user, smtp_pass)

                for entry in emails_to_send:
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = f"Placement Reminder: {entry['job_title']} at {entry['company']}"
                    msg['From'] = from_email
                    msg['To'] = entry['to']

                    html_body = f"""
                    <html><body style="margin:0; padding:0; background:#f5f5f5; font-family: 'Helvetica Neue', Arial, sans-serif;">
                    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5; padding: 40px 0;">
                      <tr><td align="center">
                        <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; overflow:hidden;">
                          <!-- header -->
                          <tr>
                            <td style="background:#0f172a; padding:28px 36px;">
                              <p style="margin:0; color:#94a3b8; font-size:11px; letter-spacing:2px; text-transform:uppercase;">Placement Cell &mdash; IITM BS</p>
                              <h1 style="margin:8px 0 0; color:#ffffff; font-size:20px; font-weight:600;">Application Deadline Reminder</h1>
                            </td>
                          </tr>
                          <!-- body -->
                          <tr>
                            <td style="padding:32px 36px;">
                              <p style="margin:0 0 20px; font-size:15px; color:#374151;">Dear <strong>{entry['name']}</strong>,</p>
                              <p style="margin:0 0 24px; font-size:14px; color:#6b7280; line-height:1.6;">This is a reminder that you have not yet applied to the following placement drive. The deadline is approaching — please log in and submit your application at the earliest.</p>
                              <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e5e7eb; border-radius:6px; overflow:hidden; margin-bottom:24px;">
                                <tr style="background:#f9fafb;">
                                  <td style="padding:12px 16px; font-size:12px; color:#9ca3af; font-weight:600; letter-spacing:1px; text-transform:uppercase; width:40%;">Company</td>
                                  <td style="padding:12px 16px; font-size:14px; color:#111827; font-weight:600;">{entry['company']}</td>
                                </tr>
                                <tr>
                                  <td style="padding:12px 16px; font-size:12px; color:#9ca3af; font-weight:600; letter-spacing:1px; text-transform:uppercase;">Role</td>
                                  <td style="padding:12px 16px; font-size:14px; color:#111827;">{entry['job_title']}</td>
                                </tr>
                                <tr style="background:#f9fafb;">
                                  <td style="padding:12px 16px; font-size:12px; color:#9ca3af; font-weight:600; letter-spacing:1px; text-transform:uppercase;">Package</td>
                                  <td style="padding:12px 16px; font-size:14px; color:#111827;">{entry['package']} LPA</td>
                                </tr>
                                <tr>
                                  <td style="padding:12px 16px; font-size:12px; color:#9ca3af; font-weight:600; letter-spacing:1px; text-transform:uppercase;">Location</td>
                                  <td style="padding:12px 16px; font-size:14px; color:#111827;">{entry['location']}</td>
                                </tr>
                                <tr style="background:#fff5f5;">
                                  <td style="padding:12px 16px; font-size:12px; color:#9ca3af; font-weight:600; letter-spacing:1px; text-transform:uppercase;">Deadline</td>
                                  <td style="padding:12px 16px; font-size:14px; color:#dc2626; font-weight:700;">{entry['deadline']}</td>
                                </tr>
                              </table>
                              <p style="margin:0 0 6px; font-size:13px; color:#6b7280;">Log in to the portal and apply before the deadline closes.</p>
                            </td>
                          </tr>
                          <!-- footer -->
                          <tr>
                            <td style="padding:20px 36px; background:#f9fafb; border-top:1px solid #e5e7eb;">
                              <p style="margin:0; font-size:12px; color:#9ca3af;">Placement Cell, IIT Madras BS Programme &mdash; This is an automated notification.</p>
                            </td>
                          </tr>
                        </table>
                      </td></tr>
                    </table>
                    </body></html>
                    """
                    msg.attach(MIMEText(html_body, 'html'))
                    server.sendmail(from_email, entry['to'], msg.as_string())
                    print(f"Reminder email sent to {entry['to']}")

                server.quit()
            except Exception as e:
                print(f"Failed to send reminder emails: {e}")
        else:
            # fallback — just print if SMTP not configured
            for msg in reminder_log:
                print(msg)

        return {"reminders_sent": len(reminder_log), "details": reminder_log[:20]}


@celery_app.task
def monthly_report():
    # make a monthly report of all placement stuff
    sys.path.insert(0, BASE_DIR)
    from app import create_app
    app = create_app()
    with app.app_context():
        from models.models import (
            StudentProfile, CompanyProfile, PlacementDrive, Application
        )
        from sqlalchemy import func

        total_students = StudentProfile.query.count()
        total_companies = CompanyProfile.query.count()
        total_drives = PlacementDrive.query.count()
        approved_drives = PlacementDrive.query.filter_by(status='Approved').count()
        total_applications = Application.query.count()
        selected = Application.query.filter_by(status='Selected').count()
        shortlisted = Application.query.filter_by(status='Shortlisted').count()
        rejected = Application.query.filter_by(status='Rejected').count()

        # get branch counts
        branch_stats = {}
        students = StudentProfile.query.all()
        for s in students:
            branch = s.branch or 'Unknown'
            if branch not in branch_stats:
                branch_stats[branch] = 0
            branch_stats[branch] += 1

        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        month_year = datetime.now().strftime('%B %Y')
        branch_rows = "".join(
            f"<tr><td style='padding:10px 16px; font-size:13px; color:#374151; border-bottom:1px solid #f3f4f6;'>{b}</td>"
            f"<td style='padding:10px 16px; font-size:13px; color:#374151; text-align:right; border-bottom:1px solid #f3f4f6;'>{c}</td></tr>"
            for b, c in branch_stats.items()
        )

        html_report = f"""
        <html><body style="margin:0; padding:0; background:#f5f5f5; font-family:'Helvetica Neue', Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5; padding:40px 0;">
          <tr><td align="center">
            <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; overflow:hidden;">

              <!-- header -->
              <tr>
                <td style="background:#0f172a; padding:32px 40px;">
                  <p style="margin:0; color:#64748b; font-size:11px; letter-spacing:2px; text-transform:uppercase;">Placement Cell &mdash; IITM BS</p>
                  <h1 style="margin:8px 0 0; color:#ffffff; font-size:22px; font-weight:600;">Monthly Placement Report</h1>
                  <p style="margin:6px 0 0; color:#94a3b8; font-size:13px;">{month_year}</p>
                </td>
              </tr>

              <!-- summary stats -->
              <tr>
                <td style="padding:32px 40px 0;">
                  <p style="margin:0 0 16px; font-size:11px; color:#9ca3af; letter-spacing:2px; text-transform:uppercase; font-weight:600;">Overview</p>
                  <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e5e7eb; border-radius:6px; overflow:hidden;">
                    <tr style="background:#f9fafb;">
                      <td style="padding:12px 16px; font-size:13px; color:#6b7280; width:60%;">Students Registered</td>
                      <td style="padding:12px 16px; font-size:13px; color:#111827; font-weight:600; text-align:right;">{total_students}</td>
                    </tr>
                    <tr>
                      <td style="padding:12px 16px; font-size:13px; color:#6b7280; border-top:1px solid #f3f4f6;">Companies Registered</td>
                      <td style="padding:12px 16px; font-size:13px; color:#111827; font-weight:600; text-align:right; border-top:1px solid #f3f4f6;">{total_companies}</td>
                    </tr>
                    <tr style="background:#f9fafb;">
                      <td style="padding:12px 16px; font-size:13px; color:#6b7280; border-top:1px solid #f3f4f6;">Total Placement Drives</td>
                      <td style="padding:12px 16px; font-size:13px; color:#111827; font-weight:600; text-align:right; border-top:1px solid #f3f4f6;">{total_drives}</td>
                    </tr>
                    <tr>
                      <td style="padding:12px 16px; font-size:13px; color:#6b7280; border-top:1px solid #f3f4f6;">Approved Drives</td>
                      <td style="padding:12px 16px; font-size:13px; color:#111827; font-weight:600; text-align:right; border-top:1px solid #f3f4f6;">{approved_drives}</td>
                    </tr>
                    <tr style="background:#f9fafb;">
                      <td style="padding:12px 16px; font-size:13px; color:#6b7280; border-top:1px solid #f3f4f6;">Total Applications</td>
                      <td style="padding:12px 16px; font-size:13px; color:#111827; font-weight:600; text-align:right; border-top:1px solid #f3f4f6;">{total_applications}</td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- application outcomes -->
              <tr>
                <td style="padding:24px 40px 0;">
                  <p style="margin:0 0 16px; font-size:11px; color:#9ca3af; letter-spacing:2px; text-transform:uppercase; font-weight:600;">Application Outcomes</p>
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="width:33%; padding:16px; background:#f0fdf4; border-radius:6px; text-align:center;">
                        <p style="margin:0; font-size:28px; font-weight:700; color:#16a34a;">{selected}</p>
                        <p style="margin:4px 0 0; font-size:11px; color:#6b7280; letter-spacing:1px; text-transform:uppercase;">Selected</p>
                      </td>
                      <td style="width:4%;"></td>
                      <td style="width:30%; padding:16px; background:#fffbeb; border-radius:6px; text-align:center;">
                        <p style="margin:0; font-size:28px; font-weight:700; color:#d97706;">{shortlisted}</p>
                        <p style="margin:4px 0 0; font-size:11px; color:#6b7280; letter-spacing:1px; text-transform:uppercase;">Shortlisted</p>
                      </td>
                      <td style="width:4%;"></td>
                      <td style="width:29%; padding:16px; background:#fef2f2; border-radius:6px; text-align:center;">
                        <p style="margin:0; font-size:28px; font-weight:700; color:#dc2626;">{rejected}</p>
                        <p style="margin:4px 0 0; font-size:11px; color:#6b7280; letter-spacing:1px; text-transform:uppercase;">Rejected</p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- branch breakdown -->
              <tr>
                <td style="padding:24px 40px 0;">
                  <p style="margin:0 0 16px; font-size:11px; color:#9ca3af; letter-spacing:2px; text-transform:uppercase; font-weight:600;">Branch Distribution</p>
                  <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e5e7eb; border-radius:6px; overflow:hidden;">
                    <tr style="background:#f9fafb;">
                      <td style="padding:10px 16px; font-size:11px; color:#9ca3af; font-weight:600; letter-spacing:1px; text-transform:uppercase;">Branch</td>
                      <td style="padding:10px 16px; font-size:11px; color:#9ca3af; font-weight:600; letter-spacing:1px; text-transform:uppercase; text-align:right;">Students</td>
                    </tr>
                    {branch_rows}
                  </table>
                </td>
              </tr>

              <!-- footer -->
              <tr>
                <td style="padding:28px 40px; margin-top:32px;">
                  <p style="margin:0; font-size:12px; color:#9ca3af;">Generated on {datetime.now().strftime('%d %B %Y at %H:%M')} &mdash; Placement Cell, IIT Madras BS Programme. This is an automated report.</p>
                </td>
              </tr>

            </table>
          </td></tr>
        </table>
        </body></html>
        """

        # Send via SMTP
        smtp_server = app.config.get('SMTP_SERVER')
        smtp_port = app.config.get('SMTP_PORT')
        smtp_user = app.config.get('SMTP_USERNAME')
        smtp_pass = app.config.get('SMTP_PASSWORD')
        from_email = app.config.get('SMTP_FROM_EMAIL')
        to_email = app.config.get('ADMIN_EMAIL')

        # if real credentials are provided
        if smtp_user != 'dummy_user':
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Monthly Placement Report - {datetime.now().strftime('%B %Y')}"
            msg["From"] = from_email
            msg["To"] = to_email
            msg.attach(MIMEText(html_report, "html"))

            try:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(from_email, to_email, msg.as_string())
            except Exception as e:
                print(f"Failed to send email: {e}")
        else:
            print("SMTP not configured. Generated Report:")
            print(html_report)

        return {
            "generated_at": datetime.now().isoformat(),
            "total_students": total_students,
            "total_companies": total_companies,
            "total_drives": total_drives,
            "total_applications": total_applications,
            "selected": selected
        }
