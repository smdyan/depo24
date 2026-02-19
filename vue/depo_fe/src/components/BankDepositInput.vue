<script setup>
  import BankDepositService from '../services/BankDeposit.js';
  import { ref, reactive, computed, onMounted, watch } from 'vue';

  const banks = ref([])        // [{id, short_name, ...}]
  const banksLoading = ref(false)
  
  async function loadBanks() {
    banksLoading.value = true
    try {
      const { data } = await BankDepositService.getBanks()
      banks.value = Array.isArray(data) ? data : []
    } 
    finally {
      banksLoading.value = false
    }
  }
  
  const customers = ref([])                     // [{id, short_name, ...}]
  const customersLoading = ref(false)

  async function loadCustomers() {
    customersLoading.value = true
    try {
      const { data } = await BankDepositService.getCustomers()
      customers.value = Array.isArray(data) ? data : []
    } 
    finally {
      customersLoading.value = false
    }
  }

  const interestModeOptions = [
    { label: "выплата", value: "payout" },
    { label: "капитализация", value: "capitalize" },
  ];

  const interestTermOptions = [
    { label: "в конце срока", value: "end_of_term" },
    { label: "ежемесячно", value: "monthly" },
  ];

  const today = new Date().toISOString().split('T')[0]

  function defaultForm() {
    return {
      bank_id: 0,
      customer_id: 0,
      description: "na",
      interest_term: "end_of_term",
      interest_period_basis: "deposit_open_date",
      interest_mode: "payout",
      nominal_rate: 9,
      duration: 365,
      date_open: today,
      principal_value: 1000,
    }
  }

  const form = reactive(defaultForm())

  function resetForm() {
    Object.assign(form, defaultForm())
  }

  watch(
    () => form.interest_term,
    (term) => {
      if (term === 'monthly') {
        form.interest_period_basis = 'calendar_month';
        form.interest_mode = 'capitalize';
      } else if (term === 'end_of_term') {
        form.interest_period_basis = 'deposit_open_date';
        form.interest_mode = 'payout';
      }
    },
    { immediate: true }
  );

  const isActive = ref(false)
  
  async function postDeposit() {
    if (isActive.value) return
    isActive.value = true

    try {
      const payload = {
        bank_id: form.bank_id,
        customer_id: form.customer_id,
        description: form.description.trim(),
        interest_term: form.interest_term,
        interest_period_basis: form.interest_period_basis,
        interest_mode: form.interest_mode,
        nominal_rate: Number(form.nominal_rate) || 0,
        duration: Number(form.duration),
        date_open: form.date_open,
        principal_value: Number(form.principal_value) || 0,
      }

    if (!payload.bank_id || !payload.customer_id) {
      throw new Error('Укажите банк и клиента')
    }
    if (!payload.date_open) {
      throw new Error('Выберите дату открытия')
    }

    const { data } = await BankDepositService.createDeposit(payload)
    resetForm()

  } catch (err) {
    console.error(err)
    alert(err?.response?.data ?? err.message ?? 'Ошибка сохранения')
  } finally {
    isActive.value = false
    }
  }

  onMounted(() => {
    console.log('mounted')
    loadBanks()
    loadCustomers()
  })

</script>

<template>
  <div class="form">
    <label>bank
      <select v-model.number="form.bank_id" :disabled="banksLoading" required>
        <option disabled :value="0">select...</option>
        <option
          v-for="b in banks"
          :key="b.id"
          :value="b.id"
          :disabled="b.status === false"
        >
          {{ b.short_name }}
        </option>
      </select>
    </label>

    <label>customer
      <select v-model.number="form.customer_id" :disabled="customersLoading" required>
        <option disabled :value="0">select...</option>
        <option
          v-for="c in customers"
          :key="c.id"
          :value="c.id"
          :disabled="c.status === false"
        >
          {{ c.full_name }}
        </option>
      </select>
    </label>

    <label>duration
      <input type="number" v-model.number="form.duration" min="1" />
    </label>

    <label>rate
      <input type="number" v-model.number="form.nominal_rate" step="1" min="0" />
    </label>

    <label>interest_term
      <select v-model="form.interest_term" required>
        <option v-for="opt in interestTermOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
    </label>

    <label>period_basis
      <select v-model="form.interest_period_basis" required>
        <option value="calendar_month">начало месяца</option>
        <option value="deposit_open_date">дата открытия</option>
      </select>
    </label>

    <label>interest mode
      <select v-model="form.interest_mode" required>
        <option v-for="opt in interestModeOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
    </label>
    
    <label>date_open
      <input type="date" v-model="form.date_open" />
    </label>

    <label>principal_value
      <input type="number" v-model.number="form.principal_value" step="1000" min="1" />
    </label>

    <label>description
      <input type="text" v-model="form.description" />
    </label>
  </div>
  <br />
  <button :disabled="isActive" @click="postDeposit">
    {{ isActive ? 'сохраняю...' : 'сохранить' }}
  </button>
</template>

<style scoped>
.form {
  --label-col: 160px;   /* ширина колонки для подписи */
  --col-gap: 16px;
  --row-gap: 10px;

  max-width: 560px;
  display: grid;
  gap: var(--row-gap);
}

/* каждый label = отдельная строка с 2 колонками */
.form label {
  display: grid;
  grid-template-columns: var(--label-col) 1fr;
  column-gap: var(--col-gap);
  align-items: center;

  margin: 0;
}

/* подпись (текст внутри label) */
.form label {
  font-weight: 500;
}

/* выравниваем текст подписи вправо */
.form label {
  justify-items: stretch;
}

/* чтобы сам текст подписи был справа, используем псевдо-колонку:
   текст label является "первым элементом" label-а, поэтому просто text-align */
.form label {
  text-align: right;
}

/* а для input/select отменяем text-align и растягиваем */
.form input,
.form select {
  text-align: left;
  width: 100%;
  max-width: 200px;
  box-sizing: border-box;
  padding: 6px 10px;
  font-size: 14px;
}

/* важно для grid, чтобы контролы не "вылезали" */
.form input,
.form select {
  min-width: 0;
}
</style>

