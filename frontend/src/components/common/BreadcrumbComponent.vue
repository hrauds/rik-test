<template>
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb mb-0">
      <li class="breadcrumb-item">
        <a href="#" @click.prevent="$emit('home-click')">Avaleht</a>
      </li>
      <li v-if="middlePage" class="breadcrumb-item">
        <a href="#" @click.prevent="$emit('middle-click')">{{ middlePage }}</a>
      </li>
      <li v-if="pageName" class="breadcrumb-item active" aria-current="page">
        {{ pageName }}
      </li>
    </ol>
  </nav>
</template>

<script>
export default {
  name: 'BreadcrumbComponent',
  props: {
    pageName: {
      type: String,
      default: ''
    },
    middlePage: {
      type: String,
      default: ''
    }
  }
}
</script>
