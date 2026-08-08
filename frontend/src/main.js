    // Axios config
    axios.defaults.baseURL = 'http://127.0.0.1:5000';
    axios.interceptors.request.use(config => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    axios.interceptors.response.use(
      response => response,
      error => {
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          localStorage.removeItem('token');
          localStorage.removeItem('role');
          localStorage.removeItem('name');
          localStorage.removeItem('user_id');
          if (window.location.hash !== '#/login') {
            window.location.hash = '#/login';
          }
        }
        return Promise.reject(error);
      }
    );

    // sfc loader config
    const options = {
      moduleCache: {
        vue: Vue,
        'vue-router': VueRouter
      },
      async getFile(url) {
        const res = await fetch(url);
        if (!res.ok)
          throw Object.assign(new Error(res.statusText + ' ' + url), { res });
        return {
          getContentData: asBinary => asBinary ? res.arrayBuffer() : res.text(),
        }
      },
      addStyle(textContent) {
        const style = Object.assign(document.createElement('style'), { textContent });
        const ref = document.head.getElementsByTagName('style')[0] || null;
        document.head.insertBefore(style, ref);
      },
    };

    const loadSfc = window['vue3-sfc-loader'].loadModule;

    // Routes
    const routes = [
      { path: '/', component: () => loadSfc('./components/Home.vue', options) },
      { path: '/login', component: () => loadSfc('./components/Login.vue', options) },
      { path: '/register', component: () => loadSfc('./components/Register.vue', options) },
      { path: '/admin', component: () => loadSfc('./components/AdminDashboard.vue', options) },
      { path: '/company', component: () => loadSfc('./components/CompanyDashboard.vue', options) },
      { path: '/student', component: () => loadSfc('./components/StudentDashboard.vue', options) },
      { path: '/change-password', component: () => loadSfc('./components/ChangePassword.vue', options) },
      { path: '/company/profile', component: () => loadSfc('./components/CompanyProfile.vue', options) },
      { path: '/student/profile', component: () => loadSfc('./components/StudentProfile.vue', options) }
    ];

    const router = VueRouter.createRouter({
      history: VueRouter.createWebHashHistory(),
      routes,
    });

    // Bootstrap Vue app
    loadSfc('./src/App.vue', options).then(App => {
      const app = Vue.createApp(App);
      app.use(router);
      app.mount('#app');
    });
