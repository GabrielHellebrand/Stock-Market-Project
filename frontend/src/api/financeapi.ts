import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // Make sure FastAPI runs on this
});

export const getQuarterlyPrediction = (symbol: string) =>
  api.get(`/predict/quarterly/${symbol}`);

export const getSp500Predictions = (limit = 50) =>
  api.get(`/predict/sp500?limit=${limit}`);

export const getChartImageUrl = (symbol: string) =>
  `${api.defaults.baseURL}/predict/quarterly/${symbol}/chart`;