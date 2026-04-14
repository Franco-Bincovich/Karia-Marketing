import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Clientes from "./pages/Clientes";
import Marcas from "./pages/Marcas";
import Usuarios from "./pages/Usuarios";
import FeatureFlags from "./pages/FeatureFlags";
import Prospeccion from "./pages/Prospeccion";
import Contenido from "./pages/Contenido";
import Calendario from "./pages/Calendario";
import SocialMedia from "./pages/SocialMedia";
import Ads from "./pages/Ads";
import SEO from "./pages/SEO";
import Analytics from "./pages/Analytics";
import Comunidad from "./pages/Comunidad";
import Onboarding from "./pages/Onboarding";
import CrearMarca from "./components/CrearMarca";

function ProtectedRoute({ children, requireSuperadmin = false, allowNoMarca = false }) {
  const { user, loading, marcaActiva } = useAuth();
  if (loading) return <div style={{ padding: "2rem", color: "#94A3B8" }}>Cargando...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (requireSuperadmin && user.rol !== "superadmin") return <Navigate to="/dashboard" replace />;
  if (!marcaActiva && !allowNoMarca) return <Navigate to="/crear-marca" replace />;
  return children;
}

function P({ children }) { return <ProtectedRoute>{children}</ProtectedRoute>; }

export default function App() {
  const { user, loading, marcaActiva } = useAuth();
  if (loading) return null;

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to={marcaActiva ? "/dashboard" : "/crear-marca"} replace /> : <Login />} />
      <Route path="/crear-marca" element={
        !user ? <Navigate to="/login" replace /> :
        marcaActiva ? <Navigate to="/dashboard" replace /> :
        <CrearMarca />
      } />
      <Route path="/dashboard" element={<P><Dashboard /></P>} />
      <Route path="/clientes" element={<ProtectedRoute requireSuperadmin allowNoMarca><Clientes /></ProtectedRoute>} />
      <Route path="/marcas" element={<ProtectedRoute allowNoMarca><Marcas /></ProtectedRoute>} />
      <Route path="/usuarios" element={<P><Usuarios /></P>} />
      <Route path="/feature-flags" element={<P><FeatureFlags /></P>} />
      <Route path="/prospeccion" element={<P><Prospeccion /></P>} />
      <Route path="/contenido" element={<P><Contenido /></P>} />
      <Route path="/calendario" element={<P><Calendario /></P>} />
      <Route path="/social-media" element={<P><SocialMedia /></P>} />
      <Route path="/ads" element={<P><Ads /></P>} />
      <Route path="/seo" element={<P><SEO /></P>} />
      <Route path="/analytics" element={<P><Analytics /></P>} />
      <Route path="/comunidad" element={<P><Comunidad /></P>} />
      <Route path="/onboarding" element={<P><Onboarding /></P>} />
      <Route path="*" element={<Navigate to={user ? (marcaActiva ? "/dashboard" : "/crear-marca") : "/login"} replace />} />
    </Routes>
  );
}
