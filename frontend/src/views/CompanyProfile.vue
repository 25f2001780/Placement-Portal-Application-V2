<template>
  <div class="container py-4">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card p-4">
          <div class="page-header mb-4">
            <h3 class="m-0 fw-bold">Company Profile</h3>
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
                  <label class="form-label">Company Name</label>
                  <input type="text" class="form-control" v-model="form.name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">HR Contact</label>
                  <input type="text" class="form-control" v-model="form.hr_contact">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Website</label>
                  <input type="url" class="form-control" v-model="form.website">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Approval Status</label>
                  <input type="text" class="form-control" :value="form.approved ? 'Approved' : 'Pending'" disabled>
                </div>
                <div class="col-12">
                  <label class="form-label">Description</label>
                  <textarea class="form-control" rows="4" v-model="form.description"></textarea>
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
        hr_contact: '',
        website: '',
        description: '',
        approved: false
      }
    }
  },
  mounted() {
    this.fetchProfile();
  },
  methods: {
    async fetchProfile() {
      try {
        const res = await axios.get('/api/company/profile');
        this.form.name = res.data.name || '';
        this.form.hr_contact = res.data.hr_contact || '';
        this.form.website = res.data.website || '';
        this.form.description = res.data.description || '';
        this.form.approved = res.data.approved;
      } catch (err) {
        this.error = "Failed to load profile.";
      } finally {
        this.loadingData = false;
      }
    },
    async updateProfile() {
      this.saving = true;
      this.error = '';
      this.success = '';
      try {
        await axios.put('/api/company/profile', {
          name: this.form.name,
          hr_contact: this.form.hr_contact,
          website: this.form.website,
          description: this.form.description
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
