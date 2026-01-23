<script setup>             //Cpmopsition API
    import BankDepositService from '../services/BankDeposit.js';
    import { ref, onMounted } from 'vue';

    const deposits = ref([])
    const loading = ref(false)
    const errorMsg = ref('')

    function toNum(v) {
      const n = Number(v)
      return Number.isFinite(n) ? n : 0
    }

    function money(n) {
      return toNum(n).toFixed(2)
    }

    function depositSum(d) {
      return money(toNum(d.principal_value) + toNum(d.topup_value))
    }

    function accruedSum(d) {
      return money(
        toNum(d.accrued_value) +
        toNum(d.capitalized_value) +
        toNum(d.paid_value)
      )
    }

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


    async function refreshWithJobs() {
      loading.value = true
      errorMsg.value = ''
      try {
        // 1) берём текущий список, чтобы знать id
        const { data: list } = await BankDepositService.getAllBankDeposit()
        const items = Array.isArray(list) ? list : []

        // 2) запускаем jobs для каждого депозита (параллельно)
        const results = await Promise.allSettled(
          items.map(d => BankDepositService.runJobs(d.id))
        )

        // 3) перезагружаем список после jobs
        const { data: updated } = await BankDepositService.getAllBankDeposit()
        deposits.value = Array.isArray(updated) ? updated : []
      } catch (err) {
        errorMsg.value = err?.response?.data ?? err?.message ?? 'Ошибка загрузки'
        deposits.value = []
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
      <button @click="refreshWithJobs" :disabled="loading">
        {{ loading ? 'загружаю...' : 'обновить' }}
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
          <th>EAR %</th>
          <th>начислено</th>
          <th>дата закрытия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="d in deposits" :key="d.id">
          <td>{{ d.id }}</td>
          <td>{{ d.bank_name }}</td>
          <td>{{ depositSum(d) }}</td>
          <td>{{ d.duration }}</td>
          <td>{{ d.effective_rate }}</td>
          <td>{{ accruedSum(d) }}</td>
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
