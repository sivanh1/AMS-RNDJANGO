import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';


const DEFAULT_API_URL = "https://unshabbily-pseudoinspiring-alfonso.ngrok-free.dev";


const api = axios.create({
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

const storage = {
  getItem: async (key) => await AsyncStorage.getItem(key),
  setItem: async (key, value) => await AsyncStorage.setItem(key, value),
  removeItem: async (key) => await AsyncStorage.removeItem(key),
  clear: async () => await AsyncStorage.clear(),
};

api.interceptors.request.use(async (config) => {

  let baseURL = await AsyncStorage.getItem('API_URL');

  if (!baseURL) {
    baseURL = DEFAULT_API_URL;
  }

  config.baseURL = baseURL;


  const token = await AsyncStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export { storage };
export default api;