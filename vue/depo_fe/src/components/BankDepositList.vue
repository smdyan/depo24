<script setup>             //Cpmopsition API
    import BankDepositService from '../services/BankDeposit.js';
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
          <th>сумма</th>
          <th>срок (дн)</th>
          <th>ставка ear %</th>
          <th>начислено</th>
          <th>выплачено</th>
          <th>всего</th>
          <th>дата закрытия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="d in deposits" :key="d.id">
          <td>{{ d.id }}</td>
          <td>{{ d.bank_name }}</td>
          <td>{{ d.principal_value }}</td>
          <td>{{ d.duration }}</td>
          <td>{{ d.effective_rate }}</td>
          <td>{{ d.interest_accrued }}</td>
          <td>{{ d.interest_paid }}</td>
          <td>{{ d.interest_total }}</td>
          <td>{{ d.date_close }}</td>
        </tr>
        <tr v-if="!loading && deposits.length === 0">
          <td colspan="7" style="text-align:center; color:#666">список пуст</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
table { border-collapse: collapse; width: 100%; max-width: 800px; }
th, td { border: 1px solid #ddd; padding: 6px 8px; font-size: 14px; }
th { background: #f6f6f6; text-align: left; }
</style>
