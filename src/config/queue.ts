import axios from 'axios';

const queue = axios.create({
  baseURL: 'https://prod.izicash.app/skynet',
});

export default queue;
