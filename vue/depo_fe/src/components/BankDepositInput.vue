<script setup>
  import BankDepositService from '../services/BankDeposit.js';
  import { ref, reactive, computed, onMounted, watch } from 'vue';

  const today = new Date().toISOString().split('T')[0]

  function defaultForm() {
    return {
      bank_id: 0,
      customer_id: 0,
      duration: 365,
      date_open: today,
      principal_value: 0,
      nominal_rate: 0,
      interest_term: 1,
      description: "na",
    }
  }

  const form = reactive(defaultForm())

  function resetForm() {
    Object.assign(form, defaultForm())
  }

  const isActive = ref(false)
  
  async function postDeposit() {
    if (isActive.value) return
    isActive.value = true

    try {
      const payload = {
        bank_id: form.bank_id,
        customer_id: form.customer_id,
        duration: Number(form.duration),
        date_open: form.date_open,
        principal_value: Number(form.principal_value) || 0,
        nominal_rate: Number(form.nominal_rate) || 0,
        interest_term: Number(form.interest_term) || 1,
        description: form.description.trim(),
      }

    if (!payload.bank_id || !payload.customer_id) {
      throw new Error('Укажите банк и клиента')
    }
    if (!payload.date_open) {
      throw new Error('Выберите дату открытия')
    }

    const { data } = await BankDepositService.create(payload)
    resetForm()

  } catch (err) {
    console.error(err)
    alert(err?.response?.data ?? err.message ?? 'Ошибка сохранения')
  } finally {
    isActive.value = false
    }
  }
</script>

<template>
  <div class="form">
    <label>название банка</label>
    <input type="text" v-model.number="form.bank_id" />
    <label>имя клиента</label>
    <input type="text" v-model.number="form.customer_id" />
    <label>срок дней</label>
    <input type="number" v-model.number="form.duration" />
    <label>ставка %</label>
    <input type="number" v-model.number="form.nominal_rate" />
    <label>порядок по %</label>
    <select v-model.number="form.interest_term" required>
      <option :value="1">в конце срока</option>
      <option :value="2">ежемесячно с капитализацией</option>
      <option :value="3">ежемесячно с выплатой</option>
    </select>
    <label>дата открытия</label>
    <input type="date" v-model="form.date_open" />
    <label>сумма вклада</label>
    <input type="number" v-model.number="form.principal_value" />
    <label>описание</label>
    <input type="text" v-model="form.description" />
  </div>
  <br>
  <button :disabled="isActive" @click="postDeposit">
  {{ isActive ? 'сохраняю...' : 'сохранить' }}
  </button>
</template>

<style scoped>
.form {
  display: grid;
  grid-template-columns: 150px 1fr; /* ширина колонки для label и input */
  gap: 8px 16px;                   /* строки и колонки */
  align-items: center;             /* вертикальное выравнивание */
  max-width: 500px;                /* чтобы форма не растягивалась слишком */
}

.form label {
  text-align: right;   /* подписи прижаты к правому краю */
  padding-right: 8px;
  font-weight: 500;
}

.form input {
  padding: 4px 8px;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
}
</style>
