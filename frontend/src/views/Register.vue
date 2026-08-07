<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card p-4 border-0 shadow-sm">
          <div class="text-center mb-4">
            <h2 class="fw-bold text-primary">Register</h2>
            <p class="text-muted">Create a new account</p>
          </div>
          
          <!-- show error message if registration fails -->
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <div v-if="success" class="alert alert-success">{{ success }}</div>
          
          <form @submit.prevent="register">
            <div class="mb-4 text-center">
              <div class="btn-group" role="group">
                <input type="radio" class="btn-check" name="role" id="roleStudent" value="student" v-model="form.role">
                <label class="btn btn-outline-primary" for="roleStudent">Student</label>
                
                <input type="radio" class="btn-check" name="role" id="roleCompany" value="company" v-model="form.role">
                <label class="btn btn-outline-primary" for="roleCompany">Company</label>
              </div>
            </div>
            
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Email address</label>
                <input type="email" class="form-control" v-model="form.email" required>
              </div>
              
              <div class="col-md-6">
                <label class="form-label">Phone Number</label>
                <input type="text" class="form-control" v-model="form.phone" required pattern="[0-9+\-\s()]+" title="Valid phone number characters only">
              </div>

              <div class="col-12">
                <label class="form-label">{{ form.role === 'company' ? 'Company Name' : 'Full Name' }}</label>
                <input type="text" class="form-control" v-model="form.name" required>
              </div>
              
              <div class="col-md-6">
                <label class="form-label">Password</label>
                <input type="password" class="form-control" v-model="form.password" required>
                
                <!-- check password strength -->
                <div class="mt-2" style="font-size: 0.85em;">
                  <!-- check length -->
                  <div v-if="pwdMinLength" style="color: green"><i class="bi bi-check2-circle"></i> At least 8 characters</div>
                  <div v-else style="color: red"><i class="bi bi-x-circle"></i> At least 8 characters</div>
                  
                  <div v-if="pwdUpper" class="text-success"><i class="bi bi-check2-circle"></i> Uppercase letter</div>
                  <div v-else class="text-danger"><i class="bi bi-x-circle"></i> Uppercase letter</div>
                  
                  <span v-if="pwdLower" class="text-success"><i class="bi bi-check2-circle"></i> Lowercase letter<br></span>
                  <span v-else class="text-danger"><i class="bi bi-x-circle"></i> Lowercase letter<br></span>
                  
                  <div :class="pwdNumber ? 'text-success' : 'text-danger'"><i class="bi" :class="pwdNumber ? 'bi-check2-circle' : 'bi-x-circle'"></i> Number</div>
                  
                  <div v-if="pwdSpecial" style="color: #198754;"><i class="bi bi-check2-circle"></i> Special character (@$!%*?&)</div>
                  <div v-else style="color: #dc3545;"><i class="bi bi-x-circle"></i> Special character (@$!%*?&)</div>
                </div>
              </div>
              
              <div class="col-md-6">
                <label class="form-label">Confirm Password</label>
                <input type="password" class="form-control" v-model="form.confirm_password" required>
                <div v-if="form.confirm_password && form.password !== form.confirm_password" class="text-danger small mt-1">
                  Passwords do not match
                </div>
              </div>
              
              <!-- fields only for student -->
              <template v-if="form.role === 'student'">
                <div class="col-md-4">
                  <label class="form-label">Branch</label>
                  <select class="form-select" v-model="form.branch" required>
                    <option value="">Select Branch...</option>
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
                  <select class="form-select" v-model="form.year" required>
                    <option value="">Select Year...</option>
                    <option value="1">1st Year</option>
                    <option value="2">2nd Year</option>
                    <option value="3">3rd Year</option>
                    <option value="4">4th Year</option>
                  </select>
                </div>
              </template>
              
              <!-- fields only for company -->
              <template v-if="form.role === 'company'">
                <div class="col-md-6">
                  <label class="form-label">HR Name</label>
                  <input type="text" class="form-control" v-model="form.hr_name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">HR Contact Email/Phone</label>
                  <input type="text" class="form-control" v-model="form.hr_contact" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Website</label>
                  <input type="url" class="form-control" v-model="form.website">
                </div>
                <div class="col-12">
                  <label class="form-label">Company Description</label>
                  <textarea class="form-control" rows="3" v-model="form.description"></textarea>
                </div>
              </template>
            </div>
            
            <div class="d-grid mt-4">
              <!-- button is disabled if form not filled correctly -->
              <button type="submit" class="btn btn-primary btn-lg" :disabled="loading || !isPasswordStrong || form.password !== form.confirm_password">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Register
              </button>
            </div>
          </form>
          
          <div class="text-center mt-4">
            <p>Already have an account? <router-link to="/login" class="text-decoration-none">Login here</router-link></p>
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
      // form data
      form: {
        role: 'student',
        email: '',
        phone: '',
        name: '',
        password: '',
        confirm_password: '',
        branch: '',
        cgpa: '',
        year: '',
        hr_name: '',
        hr_contact: '',
        website: '',
        description: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  computed: {
    // password checks
    pwdMinLength() { return this.form.password.length >= 8; },
    pwdUpper() { return /[A-Z]/.test(this.form.password); },
    pwdLower() { return /[a-z]/.test(this.form.password); },
    pwdNumber() { return /\d/.test(this.form.password); },
    pwdSpecial() { return /[@$!%*?&]/.test(this.form.password); },
    isPasswordStrong() {
      // return true if all rules pass
      return this.pwdMinLength && this.pwdUpper && this.pwdLower && this.pwdNumber && this.pwdSpecial;
    }
  },
  methods: {
    async register() {
      // clear old messages
      this.error = '';
      this.success = '';
      
      if (!this.isPasswordStrong) {
        this.error = "Password does not meet all strength requirements.";
        return;
      }
      
      if (this.form.password !== this.form.confirm_password) {
        this.error = "Passwords do not match!";
        return;
      }
      
      this.loading = true;
      
      try {
        // copy form data
        const payload = { ...this.form };
        
        // fix types for student
        if (payload.role === 'student') {
          payload.year = parseInt(payload.year);
          payload.cgpa = parseFloat(payload.cgpa);
        }
        
        // send request to backend
        await axios.post('/api/auth/register', payload);
        this.success = "Registration successful! Redirecting to login...";
        
        // redirect to login after 2 seconds
        setTimeout(() => {
          this.$router.push('/login');
        }, 2000);
      } catch (err) {
        // show error from server
        this.error = err.response?.data?.msg || 'Registration failed. Please check your details.';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
