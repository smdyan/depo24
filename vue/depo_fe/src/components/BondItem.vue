<script setup> //Cpmopsition API
    import BondService from '../services/BondService.js';
    import { ref, onMounted, watch } from 'vue';

    const num = ref(1)
    const bondItem = ref({})

    function getBondItem(id) {
        BondService.getBondItem(id).then((response) => {
            bondItem.value = response.data;
        });
    }

    onMounted(() => {
        getBondItem(num.value);
    });

    watch(num, (val) => {
        if (typeof val === 'number' && !Number.isNaN(val)) {
            getBondItem(val);
        }
    });
</script>

<template>
    <div> 
        <h1> Bond Item </h1>
        <h3>
            <label for="bondId">id:</label>
            <input type="number" id="bondId" name="bondId" v-model.number="num" />
        </h3>
        <ul>
            <li v-for="key in Object.keys( bondItem )">
                {{key}}: {{bondItem[key]}}
            </li>
        </ul>
    </div>    
</template>
