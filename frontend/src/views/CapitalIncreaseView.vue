<template>
  <MainLayout>
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <BreadcrumbComponent
            pageName="Osakapitali muutmine"
            :middlePage="company.name"
            @home-click="navigateToHome"
            @middle-click="navigateToCompany"
        />
        <button type="button" class="btn btn-primary" @click="navigateToCompany">
          <i class="bi bi-arrow-left me-1"></i> Tagasi
        </button>
      </div>

      <form @submit.prevent="submitForm">
        <div class="shadow-sm rounded bg-white p-4 mb-4">
          <h2 class="h5 mb-4">Osakapitali muutmine</h2>

          <div class="row mb-3">
            <div class="col-md-6 mb-3">
              <label for="companyName" class="form-label">Osaühingu nimi</label>
              <input
                  type="text"
                  class="form-control"
                  id="companyName"
                  v-model="company.name"
                  disabled
              >
            </div>

            <div class="col-md-6 mb-3">
              <label for="regCode" class="form-label">Registrikood</label>
              <input
                  type="text"
                  class="form-control"
                  id="regCode"
                  v-model="company.regCode"
                  disabled
              >
            </div>
          </div>

          <div class="row mb-3">
            <div class="col-md-6 mb-3">
              <label for="currentCapital" class="form-label">Praegune kogukapital (€)</label>
              <input
                  type="number"
                  class="form-control"
                  id="currentCapital"
                  v-model.number="originalCapital"
                  disabled
              >
            </div>

            <div class="col-md-6 mb-3">
              <label for="newCapital" class="form-label">Uus kogukapital (€)<span class="text-danger">*</span></label>
              <input
                  type="number"
                  class="form-control"
                  id="newCapital"
                  v-model.number="company.capital"
                  :class="{ 'is-invalid': errors.capital }"
                  min="2500"
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

          <div v-for="(shareholder, index) in company.shareholders" :key="index" class="mb-4 p-3 border rounded shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h3 class="h6 mb-0">{{ getShareholderLabel(shareholder, index) }}</h3>
              <button
                  v-if="!shareholder.original"
                  type="button"
                  class="btn btn-danger"
                  @click="removeShareholder(index)"
              >
                <i class="bi bi-trash me-1"></i> Kustuta
              </button>
            </div>

            <div v-if="!shareholder.original" class="mb-3">
              <label class="form-label d-block">Osaniku tüüp<span class="text-danger">*</span></label>
              <div class="btn-group" role="group">
                <input
                    type="radio"
                    class="btn-check"
                    :name="'shareholderType' + index"
                    :id="'individual' + index"
                    value="individual"
                    v-model="shareholder.type"
                >
                <label class="btn btn-outline-primary" :for="'individual' + index">Füüsiline isik</label>

                <input
                    type="radio"
                    class="btn-check"
                    :name="'shareholderType' + index"
                    :id="'legal' + index"
                    value="legal"
                    v-model="shareholder.type"
                >
                <label class="btn btn-outline-primary" :for="'legal' + index">Juriidiline isik</label>
              </div>
            </div>

            <div v-if="shareholder.type === 'individual' && !shareholder.original" class="mb-3">
              <div class="row">
                <div class="col-md-4 mb-3">
                  <label :for="'firstName' + index" class="form-label">Eesnimi<span class="text-danger">*</span></label>
                  <input
                      type="text"
                      class="form-control"
                      :id="'firstName' + index"
                      v-model="shareholder.firstName"
                      required
                  >
                </div>
                <div class="col-md-4 mb-3">
                  <label :for="'lastName' + index" class="form-label">Perenimi<span class="text-danger">*</span></label>
                  <input
                      type="text"
                      class="form-control"
                      :id="'lastName' + index"
                      v-model="shareholder.lastName"
                      required
                  >
                </div>
                <div class="col-md-4 mb-3">
                  <label :for="'idCode' + index" class="form-label">Isikukood<span class="text-danger">*</span></label>
                  <input
                      type="text"
                      class="form-control"
                      :id="'idCode' + index"
                      v-model="shareholder.idCode"
                      required
                  >
                </div>
              </div>
            </div>

            <div v-if="shareholder.type === 'legal' && !shareholder.original" class="mb-3">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label :for="'legalName' + index" class="form-label">Ettevõtte nimi<span class="text-danger">*</span></label>
                  <input
                      type="text"
                      class="form-control"
                      :id="'legalName' + index"
                      v-model="shareholder.legalName"
                      required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label :for="'legalCode' + index" class="form-label">Registrikood<span class="text-danger">*</span></label>
                  <input
                      type="text"
                      class="form-control"
                      :id="'legalCode' + index"
                      v-model="shareholder.legalCode"
                      required
                  >
                </div>
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label :for="'originalShare' + index" class="form-label">Hetkeosalus (€)</label>
                <input
                    type="number"
                    class="form-control"
                    :id="'originalShare' + index"
                    :value="shareholder.originalShare || 0"
                    disabled
                >
              </div>
              <div class="col-md-6 mb-3">
                <label :for="'share' + index" class="form-label">Uus osalus (€)<span class="text-danger">*</span></label>
                <input
                    type="number"
                    class="form-control"
                    :id="'share' + index"
                    v-model.number="shareholder.share"
                    :class="{ 'is-invalid': errors['share'+index] }"
                    min="1"
                    placeholder="Vähemalt 1€"
                    required
                >
                <div v-if="errors['share'+index]" class="invalid-feedback">
                  {{ errors['share'+index] }}
                </div>
              </div>
            </div>
          </div>

          <div class="text-end mt-4">
            <button type="button" class="btn btn-secondary me-2" @click="navigateToCompany">Tühista</button>
            <button type="submit" class="btn btn-primary" :disabled="!isFormValid">Salvesta</button>
          </div>
        </div>
      </form>
    </div>
  </MainLayout>
</template>

<script>
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
      originalCapital: 0,
      company: {
        name: '',
        regCode: '',
        capital: 0,
        shareholders: []
      },
      errors: {}
    }
  },
  computed: {
    calculatedCapital() {
      return this.company.shareholders.reduce((sum, shareholder) => sum + (Number(shareholder.share) || 0), 0)
    },
    capitalPercentage() {
      return this.company.capital ? (this.calculatedCapital / this.company.capital) * 100 : 0
    },
    isFormValid() {
      return (
        this.company.capital >= this.originalCapital &&
        this.company.capital >= 2500 &&
        this.company.shareholders.length > 0 &&
        this.calculatedCapital === this.company.capital
      )
    }
  },
  created() {
    this.fetchCompanyData()
  },
  methods: {
    fetchCompanyData() {
      const companyId = this.$route.params.id

      const mockCompany = {
        name: 'Näidis Osaühing OÜ',
        regCode: '1234567',
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

      if (companyId) {
        this.originalCapital = mockCompany.capital

        this.company = {
          name: mockCompany.name,
          regCode: mockCompany.regCode,
          capital: mockCompany.capital,
          shareholders: mockCompany.shareholders.map(s => ({
            ...s,
            original: true,
            originalShare: s.share
          }))
        }
      }
    },

    navigateToHome() {
      this.$router.push('/')
    },

    navigateToCompany() {
      this.$router.push('/company/' + this.company.regCode)
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
        isFounder: false,
        original: false,
        originalShare: 0
      })
    },

    removeShareholder(index) {
      if (!this.company.shareholders[index].original) {
        this.company.shareholders.splice(index, 1)
      }
    },

    getShareholderLabel(shareholder, index) {
      if (shareholder.original) {
        if (shareholder.type === 'individual') {
          return `${shareholder.firstName} ${shareholder.lastName}`
        } else {
          return shareholder.legalName
        }
      }
      return `Uus osanik ${index + 1}`
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

      this.company.shareholders.forEach((shareholder, index) => {
        if (!shareholder.share || shareholder.share < 1) {
          this.errors['share'+index] = 'Osalus peab olema vähemalt 1€'
          isValid = false
        }
      })

      return isValid
    },

    submitForm() {
      if (!this.validateForm()) {
        return
      }

      console.log('Capital increase submitted:', {
        companyId: this.company.regCode,
        newCapital: this.company.capital,
        originalCapital: this.originalCapital,
        shareholders: this.company.shareholders.map(s => ({
          id: s.original ? s.id : null,
          type: s.type,
          firstName: s.type === 'individual' ? s.firstName : null,
          lastName: s.type === 'individual' ? s.lastName : null,
          idCode: s.type === 'individual' ? s.idCode : null,
          legalName: s.type === 'legal' ? s.legalName : null,
          legalCode: s.type === 'legal' ? s.legalCode : null,
          share: s.share,
          isFounder: s.isFounder,
          isNew: !s.original
        }))
      })

      this.navigateToCompany()
    }
  }
}
</script>
