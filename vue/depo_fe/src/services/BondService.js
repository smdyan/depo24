import axios from 'axios'

const BOND_API_BASE_URL = 'http://127.0.0.1:8000/bond';
class BondService{
    getBonds(){
        return axios.get( BOND_API_BASE_URL );
    }

    getBondItem( Id ){
        return axios.get( BOND_API_BASE_URL + '/' + Id );
    }
}

export default new BondService();