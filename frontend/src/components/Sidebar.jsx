import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const SIDEBAR_FULL = 224;
const SIDEBAR_COLLAPSED = 64;

const sections = [
  { title: "PRINCIPAL", items: [
    { path: "/dashboard", label: "Dashboard", icon: "📊" },
    { path: "/prospeccion", label: "Prospección", icon: "🎯", badge: true },
    { path: "/estrategia", label: "Estrategia", icon: "🧠" },
    { path: "/agentes-ia", label: "Agentes IA", icon: "🤖" },
  ]},
  { title: "CONTENIDO", items: [
    { path: "/contenido", label: "Generar Contenido", icon: "✍️" },
    { path: "/creativo", label: "Creativo", icon: "🎨" },
    { path: "/calendario", label: "Calendario", icon: "📅" },
    { path: "/social-media", label: "Redes Sociales", icon: "📱" },
  ]},
  { title: "PUBLICIDAD & SEO", items: [
    { path: "/ads", label: "Ads", icon: "📣" },
    { path: "/seo", label: "SEO", icon: "🔍" },
  ]},
  { title: "ANÁLISIS", items: [
    { path: "/analytics", label: "Analytics", icon: "📈" },
    { path: "/comunidad", label: "Comunidad", icon: "💬", badge: true },
    { path: "/social-listening", label: "Social Listening", icon: "👂" },
    { path: "/reporting", label: "Reporting", icon: "📋" },
  ]},
  { title: "SISTEMA", items: [
    { path: "/onboarding", label: "Configuración", icon: "⚙️" },
    { path: "/marca/perfil", label: "Perfil de Marca", icon: "🏷️" },
  ]},
  { title: "ADMIN", superadminOnly: true, items: [
    { path: "/clientes", label: "Clientes", icon: "🏢" },
  ]},
];

export default function Sidebar({ collapsed, onToggle, onNavigate, isMobile }) {
  const { user, marcas, marcaActiva, setMarcaActiva, completitud, logout } = useAuth();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const initials = user?.nombre?.split(" ").map(n => n[0]).join("").slice(0, 2) || "?";

  const defaultOpen = {};
  sections.forEach(sec => { defaultOpen[sec.title] = true; });
  const [openSections, setOpenSections] = useState(defaultOpen);

  const w = collapsed ? SIDEBAR_COLLAPSED : SIDEBAR_FULL;

  function toggleSection(title) {
    if (collapsed) return;
    setOpenSections(prev => ({ ...prev, [title]: !prev[title] }));
  }

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  function handleMarcaChange(e) {
    const marca = marcas.find(m => m.id === e.target.value);
    if (marca) setMarcaActiva(marca);
  }

  function handleLinkClick() {
    if (onNavigate) onNavigate();
  }

  const visibleSections = sections.filter(sec => !sec.superadminOnly || user?.rol === "superadmin");

  return (
    <aside style={{
      width: w, height: "100vh", background: "#0F172A", display: "flex",
      flexDirection: "column", padding: collapsed ? "20px 6px" : "20px 12px",
      position: "fixed", top: 0, left: 0, zIndex: 100,
      transition: "width 200ms, padding 200ms",
      overflowX: "hidden",
    }}>
      {/* Logo + collapse toggle */}
      <div style={{
        display: "flex", alignItems: "center",
        justifyContent: collapsed ? "center" : "space-between",
        padding: collapsed ? "0" : "0 8px", marginBottom: 16, minHeight: 30,
      }}>
        {!collapsed && (
          <div>
            <div style={{ fontSize: 22, fontWeight: 800, color: "#F97316", lineHeight: 1.2 }}>KarIA</div>
            <div style={{ fontSize: 11, color: "#475569", marginTop: 2 }}>Marketing Platform</div>
          </div>
        )}
        {collapsed && (
          <div style={{ fontSize: 20, fontWeight: 800, color: "#F97316" }}>K</div>
        )}
        {!isMobile && (
          <button
            onClick={onToggle}
            style={{
              background: "none", border: "1px solid rgba(255,255,255,.12)", borderRadius: 6,
              padding: "4px 6px", cursor: "pointer", color: "#94A3B8", fontSize: 14,
              lineHeight: 1, display: "flex", alignItems: "center", justifyContent: "center",
              marginLeft: collapsed ? 0 : 0,
            }}
            aria-label={collapsed ? "Expandir sidebar" : "Colapsar sidebar"}
          >
            {collapsed ? "▸" : "◂"}
          </button>
        )}
      </div>

      {/* Marca selector */}
      {!collapsed && marcas.length > 0 && (
        <div style={{ padding: "0 8px", marginBottom: 16 }}>
          {marcas.length === 1 ? (
            <div style={{ fontSize: 12, color: "#E2E8F0", padding: "4px 0", fontWeight: 500 }}>{marcaActiva?.nombre}</div>
          ) : (
            <select
              style={{
                width: "100%", padding: "7px 8px", borderRadius: 8,
                border: "1px solid rgba(255,255,255,.1)",
                background: "rgba(255,255,255,.05)", color: "#E2E8F0", fontSize: 12, outline: "none",
              }}
              value={marcaActiva?.id || ""}
              onChange={handleMarcaChange}
            >
              {marcas.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
            </select>
          )}
        </div>
      )}

      {/* Progress bar */}
      {!collapsed && (
        <div style={{ padding: "8px 8px 0", marginBottom: 12 }}>
          <div style={{ fontSize: 10, color: "#475569", marginBottom: 4, fontWeight: 600 }}>Perfil de marca</div>
          <div style={{ height: 6, background: "rgba(255,255,255,.08)", borderRadius: 3, overflow: "hidden" }}>
            <div style={{
              height: "100%", width: `${completitud}%`,
              background: completitud >= 80 ? "#10B981" : "#F97316",
              borderRadius: 3, transition: "width 300ms",
            }} />
          </div>
          <div style={{ fontSize: 10, color: "#94A3B8", marginTop: 3, textAlign: "right" }}>{completitud}%</div>
        </div>
      )}

      {/* Navigation with scroll */}
      <nav style={{ flex: 1, overflowY: "auto", overflowX: "hidden", minHeight: 0 }}>
        {visibleSections.map((sec) => (
          <div key={sec.title}>
            {/* Section header — clickable to toggle */}
            <div
              onClick={() => toggleSection(sec.title)}
              style={{
                fontSize: 10, fontWeight: 700, color: "#334155", textTransform: "uppercase",
                letterSpacing: "0.05em",
                padding: collapsed ? "16px 4px 6px" : "16px 8px 6px",
                cursor: collapsed ? "default" : "pointer",
                display: "flex", alignItems: "center", justifyContent: "space-between",
                userSelect: "none",
              }}
            >
              {!collapsed && <span>{sec.title}</span>}
              {!collapsed && (
                <span style={{
                  fontSize: 9, transition: "transform 200ms",
                  transform: openSections[sec.title] ? "rotate(0deg)" : "rotate(-90deg)",
                }}>
                  ▾
                </span>
              )}
            </div>

            {/* Section items */}
            {(collapsed || openSections[sec.title]) && sec.items.map((item) => {
              const active = pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={handleLinkClick}
                  title={collapsed ? item.label : undefined}
                  style={{
                    display: "flex", alignItems: "center",
                    gap: collapsed ? 0 : 10,
                    justifyContent: collapsed ? "center" : "flex-start",
                    padding: collapsed ? "9px 0" : "9px 10px",
                    borderRadius: 8, fontSize: 13,
                    color: active ? "#F97316" : "#94A3B8",
                    background: active ? "rgba(249,115,22,.18)" : "transparent",
                    fontWeight: active ? 600 : 400,
                    cursor: "pointer", transition: "all 150ms", marginBottom: 2,
                    whiteSpace: "nowrap", overflow: "hidden",
                  }}
                >
                  <span style={{ fontSize: collapsed ? 18 : 13, flexShrink: 0 }}>{item.icon}</span>
                  {!collapsed && <span>{item.label}</span>}
                  {!collapsed && item.badge && (
                    <span style={{
                      background: "#EF4444", color: "#fff", fontSize: 10, fontWeight: 700,
                      padding: "1px 6px", borderRadius: 9, marginLeft: "auto",
                    }}>3</span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* User box */}
      <div style={{
        padding: collapsed ? "12px 4px" : "12px 8px",
        borderTop: "1px solid rgba(255,255,255,.08)",
        display: "flex", alignItems: "center",
        flexDirection: collapsed ? "column" : "row",
        gap: collapsed ? 8 : 10,
      }}>
        <div style={{
          width: 34, height: 34, borderRadius: "50%", display: "flex", alignItems: "center",
          justifyContent: "center", background: "linear-gradient(135deg,#F97316,#FB923C)",
          color: "#fff", fontSize: 13, fontWeight: 700, flexShrink: 0,
        }}>{initials}</div>
        {!collapsed && (
          <>
            <div style={{ minWidth: 0, flex: 1 }}>
              <div style={{ fontSize: 13, color: "#E2E8F0", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{user?.nombre || "Usuario"}</div>
              <div style={{ fontSize: 11, color: "#64748B" }}>{user?.rol || "—"}</div>
            </div>
            <button
              style={{
                marginLeft: "auto", background: "none", border: "1px solid rgba(255,255,255,.12)",
                borderRadius: 6, padding: "6px 10px", color: "#94A3B8", fontSize: 11, fontWeight: 500,
                cursor: "pointer", transition: "all 150ms", flexShrink: 0,
              }}
              onClick={handleLogout}
            >Salir</button>
          </>
        )}
        {collapsed && (
          <button
            onClick={handleLogout}
            title="Salir"
            style={{
              background: "none", border: "1px solid rgba(255,255,255,.12)",
              borderRadius: 6, padding: "4px 8px", color: "#94A3B8", fontSize: 11,
              cursor: "pointer", lineHeight: 1,
            }}
          >✕</button>
        )}
      </div>
    </aside>
  );
}
