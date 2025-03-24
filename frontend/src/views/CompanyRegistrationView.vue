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
              <ul
                v-if="shareholder.searchResults && shareholder.searchResults.length"
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
            <button type="submit" class="btn btn-primary" :disabled="!isFormValid">
              Salvesta
            </button>
          </div>
        </div>
      </form>
    </div>
  </MainLayout>
</template>

<script>
import MainLayout from '../components/layout/MainLayout.vue'
import BreadcrumbComponent from "@/components/common/BreadcrumbComponent.vue";

export default {
  name: 'CompanyForm',
  components: {
    BreadcrumbComponent,
    MainLayout
  },
  data() {
    return {
      // Mock data – replace with real search if needed
      mockIndividuals: [
        {firstName: 'Mari', lastName: 'Maasikas', idCode: '49001010000'},
        {firstName: 'Jüri', lastName: 'Õun', idCode: '38001010001'},
      ],
      mockLegals: [
        {legalName: 'Firma OÜ', legalCode: '1234567'},
        {legalName: 'Test AS', legalCode: '7654321'},
      ],

      company: {
        name: '',
        regCode: '',
        foundingDate: '',
        capital: 2500,
        shareholders: []
      },
      errors: {}
    }
  },
  computed: {
    today() {
      return new Date().toISOString().split('T')[0]
    },
    calculatedCapital() {
      return this.company.shareholders.reduce((sum, shareholder) => sum + (Number(shareholder.share) || 0), 0)
    },
    capitalPercentage() {
      return this.company.capital
          ? (this.calculatedCapital / this.company.capital) * 100
          : 0
    },
    isFormValid() {
      return (
          this.company.name.length >= 3 &&
          this.company.regCode.length === 7 &&
          this.company.foundingDate &&
          this.company.capital >= 2500 &&
          this.company.shareholders.length > 0 &&
          this.calculatedCapital === this.company.capital
      )
    }
  },
  created() {
    this.addShareholder()
  },
  methods: {
    goHome() {
      this.$router.push('/')
    },
    addShareholder() {
      this.company.shareholders.push({
        type: 'individual',
        firstName: '',
        lastName: '',
        idCode: '',
        legalName: '',
        legalCode: '',
        share: 0,

        searchQuery: '',
        searchResults: []
      })
    },
    removeShareholder(index) {
      this.company.shareholders.splice(index, 1)
    },
    validateForm() {
      this.errors = {}
      let isValid = true

      if (!this.company.name || this.company.name.length < 3 || this.company.name.length > 100) {
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
      })

      return isValid
    },
    searchPerson(index) {
      const shareholder = this.company.shareholders[index]
      const query = shareholder.searchQuery.toLowerCase().trim()

      if (!query) {
        shareholder.searchResults = []
        return
      }

      if (shareholder.type === 'individual') {

        shareholder.searchResults = this.mockIndividuals
            .filter((p) =>
                p.firstName.toLowerCase().includes(query) ||
                p.lastName.toLowerCase().includes(query) ||
                p.idCode.includes(query)
            )
            .map((p) => ({
              display: `${p.firstName} ${p.lastName} (ID: ${p.idCode})`,
              ...p
            }))
      } else {

        shareholder.searchResults = this.mockLegals
            .filter((p) =>
                p.legalName.toLowerCase().includes(query) ||
                p.legalCode.includes(query)
            )
            .map((p) => ({
              display: `${p.legalName} (Reg: ${p.legalCode})`,
              ...p
            }))
      }
    },
    selectPerson(index, person) {
      const shareholder = this.company.shareholders[index]
      if (shareholder.type === 'individual') {
        shareholder.firstName = person.firstName
        shareholder.lastName = person.lastName
        shareholder.idCode = person.idCode
      } else {
        shareholder.legalName = person.legalName
        shareholder.legalCode = person.legalCode
      }
      shareholder.searchQuery = person.display
      shareholder.searchResults = []
    },
    submitForm() {
      if (!this.validateForm()) {
        return
      }

      console.log('Form submitted:', this.company)
      this.$router.push('/company/' + this.company.regCode)
    }
  }
}
</script>
