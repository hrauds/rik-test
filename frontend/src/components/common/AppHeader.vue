<template>
  <header class="app-header">
    <nav class="navbar navbar-expand-lg navbar-light">
      <div class="container">
        <router-link to="/" class="navbar-brand">Osaühingud</router-link>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item" v-for="item in navItems" :key="item.path">
              <router-link :to="item.path" class="nav-link" active-class="active">
                {{ item.title }}
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'AppHeader',
  data() {
    return {
      navItems: [
        {title: 'Avaleht', path: '/'},
        {title: 'Minu osaühingud', path: '/company/my'},
        {title: 'Osaühingu registreerimine', path: '/register'},
        {title: 'Osaühingute otsing', path: '/search'}
      ]
    }
  }
}
</script>