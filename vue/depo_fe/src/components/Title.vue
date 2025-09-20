<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
defineProps({
  msg: {
    type: String,
    required: true,
  },
})

const usdRate = ref('load...')
let intervalId = null
async function getUsdRate() {
  try {
    const res = await fetch('https://www.cbr-xml-daily.ru/daily_json.js');
    const data = await res.json();
    usdRate.value = data.Valute.USD.Value.toFixed(2);
  } catch (e) {
    usdRate.value = 'load error'
  }
}

onMounted(() => {
       getUsdRate();
       intervalId = setInterval(getUsdRate, 300000) // автообновление
    })

onUnmounted(() => {
  clearInterval(intervalId)
})

</script>

<template>
  <div>
    <h1>{{ msg }}</h1>
    <h3> USD {{ usdRate }}</h3>
  </div>
</template>

<!-- styles removed -->
