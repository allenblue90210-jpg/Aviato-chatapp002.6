
import axios from 'axios';

const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
// Ensure no double slash if backendUrl ends with /
const baseURL = backendUrl.endsWith('/') ? backendUrl + 'api' : backendUrl + '/api';

const api = axios.create({
  baseURL: baseURL,
  // Do not set Content-Type here globally, let Axios/Browser handle it
});

// Add a request interceptor to inject the token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('aviato_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Add Timezone Offset header to align backend logic with client time
    config.headers['X-Timezone-Offset'] = new Date().getTimezoneOffset();
    return config;
  },
  (error) => Promise.reject(error)
);

// Add a response interceptor to handle 401s
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('aviato_token');
      // window.location.href = '/signin'; // Optional: auto-redirect
    }
    return Promise.reject(error);
  }
);

export default api;
