/**
 * Estado global de autenticación: usuario, token, login/logout.
 */

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import api from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = useCallback(async () => {
    try {
      const { data } = await api.get(ENDPOINTS.ME);
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetchMe();
    } else {
      setLoading(false);
    }
  }, [fetchMe]);

  const login = useCallback(async (email, password) => {
    const { data } = await api.post(ENDPOINTS.LOGIN, { email, password });
    localStorage.setItem("access_token", data.access_token);
    await fetchMe();
    return data;
  }, [fetchMe]);

  const logout = useCallback(async () => {
    try {
      await api.post(ENDPOINTS.LOGOUT);
    } finally {
      localStorage.removeItem("access_token");
      setUser(null);
    }
  }, []);

  const isSuperadmin = user?.rol === "superadmin";
  const isAdmin = user?.rol === "admin" || isSuperadmin;

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isSuperadmin, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
