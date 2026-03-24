import axios from 'axios';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const getBaseURL = () => {
  if (Platform.OS === 'android') {
    return 'https://unshabbily-pseudoinspiring-alfonso.ngrok-free.dev';
  }
  return 'http://localhost:8000';
};

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// ✅ Proper AsyncStorage wrapper
const storage = {
  getItem: async (key) => await AsyncStorage.getItem(key),
  setItem: async (key, value) => await AsyncStorage.setItem(key, value),
  removeItem: async (key) => await AsyncStorage.removeItem(key),
  clear: async () => await AsyncStorage.clear(),
};

// ✅ Attach token automatically
api.interceptors.request.use(async (config) => {
  

  const token = await AsyncStorage.getItem('access_token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export { storage };
export default api;