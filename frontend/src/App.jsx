import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

// Eager: rutas críticas (login, dashboard, crear marca)
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import CrearMarca from "./components/CrearMarca";

// Lazy: todas las demás rutas — se cargan bajo demanda
const Clientes = lazy(() => import("./pages/Clientes"));
const Marcas = lazy(() => import("./pages/Marcas"));
const Usuarios = lazy(() => import("./pages/Usuarios"));
const FeatureFlags = lazy(() => import("./pages/FeatureFlags"));
const Prospeccion = lazy(() => import("./pages/Prospeccion"));
const Contenido = lazy(() => import("./pages/Contenido"));
const Calendario = lazy(() => import("./pages/Calendario"));
const SocialMedia = lazy(() => import("./pages/SocialMedia"));
const Ads = lazy(() => import("./pages/Ads"));
const SEO = lazy(() => import("./pages/SEO"));
const Analytics = lazy(() => import("./pages/Analytics"));
const Comunidad = lazy(() => import("./pages/Comunidad"));
const Onboarding = lazy(() => import("./pages/Onboarding"));
const Estrategia = lazy(() => import("./pages/Estrategia"));
const Creativo = lazy(() => import("./pages/Creativo"));
const Reporting = lazy(() => import("./pages/Reporting"));
const SocialListening = lazy(() => import("./pages/SocialListening"));
const AgentesIA = lazy(() => import("./pages/AgentesIA"));
const Organigrama = lazy(() => import("./pages/Organigrama"));
const PerfilMarca = lazy(() => import("./pages/PerfilMarca"));
const Automatizaciones = lazy(() => import("./pages/Automatizaciones"));
const ConfiguracionAPIs = lazy(() => import("./pages/ConfiguracionAPIs"));

function ProtectedRoute({ children, requireSuperadmin = false, allowNoMarca = false }) {
  const { user, loading, marcaActiva } = useAuth();
  if (loading) return <div style={{ padding: "2rem", color: "#94A3B8" }}>Cargando...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (requireSuperadmin && user.rol !== "superadmin") return <Navigate to="/dashboard" replace />;
  if (!marcaActiva && !allowNoMarca) return <Navigate to="/crear-marca" replace />;
  return children;
}

function P({ children }) {
  return <ProtectedRoute>{children}</ProtectedRoute>;
}

export default function App() {
  const { user, loading, marcaActiva } = useAuth();
  if (loading) return null;

  return (
    <Suspense fallback={<div style={{ padding: "2rem", color: "#FF6B00" }}>Cargando...</div>}>
      <Routes>
        <Route
          path="/login"
          element={
            user ? <Navigate to={marcaActiva ? "/dashboard" : "/crear-marca"} replace /> : <Login />
          }
        />
        <Route
          path="/crear-marca"
          element={
            !user ? (
              <Navigate to="/login" replace />
            ) : marcaActiva ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <CrearMarca />
            )
          }
        />
        <Route
          path="/dashboard"
          element={
            <P>
              <Dashboard />
            </P>
          }
        />
        <Route
          path="/clientes"
          element={
            <ProtectedRoute requireSuperadmin allowNoMarca>
              <Clientes />
            </ProtectedRoute>
          }
        />
        <Route
          path="/marcas"
          element={
            <ProtectedRoute allowNoMarca>
              <Marcas />
            </ProtectedRoute>
          }
        />
        <Route
          path="/usuarios"
          element={
            <P>
              <Usuarios />
            </P>
          }
        />
        <Route
          path="/feature-flags"
          element={
            <P>
              <FeatureFlags />
            </P>
          }
        />
        <Route
          path="/prospeccion"
          element={
            <P>
              <Prospeccion />
            </P>
          }
        />
        <Route
          path="/contenido"
          element={
            <P>
              <Contenido />
            </P>
          }
        />
        <Route
          path="/calendario"
          element={
            <P>
              <Calendario />
            </P>
          }
        />
        <Route
          path="/social-media"
          element={
            <P>
              <SocialMedia />
            </P>
          }
        />
        <Route
          path="/ads"
          element={
            <P>
              <Ads />
            </P>
          }
        />
        <Route
          path="/seo"
          element={
            <P>
              <SEO />
            </P>
          }
        />
        <Route
          path="/analytics"
          element={
            <P>
              <Analytics />
            </P>
          }
        />
        <Route
          path="/comunidad"
          element={
            <P>
              <Comunidad />
            </P>
          }
        />
        <Route
          path="/onboarding"
          element={
            <P>
              <Onboarding />
            </P>
          }
        />
        <Route
          path="/estrategia"
          element={
            <P>
              <Estrategia />
            </P>
          }
        />
        <Route
          path="/creativo"
          element={
            <P>
              <Creativo />
            </P>
          }
        />
        <Route
          path="/reporting"
          element={
            <P>
              <Reporting />
            </P>
          }
        />
        <Route
          path="/social-listening"
          element={
            <P>
              <SocialListening />
            </P>
          }
        />
        <Route
          path="/agentes-ia"
          element={
            <P>
              <AgentesIA />
            </P>
          }
        />
        <Route
          path="/organigrama"
          element={
            <P>
              <Organigrama />
            </P>
          }
        />
        <Route
          path="/marca/perfil"
          element={
            <P>
              <PerfilMarca />
            </P>
          }
        />
        <Route
          path="/automatizaciones"
          element={
            <P>
              <Automatizaciones />
            </P>
          }
        />
        <Route
          path="/configuracion"
          element={
            <ProtectedRoute requireSuperadmin allowNoMarca>
              <ConfiguracionAPIs />
            </ProtectedRoute>
          }
        />
        <Route
          path="*"
          element={
            <Navigate
              to={user ? (marcaActiva ? "/dashboard" : "/crear-marca") : "/login"}
              replace
            />
          }
        />
      </Routes>
    </Suspense>
  );
}
