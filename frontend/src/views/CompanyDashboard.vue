<template>
  <div class="container-fluid py-4">
    <div class="row">
      <!-- Sidebar -->
      <div class="col-md-2 mb-4">
        <div class="card p-3">
          <div class="text-center mb-3">
            <img v-if="profile.logo_path" :src="profile.logo_path" class="rounded-circle mb-2 object-fit-cover border" width="80" height="80" alt="Logo">
            <i v-else class="bi bi-building fs-1 text-secondary d-block mb-2"></i>
            <h6 class="fw-bold mt-2 mb-0">{{ profile.name || companyName }}</h6>
          </div>
          <hr class="mt-0">
          <a class="sidebar-link" :class="{active: currentTab === 'overview'}" href="#" @click.prevent="currentTab = 'overview'">
            <i class="bi bi-speedometer2 me-2"></i> Overview
          </a>
          <a class="sidebar-link" :class="{active: currentTab === 'create'}" href="#" @click.prevent="currentTab = 'create'">
            <i class="bi bi-plus-circle me-2"></i> Create Drive
          </a>
          <a class="sidebar-link" :class="{active: currentTab === 'drives'}" href="#" @click.prevent="currentTab = 'drives'">
            <i class="bi bi-briefcase me-2"></i> My Drives
          </a>
          <a class="sidebar-link" :class="{active: currentTab === 'settings'}" href="#" @click.prevent="currentTab = 'settings'">
            <i class="bi bi-gear me-2"></i> Settings
          </a>
        </div>
      </div>
      
      <!-- Main Content -->
      <div class="col-md-10">
        
        <!-- Overview -->
        <div v-if="currentTab === 'overview'">
          <div class="page-header mb-4">
            <h3 class="m-0 fw-bold">Welcome, {{ profile.name || companyName }}!</h3>
          </div>
          <div class="row g-4">
            <div class="col-md-3">
              <div class="card stat-card p-4 text-center">
                <h2 class="text-primary fw-bold">{{ drives.length }}</h2>
                <p class="text-muted mb-0 fw-medium">Total Drives</p>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card stat-card p-4 text-center">
                <h2 class="text-warning fw-bold">{{ drives.filter(d => d.status === 'Pending').length }}</h2>
                <p class="text-muted mb-0 fw-medium">Pending</p>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card stat-card p-4 text-center">
                <h2 class="text-success fw-bold">{{ drives.filter(d => d.status === 'Approved').length }}</h2>
                <p class="text-muted mb-0 fw-medium">Approved</p>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card stat-card p-4 text-center">
                <h2 class="text-info fw-bold">{{ totalApplicants }}</h2>
                <p class="text-muted mb-0 fw-medium">Total Applicants</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Create Drive -->
        <div v-if="currentTab === 'create'">
          <div class="page-header mb-4">
            <h3 class="m-0 fw-bold">Create New Placement Drive</h3>
          </div>
          <div class="card p-4">
            <div v-if="driveMsg" class="alert alert-success">{{ driveMsg }}</div>
            <div v-if="driveErr" class="alert alert-danger">{{ driveErr }}</div>
            <form @submit.prevent="createDrive">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Job Title</label>
                  <input type="text" class="form-control" v-model="newDrive.job_title" required>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Package (LPA)</label>
                  <input type="number" step="0.1" class="form-control" v-model="newDrive.package_lpa" required>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Location</label>
                  <input type="text" class="form-control" v-model="newDrive.location">
                </div>
                <div class="col-12">
                  <label class="form-label">Job Description</label>
                  <textarea class="form-control" rows="3" v-model="newDrive.description"></textarea>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Branch Eligibility (comma-separated)</label>
                  <input type="text" class="form-control" v-model="newDrive.branch_eligibility" placeholder="e.g. CSE,IT,ECE">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Minimum CGPA Cutoff</label>
                  <input type="number" step="0.1" min="0" max="10" class="form-control" v-model="newDrive.cgpa_cutoff">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Application Deadline</label>
                  <input type="date" class="form-control" v-model="newDrive.application_deadline" required>
                </div>
                <div class="col-12 mt-4">
                  <button type="submit" class="btn btn-primary" :disabled="driveLoading">
                    <span v-if="driveLoading" class="spinner-border spinner-border-sm me-2"></span>
                    Submit for Approval
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>

        <!-- My Drives -->
        <div v-if="currentTab === 'drives'">
          <div class="page-header d-flex justify-content-between align-items-center mb-4">
            <h3 class="m-0 fw-bold">My Placement Drives</h3>
            <button class="btn btn-sm btn-outline-primary shadow-sm" @click="fetchDrives"><i class="bi bi-arrow-clockwise"></i> Refresh</button>
          </div>
          
          <div v-if="drives.length === 0" class="alert alert-info">You haven't created any drives yet.</div>
          
          <!-- show all drives in an expandable card -->
          <div class="card mb-4 hover-elevate" v-for="d in drives" :key="d.id">
            <div class="card-header bg-white d-flex justify-content-between align-items-center py-3" style="cursor:pointer" @click="toggleDriveExpand(d.id)">
              <div class="d-flex align-items-center">
                <i class="bi" :class="expandedDrive === d.id ? 'bi-chevron-down' : 'bi-chevron-right'"></i>
                <h5 class="fw-bold mb-0 ms-2 text-dark">{{ d.job_title }}</h5>
                <span class="badge ms-3" :class="statusBadge(d.status)">{{ d.status }}</span>
              </div>
              <div>
                <span class="badge bg-secondary bg-opacity-10 text-secondary border border-secondary me-2">{{ d.package_lpa || 0 }} LPA</span>
                <span class="badge bg-info bg-opacity-10 text-info border border-info">{{ d.applicant_count }} applicants</span>
              </div>
            </div>
            
            <!-- list all students that applied here -->
            <div class="card-body bg-light border-top" v-if="expandedDrive === d.id">
              <div class="d-flex justify-content-between align-items-end mb-3">
                <h6 class="fw-bold mb-0">Applicant Tracking</h6>
                <div class="input-group input-group-sm" style="width: 300px;">
                  <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
                  <input type="text" class="form-control" placeholder="Search applicants by name or branch..." v-model="searchQueries[d.id]">
                </div>
              </div>
              
              <div v-if="loadingApps" class="text-center py-4"><span class="spinner-border text-primary"></span></div>
              <div v-else-if="!filteredApps(d.id) || filteredApps(d.id).length === 0" class="alert alert-secondary py-3 mb-0 text-center">
                No matching applications found.
              </div>
              <div v-else class="card border-0 shadow-sm">
                <div class="table-responsive">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Student Name</th>
                        <th>Branch</th>
                        <th>CGPA</th>
                        <th>Applied On</th>
                        <th>Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="app in filteredApps(d.id)" :key="app.application_id">
                        <td>
                          <div class="d-flex align-items-center">
                            <img v-if="app.profile_photo_path" :src="app.profile_photo_path" class="rounded-circle me-2 object-fit-cover" width="30" height="30">
                            <i v-else class="bi bi-person-circle fs-4 text-secondary me-2"></i>
                            <span class="fw-bold">{{ app.student_name }}</span>
                          </div>
                        </td>
                        <td>{{ app.branch }}</td>
                        <td>{{ app.cgpa }}</td>
                        <td>{{ app.application_date }}</td>
                        <td>
                          <span class="badge" :class="appBadge(app.status)">{{ app.status }}</span>
                        </td>
                        <td>
                          <div class="d-flex align-items-center gap-2 flex-wrap">
                            <button class="btn btn-sm btn-outline-primary py-0 px-2" data-bs-toggle="modal" data-bs-target="#studentDetailsModal" @click="viewStudent(app)">
                              <i class="bi bi-eye"></i> View
                            </button>
                            <select class="form-select form-select-sm" style="width:120px" :value="app.status" @change="updateAppStatus(app.application_id, d.id, $event.target.value)">
                              <option value="Applied">Applied</option>
                              <option value="Shortlisted">Shortlisted</option>
                              <option value="Selected">Selected</option>
                              <option value="Rejected">Rejected</option>
                            </select>

                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Settings Tab -->
        <div v-if="currentTab === 'settings'">
          <div class="page-header mb-4">
            <h3 class="m-0 fw-bold">Company Settings</h3>
          </div>
          
          <div class="row g-4">
            <div class="col-md-7">
              <div class="card">
                <div class="card-body p-4">
                  <h5 class="fw-bold mb-4 border-bottom pb-2">Profile Information</h5>
                  <form @submit.prevent="updateProfile">
                    <div class="mb-3">
                      <label class="form-label">Company Name</label>
                      <input type="text" class="form-control" v-model="profile.name" required>
                    </div>
                    
                    <div class="mb-3">
                      <label class="form-label">Company Logo (Image)</label>
                      <input type="file" class="form-control" accept="image/*" @change="e => logoFile = e.target.files[0]">
                      <small class="text-muted" v-if="profile.logo_path">You already have a logo uploaded. Uploading a new one will replace it.</small>
                    </div>
                    
                    <div class="row mb-3">
                      <div class="col-md-4">
                        <label class="form-label">HR Name</label>
                        <input type="text" class="form-control" v-model="profile.hr_name">
                      </div>
                      <div class="col-md-4">
                        <label class="form-label">HR Contact Details</label>
                        <input type="text" class="form-control" v-model="profile.hr_contact">
                      </div>
                      <div class="col-md-4">
                        <label class="form-label">Website</label>
                        <input type="url" class="form-control" v-model="profile.website">
                      </div>
                    </div>
                    
                    <div class="mb-4">
                      <label class="form-label">About Company</label>
                      <textarea class="form-control" rows="4" v-model="profile.description"></textarea>
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

    <!-- Student Details Modal -->
    <div class="modal fade" id="studentDetailsModal" tabindex="-1" aria-hidden="true" data-bs-backdrop="static">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content shadow" v-if="selectedStudent">
          <div class="modal-header">
            <h5 class="modal-title">Student Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body text-center pb-4">
            <img v-if="selectedStudent.profile_photo_path" :src="selectedStudent.profile_photo_path" class="rounded-circle mb-3 object-fit-cover shadow-sm border" width="100" height="100">
            <i v-else class="bi bi-person-circle text-secondary d-block mb-3" style="font-size: 5rem;"></i>
            
            <h4 class="fw-bold mb-1">{{ selectedStudent.student_name }}</h4>
            <p>Status: <strong>{{ selectedStudent.status }}</strong></p>
            
            <div style="text-align: left; margin-top: 15px;">
              <ul>
                <li><strong>Branch:</strong> {{ selectedStudent.branch || 'N/A' }}</li>
                <li><strong>CGPA:</strong> {{ selectedStudent.cgpa || 'N/A' }}</li>
                <li><strong>Applied On:</strong> {{ selectedStudent.application_date }}</li>
              </ul>
            </div>
            
            <div class="mt-4" v-if="selectedStudent.resume_file_path || selectedStudent.resume_link" style="text-align: left;">
              <hr>
              <h6>Resume & Links</h6>
              <div class="d-flex flex-column gap-2 mt-2">
                <a v-if="selectedStudent.resume_file_path" :href="selectedStudent.resume_file_path" target="_blank" class="btn btn-primary">
                  View Resume File
                </a>
                <a v-if="selectedStudent.resume_link" :href="selectedStudent.resume_link" target="_blank" class="btn btn-secondary">
                  External Portfolio Link
                </a>
              </div>
            </div>
            <div class="mt-4 text-muted" v-else>
              Student has not uploaded a resume.
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
      companyName: localStorage.getItem('name') || 'Company',
      drives: [],
      newDrive: {
        job_title: '', description: '', package_lpa: '', location: '', branch_eligibility: '', cgpa_cutoff: 0, application_deadline: ''
      },
      driveLoading: false,
      driveMsg: '',
      driveErr: '',
      expandedDrive: null,
      driveApps: {},
      searchQueries: {},
      loadingApps: false,
      
      // Settings data
      profile: { name: '', description: '', hr_name: '', hr_contact: '', website: '', logo_path: '' },
      passwordForm: { old_password: '', new_password: '' },
      logoFile: null,
      savingProfile: false,
      changingPassword: false,
      
      selectedStudent: null
    }
  },
  computed: {
    // count all applicants across drives
    totalApplicants() {
      return this.drives.reduce((sum, d) => sum + (d.applicant_count || 0), 0);
    }
  },
  watch: {
    currentTab(val) {
      if (val === 'overview' || val === 'drives') this.getAllPlacements();
      if (val === 'settings') this.loadMyData();
    }
  },
  mounted() {
    this.getAllPlacements();
    this.loadMyData();
  },
  methods: {
    // get all drives for this company
    async getAllPlacements() {
      try {
        const res = await axios.get('/api/company/drives');
        this.drives = res.data;
      } catch (err) { console.error(err); }
    },
    
    // get profile info
    async loadMyData() {
      try {
        const res = await axios.get('/api/company/profile');
        this.profile = res.data;
      } catch (err) { console.error(err); }
    },
    
    // update company profile
    async saveMyData() {
      this.savingProfile = true;
      try {
        const formData = new FormData();
        formData.append('name', this.profile.name);
        formData.append('description', this.profile.description);
        formData.append('hr_name', this.profile.hr_name);
        formData.append('hr_contact', this.profile.hr_contact);
        formData.append('website', this.profile.website);
        
        if (this.logoFile) formData.append('logo', this.logoFile);
        
        await axios.put('/api/company/profile', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        alert('Profile updated successfully!');
        this.logoFile = null;
        this.loadMyData();
      } catch (err) {
        alert(err.response?.data?.msg || 'Failed to update profile');
      } finally {
        this.savingProfile = false;
      }
    },
    
    // change password
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
    
    // post a new drive
    async addNewPlacement() {
      this.driveLoading = true;
      this.driveMsg = '';
      this.driveErr = '';
      try {
        let payload = {
          job_title: this.newDrive.job_title,
          description: this.newDrive.description,
          package_lpa: parseFloat(this.newDrive.package_lpa) || 0,
          location: this.newDrive.location,
          branch_eligibility: this.newDrive.branch_eligibility,
          cgpa_cutoff: parseFloat(this.newDrive.cgpa_cutoff) || 0,
          application_deadline: this.newDrive.application_deadline
        };
        
        await axios.post('/api/company/drives', payload);
        this.driveMsg = "Drive created successfully! Pending admin approval.";
        this.newDrive = { job_title: '', description: '', package_lpa: '', location: '', branch_eligibility: '', cgpa_cutoff: 0, application_deadline: '' };
        this.getAllPlacements();
      } catch (err) {
        this.driveErr = err.response?.data?.msg || 'Failed to create drive.';
      } finally {
        this.driveLoading = false;
      }
    },
    
    // expand drive card to show applicants
    async toggleDriveExpand(driveId) {
      if (this.expandedDrive === driveId) {
        this.expandedDrive = null;
        return;
      }
      this.expandedDrive = driveId;
      this.loadingApps = true;
      try {
        const res = await axios.get(`/api/company/drives/${driveId}/applications`);
        this.driveApps[driveId] = res.data;
        if (this.searchQueries[driveId] === undefined) {
          this.searchQueries[driveId] = '';
        }
      } catch (err) { console.error(err); }
      this.loadingApps = false;
    },
    
    // filter apps based on search
    filteredApps(driveId) {
      const apps = this.driveApps[driveId];
      if (!apps) return [];
      const query = (this.searchQueries[driveId] || '').toLowerCase();
      if (!query) return apps;
      
      return apps.filter(app => {
        return (app.student_name && app.student_name.toLowerCase().includes(query)) ||
               (app.branch && app.branch.toLowerCase().includes(query));
      });
    },
    
    // change app status
    async updateAppStatus(appId, driveId, newStatus) {
      try {
        await axios.post(`/api/company/applications/${appId}/status`, { status: newStatus });
        const res = await axios.get(`/api/company/drives/${driveId}/applications`);
        this.driveApps[driveId] = res.data;
      } catch (err) {
        alert(err.response?.data?.msg || 'Failed to update status');
      }
    },
    
    // show student details in modal
    viewStudent(app) {
      this.selectedStudent = app;
    },
    
    // colors for drive status
    statusBadge(status) {
      if (status === 'Approved') return 'bg-success';
      if (status === 'Pending') return 'bg-warning text-dark';
      if (status === 'Rejected') return 'bg-danger';
      return 'bg-secondary';
    },
    
    // colors for app status
    appBadge(status) {
      if (status === 'Selected') return 'bg-success';
      if (status === 'Shortlisted') return 'bg-primary';
      if (status === 'Rejected') return 'bg-danger';
      return 'bg-secondary';
    }
  }
}
</script>

<style scoped>
.hover-elevate {
  transition: transform 0.2s, box-shadow 0.2s;
}
.hover-elevate:hover {
  transform: translateY(-2px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
}
</style>
