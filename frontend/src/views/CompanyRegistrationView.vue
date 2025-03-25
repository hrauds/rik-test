<template>
  <MainLayout>
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <BreadcrumbComponent
          pageName="Osaühingu registreerimine"
          @home-click="goHome"
        />
        <button type="button" class="btn btn-primary" @click="goHome">
          <i class="bi bi-arrow-left me-1"></i>Tagasi
        </button>
      </div>
      <form @submit.prevent="submitForm">
        <div class="shadow-sm rounded bg-white p-4 mb-4">
          <h2 class="h5 mb-4">Osaühingu andmed</h2>

          <div class="row mb-3">
            <div class="col-md-6 mb-3">
              <label for="companyName" class="form-label">Osaühingu nimi<span class="text-danger">*</span></label>
              <input
                  type="text"
                  class="form-control"
                  id="companyName"
                  v-model="company.name"
                  :class="{ 'is-invalid': errors.name }"
                  placeholder="3-100 tähemärki"
                  required
              >
              <div v-if="errors.name" class="invalid-feedback">{{ errors.name }}</div>
            </div>
            <div class="col-md-6 mb-3">
              <label for="regCode" class="form-label">Registrikood<span class="text-danger">*</span></label>
              <input
                  type="text"
                  class="form-control"
                  id="regCode"
                  v-model="company.regCode"
                  :class="{ 'is-invalid': errors.regCode }"
                  placeholder="7-kohaline number"
                  required
              >
              <div v-if="errors.regCode" class="invalid-feedback">{{ errors.regCode }}</div>
            </div>
          </div>

          <div class="row mb-3">
            <div class="col-md-6 mb-3">
              <label for="foundingDate" class="form-label">Asutamiskuupäev<span class="text-danger">*</span></label>
              <input
                  type="date"
                  class="form-control"
                  id="foundingDate"
                  v-model="company.foundingDate"
                  :class="{ 'is-invalid': errors.foundingDate }"
                  :max="today"
                  required
              >
              <div v-if="errors.foundingDate" class="invalid-feedback">{{ errors.foundingDate }}</div>
            </div>

            <div class="col-md-6 mb-3">
              <label for="capital" class="form-label">Kogukapital (€)<span class="text-danger">*</span></label>
              <input
                  type="number"
                  class="form-control"
                  id="capital"
                  v-model.number="company.capital"
                  :class="{ 'is-invalid': errors.capital }"
                  min="2500"
                  placeholder="Vähemalt 2500€"
                  required
              >
              <div v-if="errors.capital" class="invalid-feedback">{{ errors.capital }}</div>
            </div>
          </div>

          <div v-if="company.shareholders.length > 0" class="alert alert-secondary mb-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>Jaotatud kapital:</div>
              <div>{{ calculatedCapital }}€ / {{ company.capital }}€</div>
            </div>
            <div class="progress" style="height: 6px;">
              <div
                  class="progress-bar"
                  :class="calculatedCapital === company.capital ? 'bg-success' : ''"
                  role="progressbar"
                  :style="{ width: capitalPercentage + '%' }"
                  aria-valuemin="0"
                  aria-valuemax="100"
              ></div>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="h5 mb-0">Osanikud</h2>
            <button type="button" class="btn btn-primary" @click="addShareholder">
              <i class="bi bi-plus-circle me-1"></i> Lisa osanik
            </button>
          </div>

          <div v-if="errors.shareholders" class="alert alert-danger mb-3">
            {{ errors.shareholders }}
          </div>

          <div
            v-for="(shareholder, index) in company.shareholders"
            :key="index"
            class="mb-4 p-3 border rounded shadow-sm"
          >
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h3 class="h6 mb-0">Osanik {{ index + 1 }}</h3>
              <button
                  type="button"
                  class="btn btn-danger"
                  @click="removeShareholder(index)"
                  :disabled="company.shareholders.length === 1"
              >
                <i class="bi bi-trash me-1"></i> Kustuta
              </button>
            </div>

            <div class="mb-3">
              <label class="form-label d-block"
                >Osaniku tüüp<span class="text-danger">*</span></label
              >
              <div class="btn-group" role="group">
                <input
                    type="radio"
                    class="btn-check"
                    :name="'shareholderType' + index"
                    :id="'individual' + index"
                    value="individual"
                    v-model="shareholder.type"
                />
                <label
                  class="btn btn-outline-primary"
                  :for="'individual' + index"
                >
                  Füüsiline isik
                </label>

                <input
                    type="radio"
                    class="btn-check"
                    :name="'shareholderType' + index"
                    :id="'legal' + index"
                    value="legal"
                    v-model="shareholder.type"
                />
                <label class="btn btn-outline-primary" :for="'legal' + index">
                  Juriidiline isik
                </label>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label d-block"
                >Otsi isikut või ettevõtet</label
              >
              <input
                  type="text"
                  class="form-control"
                  v-model="shareholder.searchQuery"
                  @input="searchPerson(index)"
                  placeholder="Otsi..."
              />
              <div v-if="shareholder.isSearching" class="mt-2">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                  <span class="visually-hidden">Otsin...</span>
                </div>
                <span class="ms-2">Otsin...</span>
              </div>
              <ul
                v-else-if="shareholder.searchResults && shareholder.searchResults.length"
                class="list-group mt-2"
              >
                <li
                  v-for="(result, rIndex) in shareholder.searchResults"
                  :key="rIndex"
                  class="list-group-item list-group-item-action"
                  @click="selectPerson(index, result)"
                >
                  {{ result.display }}
                </li>
              </ul>
              <div v-else-if="shareholder.searchPerformed && !shareholder.searchResults.length && shareholder.searchQuery" class="alert alert-info mt-2">
                Tulemusi ei leitud. Sisesta täpsem otsingusõna või lisa uus.
              </div>
            </div>

            <div v-if="shareholder.type === 'individual'" class="mb-3">
              <div class="row">
                <div class="col-md-4 mb-3">
                  <label :for="'firstName' + index" class="form-label"
                    >Eesnimi<span class="text-danger">*</span></label
                  >
                  <input
                      type="text"
                      class="form-control"
                      :id="'firstName' + index"
                      v-model="shareholder.firstName"
                      required
                  />
                </div>
                <div class="col-md-4 mb-3">
                  <label :for="'lastName' + index" class="form-label"
                    >Perenimi<span class="text-danger">*</span></label
                  >
                  <input
                      type="text"
                      class="form-control"
                      :id="'lastName' + index"
                      v-model="shareholder.lastName"
                      required
                  />
                </div>
                <div class="col-md-4 mb-3">
                  <label :for="'idCode' + index" class="form-label"
                    >Isikukood<span class="text-danger">*</span></label
                  >
                  <input
                      type="text"
                      class="form-control"
                      :id="'idCode' + index"
                      v-model="shareholder.idCode"
                      required
                  />
                </div>
              </div>
            </div>

            <div v-if="shareholder.type === 'legal'" class="mb-3">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label :for="'legalName' + index" class="form-label"
                    >Ettevõtte nimi<span class="text-danger">*</span></label
                  >
                  <input
                      type="text"
                      class="form-control"
                      :id="'legalName' + index"
                      v-model="shareholder.legalName"
                      required
                  />
                </div>
                <div class="col-md-6 mb-3">
                  <label :for="'legalCode' + index" class="form-label"
                    >Registrikood<span class="text-danger">*</span></label
                  >
                  <input
                      type="text"
                      class="form-control"
                      :id="'legalCode' + index"
                      v-model="shareholder.legalCode"
                      required
                  />
                </div>
              </div>
            </div>

            <div class="mb-3">
              <label :for="'share' + index" class="form-label"
                >Osalus (€)<span class="text-danger">*</span></label
              >
              <input
                  type="number"
                  class="form-control"
                  :id="'share' + index"
                  v-model.number="shareholder.share"
                  :class="{ 'is-invalid': errors['share'+index] }"
                  min="1"
                  placeholder="Vähemalt 1€"
                  required
              />
              <div v-if="errors['share'+index]" class="invalid-feedback">
                {{ errors['share'+index] }}
              </div>
            </div>
          </div>

          <div class="text-end mt-4">
            <button type="button" class="btn btn-secondary me-2" @click="goHome">
              Tühista
            </button>
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
    </div>
  </MainLayout>
</template>

<script>
import axios from 'axios'
import MainLayout from '../components/layout/MainLayout.vue'
import BreadcrumbComponent from "@/components/common/BreadcrumbComponent.vue";

export default {
  name: 'CompanyRegistrationView',
  components: {
    BreadcrumbComponent,
    MainLayout
  },

  data() {
    return {
      company: {
        name: '',
        regCode: '',
        foundingDate: '',
        capital: 2500,
        shareholders: []
      },
      errors: {},
      searchTimeout: null,
      submitting: false
    }
  },

  computed: {
    today() {
      return new Date().toISOString().split('T')[0]
    },
    calculatedCapital() {
      return this.company.shareholders.reduce(
        (sum, shareholder) => sum + (Number(shareholder.share) || 0),
        0
      )
    },
    capitalPercentage() {
      return this.company.capital
        ? (this.calculatedCapital / this.company.capital) * 100
        : 0
    },
    isFormValid() {
      return (
        this.company.name.length >= 3 &&
        this.company.name.length <= 100 &&
        this.company.regCode.length === 7 &&
        /^\d{7}$/.test(this.company.regCode) &&
        this.company.foundingDate &&
        this.company.capital >= 2500 &&
        this.company.shareholders.length > 0 &&
        this.calculatedCapital === this.company.capital
      )
    }
  },

  created() {
    this.addShareholder()
    const companyId = this.$route.params.id
    if (companyId) {
      this.loadCompany(companyId)
    }
  },

  methods: {
    goHome() {
      this.$router.push('/')
    },

    addShareholder() {
      this.company.shareholders.push({
        id: null,
        type: 'individual',
        firstName: '',
        lastName: '',
        idCode: '',
        legalName: '',
        legalCode: '',
        share: 0,
        searchQuery: '',
        searchResults: [],
        isSearching: false,
        searchPerformed: false
      })
    },

    removeShareholder(index) {
      this.company.shareholders.splice(index, 1)
      if (this.company.shareholders.length === 0) {
        this.addShareholder()
      }
    },

    async loadCompany(id) {
      try {
        const apiBaseUrl = process.env.VUE_APP_API_URL || '';
        const response = await axios.get(`${apiBaseUrl}/companies/${id}`)
        const data = response.data

        this.company = {
          name: data.name,
          regCode: data.reg_code,
          foundingDate: data.founding_date,
          capital: Number(data.capital),
          shareholders: (data.shareholders || []).map(s => ({
            id: s.id,
            type: s.type,
            share: Number(s.share),
            ...(s.type === 'individual'
              ? {
                  firstName: s.first_name,
                  lastName: s.last_name,
                  idCode: s.id_code,
                  searchQuery: `${s.first_name} ${s.last_name}`,
                  legalName: '',
                  legalCode: ''
                }
              : {
                  legalName: s.name,
                  legalCode: s.reg_code,
                  searchQuery: s.name,
                  firstName: '',
                  lastName: '',
                  idCode: ''
                }),
            searchResults: [],
            isSearching: false,
            searchPerformed: false
          }))
        }

        if (this.company.shareholders.length === 0) {
          this.addShareholder()
        }
      } catch (error) {
        console.error('Failed to load company:', error)
        alert(`Viga osaühingu laadimisel: ${error.response?.data?.detail || error.message}`)
      }
    },

    validateForm() {
      this.errors = {}
      let isValid = true

      if (!this.company.name?.trim() || this.company.name.length < 3 || this.company.name.length > 100) {
        this.errors.name = 'Nimi peab olema 3 kuni 100 tähemärki pikk'
        isValid = false
      }

      if (!this.company.regCode || !/^\d{7}$/.test(this.company.regCode)) {
        this.errors.regCode = 'Registrikood peab olema 7-kohaline number'
        isValid = false
      }

      if (!this.company.foundingDate) {
        this.errors.foundingDate = 'Asutamiskuupäev on kohustuslik'
        isValid = false
      }

      if (!this.company.capital || this.company.capital < 2500) {
        this.errors.capital = 'Kogukapital peab olema vähemalt 2500€'
        isValid = false
      }

      if (this.calculatedCapital !== this.company.capital) {
        this.errors.shareholders = 'Osanike osade summa peab võrduma kogukapitaliga'
        isValid = false
      }

      this.company.shareholders.forEach((shareholder, index) => {
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
      if (!this.validateForm() || this.submitting) return

      this.submitting = true
      const apiBaseUrl = process.env.VUE_APP_API_URL || '';

      try {
        const validatedShareholders = []
        for (const shareholder of this.company.shareholders) {
          let personId = shareholder.id;

          if (!personId) {
            try {
              let personData;

              if (shareholder.type === 'individual') {
                personData = {
                  type: 'individual',
                  first_name: shareholder.firstName,
                  last_name: shareholder.lastName,
                  id_code: shareholder.idCode
                };
              } else {
                personData = {
                  type: 'legal',
                  legal_name: shareholder.legalName,
                  reg_code: shareholder.legalCode
                };
              }

              console.log('Creating person with data:', personData);
              const response = await axios.post(`${apiBaseUrl}/persons/`, personData);
              personId = response.data.id;
              console.log('Person created with ID:', personId);
            } catch (error) {
              console.error('Person creation error:', error);
              console.error('Response:', error.response?.data);
              throw new Error(`Isiku lisamine ebaõnnestus: ${error.response?.data?.detail || error.message}`);
            }
          } else {
            try {
              await axios.get(`${apiBaseUrl}/persons/${personId}`);
            } catch (error) {
              throw new Error(`Isikut ei leitud: ${error.response?.data?.detail || error.message}`);
            }
          }

          validatedShareholders.push({
            ...shareholder,
            personId: personId
          });
        }

        const companyData = {
          name: this.company.name,
          reg_code: this.company.regCode,
          founding_date: this.company.foundingDate,
          capital: String(this.company.capital)
        };

        let savedCompany;
        try {
          if (this.$route.params.id) {
            const response = await axios.put(`${apiBaseUrl}/companies/${this.$route.params.id}`, companyData);
            savedCompany = response.data;
          } else {
            const response = await axios.post(`${apiBaseUrl}/companies/`, companyData);
            savedCompany = response.data;
          }
        } catch (error) {
          throw new Error(`Osaühingu salvestamine ebaõnnestus: ${error.response?.data?.detail || error.message}`);
        }

        for (const shareholder of validatedShareholders) {
          const shareData = {
            company_id: savedCompany.id,
            person_id: shareholder.personId,
            share: String(shareholder.share)
          };

          try {
            await axios.post(`${apiBaseUrl}/shareholdings/`, shareData);
          } catch (error) {
            throw new Error(`Osaluse salvestamine ebaõnnestus: ${error.response?.data?.detail || error.message}`);
          }
        }

        alert(this.$route.params.id ? 'Osaühing edukalt uuendatud!' : 'Osaühing edukalt registreeritud!');
        this.$router.push('/company/' + savedCompany.id);
      } catch (error) {
        console.error('Submit error:', error);
        console.error('Response data:', error.response?.data);
        console.error('Response status:', error.response?.status);
        alert(`Viga salvestamisel: ${error.message}`);
      } finally {
        this.submitting = false;
      }
    },

    async searchPerson(index) {
      const shareholder = this.company.shareholders[index]
      const query = shareholder.searchQuery?.toLowerCase().trim() || ''

      shareholder.isSearching = query.length >= 2
      shareholder.searchResults = []

      clearTimeout(this.searchTimeout)

      if (query.length < 2) return

      this.searchTimeout = setTimeout(async () => {
        try {
          const apiBaseUrl = process.env.VUE_APP_API_URL || '';
          const params = new URLSearchParams();
          params.append('type', shareholder.type);
          if (query) params.append('search', query);

          const response = await axios.get(`${apiBaseUrl}/persons/`, {params});
          const results = response.data;

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
                    display: `${p.name} (${p.reg_code || 'N/A'})`,
                    name: p.name,
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
      const shareholder = this.company.shareholders[index]

      shareholder.id = person.id

      if (shareholder.type === 'individual') {
        shareholder.firstName = person.first_name
        shareholder.lastName = person.last_name
        shareholder.idCode = person.id_code
        shareholder.legalName = ''
        shareholder.legalCode = ''
      } else {
        shareholder.legalName = person.name
        shareholder.legalCode = person.reg_code
        shareholder.firstName = ''
        shareholder.lastName = ''
        shareholder.idCode = ''
      }

      shareholder.searchQuery = person.display
      shareholder.searchResults = []
    }
  }
}
</script>
