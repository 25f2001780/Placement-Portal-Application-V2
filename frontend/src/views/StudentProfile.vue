<template>
  <div class="container py-4">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card p-4">
          <div class="page-header mb-4">
            <h3 class="m-0 fw-bold">Student Profile</h3>
          </div>
          
          <div v-if="loadingData" class="text-center py-4">
            <span class="spinner-border"></span>
          </div>
          
          <div v-else>
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div v-if="success" class="alert alert-success">{{ success }}</div>
            
            <form @submit.prevent="updateProfile">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Full Name</label>
                  <input type="text" class="form-control" v-model="form.name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Resume Link</label>
                  <input type="url" class="form-control" v-model="form.resume_link" placeholder="https://...">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Branch</label>
                  <select class="form-select" v-model="form.branch" required>
                    <option value="CSE">CSE</option>
                    <option value="IT">IT</option>
                    <option value="ECE">ECE</option>
                    <option value="EE">EE</option>
                    <option value="ME">ME</option>
                    <option value="CE">CE</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">CGPA</label>
                  <input type="number" step="0.01" min="0" max="10" class="form-control" v-model="form.cgpa" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Year</label>
                  <select class="form-select" v-model.number="form.year" required>
                    <option value="1">1st Year</option>
                    <option value="2">2nd Year</option>
                    <option value="3">3rd Year</option>
                    <option value="4">4th Year</option>
                  </select>
                </div>
                
                <div class="col-12 mt-4 text-end">
                  <button type="submit" class="btn btn-primary px-4" :disabled="saving">
                    <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                    Save Profile
                  </button>
                </div>
              </div>
            </form>
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
      loadingData: true,
      saving: false,
      error: '',
      success: '',
      form: {
        name: '',
        branch: '',
        cgpa: '',
        year: '',
        resume_link: ''
      }
    }
  },
  mounted() {
    this.loadMyData();
  },
  methods: {
    async loadMyData() {
      try {
        const res = await axios.get('/api/student/profile');
        this.form.name = res.data.name || '';
        this.form.branch = res.data.branch || '';
        this.form.cgpa = res.data.cgpa || '';
        this.form.year = res.data.year || '';
        this.form.resume_link = res.data.resume_link || '';
      } catch (err) {
        this.error = "Failed to load profile.";
      } finally {
        this.loadingData = false;
      }
    },
    async saveMyData() {
      this.saving = true;
      this.error = '';
      this.success = '';
      try {
        await axios.put('/api/student/profile', {
          name: this.form.name,
          branch: this.form.branch,
          cgpa: parseFloat(this.form.cgpa),
          year: parseInt(this.form.year),
          resume_link: this.form.resume_link
        });
        this.success = "Profile updated successfully.";
        localStorage.setItem('name', this.form.name);
        this.$emit('auth-change');
      } catch (err) {
        this.error = err.response?.data?.msg || "Failed to update profile.";
      } finally {
        this.saving = false;
      }
    }
  }
}
</script>
