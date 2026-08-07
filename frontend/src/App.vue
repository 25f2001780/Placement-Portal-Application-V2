<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light sticky-top">
      <div class="container">
        <router-link class="navbar-brand d-flex align-items-center" to="/">
          <i class="bi bi-mortarboard fs-4 me-2"></i> PPA
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Home</router-link>
            </li>
            <li class="nav-item" v-if="isLoggedIn">
              <router-link class="nav-link" :to="'/' + role">Dashboard</router-link>
            </li>
          </ul>
          
          <ul class="navbar-nav">
            <template v-if="!isLoggedIn">
              <li class="nav-item">
                <router-link class="nav-link" to="/login">Login</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/register">Register</router-link>
              </li>
            </template>
            <template v-else>
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                  <i class="bi bi-person-circle me-1"></i> {{ userName }}
                </a>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li v-if="role === 'student' || role === 'company'">
                    <router-link class="dropdown-item" :to="'/' + role + '/profile'">Profile</router-link>
                  </li>
                  <li><router-link class="dropdown-item" to="/change-password">Change Password</router-link></li>
                  <li><hr class="dropdown-divider"></li>
                  <li><a class="dropdown-item text-danger" href="#" @click.prevent="logout">Logout</a></li>
                </ul>
              </li>
            </template>
          </ul>
        </div>
      </div>
    </nav>

    <main>
      <router-view @auth-change="checkAuth"></router-view>
    </main>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isLoggedIn: false,
      role: '',
      userName: ''
    }
  },
  created() {
    this.checkAuth();
  },
  watch: {
    $route() {
      this.checkAuth();
    }
  },
  methods: {
    checkAuth() {
      const token = localStorage.getItem('token');
      this.isLoggedIn = !!token;
      if (this.isLoggedIn) {
        this.role = localStorage.getItem('role') || '';
        this.userName = localStorage.getItem('name') || 'User';
      }
    },
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('name');
      localStorage.removeItem('user_id');
      this.checkAuth();
      this.$router.push('/login');
    }
  }
}
</script>
