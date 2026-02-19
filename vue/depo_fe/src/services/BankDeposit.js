import axios from 'axios'

const DEPOSIT_API_BASE_URL = 'http://127.0.0.1:8000/deposits/';
const REFS_API_BASE_URL = 'http://127.0.0.1:8000/refs/';
class BankDepositService{
    getBankDeposit(id){
        return axios.get( DEPOSIT_API_BASE_URL + id );
    }

    getAllBankDeposit(){
        return axios.get( DEPOSIT_API_BASE_URL );
    }

    runJobs(id) {
        return axios.post(`${DEPOSIT_API_BASE_URL}${id}/run-jobs`)
    }

    createDeposit(payload) {
        return axios.post(DEPOSIT_API_BASE_URL, payload, {
        headers: { 'Content-Type': 'application/json' }
        })
    }

    getBanks() {
        return axios.get(REFS_API_BASE_URL + 'banks/')
    }

    getCustomers() {
        return axios.get(REFS_API_BASE_URL + 'customers/')
    }
}

export default new BankDepositService();