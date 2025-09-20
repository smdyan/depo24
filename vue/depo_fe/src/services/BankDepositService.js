import axios from 'axios'

const DEPOSIT_API_BASE_URL = 'http://127.0.0.1:8000/deposit';
class BankDepositService{
    getBankDeposit( Id ){
        return axios.get( DEPOSIT_API_BASE_URL + '/' + Id );
    }
}

export default new BankDepositService();