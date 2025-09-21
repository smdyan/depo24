<script setup>
    import BankDepositService from '../services/BankDepositService.js';
    import { useDateField } from '../composables/useDateField.js'
    import { ref, computed, onMounted, watch } from 'vue';

    const bankName = ref('')
    const clientName = ref('')
    const duration = ref(0)
    const interestRate = ref(0)
    const interest_terms = ref(1)
    const { date: dateOpen, dateStr: dateOpenStr } = useDateField()
    const { date: dateClose, dateStr: dateCloseStr } = useDateField()
    const faceValue = ref(0)
    const description = ref('')
    const isActive = ref(false)

    function toggle() {
      isActive.value = !isActive.value
      const d = new Date(dateOpen.value)
      d.setDate(d.getDate() + duration.value)
      dateClose.value = d
    }
</script>

<template>
  <div class="form">
    <label>название банка</label>
    <input type="text" v-model="bankName" />
    <label>имя клиента</label>
    <input type="text" v-model="clientName" />
    <label>срок дней</label>
    <input type="number" v-model.number="duration" />
    <label>ставка %</label>
    <input type="number" v-model.number="interestRate" />
    <label for="interest_terms">порядок по %</label>
    <select id="interest_terms" v-model="interest_terms" required>
      <option value=1>в конце срока</option>
      <option value=2>ежемесячно с капитализацией</option>
      <option value=3>ежемесячно с выплатой</option>
    </select>
    <label>дата открытия</label>
    <input type="date" v-model.date="dateOpenStr" />
    <label>сумма вклада</label>
    <input type="number" v-model.number="faceValue" />
    <label>описание</label>
    <input type="text" v-model="description" />
    <div>дата закрытия </div>
    <div>{{ dateCloseStr }}</div>
  </div>
  <br>
  <button @click="toggle">расчитать</button>
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
