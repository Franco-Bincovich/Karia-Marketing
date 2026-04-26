import { createContext, useCallback, useContext, useEffect, useState } from "react";
import api from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [marcas, setMarcas] = useState([]);
  const [marcaActiva, setMarcaActivaState] = useState(null);
  const [modo, setModo] = useState("copilot");
  const [completitud, setCompletitud] = useState(0);

  function setMarcaActiva(marca) {
    setMarcaActivaState(marca);
    if (marca?.id) {
      localStorage.setItem("marca_activa_id", marca.id);
    } else {
      localStorage.removeItem("marca_activa_id");
    }
  }

  const fetchMarcas = useCallback(async (clienteId) => {
    try {
      const { data } = await api.get(ENDPOINTS.CLIENTE_MARCAS(clienteId));
      const list = Array.isArray(data) ? data : data.data || [];
      setMarcas(list);
      const savedId = localStorage.getItem("marca_activa_id");
      const saved = list.find((m) => m.id === savedId);
      if (saved) {
        setMarcaActiva(saved);
      } else if (list.length > 0) {
        setMarcaActiva(list[0]);
      } else {
        setMarcaActiva(null);
      }
      return list;
    } catch {
      setMarcas([]);
      setMarcaActiva(null);
      return [];
    }
  }, []);

  const fetchCompletitud = useCallback(async () => {
    try {
      const { data } = await api.get(ENDPOINTS.ONBOARDING_ESTADO);
      setCompletitud(data.completitud || 0);
      return data.completitud || 0;
    } catch {
      return 0;
    }
  }, []);

  const fetchMe = useCallback(async () => {
    try {
      const { data } = await api.get(ENDPOINTS.ME);
      setUser(data);
      if (data.cliente_id) {
        const list = await fetchMarcas(data.cliente_id);
        if (list.length > 0) {
          // fetchCompletitud will run after marca_activa_id is set in localStorage
          setTimeout(() => fetchCompletitud(), 100);
        }
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [fetchMarcas, fetchCompletitud]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) fetchMe();
    else setLoading(false);
  }, [fetchMe]);

  const login = useCallback(
    async (email, password) => {
      const { data } = await api.post(ENDPOINTS.LOGIN, { email, password });
      localStorage.setItem("access_token", data.access_token);
      await fetchMe();
      return data;
    },
    [fetchMe]
  );

  const logout = useCallback(async () => {
    try {
      await api.post(ENDPOINTS.LOGOUT);
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("marca_activa_id");
      setUser(null);
      setMarcaActiva(null);
      setMarcas([]);
    }
  }, []);

  const addMarca = useCallback((marca) => {
    setMarcas((prev) => [...prev, marca]);
    setMarcaActiva(marca);
  }, []);

  const isSuperadmin = user?.rol === "superadmin";
  const isAdmin = user?.rol === "admin" || isSuperadmin;

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isSuperadmin,
        isAdmin,
        marcas,
        marcaActiva,
        setMarcaActiva,
        addMarca,
        modo,
        setModo,
        completitud,
        setCompletitud,
        fetchCompletitud,
        fetchMarcas,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
