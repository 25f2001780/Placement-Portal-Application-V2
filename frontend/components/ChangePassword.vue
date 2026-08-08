<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card p-4">
          <div class="text-center mb-4">
            <h3 class="fw-bold">Change Password</h3>
          </div>
          
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <div v-if="success" class="alert alert-success">{{ success }}</div>
          
          <form @submit.prevent="changePassword">
            <div class="mb-3">
              <label class="form-label">Current Password</label>
              <input type="password" class="form-control" v-model="form.current_password" required>
            </div>
            
            <div class="mb-3">
              <label class="form-label">New Password</label>
              <input type="password" class="form-control" v-model="form.new_password" required minlength="6">
            </div>
            
            <div class="mb-4">
              <label class="form-label">Confirm New Password</label>
              <input type="password" class="form-control" v-model="form.confirm_new_password" required minlength="6">
            </div>
            
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Update Password
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        current_password: '',
        new_password: '',
        confirm_new_password: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  methods: {
    async changePassword() {
      this.error = '';
      this.success = '';
      
      if (this.form.new_password !== this.form.confirm_new_password) {
        this.error = "New passwords do not match.";
        return;
      }
      
      this.loading = true;
      try {
        await axios.post('/api/auth/change-password', {
          old_password: this.form.current_password,
          new_password: this.form.new_password
        });
        
        this.success = "Password updated successfully.";
        this.form = { current_password: '', new_password: '', confirm_new_password: '' };
      } catch (err) {
        this.error = err.response?.data?.msg || "Failed to update password.";
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
