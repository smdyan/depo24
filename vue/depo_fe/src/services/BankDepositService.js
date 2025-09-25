import axios from 'axios'

const DEPOSIT_API_BASE_URL = 'http://127.0.0.1:8000/deposit/';
class BankDepositService{
    getBankDeposit(id){
        return axios.get( DEPOSIT_API_BASE_URL + id );
    }

    getAllBankDeposit(){
        return axios.get( DEPOSIT_API_BASE_URL );
    }

    create(payload) {
    return axios.post(DEPOSIT_API_BASE_URL, payload, {
        headers: { 'Content-Type': 'application/json' }
        })
    }
}

export default new BankDepositService();