<script setup>
  import BankDepositService from '../services/BankDepositService.js';
  import { ref, reactive, computed, onMounted, watch } from 'vue';

  const today = new Date().toISOString().split('T')[0]

  const form = reactive({
    bank_name: 'sber',
    client_name: 'alfat',
    duration: 365,
    interest_rate: 10,
    interest_term: 1,
    date_open: today,
    face_value: 1000,
    description: 'na'
  })
  
  const isActive = ref(false)

  function resetForm() {
    Object.assign(form, {
      bank_name: '',
      client_name: '',
      duration: 0,
      interest_rate: 0,
      interest_term: 1,
      date_open: '',
      face_value: 0,
      description: ''
    })
  }

  async function postDeposit() {
    if (isActive.value) return
    isActive.value = true


    try {
      const payload = {
        bank_name: form.bank_name.trim(),
        client_name: form.client_name.trim(),
        duration: Number(form.duration) || 0,
        interest_rate: Number(form.interest_rate) || 0,
        date_open: form.date_open,
        face_value: Number(form.face_value) || 0,
        description: form.description.trim(),
        interest_term: Number(form.interest_term) || 1,
      }

    if (!payload.bank_name || !payload.client_name) {
      throw new Error('Заполните название банка и имя клиента')
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
    <input type="text" v-model="form.bank_name" />
    <label>имя клиента</label>
    <input type="text" v-model="form.client_name" />
    <label>срок дней</label>
    <input type="number" v-model.number="form.duration" />
    <label>ставка %</label>
    <input type="number" v-model.number="form.interest_rate" />
    <label>порядок по %</label>
    <select v-model.number="form.interest_term" required>
      <option :value="1">в конце срока</option>
      <option :value="2">ежемесячно с капитализацией</option>
      <option :value="3">ежемесячно с выплатой</option>
    </select>
    <label>дата открытия</label>
    <input type="date" v-model="form.date_open" />
    <label>сумма вклада</label>
    <input type="number" v-model.number="form.face_value" />
    <label>описание</label>
    <input type="text" v-model="form.description" />
  </div>
  <br>
  <button :disabled="isActive || !form.bank_name || !form.client_name || !form.date_open" @click="postDeposit">
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
