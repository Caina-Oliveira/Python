/* eslint-disable import-helpers/order-imports */
import * as rax from 'retry-axios';
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.SKYNET_BASE_URL,
  headers: {
    authorization: `Bearer ${process.env.INTEGRATION_KEY}`,
  },
});

api.defaults.raxConfig = {
  instance: api,
  retry: 10,
  retryDelay: 5000, // 5 segundos
};

rax.attach(api);

export default api;
