import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'token';

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

let isRedirectingToLogin = false;

client.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      
      if (!isRedirectingToLogin && !window.location.pathname.includes('/login')) {
        isRedirectingToLogin = true;
        window.location.href = '/login';
      }
    }
    
    if (error.response?.status === 403) {
      console.error('접근 권한이 없습니다.');
    }
    
    if (error.response?.status === 500) {
      console.error('서버 오류가 발생했습니다.');
    }
    
    if (!error.response) {
      console.error('네트워크 오류가 발생했습니다.');
    }
    
    return Promise.reject(error);
  }
);

export function resetRedirectFlag() {
  isRedirectingToLogin = false;
}

export default client;
