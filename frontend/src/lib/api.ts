
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true, // Critical: sends cookies
});

// Access token is short-lived and sent in response body only

export default api;