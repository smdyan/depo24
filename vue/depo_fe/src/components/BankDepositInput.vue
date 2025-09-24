<script setup>
  import BankDepositService from '../services/BankDepositService.js';
  import { ref, reactive, computed, onMounted, watch } from 'vue';

  
  const form = reactive({
    bankName: '',
    clientName: '',
    duration: 0,
    interestRate: 0,
    interestTerm: 1,
    dateOpen: '',
    faceValue: 0,
    description: ''
  })
  
  const isActive = ref(false)

  function resetForm() {
    Object.assign(form, {
      bankName: '',
      clientName: '',
      duration: 0,
      interestRate: 0,
      interestTerm: 1,
      dateOpen: '',
      faceValue: 0,
      description: ''
    })
  }

  async function postDeposit() {
    if (isActive.value) return
    isActive.value = true


    try {
      const payload = {
        bankName: form.bankName.trim(),
        clientName: form.clientName.trim(),
        duration: Number(form.duration) || 0,
        interestRate: Number(form.interestRate) || 0,
        dateOpen: form.dateOpen,
        faceValue: Number(form.faceValue) || 0,
        description: form.description.trim(),
        interestTerm: Number(form.interestTerm) || 1,
      }

    if (!payload.bankName || !payload.clientName) {
      throw new Error('Заполните название банка и имя клиента')
    }
    if (!payload.dateOpen) {
      throw new Error('Выберите дату открытия')
    }

    const { data } = await BankDepositService.create(payload)
    console.log("ответ сервера:", data)
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
    <input type="text" v-model="form.bankName" />
    <label>имя клиента</label>
    <input type="text" v-model="form.clientName" />
    <label>срок дней</label>
    <input type="number" v-model.number="form.duration" />
    <label>ставка %</label>
    <input type="number" v-model.number="form.interestRate" />
    <label>порядок по %</label>
    <select v-model.number="form.interestTerm" required>
      <option :value="1">в конце срока</option>
      <option :value="2">ежемесячно с капитализацией</option>
      <option :value="3">ежемесячно с выплатой</option>
    </select>
    <label>дата открытия</label>
    <input type="date" v-model="form.dateOpen" />
    <label>сумма вклада</label>
    <input type="number" v-model.number="form.faceValue" />
    <label>описание</label>
    <input type="text" v-model="form.description" />
  </div>
  <br>
  <button :disabled="isActive || !form.bankName || !form.clientName || !form.dateOpen" @click="postDeposit">
  {{ isActive ? 'сохраняю...' : 'сохранить' }}
  </button>
  <dev> {{ form.dateOpen }}</dev>
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
