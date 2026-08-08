<template>
  <div class="container-fluid py-4">
    <div class="row">
      <!-- sidebar -->
      <div class="col-md-2 mb-4">
        <div class="card p-3">
          <div class="text-center mb-3">
            <img v-if="profile.profile_photo_path" :src="profile.profile_photo_path" class="rounded-circle mb-2 object-fit-cover" width="80" height="80" alt="Profile">
            <i v-else class="bi bi-person-circle text-secondary" style="font-size: 4rem;"></i>
            <h6 class="fw-bold mt-2 mb-0">{{ profile.name || 'Student Panel' }}</h6>
          </div>
          <hr class="mt-0">
          <a class="sidebar-link" :class="{active: currentTab === 'drives'}" href="#" @click.prevent="currentTab = 'drives'">
            <i class="bi bi-briefcase me-2"></i> Available Drives
          </a>
          <a class="sidebar-link" :class="{active: currentTab === 'applications'}" href="#" @click.prevent="currentTab = 'applications'">
            <i class="bi bi-file-earmark-text me-2"></i> My Applications
          </a>
          <a class="sidebar-link" :class="{active: currentTab === 'settings'}" href="#" @click.prevent="currentTab = 'settings'">
            <i class="bi bi-gear me-2"></i> Settings
          </a>
        </div>
      </div>
      
      <!-- main content -->
      <div class="col-md-10">
        
        <!-- available drives -->
        <div v-if="currentTab === 'drives'">
          <div class="page-header d-flex justify-content-between align-items-center mb-4">
            <h3 class="m-0 fw-bold">Available Placement Drives</h3>
            <button class="btn btn-sm btn-outline-primary" @click="fetchDrives"><i class="bi bi-arrow-clockwise"></i> Refresh</button>
          </div>
          
          <div v-if="drives.length === 0" class="alert alert-info">No available drives at the moment.</div>
          
          <!-- drive cards -->
          <div class="row g-4">
            <div class="col-md-6 col-lg-4" v-for="d in drives" :key="d.id">
              <div class="card h-100 hover-elevate">
                <div class="card-body pb-2">
                  <div class="d-flex align-items-center mb-3">
                    <img v-if="d.company_logo" :src="d.company_logo" class="rounded me-2 object-fit-cover border" width="40" height="40">
                    <i v-else class="bi bi-building fs-3 text-secondary me-2"></i>
                    <div>
                      <h6 class="card-title fw-bold text-primary mb-0 lh-1">{{ d.job_title }}</h6>
                      <small class="text-muted">{{ d.company_name }}</small>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <span class="badge bg-success bg-opacity-10 text-success border border-success me-2" v-if="d.package_lpa">{{ d.package_lpa }} LPA</span>
                    <span class="badge bg-secondary bg-opacity-10 text-secondary border border-secondary" v-if="d.location"><i class="bi bi-geo-alt"></i> {{ d.location }}</span>
                  </div>
                  
                  <div class="small text-danger fw-medium">
                    <i class="bi bi-clock me-1"></i> Deadline: {{ d.application_deadline }}
                  </div>
                </div>
                <div class="card-footer border-top-0 pt-0">
                  <button class="btn btn-outline-primary w-100" data-bs-toggle="modal" data-bs-target="#driveDetailsModal" @click="openDriveDetails(d)">
                    <i class="bi bi-eye me-1"></i> View Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- my applications -->
        <div v-if="currentTab === 'applications'">
          <div class="page-header d-flex justify-content-between align-items-center mb-4">
            <h3 class="m-0 fw-bold">My Applications</h3>
            <div class="d-flex gap-2">
              <button class="btn btn-sm btn-outline-success" @click="downloadStudentData" v-if="applications.length > 0" :disabled="exporting">
                <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-file-earmark-spreadsheet me-1"></i> 
                {{ exporting ? 'Exporting...' : 'Export CSV' }}
              </button>
              <button class="btn btn-sm btn-outline-primary" @click="fetchApplications"><i class="bi bi-arrow-clockwise"></i> Refresh</button>
            </div>
          </div>
          
          <div class="card">
            <div class="table-responsive">
              <table class="table table-hover mb-0 align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Company</th>
                    <th>Job Title</th>
                    <th>Package (LPA)</th>
                    <th>Applied On</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="applications.length === 0">
                    <td colspan="5" class="text-center py-4 text-muted">You haven't applied to any drives yet.</td>
                  </tr>
                  <tr v-for="app in applications" :key="app.id">
                    <td class="fw-bold">
                      {{ app.company_name }}
                      <div v-if="app.warning" class="text-danger small fw-normal mt-1"><i class="bi bi-exclamation-triangle"></i> {{ app.warning }}</div>
                    </td>
                    <td>{{ app.job_title }}</td>
                    <td>{{ app.package_lpa || '-' }}</td>
                    <td>{{ app.application_date }}</td>
                    <td>
                      <span class="badge" :class="appBadge(app.status)">{{ app.status }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- settings form -->
        <div v-if="currentTab === 'settings'">
          <div class="page-header mb-4">
            <h3 class="m-0 fw-bold">Account Settings</h3>
          </div>
          
          <div class="row g-4">
            <div class="col-md-7">
              <div class="card">
                <div class="card-body p-4">
                  <h5 class="fw-bold mb-4 border-bottom pb-2">Profile Information</h5>
                  <form @submit.prevent="saveMyData">
                    <div class="mb-3">
                      <label class="form-label">Full Name</label>
                      <input type="text" class="form-control" v-model="profile.name" required>
                    </div>
                    
                    <div class="row mb-3">
                      <div class="col-md-4">
                        <label class="form-label">Branch</label>
                        <select class="form-select" v-model="profile.branch">
                          <option value="CSE">CSE</option>
                          <option value="ECE">ECE</option>
                          <option value="MECH">MECH</option>
                          <option value="CIVIL">CIVIL</option>
                          <option value="IT">IT</option>
                        </select>
                      </div>
                      <div class="col-md-4">
                        <label class="form-label">CGPA</label>
                        <input type="number" step="0.01" class="form-control" v-model="profile.cgpa">
                      </div>
                      <div class="col-md-4">
                        <label class="form-label">Year of Study</label>
                        <input type="number" class="form-control" v-model="profile.year">
                      </div>
                    </div>
                    
                    <div class="mb-3">
                      <label class="form-label">Profile Photo</label>
                      <input type="file" class="form-control" accept="image/*" @change="e => photoFile = e.target.files[0]">
                      <small class="text-muted" v-if="profile.profile_photo_path">You already have a photo uploaded. Uploading a new one will replace it.</small>
                    </div>

                    <div class="mb-3">
                      <label class="form-label">Resume (PDF)</label>
                      <input type="file" class="form-control" accept=".pdf" @change="e => resumeFile = e.target.files[0]">
                      <div v-if="profile.resume_file_path" class="mt-1">
                        <a :href="profile.resume_file_path" target="_blank" class="badge bg-secondary text-decoration-none"><i class="bi bi-file-pdf me-1"></i> View Current Resume</a>
                      </div>
                    </div>
                    
                    <div class="mb-4">
                      <label class="form-label">External Portfolio / Resume Link (Optional)</label>
                      <input type="url" class="form-control" v-model="profile.resume_link" placeholder="https://linkedin.com/in/... or Google Drive link">
                    </div>
                    
                    <button type="submit" class="btn btn-primary px-4" :disabled="savingProfile">
                      <span v-if="savingProfile" class="spinner-border spinner-border-sm me-2"></span>
                      Save Changes
                    </button>
                  </form>
                </div>
              </div>
            </div>
            
            <div class="col-md-5">
              <div class="card">
                <div class="card-body p-4">
                  <h5 class="fw-bold mb-4 border-bottom pb-2">Change Password</h5>
                  <form @submit.prevent="changePassword">
                    <div class="mb-3">
                      <label class="form-label">Current Password</label>
                      <input type="password" class="form-control" v-model="passwordForm.old_password" required>
                    </div>
                    <div class="mb-3">
                      <label class="form-label">New Password</label>
                      <input type="password" class="form-control" v-model="passwordForm.new_password" required>
                    </div>
                    <button type="submit" class="btn btn-outline-primary px-4" :disabled="changingPassword">
                      <span v-if="changingPassword" class="spinner-border spinner-border-sm me-2"></span>
                      Update Password
                    </button>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- popup for drive details -->
    <div class="modal fade" id="driveDetailsModal" tabindex="-1" aria-hidden="true" data-bs-backdrop="static">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow" v-if="selectedDrive">
          
          <!-- just showing details -->
          <div v-if="!confirmApplyState">
            <div class="modal-header border-bottom-0 pb-0">
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" @click="resetModal"></button>
            </div>
            
            <div class="modal-body pt-0">
              <div class="text-center mb-4">
                <img v-if="selectedDrive.company_logo" :src="selectedDrive.company_logo" class="rounded object-fit-cover mb-3 border shadow-sm" width="80" height="80">
                <i v-else class="bi bi-building fs-1 text-secondary d-block mb-2"></i>
                <h4 class="fw-bold text-dark mb-1">{{ selectedDrive.job_title }}</h4>
                <h5 class="text-primary">{{ selectedDrive.company_name }}</h5>
              </div>
              
              <div class="row g-3 mb-4 bg-light rounded p-3">
                <div class="col-md-4">
                  <p class="mb-1 text-muted small fw-bold"><i class="bi bi-cash-coin me-1"></i> Package</p>
                  <p class="fw-bold mb-0">{{ selectedDrive.package_lpa ? selectedDrive.package_lpa + ' LPA' : 'Not specified' }}</p>
                </div>
                <div class="col-md-4">
                  <p class="mb-1 text-muted small fw-bold"><i class="bi bi-geo-alt me-1"></i> Location</p>
                  <p class="fw-bold mb-0">{{ selectedDrive.location || 'Not specified' }}</p>
                </div>
                <div class="col-md-4">
                  <p class="mb-1 text-muted small fw-bold"><i class="bi bi-clock me-1"></i> Deadline</p>
                  <p class="fw-bold text-danger mb-0">{{ selectedDrive.application_deadline }}</p>
                </div>
                <div class="col-md-6 mt-3">
                  <p class="mb-1 text-muted small fw-bold"><i class="bi bi-mortarboard me-1"></i> Minimum CGPA</p>
                  <p class="fw-bold mb-0">{{ selectedDrive.cgpa_cutoff || 'No cutoff' }}</p>
                </div>
                <div class="col-md-6 mt-3">
                  <p class="mb-1 text-muted small fw-bold"><i class="bi bi-diagram-3 me-1"></i> Eligible Branches</p>
                  <p class="fw-bold mb-0">{{ selectedDrive.branch_eligibility || 'All branches' }}</p>
                </div>
              </div>
              
              <div v-if="selectedDrive.description">
                <h6 class="fw-bold mb-2">Job Description</h6>
                <div class="text-secondary" style="white-space: pre-wrap; font-size: 0.95rem; line-height: 1.6;">
                  {{ selectedDrive.description }}
                </div>
              </div>
            </div>
            
            <div class="modal-footer bg-light border-top-0 rounded-bottom">
              <div class="w-100">
                <button v-if="selectedDrive.applied" class="btn btn-success w-100" disabled>
                  <i class="bi bi-check-circle me-1"></i> You Have Already Applied
                </button>
                <button v-else class="btn btn-primary w-100 btn-lg shadow-sm" @click="confirmApplyState = true">
                  <i class="bi bi-send me-1"></i> Apply Now
                </button>
              </div>
            </div>
          </div>
          
          <!-- ask before applying -->
          <div v-else class="text-center p-5">
            <div class="mb-4">
              <i class="bi bi-question-circle text-primary" style="font-size: 4rem;"></i>
            </div>
            <h4 class="fw-bold mb-3">Confirm Application</h4>
            <p class="text-muted mb-4">
              Are you sure you want to apply for <strong>{{ selectedDrive.job_title }}</strong> at <strong>{{ selectedDrive.company_name }}</strong>?
              <br><small>Your profile details and uploaded resume will be shared with the company.</small>
            </p>
            
            <div class="d-flex justify-content-center gap-3">
              <button class="btn btn-outline-secondary px-4" @click="confirmApplyState = false" :disabled="applying">
                Cancel
              </button>
              <button class="btn btn-primary px-5 shadow-sm" @click="applyToDrive(selectedDrive.id)" :disabled="applying">
                <span v-if="applying" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-check2-circle me-1"></i> Yes, Apply
              </button>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentTab: 'drives',
      drives: [],
      applications: [],
      profile: { name: '', branch: '', cgpa: '', year: '', resume_link: '', resume_file_path: '', profile_photo_path: '' },
      passwordForm: { old_password: '', new_password: '' },
      photoFile: null,
      resumeFile: null,
      selectedDrive: null,
      confirmApplyState: false,
      applying: false,
      savingProfile: false,
      changingPassword: false,
      exporting: false
    }
  },
  watch: {
    currentTab(val) {
      if (val === 'drives') this.getAllPlacements();
      if (val === 'applications') this.fetchApplications();
      if (val === 'settings') this.loadMyData();
    }
  },
  mounted() {
    this.getAllPlacements();
    this.loadMyData();
  },
  methods: {
    // get available drives from db
    async getAllPlacements() {
      try {
        const res = await axios.get('/api/student/drives');
        this.drives = res.data;
      } catch (err) { console.error(err); }
    },
    // get student's applications
    async fetchApplications() {
      try {
        const res = await axios.get('/api/student/applications');
        this.applications = res.data;
      } catch (err) { console.error(err); }
    },
    // get user profile details
    async loadMyData() {
      try {
        const res = await axios.get('/api/student/profile');
        this.profile = res.data;
      } catch (err) { console.error(err); }
    },
    // save profile changes
    async saveMyData() {
      this.savingProfile = true;
      try {
        const formData = new FormData();
        formData.append('name', this.profile.name);
        formData.append('branch', this.profile.branch);
        formData.append('cgpa', this.profile.cgpa);
        formData.append('year', this.profile.year);
        formData.append('resume_link', this.profile.resume_link);
        
        if (this.photoFile) formData.append('photo', this.photoFile);
        if (this.resumeFile) formData.append('resume', this.resumeFile);
        
        await axios.put('/api/student/profile', formData);
        
        alert('Profile updated successfully!');
        this.photoFile = null;
        this.resumeFile = null;
        this.loadMyData();
      } catch (err) {
        alert(err.response?.data?.msg || 'Failed to update profile');
      } finally {
        this.savingProfile = false;
      }
    },
    // change the user password
    async changePassword() {
      this.changingPassword = true;
      try {
        await axios.post('/api/auth/change-password', this.passwordForm);
        alert('Password changed successfully');
        this.passwordForm.old_password = '';
        this.passwordForm.new_password = '';
      } catch (err) {
        alert(err.response?.data?.msg || 'Error changing password');
      } finally {
        this.changingPassword = false;
      }
    },
    openDriveDetails(drive) {
      this.selectedDrive = drive;
      this.confirmApplyState = false;
    },
    resetModal() {
      setTimeout(() => {
        this.selectedDrive = null;
        this.confirmApplyState = false;
      }, 300);
    },
    // apply for a drive
    async applyToDrive(driveId) {
      this.applying = true;
      try {
        await axios.post(`/api/student/drives/${driveId}/apply`);
        
        const modalEl = document.getElementById('driveDetailsModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        
        this.getAllPlacements();
        this.resetModal();
      } catch (err) {
        alert(err.response?.data?.msg || 'Failed to apply');
        this.confirmApplyState = false;
      } finally {
        this.applying = false;
      }
    },
    appBadge(status) {
      if (status === 'Selected') return 'bg-success';
      if (status === 'Shortlisted') return 'bg-primary';
      if (status === 'Rejected') return 'bg-danger';
      return 'bg-secondary';
    },
    // queue celery job then poll until done
    async downloadStudentData() {
      this.exporting = true;
      try {
        // trigger the async task
        const res = await axios.post('/api/student/export-csv');
        const taskId = res.data.task_id;

        // poll every 2 seconds for result
        const poll = setInterval(async () => {
          try {
            const statusRes = await axios.get(`/api/student/export-csv/status/${taskId}`);
            const state = statusRes.data.state;

            if (state === 'SUCCESS') {
              clearInterval(poll);
              this.exporting = false;

              // build a blob from the csv string returned by the task
              const csvContent = statusRes.data.result.csv_content;
              const filename = statusRes.data.result.filename || 'applications.csv';
              const blob = new Blob([csvContent], { type: 'text/csv' });
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute('download', filename);
              document.body.appendChild(link);
              link.click();
              link.remove();
              window.URL.revokeObjectURL(url);

            } else if (state === 'FAILURE') {
              clearInterval(poll);
              this.exporting = false;
              alert('Export failed. Please try again.');
            }
            // PENDING / STARTED — keep polling
          } catch (e) {
            clearInterval(poll);
            this.exporting = false;
            console.error('Polling error', e);
          }
        }, 2000);

      } catch (err) {
        this.exporting = false;
        alert('Failed to start export. Make sure the Celery worker is running.');
        console.error(err);
      }
    }
  }
}
</script>

<style scoped>
.hover-elevate {
  transition: transform 0.2s, box-shadow 0.2s;
}
.hover-elevate:hover {
  transform: translateY(-3px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
}
</style>
