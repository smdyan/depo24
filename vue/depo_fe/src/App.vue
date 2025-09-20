<script setup>
  import Title from './components/Title.vue'
  import BondItem from './components/BondItem.vue'
  import Demo from './components/Demo.vue'
</script>

<template>
  <header>
    <div>
      <Title msg="Depo24" />
    </div>
  </header>

  <main>
    <!-- <BondItem /> -->
    <Demo />
  </main>
</template>

<style>
body {
  background-color: #f0f0f0;
}
</style>
