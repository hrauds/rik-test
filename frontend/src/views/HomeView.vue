<template>
  <MainLayout>
    <section class="hero-section text-center">
      <div class="container">
        <h1 class="hero-title display-4">Tere tulemast</h1>
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <p class="hero-subtitle">
              Osaühingute register võimaldab hallata ja asutada uusi osaühinguid ning otsida olemasolevaid osaühinguid.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="py-5">
      <div class="container">
        <div class="row">
          <div class="col-md-4 mb-4">
            <div class="card card-custom h-100">
              <div class="card-body text-center">
                <i class="bi bi-building fs-1 text-primary mb-3"></i>
                <h3>Asuta osaühing</h3>
                <p>Registreeri osaühinguid.</p>
              </div>
            </div>
          </div>
          <div class="col-md-4 mb-4">
            <div class="card card-custom h-100">
              <div class="card-body text-center">
                <i class="bi bi-pencil-square fs-1 text-primary mb-3"></i>
                <h3>Halda osaühinguid</h3>
                <p>Muuda oma osaühingu infot ja halda osanikke.</p>
              </div>
            </div>
          </div>
          <div class="col-md-4 mb-4">
            <div class="card card-custom h-100">
              <div class="card-body text-center">
                <i class="bi bi-search fs-1 text-primary mb-3"></i>
                <h3>Otsi osaühinguid</h3>
                <p>Leia infot olemasolevate osaühingute kohta.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </MainLayout>
</template>

<script>
import MainLayout from '../components/layout/MainLayout.vue'

export default {
  name: 'HomeView',
  components: {
    MainLayout
  },

  methods: {

  }
}
</script>
