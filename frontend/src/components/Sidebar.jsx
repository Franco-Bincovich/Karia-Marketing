import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Tooltip from "./ui/Tooltip";

const SIDEBAR_FULL = 240;
const SIDEBAR_COL  =  64;

const sections = [
  { title: "PRINCIPAL", items: [
    { path: "/dashboard",         label: "Dashboard",        icon: "⊞" },
    { path: "/prospeccion",       label: "Prospección",      icon: "◎", badge: true },
    { path: "/estrategia",        label: "Estrategia",       icon: "◈" },
    { path: "/agentes-ia",        label: "Agentes IA",       icon: "✦" },
  ]},
  { title: "CONTENIDO", items: [
    { path: "/contenido",         label: "Generar Contenido",icon: "✎" },
    { path: "/creativo",          label: "Creativo IA",      icon: "◇" },
    { path: "/calendario",        label: "Calendario",       icon: "▦" },
    { path: "/social-media",      label: "Redes Sociales",   icon: "◎" },
  ]},
  { title: "PUBLICIDAD & SEO", items: [
    { path: "/ads",               label: "Ads",              icon: "◉" },
    { path: "/seo",               label: "SEO",              icon: "⊕" },
  ]},
  { title: "ANÁLISIS", items: [
    { path: "/analytics",         label: "Analytics",        icon: "◬" },
    { path: "/comunidad",         label: "Comunidad",        icon: "◎", badge: true },
    { path: "/social-listening",  label: "Social Listening", icon: "◌" },
    { path: "/reporting",         label: "Reporting",        icon: "▤" },
  ]},
  { title: "SISTEMA", items: [
    { path: "/onboarding",        label: "Configuración",    icon: "⊙" },
    { path: "/marca/perfil",      label: "Perfil de Marca",  icon: "◫" },
    { path: "/automatizaciones",  label: "Automatizaciones", icon: "↻" },
  ]},
  { title: "ADMIN", superadminOnly: true, items: [
    { path: "/clientes",          label: "Clientes",         icon: "▦" },
  ]},
];

export default function Sidebar({ collapsed, onToggle, onNavigate, isMobile }) {
  const { user, marcas, marcaActiva, setMarcaActiva, completitud, logout } = useAuth();
  const { pathname } = useLocation();
  const navigate = useNavigate();

  const initials = user?.nombre?.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase() || "?";
  const plan = user?.plan || "Basic";

  const defaultOpen = {};
  sections.forEach(sec => { defaultOpen[sec.title] = true; });
  const [openSections, setOpenSections] = useState(defaultOpen);

  const w = collapsed ? SIDEBAR_COL : SIDEBAR_FULL;

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

  const visibleSections = sections.filter(
    sec => !sec.superadminOnly || user?.rol === "superadmin"
  );

  return (
    <aside style={{
      width: w,
      minWidth: w,
      height: "100vh",
      background: "var(--sidebar-bg)",
      display: "flex",
      flexDirection: "column",
      position: "fixed",
      top: 0,
      left: 0,
      zIndex: 100,
      transition: "width var(--t), min-width var(--t)",
      overflowX: "hidden",
    }}>
      {/* ── Logo ── */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: collapsed ? "center" : "space-between",
        padding: collapsed ? "20px 0" : "20px 16px",
        minHeight: 68,
        borderBottom: "1px solid var(--sidebar-border)",
      }}>
        {collapsed ? (
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: "linear-gradient(135deg, #FF6B2B, #F5A623)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 16, fontWeight: 900, color: "#fff",
          }}>N</div>
        ) : (
          <div>
            <div style={{ fontSize: 20, fontWeight: 900, color: "#fff", letterSpacing: "-0.5px", lineHeight: 1.2 }}>
              NEXO
              <span style={{ fontSize: 9, fontWeight: 700, color: "var(--primary)", marginLeft: 4, letterSpacing: "0.08em", opacity: 0.9 }}>MKTG</span>
            </div>
            <div style={{ fontSize: 11, color: "var(--sidebar-text)", marginTop: 1 }}>Marketing AI Platform</div>
          </div>
        )}
        {!isMobile && (
          <button
            onClick={onToggle}
            style={{
              background: "rgba(255,255,255,0.06)",
              border: "none",
              borderRadius: 8,
              padding: "7px 8px",
              cursor: "pointer",
              color: "var(--sidebar-text)",
              fontSize: 13,
              lineHeight: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "background var(--t-fast)",
              flexShrink: 0,
              marginLeft: collapsed ? 0 : 8,
            }}
            onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.12)"}
            onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.06)"}
            aria-label={collapsed ? "Expandir sidebar" : "Colapsar sidebar"}
          >
            {collapsed ? "›" : "‹"}
          </button>
        )}
      </div>

      {/* ── Marca activa ── */}
      {!collapsed && marcas.length > 0 && (
        <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--sidebar-border)" }}>
          {marcas.length === 1 ? (
            <div style={{ fontSize: 13, color: "#fff", fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {marcaActiva?.nombre || "Sin marca"}
            </div>
          ) : (
            <select
              style={{
                width: "100%",
                padding: "7px 8px",
                borderRadius: 8,
                border: "1px solid rgba(255,255,255,0.10)",
                background: "rgba(255,255,255,0.06)",
                color: "#fff",
                fontSize: 12,
                outline: "none",
                cursor: "pointer",
              }}
              value={marcaActiva?.id || ""}
              onChange={handleMarcaChange}
            >
              {marcas.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
            </select>
          )}

          {/* Completitud */}
          <div style={{ marginTop: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
              <span style={{ fontSize: 10, color: "var(--sidebar-text)", fontWeight: 600 }}>PERFIL DE MARCA</span>
              <span style={{ fontSize: 10, color: completitud >= 100 ? "#34D399" : "var(--primary)", fontWeight: 700 }}>{completitud}%</span>
            </div>
            <div style={{ height: 4, background: "rgba(255,255,255,0.08)", borderRadius: 999, overflow: "hidden" }}>
              <div style={{
                height: "100%",
                width: `${completitud}%`,
                background: completitud >= 100 ? "#10B981" : "linear-gradient(90deg, #FF6B2B, #F5A623)",
                borderRadius: 999,
                transition: "width var(--t-slow)",
              }} />
            </div>
          </div>
        </div>
      )}

      {/* ── Navegación ── */}
      <nav style={{ flex: 1, overflowY: "auto", overflowX: "hidden", padding: collapsed ? "8px 4px" : "8px 8px", minHeight: 0 }}>
        {visibleSections.map(sec => (
          <div key={sec.title}>
            {/* Section header */}
            <div
              onClick={() => toggleSection(sec.title)}
              style={{
                fontSize: 9,
                fontWeight: 700,
                color: "var(--sidebar-section)",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                padding: collapsed ? "14px 0 6px" : "14px 8px 6px",
                cursor: collapsed ? "default" : "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                userSelect: "none",
              }}
            >
              {!collapsed && <span>{sec.title}</span>}
              {!collapsed && (
                <span style={{
                  fontSize: 9,
                  transition: "transform var(--t-fast)",
                  transform: openSections[sec.title] ? "rotate(0)" : "rotate(-90deg)",
                  color: "var(--sidebar-text)",
                }}>▾</span>
              )}
            </div>

            {/* Items */}
            {(collapsed || openSections[sec.title]) && sec.items.map(item => {
              const active = pathname === item.path || (item.path !== "/dashboard" && pathname.startsWith(item.path));
              const content = (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={handleLinkClick}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: collapsed ? 0 : 10,
                    justifyContent: collapsed ? "center" : "flex-start",
                    padding: collapsed ? "10px 0" : "9px 10px",
                    borderRadius: 8,
                    fontSize: 13,
                    fontWeight: active ? 600 : 400,
                    color: active ? "var(--sidebar-text-active)" : "var(--sidebar-text)",
                    background: active ? "var(--sidebar-active)" : "transparent",
                    cursor: "pointer",
                    transition: "all var(--t-fast)",
                    marginBottom: 2,
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textDecoration: "none",
                    position: "relative",
                  }}
                  onMouseEnter={e => { if (!active) e.currentTarget.style.background = "var(--sidebar-hover)"; e.currentTarget.style.color = "#fff"; }}
                  onMouseLeave={e => { if (!active) { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "var(--sidebar-text)"; }}}
                >
                  {active && !collapsed && (
                    <span style={{
                      position: "absolute",
                      left: 0,
                      top: "50%",
                      transform: "translateY(-50%)",
                      width: 3,
                      height: 16,
                      background: "var(--primary)",
                      borderRadius: "0 2px 2px 0",
                    }} />
                  )}
                  <span style={{ fontSize: collapsed ? 16 : 13, flexShrink: 0, lineHeight: 1 }}>{item.icon}</span>
                  {!collapsed && <span style={{ flex: 1 }}>{item.label}</span>}
                  {!collapsed && item.badge && (
                    <span style={{
                      background: "#EF4444",
                      color: "#fff",
                      fontSize: 9,
                      fontWeight: 700,
                      padding: "2px 5px",
                      borderRadius: 9,
                      minWidth: 16,
                      textAlign: "center",
                    }}>3</span>
                  )}
                </Link>
              );

              return collapsed ? (
                <Tooltip key={item.path} text={item.label} delay={300}>
                  {content}
                </Tooltip>
              ) : content;
            })}
          </div>
        ))}
      </nav>

      {/* ── User box ── */}
      <div style={{
        borderTop: "1px solid var(--sidebar-border)",
        padding: collapsed ? "12px 4px" : "12px 12px",
      }}>
        {collapsed ? (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
            <Tooltip text={user?.nombre || "Usuario"} delay={200}>
              <div style={{
                width: 36, height: 36, borderRadius: "50%",
                background: "linear-gradient(135deg, #FF6B2B, #F5A623)",
                display: "flex", alignItems: "center", justifyContent: "center",
                color: "#fff", fontSize: 12, fontWeight: 700, cursor: "default",
              }}>{initials}</div>
            </Tooltip>
            <Tooltip text="Cerrar sesión" delay={200}>
              <button
                onClick={handleLogout}
                style={{
                  background: "rgba(255,255,255,0.06)", border: "none",
                  borderRadius: 8, padding: "6px 8px", color: "rgba(255,255,255,0.4)",
                  fontSize: 11, cursor: "pointer",
                }}
              >↪</button>
            </Tooltip>
          </div>
        ) : (
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 36, height: 36, borderRadius: "50%", flexShrink: 0,
              background: "linear-gradient(135deg, #FF6B2B, #F5A623)",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "#fff", fontSize: 12, fontWeight: 700,
            }}>{initials}</div>
            <div style={{ minWidth: 0, flex: 1 }}>
              <div style={{ fontSize: 13, color: "#fff", fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {user?.nombre || "Usuario"}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 5, marginTop: 2 }}>
                <span style={{
                  fontSize: 9, fontWeight: 700,
                  color: plan === "Premium" ? "#A78BFA" : "rgba(255,255,255,0.35)",
                  background: plan === "Premium" ? "rgba(139,92,246,0.2)" : "rgba(255,255,255,0.08)",
                  padding: "1px 6px", borderRadius: 4, letterSpacing: "0.06em",
                }}>
                  {plan?.toUpperCase()}
                </span>
              </div>
            </div>
            <button
              onClick={handleLogout}
              style={{
                background: "rgba(255,255,255,0.06)",
                border: "none",
                borderRadius: 8,
                padding: "7px 8px",
                color: "rgba(255,255,255,0.4)",
                fontSize: 11,
                cursor: "pointer",
                flexShrink: 0,
                transition: "background var(--t-fast)",
              }}
              onMouseEnter={e => e.currentTarget.style.background = "rgba(239,68,68,0.2)"}
              onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.06)"}
              title="Cerrar sesión"
            >↪</button>
          </div>
        )}
      </div>
    </aside>
  );
}
