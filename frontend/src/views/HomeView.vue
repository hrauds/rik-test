<template>
  <MainLayout>
    <div class="py-5 mb-5 bg-light rounded">
      <div class="container text-center">
        <h1 class="display-5 fw-bold mb-3">Tere tulemast osaühingute registrisse</h1>
        <div class="row justify-content-center">
          <div class="col-lg-6">
            <p class="lead mb-4">
              Osaühingute register võimaldab hallata ja asutada uusi osaühinguid ning otsida olemasolevaid ettevõtteid.
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

            <select class="form-select flex-grow-0 w-auto" v-model="searchMode" aria-label="Otsingu tüüp">
              <option value="company">Osaühing</option>
              <option value="shareholder">Osanik</option>
            </select>
            <input
              type="text"
              class="form-control"
              v-model="searchQuery"
              :placeholder="getPlaceholder()"
              aria-label="Otsisõna"
            />
            <button type="submit" class="btn btn-primary" aria-label="Otsi">Otsi</button>
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
              :key="company.id"
              href="#"
              @click.prevent="viewCompany(company.id)"
              class="list-group-item list-group-item-action"
              :aria-label="`Vaata osaühingut ${company.name}`"
            >
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <div class="fw-medium">{{ company.name }}</div>
                  <small class="text-muted">Registrikood: {{ company.reg_code }}</small>
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
import axios from 'axios'

export default {
  name: 'HomeView',
  components: {
    MainLayout
  },
  data() {
    return {
      searchQuery: '',
      // Two modes: "company" or "shareholder"
      searchMode: 'company',
      searchResults: [],
      searched: false,
      allCompanies: [],
      error: null
    }
  },
  mounted() {
    const apiBaseUrl = process.env.VUE_APP_API_URL || ''
    axios.get(`${apiBaseUrl}/companies`)
      .then(response => {
        this.allCompanies = response.data
      })
      .catch(error => {
        console.error('Error fetching companies:', error)
        this.error = 'Andmete laadimisel ilmnes viga.'
      })
  },
  methods: {
    getPlaceholder() {
      return this.searchMode === 'company'
        ? 'Sisesta osaühingu nimi või registrikood...'
        : 'Sisesta osaniku nimi või kood...'
    },
    performSearch() {
      this.searched = true

      if (!this.searchQuery || !this.searchQuery.trim()) {
        this.searchResults = this.allCompanies
        return
      }
      const query = this.searchQuery.trim().toLowerCase()
      this.searchResults = this.allCompanies.filter(company => {

        if (this.searchMode === 'company') {
          const combined = `${company.name} ${company.reg_code}`.toLowerCase()
          return combined.includes(query)

        } else {
          if (!company.shareholders || company.shareholders.length === 0) return false
          return company.shareholders.some(sh => {

            if (sh.person && sh.person.type === 'individual') {
              const fullName = `${sh.person.first_name} ${sh.person.last_name}`.toLowerCase()
              const idCode = (sh.person.id_code || '').toLowerCase()
              return fullName.includes(query) || idCode.includes(query)
            } else if (sh.person) {
              const legalInfo = `${sh.person.legal_name} ${sh.person.reg_code}`.toLowerCase()
              return legalInfo.includes(query)
            }
            return false
          })
        }
      })
    },

    viewCompany(id) {
      if (id) {
        this.$router.push(`/company/${id}`)
      }
    },
    navigateToRegistration() {
      this.$router.push('/register')
    }
  }
}
</script>
