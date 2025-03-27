<template>
  <MainLayout>
    <div class="container">
      <div v-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <template v-else-if="company">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <BreadcrumbComponent
            :pageName="company.name"
            @home-click="goHome"
            @middle-click="goHome"
          />
          <button type="button" class="btn btn-primary" @click="goHome">
            <i class="bi bi-arrow-left me-1"></i> Tagasi
          </button>
        </div>

        <form @submit.prevent="submitForm">
          <div class="shadow-sm rounded bg-white p-4 mb-4">
            <h2 class="h5 mb-4">Osakapitali muutmine</h2>

            <!-- Company information -->
            <div class="row mb-3">
              <div class="col-md-6 mb-3">
                <label for="companyName" class="form-label">Osaühingu nimi</label>
                <input type="text" class="form-control" id="companyName" v-model="company.name" disabled>
              </div>
              <div class="col-md-6 mb-3">
                <label for="regCode" class="form-label">Registrikood</label>
                <input type="text" class="form-control" id="regCode" v-model="company.reg_code" disabled>
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-6 mb-3">
                <label for="currentCapital" class="form-label">Praegune kogukapital (€)</label>
                <input type="number" class="form-control" id="currentCapital" v-model.number="originalCapital" disabled>
              </div>
              <div class="col-md-6 mb-3">
                <label for="newCapital" class="form-label">
                  Uus kogukapital (€)<span class="text-danger">*</span>
                </label>
                <input type="number" class="form-control" id="newCapital" v-model.number="company.capital"
                       :class="{ 'is-invalid': errors.capital }" min="2500" required>
                <div v-if="errors.capital" class="invalid-feedback">
                  {{ errors.capital }}
                </div>
              </div>
            </div>

            <div v-if="shareholders.length > 0" class="alert alert-secondary mb-4">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div>Jaotatud kapital:</div>
                <div>{{ calculatedCapital }}€ / {{ company.capital }}€</div>
              </div>
              <div class="progress" style="height: 6px;">
                <div class="progress-bar"
                     :class="calculatedCapital === company.capital ? 'bg-success' : ''"
                     role="progressbar" :style="{ width: capitalPercentage + '%' }"
                     aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </div>

            <!-- Shareholders section -->
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h2 class="h5 mb-0">Osanikud</h2>
              <button type="button" class="btn btn-primary" @click="addShareholder">
                <i class="bi bi-plus-circle me-1"></i> Lisa osanik
              </button>
            </div>
            <div v-if="errors.shareholders" class="alert alert-danger mb-3">
              {{ errors.shareholders }}
            </div>

            <div v-for="(sh, index) in shareholders" :key="index" class="mb-4 p-3 border rounded shadow-sm">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <p><strong>Osanik:</strong> <strong>{{ getShareholderLabel(sh, index) }}</strong></p>
                <button v-if="!sh.original" type="button" class="btn btn-danger" @click="removeShareholder(index)">
                  <i class="bi bi-trash me-1"></i> Kustuta
                </button>
              </div>

              <div v-if="!sh.original" class="mb-3">
                <label class="form-label d-block">Osaniku tüüp<span class="text-danger">*</span></label>
                <div class="btn-group" role="group">
                  <input type="radio" class="btn-check" :name="'shareholderType' + index" :id="'individual' + index"
                         value="individual" v-model="sh.type">
                  <label class="btn btn-outline-primary" :for="'individual' + index">Füüsiline isik</label>
                  <input type="radio" class="btn-check" :name="'shareholderType' + index" :id="'legal' + index"
                         value="legal" v-model="sh.type">
                  <label class="btn btn-outline-primary" :for="'legal' + index">Juriidiline isik</label>
                </div>
              </div>

              <div v-if="!sh.original" class="mb-3">
                <label class="form-label d-block">Otsi isikut või ettevõtet</label>
                <input type="text" class="form-control" v-model="sh.searchQuery"
                       @input="searchPerson(index)" placeholder="Otsi...">
                <div v-if="sh.isSearching" class="mt-2">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Otsin...</span>
                  </div>
                  <span class="ms-2">Otsin...</span>
                </div>
                <ul v-else-if="sh.searchResults && sh.searchResults.length" class="list-group mt-2">
                  <li v-for="(result, rIndex) in sh.searchResults" :key="rIndex"
                      class="list-group-item list-group-item-action" @click="selectPerson(index, result)">
                    {{ result.display }}
                  </li>
                </ul>
                <div v-else-if="sh.searchPerformed && !sh.searchResults.length && sh.searchQuery" class="alert alert-info mt-2">
                  Tulemusi ei leitud. Sisesta täpsem otsingusõna või lisa uus.
                </div>
              </div>

              <!-- Editable fields for individuals -->
              <div v-if="sh.type === 'individual' && !sh.original" class="mb-3">
                <div class="row">
                  <div class="col-md-4 mb-3">
                    <label :for="'firstName' + index" class="form-label">Eesnimi<span class="text-danger">*</span></label>
                    <input type="text" class="form-control" :id="'firstName' + index" v-model="sh.firstName" required>
                  </div>
                  <div class="col-md-4 mb-3">
                    <label :for="'lastName' + index" class="form-label">Perenimi<span class="text-danger">*</span></label>
                    <input type="text" class="form-control" :id="'lastName' + index" v-model="sh.lastName" required>
                  </div>
                  <div class="col-md-4 mb-3">
                    <label :for="'idCode' + index" class="form-label">Isikukood<span class="text-danger">*</span></label>
                    <input type="text" class="form-control" :id="'idCode' + index" v-model="sh.idCode" required>
                  </div>
                </div>
              </div>

              <!-- Legal entity editable fields -->
              <div v-if="sh.type === 'legal' && !sh.original" class="mb-3">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label :for="'legalName' + index" class="form-label">Ettevõtte nimi<span class="text-danger">*</span></label>
                    <input type="text" class="form-control" :id="'legalName' + index" v-model="sh.legalName" required>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label :for="'legalCode' + index" class="form-label">Registrikood<span class="text-danger">*</span></label>
                    <input type="text" class="form-control" :id="'legalCode' + index" v-model="sh.legalCode" required>
                  </div>
                </div>
              </div>

              <!-- Static info -->
              <div class="row">
                <div class="col-md-6 mb-3">
                  <p>Isikutüüp: {{ sh.type === 'individual' ? 'Füüsiline isik' : 'Juriidiline isik' }}</p>
                </div>
                <div class="col-md-6 mb-3">
                  <p>Asutaja: {{ sh.isFounder ? 'Jah' : 'Ei' }}</p>
                </div>
              </div>

              <!-- Share inputs -->
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label :for="'originalShare' + index" class="form-label">Hetkeosalus (€)</label>
                  <input type="number" class="form-control" :id="'originalShare' + index" :value="sh.originalShare || 0" disabled>
                </div>
                <div class="col-md-6 mb-3">
                  <label :for="'share' + index" class="form-label">Uus osalus (€)<span class="text-danger">*</span></label>
                  <input type="number" class="form-control" :id="'share' + index" v-model.number="sh.share"
                         :class="{ 'is-invalid': errors['share' + index] }" min="1" placeholder="Vähemalt 1€" required>
                  <div v-if="errors['share' + index]" class="invalid-feedback">
                    {{ errors['share' + index] }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Form buttons -->
            <div class="text-end mt-4">
              <button type="button" class="btn btn-secondary me-2" @click="navigateToCompany">Tühista</button>
              <button type="submit" class="btn btn-primary" :disabled="!isFormValid || submitting">
                <span v-if="submitting">
                  <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                  Salvestamine...
                </span>
                <span v-else>Salvesta</span>
              </button>
            </div>
          </div>
        </form>
      </template>

      <div v-else class="container text-center mt-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Laadimine...</span>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import axios from 'axios'
import MainLayout from '../components/layout/MainLayout.vue'
import BreadcrumbComponent from '../components/common/BreadcrumbComponent.vue'

export default {
  name: 'CapitalIncreaseView',
  components: {
    MainLayout,
    BreadcrumbComponent
  },
  data() {
    return {
      error: null,
      originalCapital: 0,
      company: {
        id: null,
        name: '',
        reg_code: '',
        capital: 0
      },
      shareholders: [],
      errors: {},
      submitting: false,
      searchTimeout: null
    }
  },
  computed: {
    calculatedCapital() {
      return this.shareholders.reduce((sum, sh) => sum + (Number(sh.share) || 0), 0)
    },
    capitalPercentage() {
      return this.company.capital ? (this.calculatedCapital / this.company.capital) * 100 : 0
    },
    isFormValid() {
      return (
        this.company.capital >= this.originalCapital &&
        this.company.capital >= 2500 &&
        this.shareholders.length > 0 &&
        this.calculatedCapital === this.company.capital
      )
    }
  },
  created() {
    const companyId = this.$route.params.id
    if (companyId) {
      this.loadCompany(companyId)
    }
  },
  methods: {
    goHome() {
      this.$router.push('/')
    },
    navigateToCompany() {
      this.$router.push('/company/' + this.company.id)
    },
    addShareholder() {
      this.shareholders.push({
        id: null,
        type: 'individual',
        firstName: '',
        lastName: '',
        idCode: '',
        legalName: '',
        legalCode: '',
        share: 0,
        isFounder: false,
        original: false,
        originalShare: 0,
        searchQuery: '',
        searchResults: [],
        isSearching: false,
        searchPerformed: false
      })
    },
    removeShareholder(index) {
      this.shareholders.splice(index, 1)
      if (this.shareholders.length === 0) this.addShareholder()
    },
    getShareholderLabel(shareholder, index) {
      if (shareholder.original) {
        if (shareholder.type === 'individual') {
          return `${shareholder.firstName} ${shareholder.lastName}`
        } else {
          return shareholder.legalName
        }
      }
      return `${index + 1}`
    },
    async loadCompany(id) {
      try {
        const apiBaseUrl = process.env.VUE_APP_API_URL || ''
        const companyResponse = await axios.get(`${apiBaseUrl}/companies/${id}`)
        const data = companyResponse.data
        this.company = {
          id: data.id,
          name: data.name,
          reg_code: data.reg_code,
          capital: Number(data.capital)
        }
        this.originalCapital = Number(data.capital)
        const shResponse = await axios.get(`${apiBaseUrl}/shareholdings/`, { params: { company_id: id } })
        this.shareholders = await Promise.all(
          shResponse.data.map(async sh => {
            const personResponse = await axios.get(`${apiBaseUrl}/persons/${sh.person_id}`)
            const person = personResponse.data
            return {
              id: sh.id,
              type: person.type,
              firstName: person.first_name || '',
              lastName: person.last_name || '',
              idCode: person.id_code || '',
              legalName: person.legal_name || '',
              legalCode: person.reg_code || '',
              share: sh.share,
              isFounder: sh.is_founder || false,
              original: true,
              originalShare: Number(sh.share),
              searchQuery: '',
              searchResults: [],
              isSearching: false,
              searchPerformed: false
            }
          })
        )
      } catch (error) {
        console.error('Failed to load company:', error)
        alert(`Viga osaühingu laadimisel: ${error.response?.data?.detail || error.message}`)
      }
    },
    async searchPerson(index) {
      const shareholder = this.shareholders[index]
      const query = shareholder.searchQuery?.toLowerCase().trim() || ''
      shareholder.isSearching = query.length >= 2
      shareholder.searchResults = []
      clearTimeout(this.searchTimeout)
      if (query.length < 2) return

      this.searchTimeout = setTimeout(async () => {
        try {
          const apiBaseUrl = process.env.VUE_APP_API_URL || ''
          const params = new URLSearchParams()
          params.append('type', shareholder.type)
          if (query) params.append('search', query)
          const response = await axios.get(`${apiBaseUrl}/persons/`, { params })
          const results = response.data
          shareholder.searchResults = results.map(p =>
            shareholder.type === 'individual'
              ? {
                  id: p.id,
                  display: `${p.first_name} ${p.last_name} (${p.id_code || 'N/A'})`,
                  first_name: p.first_name,
                  last_name: p.last_name,
                  id_code: p.id_code
                }
              : {
                  id: p.id,
                  display: `${p.legal_name} (${p.reg_code || 'N/A'})`,
                  legal_name: p.legal_name,
                  reg_code: p.reg_code
                }
          )
        } catch (error) {
          console.error('Search failed:', error)
          alert('Otsingul esines viga')
        } finally {
          shareholder.isSearching = false
          shareholder.searchPerformed = true
        }
      }, 300)
    },
    selectPerson(index, person) {
      const shareholder = this.shareholders[index]
      shareholder.id = person.id
      if (shareholder.type === 'individual') {
        shareholder.firstName = person.first_name
        shareholder.lastName = person.last_name
        shareholder.idCode = person.id_code
        shareholder.legalName = ''
        shareholder.legalCode = ''
      } else {
        shareholder.legalName = person.legal_name
        shareholder.legalCode = person.reg_code
        shareholder.firstName = ''
        shareholder.lastName = ''
        shareholder.idCode = ''
      }
      shareholder.searchQuery = person.display
      shareholder.searchResults = []
      shareholder.searchPerformed = false
    },

    validateForm() {
      this.errors = {}
      let isValid = true

      if (!this.company.capital || this.company.capital < 2500) {
        this.errors.capital = 'Kogukapital peab olema vähemalt 2500€'
        isValid = false
      }
      if (this.company.capital < this.originalCapital) {
        this.errors.capital = 'Uus kapital ei saa olla väiksem kui esialgne kapital'
        isValid = false
      }
      if (this.calculatedCapital !== this.company.capital) {
        this.errors.shareholders = 'Osanike osade summa peab võrduma kogukapitaliga'
        isValid = false
      }
      this.shareholders.forEach((shareholder, index) => {
        if (!shareholder.share || shareholder.share < 1) {
          this.errors['share' + index] = 'Osalus peab olema vähemalt 1€'
          isValid = false
        }
        if (shareholder.type === 'individual') {
          if (!shareholder.firstName?.trim()) {
            this.errors[`firstName${index}`] = 'Eesnimi on kohustuslik'
            isValid = false
          }
          if (!shareholder.lastName?.trim()) {
            this.errors[`lastName${index}`] = 'Perenimi on kohustuslik'
            isValid = false
          }
          if (!shareholder.idCode?.trim()) {
            this.errors[`idCode${index}`] = 'Isikukood on kohustuslik'
            isValid = false
          }
        } else {
          if (!shareholder.legalName?.trim()) {
            this.errors[`legalName${index}`] = 'Ettevõtte nimi on kohustuslik'
            isValid = false
          }
          if (!shareholder.legalCode?.trim()) {
            this.errors[`legalCode${index}`] = 'Registrikood on kohustuslik'
            isValid = false
          }
        }
      })
      return isValid
    },
    async submitForm() {
      if (!this.validateForm()) return
      const apiBaseUrl = process.env.VUE_APP_API_URL || ''
      const companyId = this.company.id

      const payload = {
        new_capital: String(this.company.capital),
        original_capital: String(this.originalCapital),
        shareholders: this.shareholders.map(s => ({
          id: s.original ? s.id : null,
          type: s.type,
          first_name: s.type === 'individual' ? s.firstName : null,
          last_name: s.type === 'individual' ? s.lastName : null,
          id_code: s.type === 'individual' ? s.idCode : null,
          legal_name: s.type === 'legal' ? s.legalName : null,
          reg_code: s.type === 'legal' ? s.legalCode : null,
          share: String(s.share),
          is_founder: s.isFounder
        }))
      }

      try {
        await axios.put(`${apiBaseUrl}/companies/${companyId}/capital_update`, payload)
        alert('Osakapital edukalt uuendatud!')
        this.navigateToCompany()
      } catch (error) {
        console.error('Submit error:', error)
        alert(`Viga salvestamisel: ${error.response?.data?.detail || error.message}`)
      }
    }
  }
}
</script>
