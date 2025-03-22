<script>
export default {
  name: 'NavBar',
  props: {
    navItems: {
      type: Array,
      required: true
    }
  }
}
</script>

<template>
  <nav>
    <ul class="nav">
      <li class="nav-item" v-for="item in navItems" :key="item.path">
        <router-link :to="item.path" class="nav-link">
          {{ item.title }}
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<style scoped>

</style>