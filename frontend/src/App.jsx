/**
 * Router principal con rutas protegidas por rol.
 */

import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Clientes from "./pages/Clientes";
import Marcas from "./pages/Marcas";
import Usuarios from "./pages/Usuarios";
import FeatureFlags from "./pages/FeatureFlags";

function ProtectedRoute({ children, requireSuperadmin = false }) {
  const { user, loading } = useAuth();

  if (loading) return <div style={{ padding: "2rem" }}>Cargando...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (requireSuperadmin && user.rol !== "superadmin") return <Navigate to="/dashboard" replace />;

  return children;
}

export default function App() {
  const { user, loading } = useAuth();

  if (loading) return null;

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/dashboard" replace /> : <Login />}
      />
      <Route
        path="/dashboard"
        element={<ProtectedRoute><Dashboard /></ProtectedRoute>}
      />
      <Route
        path="/clientes"
        element={<ProtectedRoute requireSuperadmin><Clientes /></ProtectedRoute>}
      />
      <Route
        path="/marcas"
        element={<ProtectedRoute><Marcas /></ProtectedRoute>}
      />
      <Route
        path="/usuarios"
        element={<ProtectedRoute><Usuarios /></ProtectedRoute>}
      />
      <Route
        path="/feature-flags"
        element={<ProtectedRoute><FeatureFlags /></ProtectedRoute>}
      />
      <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} replace />} />
    </Routes>
  );
}
