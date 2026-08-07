<template>
  <div class="container-fluid py-4">
    <div class="row">
      <!-- Sidebar -->
      <div class="col-md-2 mb-4">
        <div class="card p-3">
          <h5 class="fw-bold text-center border-bottom pb-3 mb-3">Admin Panel</h5>
          <a class="sidebar-link" :class="{active: currentTab === 'overview'}" href="#" @click.prevent="currentTab = 'overview'">
            <i class="bi bi-speedometer2 me-2"></i> Overview
          </a>
          <a class="sidebar-link" :class="{active: currentTab === 'companies'}" href="#" @click.prevent="currentTab = 'companies'">
            <i class="bi bi-building me-2"></i> Companies
          </a>
          <a class="sidebar-link" :class="{active: currentTab === 'students'}" href="#" @click.prevent="currentTab = 'students'">
            <i class="bi bi-people me-2"></i> Students
          </a>
          <a class="sidebar-link" :class="{active: currentTab === 'drives'}" href="#" @click.prevent="currentTab = 'drives'">
            <i class="bi bi-briefcase me-2"></i> Drives
          </a>
          <a class="sidebar-link" :class="{active: currentTab === 'analytics'}" href="#" @click.prevent="currentTab = 'analytics'">
            <i class="bi bi-bar-chart-line me-2"></i> Analytics
          </a>
          <a class="sidebar-link" :class="{active: currentTab === 'settings'}" href="#" @click.prevent="currentTab = 'settings'">
            <i class="bi bi-gear me-2"></i> Settings & Reports
          </a>
        </div>
      </div>
      
      <!-- Main Content -->
      <div class="col-md-10">
        
        <!-- Overview Tab -->
        <div v-if="currentTab === 'overview'">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 class="m-0 fw-bold">Dashboard Overview</h3>
            <button class="btn btn-sm btn-outline-primary" @click="fetchStats"><i class="bi bi-arrow-clockwise"></i> Refresh</button>
          </div>
          
          <!-- stats grid -->
          <div class="row g-4 mb-4">
            <div class="col-md-4 col-lg-2">
              <div class="card stat-card">
                <h2 class="text-primary">{{ stats.total_students }}</h2>
                <p>Students</p>
              </div>
            </div>
            <div class="col-md-4 col-lg-2">
              <div class="card stat-card">
                <h2 class="text-success">{{ stats.total_companies }}</h2>
                <p>Companies</p>
              </div>
            </div>
            <div class="col-md-4 col-lg-2">
              <div class="card stat-card">
                <h2 class="text-info">{{ stats.approved_companies }}</h2>
                <p>Approved Co.</p>
              </div>
            </div>
            <div class="col-md-4 col-lg-2">
              <div class="card stat-card">
                <h2 class="text-warning">{{ stats.total_drives }}</h2>
                <p>Drives</p>
              </div>
            </div>
            <div class="col-md-4 col-lg-2">
              <div class="card stat-card">
                <h2 class="text-secondary">{{ stats.total_applications }}</h2>
                <p>Applications</p>
              </div>
            </div>
            <div class="col-md-4 col-lg-2">
              <div class="card stat-card">
                <h2 class="text-success">{{ stats.selected_students }}</h2>
                <p>Selected</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Companies Tab -->
        <div v-if="currentTab === 'companies'">
          <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
            <h3 style="margin: 0; font-weight: bold;">Manage Companies</h3>
            <div style="display: flex; width: 300px;">
              <span style="background: white; border: 1px solid #ccc; padding: 5px 10px;"><i class="bi bi-search"></i></span>
              <input type="text" class="form-control" placeholder="Search by name, email, ID..." v-model="searchCompaniesQuery">
            </div>
          </div>
          
          <div class="card table-responsive">
            <table class="table table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Approved</th>
                  <th>Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in filteredCompanies" :key="c.id">
                  <td class="text-muted">#{{ c.id }}</td>
                  <td class="fw-bold">
                    <img v-if="c.logo_path" :src="c.logo_path" class="rounded me-2 object-fit-cover border" width="28" height="28">
                    <i v-else class="bi bi-building text-secondary me-2 fs-5"></i>
                    {{ c.name }}
                  </td>
                  <td>{{ c.email }}</td>
                  <td>
                    <span class="badge" :class="c.approved ? 'bg-success' : 'bg-warning text-dark'">{{ c.approved ? 'Yes' : 'Pending' }}</span>
                  </td>
                  <td>
                    <span class="badge" :class="c.active ? 'bg-success' : 'bg-danger'">{{ c.active ? 'Active' : 'Blocked' }}</span>
                  </td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#companyModal" @click="selectedCompany = c">
                      <i class="bi bi-eye"></i> View Details
                    </button>
                  </td>
                </tr>
                <tr v-if="filteredCompanies.length === 0">
                  <td colspan="6" class="text-center text-muted py-4">No companies found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Students Tab -->
        <div v-if="currentTab === 'students'">
          <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
            <h3 style="margin: 0; font-weight: bold;">Manage Students</h3>
            <div style="display: flex; width: 300px;">
              <span style="background: white; border: 1px solid #ccc; padding: 5px 10px;"><i class="bi bi-search"></i></span>
              <input type="text" class="form-control" placeholder="Search by name, email, ID..." v-model="searchStudentsQuery">
            </div>
          </div>
          
          <div class="card table-responsive">
            <table class="table table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Branch</th>
                  <th>Year</th>
                  <th>Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in filteredStudents" :key="s.id">
                  <td class="text-muted">#{{ s.id }}</td>
                  <td class="fw-bold">
                    <img v-if="s.profile_photo_path" :src="s.profile_photo_path" class="rounded-circle me-2 object-fit-cover border" width="28" height="28">
                    <i v-else class="bi bi-person-circle text-secondary me-2 fs-5"></i>
                    {{ s.name }}
                  </td>
                  <td>{{ s.email }}</td>
                  <td>{{ s.branch }}</td>
                  <td>{{ s.year }}</td>
                  <td>
                    <span class="badge" :class="s.active ? 'bg-success' : 'bg-danger'">{{ s.active ? 'Active' : 'Blocked' }}</span>
                  </td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#studentModal" @click="selectedStudent = s">
                      <i class="bi bi-eye"></i> View Details
                    </button>
                  </td>
                </tr>
                <tr v-if="filteredStudents.length === 0">
                  <td colspan="7" class="text-center text-muted py-4">No students found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Drives Tab -->
        <div v-if="currentTab === 'drives'">
          <div>
            <h3 style="margin: 0; font-weight: bold; margin-bottom: 15px;">Manage Placement Drives</h3>
          </div>
          
          <div class="card table-responsive">
            <table class="table table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Package (LPA)</th>
                  <th>Deadline</th>
                  <th>Applicants</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="d in drives" :key="d.id">
                  <td class="fw-bold">{{ d.job_title }}</td>
                  <td>{{ d.company_name }}</td>
                  <td>{{ d.package_lpa || '-' }}</td>
                  <td>{{ d.application_deadline }}</td>
                  <td>{{ d.applicant_count }}</td>
                  <td>
                    <span class="badge" :class="statusBadge(d.status)">{{ d.status }}</span>
                  </td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#driveModal" @click="selectedDrive = d">
                      <i class="bi bi-eye"></i> View Details
                    </button>
                  </td>
                </tr>
                <tr v-if="drives.length === 0">
                  <td colspan="7" class="text-center text-muted py-4">No drives created yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Analytics Tab -->
        <div v-if="currentTab === 'analytics'">
          <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <h3 style="margin: 0; font-weight: bold;">Placement Analytics</h3>
            <button class="btn btn-sm btn-outline-primary" @click="fetchAnalytics"><i class="bi bi-arrow-clockwise"></i> Refresh</button>
          </div>

          <div v-if="!analyticsData" class="text-center py-5 text-muted">
            <i class="bi bi-bar-chart-line" style="font-size: 3rem;"></i>
            <p class="mt-3">Loading analytics...</p>
          </div>

          <div v-else>
            <div class="row g-4 mb-4">
              <div class="col-md-6">
                <div class="card card-body">
                  <h6 class="fw-bold mb-3"><i class="bi bi-bar-chart me-2"></i>Applications by Branch</h6>
                  <canvas id="branchChart" height="260"></canvas>
                </div>
              </div>
              <div class="col-md-6">
                <div class="card card-body">
                  <h6 class="fw-bold mb-3"><i class="bi bi-pie-chart me-2"></i>Drive Status Distribution</h6>
                  <canvas id="driveStatusChart" height="260"></canvas>
                </div>
              </div>
            </div>
            <div class="row g-4">
              <div class="col-md-6">
                <div class="card card-body">
                  <h6 class="fw-bold mb-3"><i class="bi bi-building me-2"></i>Company Recruitment Breakdown</h6>
                  <canvas id="companyChart" height="260"></canvas>
                </div>
              </div>
              <div class="col-md-6">
                <div class="card card-body">
                  <h6 class="fw-bold mb-3"><i class="bi bi-graph-up me-2"></i>Application Status Overview</h6>
                  <canvas id="appStatusChart" height="260"></canvas>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Settings & Reports Tab -->
        <div v-if="currentTab === 'settings'">
          <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <h3 style="margin: 0; font-weight: bold;">Settings & Reports</h3>
          </div>
          
          <div class="row g-4">
            <div class="col-md-6">
              <div class="card card-body h-100 shadow-sm border-0">
                <h5 class="fw-bold mb-3 border-bottom pb-2">Manual Triggers</h5>
                <p class="text-muted small mb-4">Instantly trigger background tasks. Useful for testing and presentations.</p>
                
                <div class="d-grid gap-3">
                  <button class="btn btn-primary" @click="triggerReport" :disabled="triggeringReport">
                    <span v-if="triggeringReport" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-envelope-paper me-2"></i> Send Monthly Report Now
                  </button>
                  
                  <button class="btn btn-info text-white" @click="triggerReminders" :disabled="triggeringReminders">
                    <span v-if="triggeringReminders" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-bell me-2"></i> Send Student Reminders Now
                  </button>
                </div>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="card card-body h-100 shadow-sm border-0">
                <h5 class="fw-bold mb-3 border-bottom pb-2">Scheduled Job Configurations</h5>
                <p class="text-muted small mb-3">Configure when background tasks run automatically.</p>
                
                <form @submit.prevent="saveSettings">
                  <div class="mb-3">
                    <label class="form-label fw-bold small">Monthly Report Schedule</label>
                    <div class="input-group">
                      <span class="input-group-text bg-light text-muted">Day</span>
                      <input type="number" class="form-control" v-model="settingsForm.report_day" min="1" max="28" required>
                      <span class="input-group-text bg-light text-muted">Hour</span>
                      <input type="number" class="form-control" v-model="settingsForm.report_hour" min="0" max="23" required>
                    </div>
                  </div>
                  
                  <div class="mb-4">
                    <label class="form-label fw-bold small">Daily Student Reminders</label>
                    <div class="input-group">
                      <span class="input-group-text bg-light text-muted">Hour</span>
                      <input type="number" class="form-control" v-model="settingsForm.reminder_hour" min="0" max="23" required>
                    </div>
                  </div>
                  
                  <button type="submit" class="btn btn-success w-100" :disabled="savingSettings">
                    <span v-if="savingSettings" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-save me-2"></i> Save Schedules
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Modals -->
    <!-- Company Modal -->
    <div class="modal fade" id="companyModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedCompany">
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold">
              <img v-if="selectedCompany.logo_path" :src="selectedCompany.logo_path" class="rounded me-2 object-fit-cover border" width="30" height="30">
              {{ selectedCompany.name }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row mb-3">
              <!-- company contact info -->
              <div class="col-md-6">
                <p class="mb-1 text-muted small">Email</p>
                <p class="fw-bold">{{ selectedCompany.email }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small">Phone</p>
                <p class="fw-bold">{{ selectedCompany.phone || 'N/A' }}</p>
              </div>
              
              <!-- hr details -->
              <div class="col-md-6">
                <p class="mb-1 text-muted small">HR Name</p>
                <p class="fw-bold">{{ selectedCompany.hr_name || 'N/A' }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small">HR Contact Details</p>
                <p class="fw-bold">{{ selectedCompany.hr_contact || 'N/A' }}</p>
              </div>
              
              <!-- extra info -->
              <div class="col-md-6">
                <p class="mb-1 text-muted small">Website</p>
                <p class="fw-bold">
                  <a v-if="selectedCompany.website" :href="selectedCompany.website" target="_blank">{{ selectedCompany.website }}</a>
                  <span v-else>N/A</span>
                </p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small">Account Status</p>
                <p>
                  <span class="badge me-2" :class="selectedCompany.approved ? 'bg-success' : 'bg-warning text-dark'">{{ selectedCompany.approved ? 'Approved' : 'Pending Approval' }}</span>
                  <span class="badge" :class="selectedCompany.active ? 'bg-success' : 'bg-danger'">{{ selectedCompany.active ? 'Active' : 'Blocked' }}</span>
                </p>
              </div>
            </div>
            
            <div style="display: flex; gap: 10px; border-top: 1px solid #ccc; padding-top: 15px; margin-top: 20px;">
              <button v-if="!selectedCompany.approved" class="btn btn-success flex-grow-1" @click="approveCompany(selectedCompany.id)" data-bs-dismiss="modal">
                <i class="bi bi-check-circle"></i> Approve Company
              </button>
              <button v-if="!selectedCompany.approved" class="btn btn-danger flex-grow-1" @click="rejectCompany(selectedCompany.id)" data-bs-dismiss="modal">
                <i class="bi bi-x-circle"></i> Reject (Delete)
              </button>
              <button class="btn flex-grow-1" :class="selectedCompany.active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggleUser(selectedCompany.user_id, 'companies')">
                <i class="bi" :class="selectedCompany.active ? 'bi-lock' : 'bi-unlock'"></i> {{ selectedCompany.active ? 'Block Access' : 'Unblock Access' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Student Modal -->
    <div class="modal fade" id="studentModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedStudent">
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold">
              <img v-if="selectedStudent.profile_photo_path" :src="selectedStudent.profile_photo_path" class="rounded-circle me-2 object-fit-cover border" width="30" height="30">
              {{ selectedStudent.name }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <!-- student details -->
            <div class="row mb-3">
              <div class="col-md-6">
                <p class="mb-1 text-muted small">Email</p>
                <p class="fw-bold">{{ selectedStudent.email }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small">Phone</p>
                <p class="fw-bold">{{ selectedStudent.phone || 'N/A' }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small">Branch</p>
                <p class="fw-bold">{{ selectedStudent.branch || 'N/A' }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small">CGPA</p>
                <p class="fw-bold">{{ selectedStudent.cgpa || 'N/A' }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small">Year</p>
                <p class="fw-bold">{{ selectedStudent.year || 'N/A' }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small">Account Status</p>
                <p>
                  <span class="badge" :class="selectedStudent.active ? 'bg-success' : 'bg-danger'">{{ selectedStudent.active ? 'Active' : 'Blocked' }}</span>
                </p>
              </div>
            </div>
            
            <div class="mt-3 px-2" v-if="selectedStudent.resume_file_path || selectedStudent.resume_link">
              <h6 class="fw-bold text-start border-bottom pb-2 mb-2">Resume & Links</h6>
              <div style="display: flex; gap: 10px;">
                <a v-if="selectedStudent.resume_file_path" :href="selectedStudent.resume_file_path" target="_blank" class="btn btn-sm btn-outline-primary">
                  <i class="bi bi-file-pdf"></i> View Resume PDF
                </a>
                <a v-if="selectedStudent.resume_link" :href="selectedStudent.resume_link" target="_blank" class="btn btn-sm btn-outline-secondary">
                  <i class="bi bi-link"></i> External Link
                </a>
              </div>
            </div>
            
            <div style="display: flex; gap: 10px; border-top: 1px solid #ccc; padding-top: 15px; margin-top: 20px;">
              <button class="btn flex-grow-1" :class="selectedStudent.active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggleUser(selectedStudent.user_id, 'students')">
                <i class="bi" :class="selectedStudent.active ? 'bi-lock' : 'bi-unlock'"></i> {{ selectedStudent.active ? 'Block Access' : 'Unblock Access' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Drive Modal -->
    <div class="modal fade" id="driveModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedDrive">
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold">
              <img v-if="selectedDrive.company_logo" :src="selectedDrive.company_logo" class="rounded me-2 object-fit-cover border" width="30" height="30">
              {{ selectedDrive.job_title }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
              <h5 class="text-primary mb-0">{{ selectedDrive.company_name }}</h5>
              <span class="badge fs-6" :class="statusBadge(selectedDrive.status)">{{ selectedDrive.status }}</span>
            </div>
            
            <div class="row g-3 mb-4">
              <!-- job details -->
              <div class="col-md-6">
                <p class="mb-1 text-muted small"><i class="bi bi-cash-coin me-1"></i> Package (LPA)</p>
                <p class="fw-bold">{{ selectedDrive.package_lpa || 'Not specified' }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small"><i class="bi bi-geo-alt me-1"></i> Location</p>
                <p class="fw-bold">{{ selectedDrive.location || 'Not specified' }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small"><i class="bi bi-mortarboard me-1"></i> CGPA Cutoff</p>
                <p class="fw-bold">{{ selectedDrive.cgpa_cutoff || 'No cutoff' }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small"><i class="bi bi-diagram-3 me-1"></i> Branch Eligibility</p>
                <p class="fw-bold">{{ selectedDrive.branch_eligibility || 'All branches' }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small"><i class="bi bi-clock me-1"></i> Application Deadline</p>
                <p class="fw-bold">{{ selectedDrive.application_deadline }}</p>
              </div>
              <div class="col-md-6">
                <p class="mb-1 text-muted small"><i class="bi bi-people me-1"></i> Total Applicants</p>
                <p class="fw-bold">{{ selectedDrive.applicant_count }}</p>
              </div>
            </div>
            
            <div v-if="selectedDrive.description" class="mb-4">
              <p class="mb-1 text-muted small">Description</p>
              <div class="p-3 bg-light rounded" style="white-space: pre-wrap;">{{ selectedDrive.description }}</div>
            </div>
            
            <div class="mb-4 border border-info rounded">
              <div class="bg-info bg-opacity-10 p-2 cursor-pointer" style="display: flex; justify-content: space-between; align-items: center;" @click="fetchDriveApps(selectedDrive.id)">
                <h6 class="m-0 text-info fw-bold px-2"><i class="bi bi-people-fill me-2"></i> View Applicants ({{ selectedDrive.applicant_count }})</h6>
                <button class="btn btn-sm btn-link text-info"><i class="bi" :class="driveApps ? 'bi-chevron-up' : 'bi-chevron-down'"></i></button>
              </div>
              
              <div v-if="loadingApps" class="text-center py-3"><span class="spinner-border spinner-border-sm text-info"></span></div>
              <div v-else-if="driveApps && driveApps.length === 0" class="p-3 text-center text-muted">No applications found.</div>
              <div v-else-if="driveApps && driveApps.length > 0" class="p-2 table-responsive">
                <table class="table table-sm table-hover mb-0 align-middle">
                  <thead class="table-light">
                    <tr>
                      <th>Student</th>
                      <th>Branch</th>
                      <th>CGPA</th>
                      <th>Status</th>
                      <th>Resume</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="app in driveApps" :key="app.application_id">
                      <td>
                        <img v-if="app.profile_photo_path" :src="app.profile_photo_path" class="rounded-circle me-1 object-fit-cover" width="20" height="20">
                        {{ app.student_name }}
                      </td>
                      <td>{{ app.branch }}</td>
                      <td>{{ app.cgpa }}</td>
                      <td><span class="badge" :class="appBadge(app.status)">{{ app.status }}</span></td>
                      <td>
                        <a v-if="app.resume_file_path" :href="app.resume_file_path" target="_blank" class="text-primary me-2" title="Resume"><i class="bi bi-file-pdf"></i></a>
                        <a v-if="app.resume_link" :href="app.resume_link" target="_blank" class="text-secondary" title="External Link"><i class="bi bi-link"></i></a>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <div style="display: flex; gap: 10px; border-top: 1px solid #ccc; padding-top: 15px;">
              <template v-if="selectedDrive.status === 'Pending'">
                <button class="btn btn-success flex-grow-1" @click="approveDrive(selectedDrive.id)" data-bs-dismiss="modal">
                  <i class="bi bi-check-circle"></i> Approve Drive
                </button>
                <button class="btn btn-danger flex-grow-1" @click="rejectDrive(selectedDrive.id)" data-bs-dismiss="modal">
                  <i class="bi bi-x-circle"></i> Reject Drive
                </button>
              </template>
              <template v-else>
                <button class="btn btn-warning flex-grow-1 text-dark" @click="unapproveDrive(selectedDrive.id)" data-bs-dismiss="modal">
                  <i class="bi bi-arrow-counterclockwise"></i> Unapprove (Set to Pending)
                </button>
              </template>
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
      currentTab: 'overview',
      stats: { total_students: 0, total_companies: 0, approved_companies: 0, total_drives: 0, approved_drives: 0, total_applications: 0, selected_students: 0 },
      companies: [],
      students: [],
      drives: [],
      searchCompaniesQuery: '',
      searchStudentsQuery: '',
      selectedCompany: null,
      selectedStudent: null,
      selectedDrive: null,
      driveApps: null,
      loadingApps: false,
      analyticsData: null,
      chartInstances: {},
      settingsForm: { report_day: 1, report_hour: 10, reminder_hour: 9 },
      triggeringReport: false,
      triggeringReminders: false,
      savingSettings: false
    }
  },
  computed: {
    filteredCompanies() {
      if (!this.searchCompaniesQuery) return this.companies;
      const q = this.searchCompaniesQuery.toLowerCase();
      return this.companies.filter(c => 
        String(c.id).includes(q) || 
        c.name.toLowerCase().includes(q) || 
        c.email.toLowerCase().includes(q)
      );
    },
    filteredStudents() {
      if (!this.searchStudentsQuery) return this.students;
      const q = this.searchStudentsQuery.toLowerCase();
      return this.students.filter(s => 
        String(s.id).includes(q) || 
        s.name.toLowerCase().includes(q) || 
        s.email.toLowerCase().includes(q)
      );
    }
  },
  mounted() {
    this.fetchStats();
  },
  methods: {
    // get stats for main page
    async fetchStats() {
      try {
        const res = await axios.get('/api/admin/stats');
        this.stats = res.data;
      } catch (err) { console.error(err); }
    },
    
    async fetchSettings() {
      try {
        const res = await axios.get('/api/admin/settings');
        if (res.data.report_day !== undefined) this.settingsForm = res.data;
      } catch (err) { console.error(err); }
    },
    
    async saveSettings() {
      this.savingSettings = true;
      try {
        await axios.post('/api/admin/settings', this.settingsForm);
        alert('Settings saved successfully!');
      } catch (err) {
        alert('Failed to save settings');
      } finally {
        this.savingSettings = false;
      }
    },
    
    async triggerReport() {
      this.triggeringReport = true;
      try {
        await axios.post('/api/admin/trigger-report');
        alert('Monthly Report triggered! Check the Celery logs and your email/webhook.');
      } catch (err) {
        alert('Failed to trigger report');
      } finally {
        this.triggeringReport = false;
      }
    },
    
    async triggerReminders() {
      this.triggeringReminders = true;
      try {
        await axios.post('/api/admin/trigger-reminders');
        alert('Student Reminders triggered! Check the Celery logs and your webhook.');
      } catch (err) {
        alert('Failed to trigger reminders');
      } finally {
        this.triggeringReminders = false;
      }
    },
    
    // load companies from api
    async fetchCompanies() {
      try {
        const res = await axios.get('/api/admin/companies');
        this.companies = res.data;
      } catch (err) { console.error(err); }
    },
    
    // get all students
    async fetchStudents() {
      try {
        const res = await axios.get('/api/admin/students');
        this.students = res.data;
      } catch (err) { console.error(err); }
    },
    
    async fetchDrives() {
      try {
        const res = await axios.get('/api/admin/drives');
        this.drives = res.data;
      } catch (err) { console.error(err); }
    },
    
    async approveCompany(id) {
      try {
        await axios.post(`/api/admin/companies/${id}/approve`);
        this.fetchCompanies();
        this.fetchStats();
      } catch (err) { alert(err.response?.data?.msg || 'Error'); }
    },
    
    async rejectCompany(id) {
      if (!confirm('This will permanently delete the company account. Continue?')) return;
      try {
        await axios.post(`/api/admin/companies/${id}/reject`);
        this.fetchCompanies();
        this.fetchStats();
      } catch (err) { alert(err.response?.data?.msg || 'Error'); }
    },
    
    async toggleUser(userId, tabContext) {
      try {
        await axios.post(`/api/admin/users/${userId}/toggle`);
        if (tabContext === 'companies') {
          this.fetchCompanies();
          if (this.selectedCompany) this.selectedCompany.active = !this.selectedCompany.active;
        }
        if (tabContext === 'students') {
          this.fetchStudents();
          if (this.selectedStudent) this.selectedStudent.active = !this.selectedStudent.active;
        }
      } catch (err) { alert(err.response?.data?.msg || 'Error'); }
    },
    
    async approveDrive(id) {
      try {
        await axios.post(`/api/admin/drives/${id}/approve`);
        this.fetchDrives();
        this.fetchStats();
      } catch (err) { alert(err.response?.data?.msg || 'Error'); }
    },
    
    async rejectDrive(id) {
      try {
        await axios.post(`/api/admin/drives/${id}/reject`);
        this.fetchDrives();
        this.fetchStats();
      } catch (err) { alert(err.response?.data?.msg || 'Error'); }
    },
    
    async unapproveDrive(id) {
      try {
        await axios.post(`/api/admin/drives/${id}/unapprove`);
        this.fetchDrives();
        this.fetchStats();
      } catch (err) { alert(err.response?.data?.msg || 'Error'); }
    },
    
    statusBadge(status) {
      if (status === 'Approved') return 'bg-success';
      if (status === 'Pending') return 'bg-warning text-dark';
      if (status === 'Rejected') return 'bg-danger';
      return 'bg-secondary';
    },
    
    appBadge(status) {
      if (status === 'Selected') return 'bg-success';
      if (status === 'Shortlisted') return 'bg-primary';
      if (status === 'Rejected') return 'bg-danger';
      return 'bg-secondary';
    },
    
    async fetchDriveApps(driveId) {
      if (this.driveApps !== null) {
        this.driveApps = null; // Toggle off
        return;
      }
      this.loadingApps = true;
      try {
        const res = await axios.get(`/api/admin/drives/${driveId}/applications`);
        this.driveApps = res.data;
      } catch (err) { console.error(err); }
      this.loadingApps = false;
    },
    
    async fetchAnalytics() {
      try {
        const res = await axios.get('/api/admin/analytics');
        this.analyticsData = res.data;
        this.$nextTick(() => this.renderCharts());
      } catch (err) { console.error(err); }
    },
    
    // show charts
    renderCharts() {
      // destroy old charts
      if (this.chartInstances.branch) this.chartInstances.branch.destroy();
      if (this.chartInstances.driveStatus) this.chartInstances.driveStatus.destroy();
      if (this.chartInstances.company) this.chartInstances.company.destroy();
      if (this.chartInstances.appStatus) this.chartInstances.appStatus.destroy();

      // 1. Applications by Branch
      const branchCtx = document.getElementById('branchChart');
      if (branchCtx && this.analyticsData.branch_applications) {
        this.chartInstances.branch = new Chart(branchCtx, {
          type: 'bar',
          data: {
            labels: this.analyticsData.branch_applications.labels,
            datasets: [{
              label: 'Applications',
              data: this.analyticsData.branch_applications.data,
              backgroundColor: ['#ffffff', '#28a745', '#ffc107', '#dc3545', '#17a2b8', '#6f42c1', '#fd7e14', '#20c997'].slice(0, this.analyticsData.branch_applications.labels.length),
              borderWidth: 0,
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
              x: { ticks: { color: '#aaaaaa', font: { family: "'Segoe UI'", size: 12 } }, grid: { color: '#222' } },
              y: { ticks: { color: '#aaaaaa', font: { family: "'Segoe UI'", size: 12 } }, grid: { color: '#222' }, beginAtZero: true }
            }
          }
        });
      }

      // 2. Drive Status
      const driveCtx = document.getElementById('driveStatusChart');
      if (driveCtx && this.analyticsData.drive_status) {
        this.chartInstances.driveStatus = new Chart(driveCtx, {
          type: 'doughnut',
          data: {
            labels: this.analyticsData.drive_status.labels,
            datasets: [{
              data: this.analyticsData.drive_status.data,
              backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
              borderColor: '#121212',
              borderWidth: 3
            }]
          },
          options: {
            responsive: true,
            cutout: '60%',
            plugins: { legend: { labels: { color: '#aaaaaa', font: { family: "'Segoe UI'", size: 12 } } } }
          }
        });
      }

      // 3. Company Recruitment
      const companyCtx = document.getElementById('companyChart');
      if (companyCtx && this.analyticsData.company_recruitment) {
        this.chartInstances.company = new Chart(companyCtx, {
          type: 'bar',
          data: {
            labels: this.analyticsData.company_recruitment.labels,
            datasets: [{
              label: 'Applicants',
              data: this.analyticsData.company_recruitment.data,
              backgroundColor: '#ffffff',
              borderWidth: 0,
              borderRadius: 6
            }]
          },
          options: {
            indexAxis: 'y',
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
              x: { ticks: { color: '#aaaaaa', font: { family: "'Segoe UI'", size: 12 } }, grid: { color: '#222' }, beginAtZero: true },
              y: { ticks: { color: '#aaaaaa', font: { family: "'Segoe UI'", size: 12 } }, grid: { color: '#222' } }
            }
          }
        });
      }

      // 4. Application Status
      const appCtx = document.getElementById('appStatusChart');
      if (appCtx && this.analyticsData.application_status) {
        this.chartInstances.appStatus = new Chart(appCtx, {
          type: 'pie',
          data: {
            labels: this.analyticsData.application_status.labels,
            datasets: [{
              data: this.analyticsData.application_status.data,
              backgroundColor: ['#6c757d', '#ffc107', '#28a745', '#dc3545'],
              borderColor: '#121212',
              borderWidth: 3
            }]
          },
          options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#aaaaaa', font: { family: "'Segoe UI'", size: 12 } } } }
          }
        });
      }
    }
  },
  watch: {
    selectedDrive() {
      this.driveApps = null;
    },
    currentTab(val) {
      if (val === 'overview') this.fetchStats();
      if (val === 'companies') this.fetchCompanies();
      if (val === 'students') this.fetchStudents();
      if (val === 'drives') this.fetchDrives();
      if (val === 'analytics') this.fetchAnalytics();
      if (val === 'settings') this.fetchSettings();
    }
  }
}
</script>
