<template>
  <MainLayout>
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <template v-else-if="company">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <BreadcrumbComponent
            :pageName="company.name"
            @home-click="goHome"
            @middle-click="goHome"
          />
          <button type="button" class="btn btn-primary" @click="goHome">
            <i class="bi bi-arrow-left me-1"></i>Tagasi
          </button>
        </div>

        <div class="shadow-sm rounded bg-white p-4">
          <div class="mb-4">
            <h2 class="h5 mb-3">Põhiandmed</h2>

            <dl class="row">
              <dt class="col-sm-2">Nimi:</dt>
              <dd class="col-sm-9">{{ company.name }}</dd>

              <dt class="col-sm-2">Registrikood:</dt>
              <dd class="col-sm-9">{{ company.reg_code }}</dd>

              <dt class="col-sm-2">Asutamiskuupäev:</dt>
              <dd class="col-sm-9">{{ formatDate(company.founding_date) }}</dd>

              <dt class="col-sm-2">Kogukapital:</dt>
              <dd class="col-sm-9">{{ company.capital }} €</dd>

              <dt class="col-sm-2">Osanike arv:</dt>
              <dd class="col-sm-9">{{ shareholders.length }}</dd>
            </dl>
          </div>

          <div>
            <h2 class="h5 mb-3">Osanikud</h2>
            <div class="table-responsive">
              <table class="table">
                <thead>
                  <tr>
                    <th style="width: 25%">Nimi</th>
                    <th style="width: 15%">Isiku tüüp</th>
                    <th style="width: 20%">Isikukood / Registrikood</th>
                    <th style="width: 15%">Osalus (€)</th>
                    <th style="width: 15%">Osalus (%)</th>
                    <th style="width: 10%">Asutaja</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(shareholder, index) in shareholders" :key="index">
                    <td>
                      <span v-if="shareholder.type === 'individual'">
                        {{ shareholder.first_name }} {{ shareholder.last_name }}
                      </span>
                      <span v-else>
                        {{ shareholder.legal_name }}
                      </span>
                    </td>
                    <td>
                      {{ shareholder.type === 'individual' ? 'Füüsiline isik' : 'Juriidiline isik' }}
                    </td>
                    <td>
                      <span v-if="shareholder.type === 'individual'">
                        {{ shareholder.id_code }}
                      </span>
                      <span v-else>
                        {{ shareholder.reg_code }}
                      </span>
                    </td>
                    <td>{{ shareholder.share }} €</td>
                    <td>{{ calculatePercentage(shareholder.share, company.capital) }}%</td>
                    <td>{{ shareholder.isFounder ? 'Jah' : 'Ei' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="mt-3">
              <button type="button" class="btn btn-primary" @click="navigateToCapitalIncrease">
                <i class="bi bi-plus-circle me-1"></i> Suurenda või muuda osakapitali
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="container text-center mt-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Laadimine...</span>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import axios from 'axios'
import MainLayout from '../components/layout/MainLayout.vue'
import BreadcrumbComponent from "../components/common/BreadcrumbComponent.vue";

export default {
  name: 'CompanyView',
  components: {
    BreadcrumbComponent,
    MainLayout
  },
  data() {
    return {
      error: null,
      company: null,
      shareholders: []
    }
  },
  created() {
    this.fetchCompanyData()
  },
  methods: {
    async fetchCompanyData() {
      try {
        const companyId = this.$route.params.id
        if (!companyId) {
          this.error = 'Osaühingut ei leitud'
          return
        }

        const apiBaseUrl = process.env.VUE_APP_API_URL || ''

        const companyResponse = await axios.get(`${apiBaseUrl}/companies/${companyId}`)
        this.company = companyResponse.data

        const shareholdingsResponse = await axios.get(`${apiBaseUrl}/shareholdings/`, {
          params: { company_id: companyId }
        })

        this.shareholders = await Promise.all(
          shareholdingsResponse.data.map(async (shareholding) => {
            const personResponse = await axios.get(`${apiBaseUrl}/persons/${shareholding.person_id}`)
            return {
              ...personResponse.data,
              share: shareholding.share,
              isFounder: shareholding.isFounder || false
            }
          })
        )
      } catch (error) {
        console.error('Error fetching company data:', error)
        this.error = 'Viga andmete laadimisel: ' + (error.response?.data?.detail || error.message)
      }
    },
    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('et-EE')
    },
    calculatePercentage(share, total) {
      if (!total) return '0.0'
      return ((share / total) * 100).toFixed(1)
    },
    goHome() {
      this.$router.push('/')
    },
    navigateToCapitalIncrease() {
      const companyId = this.company?.id
      if (companyId) {
        this.$router.push(`/company/${companyId}/capital`)
      }
    }
  }
}
</script>
