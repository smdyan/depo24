import axios from 'axios'

const BANK_API_URL = 'http://127.0.0.1:8000/banks/';

class miscService{

    getBank(id){
        return axios.get( BANK_API_URL + id );
    }

    getAllBank(){
        return axios.get( BANK_API_URL );
    }
}

export default new miscService();