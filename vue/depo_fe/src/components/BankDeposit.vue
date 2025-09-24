<script setup> //Cpmopsition API
    import BankDepositService from '../services/BankDepositService.js';
    import { ref, onMounted, watch } from 'vue';

    const num = ref(1)
    const bankDeposit = ref({})

    function getBankDeposit(id) {
        BankDepositService.getBankDeposit(id).then((response) => {
            bankDeposit.value = response.data;
        });
    }

    onMounted(() => {
        getBankDeposit(num.value);
    });

    watch(num, (val) => {
        if (typeof val === 'number' && !Number.isNaN(val)) {
            getBankDeposit(val);
        }
    });
</script>

<template>
    <div class="tab"> 
        <div>
            <label>id:</label>
            <input type="number" v-model.number="num" />
            <button @click="num--">prev</button>
            <button @click="num++">next</button>
        </div>
        <ul>
            <li v-for="key in Object.keys( bankDeposit )">
                {{key}}: {{bankDeposit[key]}}
            </li>
        </ul>
    </div>    
</template>
