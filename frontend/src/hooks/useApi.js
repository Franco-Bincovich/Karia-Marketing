/**
 * Hook de Axios con interceptors para JWT y manejo de 401.
 */

import axios from "axios";
import { useCallback } from "react";

const api = axios.create({ baseURL: "/" });

// Interceptor de request: adjunta JWT si existe
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor de response: limpia sesión en 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export function useApi() {
  const get = useCallback((url, params) => api.get(url, { params }), []);
  const post = useCallback((url, data) => api.post(url, data), []);
  const patch = useCallback((url, data) => api.patch(url, data), []);
  const del = useCallback((url) => api.delete(url), []);

  return { get, post, patch, delete: del, api };
}

export default api;
