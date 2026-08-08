<template>
  <div>
    <div class="hero-section">
      <div class="container">
        <h1 class="display-4">Placement Portal Application</h1>
        <p class="lead">Connecting bright minds with great opportunities seamlessly.</p>
        
        <!-- buttons for guest -->
        <div class="mt-4" v-if="!isLoggedIn">
          <router-link to="/login" class="btn btn-light btn-lg me-3 px-4">Login</router-link>
          <router-link to="/register" class="btn btn-outline-light btn-lg px-4">Register</router-link>
        </div>
        
        <!-- button if already logged in -->
        <div class="mt-4" v-else>
          <router-link :to="'/' + role" class="btn btn-light btn-lg px-4">Go to Dashboard</router-link>
        </div>
      </div>
    </div>

    <!-- features section -->
    <div class="container mb-5">
      <div class="row g-4">
        
        <!-- student card -->
        <div class="col-md-4">
          <div class="card h-100 text-center p-4">
            <div class="card-body">
              <i class="bi bi-person-workspace text-primary mb-3" style="font-size: 3rem;"></i>
              <h3 class="card-title h4">For Students</h3>
              <p class="card-text text-muted" style="font-size: 14px;">Create your profile, browse upcoming placement drives, and apply with a single click. Track your application status in real-time.</p>
            </div>
          </div>
        </div>
        
        <!-- company card -->
        <div class="col-md-4">
          <div class="card h-100 text-center p-4">
            <div class="card-body">
              <i class="bi bi-building text-primary mb-3" style="font-size: 3rem;"></i>
              <h3 class="card-title h4">For Companies</h3>
              <p class="card-text text-muted" style="font-size: 14px;">Post job requirements, schedule placement drives, and manage student applications efficiently through a dedicated dashboard.</p>
            </div>
          </div>
        </div>
        
        <!-- admin card -->
        <div class="col-md-4">
          <div class="card h-100 text-center p-4">
            <div class="card-body">
              <i class="bi bi-shield-lock text-primary mb-3" style="font-size: 3rem;"></i>
              <h3 class="card-title h4">For Admin</h3>
              <p class="card-text text-muted" style="font-size: 14px;">Oversee the entire placement process, manage user registrations, approve companies, and monitor overall statistics.</p>
            </div>
          </div>
        </div>
        
      </div>
    </div>

    <footer class="bg-white border-top py-4 mt-5 text-center text-muted">
      <div class="container">
        <p class="mb-0">&copy; {{ new Date().getFullYear() }} Placement Portal Application. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isLoggedIn: false,
      role: '' // user role
    }
  },
  created() {
    // check if token exists in storage
    this.isLoggedIn = !!localStorage.getItem('token');
    
    if (this.isLoggedIn) {
      // set role so we can redirect to right dashboard
      this.role = localStorage.getItem('role') || '';
    }
  }
}
</script>
