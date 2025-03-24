<template>
  <MainLayout>
    <div class="py-5 mb-5 bg-light rounded">
      <div class="container text-center">
        <h1 class="display-5 fw-bold mb-3">Tere tulemast osaühingute registrisse</h1>
        <div class="row justify-content-center">
          <div class="col-lg-6">
            <p class="lead mb-4">
              Osaühingute register võimaldab hallata ja asutada uusi osaühinguid ning
              otsida olemasolevaid ettevõtteid.
            </p>
            <button
              type="button"
              @click="navigateToRegistration"
              class="btn btn-primary"
              aria-label="Alusta osaühingu asutamist"
            >
              Alusta asutamist
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <div class="shadow-sm rounded bg-white p-4 mb-5">
        <h5 class="mb-3">Otsi osaühingut</h5>

        <form @submit.prevent="performSearch">
          <div class="input-group">
            <select
              class="form-select flex-grow-0 w-auto"
              v-model="searchType"
              aria-label="Otsingu tüüp"
            >
              <option value="name">Nimi</option>
              <option value="regCode">Registrikood</option>
              <option value="shareholder">Osanik</option>
            </select>
            <input
              type="text"
              class="form-control"
              v-model="searchQuery"
              :placeholder="getPlaceholder()"
              aria-label="Otsisõna"
            />
            <button
              type="submit"
              class="btn btn-primary"
              aria-label="Otsi"
            >
              Otsi
            </button>
          </div>
        </form>

        <div v-if="searched && searchResults.length > 0" class="mt-4">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-3">Tulemused</h5>
            <span class="badge bg-primary">{{ searchResults.length }}</span>
          </div>

          <div class="list-group">
            <a
              v-for="company in searchResults"
              :key="company.reg_code"
              href="#"
              @click.prevent="viewCompany(company.reg_code)"
              class="list-group-item list-group-item-action"
              :aria-label="`Vaata osaühingut ${company.name}`"
            >
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <div class="fw-medium">{{ company.name }}</div>
                  <small class="text-muted">
                    Registrikood: {{ company.reg_code }}
                  </small>
                </div>
                <i class="bi bi-chevron-right"></i>
              </div>
            </a>
          </div>
        </div>

        <div
          v-if="searched && searchResults.length === 0"
          class="alert alert-info mt-4"
          role="alert"
        >
          <small>Otsingu tulemusi ei leitud.</small>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import MainLayout from '../components/layout/MainLayout.vue'

export default {
  name: 'HomeView',
  components: {
    MainLayout
  },
  data() {
    return {
      searchQuery: '',
      searchType: 'name',
      searchResults: [],
      searched: false,

      allCompanies: [],
      error: null
    }
  },
  mounted() {
    const apiBaseUrl = process.env.VUE_APP_API_URL || '';
    fetch(`${apiBaseUrl}/api/companies`)
      .then((resp) => resp.json())
      .then((data) => {
        this.allCompanies = data
      })
      .catch((err) => {
        console.error('Fetch error:', err)
        this.error = 'Andmete laadimisel ilmnes viga.'
      })

  },
  methods: {
    getPlaceholder() {
      switch (this.searchType) {
        case 'name':
          return 'Sisesta osaühingu nimi või selle osa...'
        case 'regCode':
          return 'Sisesta registrikood...'
        case 'shareholder':
          return 'Sisesta osaniku nimi või kood...'
        default:
          return 'Sisesta otsisõna...'
      }
    },
    performSearch() {
      this.searched = true

      if (!this.searchQuery || !this.searchQuery.trim()) {
        this.searchResults = this.allCompanies
        return
      }

      const query = this.searchQuery.trim().toLowerCase()

      this.searchResults = this.allCompanies.filter((company) => {
        if (this.searchType === 'name') {
          return company.name.toLowerCase().includes(query)
        } else if (this.searchType === 'regCode') {
          return company.reg_code.includes(query)
        } else if (this.searchType === 'shareholder') {
          if (!company.shareholders) return false
          return company.shareholders.some((sh) =>
            sh.name.toLowerCase().includes(query)
          )
        }
        return false
      })
    },
    viewCompany(regCode) {
      if (regCode && /^\d{7}$/.test(regCode)) {
        this.$router.push(`/company/${regCode}`)
      }
    },
    navigateToRegistration() {
      this.$router.push('/register')
    }
  }
}
</script>
