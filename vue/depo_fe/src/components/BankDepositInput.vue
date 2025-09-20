<script setup>
    import BankDepositService from '../services/BankDepositService.js';
    import { useDateField } from '../composables/useDateField.js'
    import { ref, computed, onMounted, watch } from 'vue';

    const bankName = ref('')
    const clientName = ref('')
    
    
    const  = computed({
      get() { 
        if (!dateOpen.value || !dateClose.value) {
          return 0 // значение по умолчанию
        }
        const difMs = dateClose.value - dateOpen.value
        const difDays = difMs / (1000 * 60 * 60 * 24)
        return difDays
      },
      set(newValue) {
        const d = new Date(dateOpen.value)
        d.setDate(d.getDate() + newValue)
        dateClose.value = d
      }
    })
    const interestRate = ref(0)
    const interestPeriod = ref(0)
    const { date: dateOpen, dateStr: dateOpenStr } = useDateField()
    const { date: dateClose, dateStr: dateCloseStr } = useDateField()
    const faceValue = ref(0)
    const description = ref('')

    watch(duration, (val) => {
        interestPeriod.value = val
    });
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
    <label>период выплат %</label>
    <input type="number" v-model.number="interestPeriod" />
    <label>дата открытия</label>
    <input type="date" v-model.date="dateOpenStr" />
    <label>сумма вклада</label>
    <input type="number" v-model.number="faceValue" />
    <label>описание</label>
    <input type="text" v-model="description" />
  </div>
  <div>
    <span>дата закрытия </span>
    <span>{{ dateCloseStr ?? '—' }}</span>
  </div>
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

    <!-- const duration = computed({
      get() { 
        if (!dateOpen.value || !dateClose.value) {
          return 0 // значение по умолчанию
        }
        const difMs = dateClose.value - dateOpen.value
        const difDays = difMs / (1000 * 60 * 60 * 24)
        return difDays
      },
      set(newValue) {
        const d = new Date(dateOpen.value)
        d.setDate(d.getDate() + newValue)
        dateClose.value = d
      }
    }) -->