/**
 * Dashboard principal post-login con navegación lateral.
 */

import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { path: "/dashboard", label: "Dashboard", roles: ["superadmin", "admin", "subusuario"] },
  { path: "/clientes", label: "Clientes", roles: ["superadmin"] },
  { path: "/marcas", label: "Marcas", roles: ["superadmin", "admin"] },
  { path: "/usuarios", label: "Usuarios", roles: ["superadmin", "admin"] },
  { path: "/feature-flags", label: "Feature Flags", roles: ["superadmin", "admin"] },
];

const s = {
  layout: { display: "flex", minHeight: "100vh", fontFamily: "var(--font-sans)" },
  sidebar: {
    width: "var(--sidebar-width)", background: "var(--sidebar-bg)", color: "var(--sidebar-text)",
    padding: "var(--spacing-6)", display: "flex", flexDirection: "column",
  },
  logo: { fontSize: "var(--font-size-lg)", fontWeight: 700, color: "#fff", marginBottom: "var(--spacing-8)" },
  navLink: (active) => ({
    display: "block", padding: "10px var(--spacing-3)", borderRadius: "var(--radius-md)",
    color: active ? "#fff" : "var(--sidebar-text)", textDecoration: "none",
    background: active ? "var(--sidebar-active)" : "transparent",
    marginBottom: "var(--spacing-1)", fontSize: "var(--font-size-sm)",
  }),
  main: { flex: 1, padding: "var(--spacing-8)", background: "var(--color-bg)" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--spacing-8)" },
  title: { fontSize: "var(--font-size-2xl)", fontWeight: 700, color: "var(--color-text)" },
  badge: {
    background: "var(--color-primary-light)", color: "var(--color-primary)",
    padding: "4px 12px", borderRadius: "var(--radius-full)", fontSize: "var(--font-size-xs)", fontWeight: 600,
  },
  logoutBtn: {
    background: "none", border: "1px solid rgba(255,255,255,0.2)", color: "var(--sidebar-text)",
    padding: "8px 16px", borderRadius: "var(--radius-md)", cursor: "pointer",
    fontSize: "var(--font-size-sm)", marginTop: "auto",
  },
};

export default function Dashboard() {
  const { user, logout, isSuperadmin } = useAuth();
  const location = useLocation();

  const visibleNav = navItems.filter((item) => item.roles.includes(user?.rol));

  return (
    <div style={s.layout}>
      <aside style={s.sidebar}>
        <div style={s.logo}>KarIA</div>
        <nav>
          {visibleNav.map((item) => (
            <Link key={item.path} to={item.path} style={s.navLink(location.pathname === item.path)}>
              {item.label}
            </Link>
          ))}
        </nav>
        <button style={s.logoutBtn} onClick={logout}>Cerrar sesión</button>
      </aside>
      <main style={s.main}>
        <div style={s.header}>
          <h1 style={s.title}>Bienvenido, {user?.nombre}</h1>
          <span style={s.badge}>{user?.rol}</span>
        </div>
        <p style={{ color: "var(--color-text-muted)" }}>
          Seleccioná una sección del menú para comenzar.
          {isSuperadmin && " Tenés acceso completo como superadmin."}
        </p>
      </main>
    </div>
  );
}
