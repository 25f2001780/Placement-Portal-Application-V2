<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card p-4">
          <div class="text-center mb-4">
            <h2 class="fw-bold text-primary">Login</h2>
            <p class="text-muted">Welcome back! Please login to your account.</p>
          </div>
          
          <!-- error alert -->
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          
          <form @submit.prevent="login">
            <div class="mb-3">
              <label class="form-label">Email address</label>
              <input type="email" class="form-control" v-model="email" required>
            </div>
            
            <div class="mb-4">
              <label class="form-label">Password</label>
              <input type="password" class="form-control" v-model="password" required>
            </div>
            
            <div class="d-grid">
              <!-- login button -->
              <button type="submit" class="btn btn-primary btn-lg" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Login
              </button>
            </div>
          </form>
          
          <div class="text-center mt-4">
            <p>Don't have an account? <router-link to="/register" style="text-decoration: none;">Register here</router-link></p>
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
      email: '',
      password: '',
      loading: false,
      error: '' // stores error msg
    }
  },
  methods: {
    async login() {
      this.loading = true;
      this.error = '';
      
      try {
        // call login api
        const res = await axios.post('/api/auth/login', {
          email: this.email,
          password: this.password
        });
        
        // save user details to local storage
        localStorage.setItem('token', res.data.token);
        localStorage.setItem('role', res.data.role);
        localStorage.setItem('name', res.data.name);
        localStorage.setItem('user_id', res.data.user_id);
        
        this.$emit('auth-change');
        
        // go to role dashboard
        this.$router.push(`/${res.data.role}`);
      } catch (e) {
        // handle login error
        this.error = e.response?.data?.msg || 'Failed to login. Please check your credentials.';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
