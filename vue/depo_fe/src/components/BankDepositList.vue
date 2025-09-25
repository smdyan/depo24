<script setup>             //Cpmopsition API
    import BankDepositService from '../services/BankDepositService.js';
    import { ref, onMounted } from 'vue';

    const deposits = ref([])
    const loading = ref(false)
    const errorMsg = ref('')


    async function getAllBankDeposit() {
        loading.value = true
        errorMsg.value = ''
        deposits.value = []
        try {
            const { data } = await BankDepositService.getAllBankDeposit()
            // ожидаем массив BankDepositPublic
            deposits.value = Array.isArray(data) ? data : []
        } catch (err) {
            errorMsg.value = err?.response?.data ?? err?.message ?? 'Ошибка загрузки'
        } finally {
            loading.value = false
        }
    }

    onMounted(() => {
        getAllBankDeposit()
    })

</script>

<template>
  <div class="tab">
    <div style="margin-bottom:8px">
      <button @click="getAllBankDeposit" :disabled="loading">
        {{ loading ? 'загружаю...' : 'обновить список' }}
      </button>
    </div>

    <div v-if="errorMsg" style="color:#b00">{{ errorMsg }}</div>

    <table v-else>
      <thead>
        <tr>
          <th>id</th>
          <th>банк</th>
          <th>ставка* %</th>
          <th>срок (дн)</th>
          <th>дата открытия</th>
          <th>дата закрытия</th>
          <th>сумма</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="d in deposits" :key="d.id">
          <td>{{ d.id }}</td>
          <td>{{ d.bankName }}</td>
          <td>{{ d.interestRate }}</td>
          <td>{{ d.duration }}</td>
          <td>{{ d.dateOpen }}</td>
          <td>{{ d.dateClose }}</td>
          <td>{{ d.faceValue }}</td>
        </tr>
        <tr v-if="!loading && deposits.length === 0">
          <td colspan="7" style="text-align:center; color:#666">список пуст</td>
        </tr>
      </tbody>
    </table>
    <span> * с учетом капитализации</span>
  </div>
</template>

<style scoped>
table { border-collapse: collapse; width: 100%; max-width: 800px; }
th, td { border: 1px solid #ddd; padding: 6px 8px; font-size: 14px; }
th { background: #f6f6f6; text-align: left; }
</style>
