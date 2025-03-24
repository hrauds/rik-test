<template>
  <div>
    <AppHeader />
    <main class="main-content">
      <div class="container">
        <slot></slot>
      </div>
    </main>
    <footer class="app-footer">
      <div class="container">
        <div class="row">
          <div class="col-md-6">
            <p>&copy; {{ currentYear }} Osaühingute register</p>
          </div>
          <div class="col-md-6 text-md-end">
            <p>Kõik õigused kaitstud</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import AppHeader from '../common/AppHeader.vue'

export default {
  name: 'MainLayout',
  components: {
    AppHeader
  },
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script>