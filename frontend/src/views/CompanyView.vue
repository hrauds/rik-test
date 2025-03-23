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
              <dd class="col-sm-9">{{ company.regCode }}</dd>

              <dt class="col-sm-2">Asutamiskuupäev:</dt>
              <dd class="col-sm-9">{{ formatDate(company.foundingDate) }}</dd>

              <dt class="col-sm-2">Kogukapital:</dt>
              <dd class="col-sm-9">{{ company.capital }} €</dd>

              <dt class="col-sm-2">Osanike arv:</dt>
              <dd class="col-sm-9">{{ company.shareholders.length }}</dd>
            </dl>
          </div>

          <div>
            <h2 class="h5 mb-3">Osanikud</h2>
            <div class="table-responsive">
              <table class="table">
                <thead>
                  <tr>
                    <th style="width: 30%">Nimi</th>
                    <th style="width: 25%">Isikukood</th>
                    <th style="width: 15%">Osalus (€)</th>
                    <th style="width: 15%">Osalus (%)</th>
                    <th style="width: 15%">Asutaja</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(shareholder, index) in company.shareholders" :key="index">
                    <td>
                      <span v-if="shareholder.type === 'individual'">
                        {{ shareholder.firstName }} {{ shareholder.lastName }}
                      </span>
                      <span v-else>
                        {{ shareholder.legalName }}
                      </span>
                    </td>
                    <td>
                      <span v-if="shareholder.type === 'individual'">
                        {{ shareholder.idCode }}
                      </span>
                      <span v-else>
                        {{ shareholder.legalCode }}
                      </span>
                    </td>
                    <td>{{ shareholder.share }} €</td>
                    <td>{{ calculatePercentage(shareholder.share, company.capital) }}%</td>
                    <td>
                      <span v-if="shareholder.isFounder">Jah</span>
                      <span v-else>Ei</span>
                    </td>
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
  </MainLayout>
</template>

<script>
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
      company: null
    }
  },
  created() {
    this.fetchCompanyData()
  },
  methods: {
    fetchCompanyData() {
      const companyId = this.$route.params.id

      if (companyId) {
        this.company = {
          name: 'Näidis Osaühing OÜ',
          regCode: '1234567',
          foundingDate: '2023-05-15',
          capital: 5000,
          shareholders: [
            {
              type: 'individual',
              firstName: 'Marju',
              lastName: 'Lepik',
              idCode: '48702124567',
              share: 2500,
              isFounder: true
            },
            {
              type: 'individual',
              firstName: 'Jaak',
              lastName: 'Tamm',
              idCode: '38505176238',
              share: 1500,
              isFounder: true
            },
            {
              type: 'legal',
              legalName: 'Investeeringud OÜ',
              legalCode: '12345678',
              share: 1000,
              isFounder: false
            }
          ]
        }
      } else {
        this.error = 'Osaühingut ei leitud'
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
      const regCode = this.company?.regCode
      if (regCode) {
        this.$router.push(`/company/${regCode}/capital`)
      }
    }
  }
}
</script>