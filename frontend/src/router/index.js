import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/company/:id',
    name: 'company',
    component: () => import('../views/CompanyView.vue')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/CompanyRegistrationView.vue')
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('../views/CompanySearchView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  linkActiveClass: 'active'
})

export default router
