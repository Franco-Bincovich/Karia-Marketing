import axios from "axios";
import { useCallback } from "react";

const api = axios.create({ baseURL: "/" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  const marca = localStorage.getItem("marca_activa_id");
  if (marca) config.headers["X-Marca-ID"] = marca;
  return config;
});

api.interceptors.response.use(
  (r) => r,
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
