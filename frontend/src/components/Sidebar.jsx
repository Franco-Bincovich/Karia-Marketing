import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Tooltip from "./ui/Tooltip";
import api from "../hooks/useApi";

const SIDEBAR_FULL = 240;
const SIDEBAR_COL = 64;

const sections = [
  {
    title: "PRINCIPAL",
    items: [
      { path: "/dashboard", label: "Dashboard", icon: "⊞" },
      { path: "/prospeccion", label: "Prospección", icon: "⊙", badge: true },
      { path: "/estrategia", label: "Estrategia", icon: "◈" },
      { path: "/agentes-ia", label: "Agentes IA", icon: "✦" },
      { path: "/organigrama", label: "Organigrama", icon: "⊟" },
    ],
  },
  {
    title: "CONTENIDO",
    items: [
      { path: "/contenido", label: "Generar Contenido", icon: "✎" },
      { path: "/creativo", label: "Creativo IA", icon: "✴" },
      { path: "/calendario", label: "Calendario", icon: "▦" },
      { path: "/social-media", label: "Redes Sociales", icon: "◉" },
    ],
  },
  {
    title: "PUBLICIDAD & SEO",
    items: [
      { path: "/ads", label: "Ads", icon: "⊕", v2: true },
      { path: "/seo", label: "SEO", icon: "◎", v2: true },
    ],
  },
  {
    title: "ANÁLISIS",
    items: [
      { path: "/analytics", label: "Analytics", icon: "◬" },
      { path: "/comunidad", label: "Comunidad", icon: "◑", badge: true },
      { path: "/social-listening", label: "Social Listening", icon: "⊛" },
      { path: "/reporting", label: "Reporting", icon: "▤" },
    ],
  },
  {
    title: "SISTEMA",
    items: [
      { path: "/onboarding", label: "Configuración", icon: "⚙" },
      { path: "/marca/perfil", label: "Perfil de Marca", icon: "◫" },
      { path: "/automatizaciones", label: "Automatizaciones", icon: "↻" },
    ],
  },
  {
    title: "ADMIN",
    superadminOnly: true,
    items: [
      { path: "/clientes", label: "Clientes", icon: "◧" },
      { path: "/configuracion", label: "Configuración APIs", icon: "⚙" },
    ],
  },
];

export default function Sidebar({ collapsed, onToggle, onNavigate, isMobile }) {
  const { user, marcas, marcaActiva, setMarcaActiva, completitud, logout } = useAuth();
  const { pathname } = useLocation();
  const navigate = useNavigate();

  const initials =
    user?.nombre
      ?.split(" ")
      .map((n) => n[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "?";
  const plan = user?.plan || "Basic";

  const defaultOpen = {};
  sections.forEach((sec) => {
    defaultOpen[sec.title] = true;
  });
  const [openSections, setOpenSections] = useState(defaultOpen);

  const w = collapsed ? SIDEBAR_COL : SIDEBAR_FULL;
  const [pendientesCount, setPendientesCount] = useState(0);

  useEffect(() => {
    if (marcaActiva) {
      api
        .get("/api/comunidad/mensajes/pendientes")
        .then((r) => setPendientesCount(r.data.count || 0))
        .catch(() => {});
    }
  }, [marcaActiva]);

  function toggleSection(title) {
    if (collapsed) return;
    setOpenSections((prev) => ({ ...prev, [title]: !prev[title] }));
  }

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  function handleMarcaChange(e) {
    const marca = marcas.find((m) => m.id === e.target.value);
    if (marca) setMarcaActiva(marca);
  }

  function handleLinkClick() {
    if (onNavigate) onNavigate();
  }

  const visibleSections = sections.filter(
    (sec) => !sec.superadminOnly || user?.rol === "superadmin"
  );

  return (
    <aside
      style={{
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
      }}
    >
      {/* ── Logo ── */}
      {collapsed ? (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 6,
            padding: "14px 0 10px",
            minHeight: 68,
            borderBottom: "1px solid var(--sidebar-border)",
          }}
        >
          <div
            style={{
              width: 38,
              height: 38,
              borderRadius: 10,
              background: "#FF6B00",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 20,
              fontWeight: 900,
              color: "#fff",
              flexShrink: 0,
            }}
          >
            N
          </div>
          {!isMobile && (
            <button
              onClick={onToggle}
              style={{
                background: "rgba(255,255,255,0.08)",
                border: "none",
                borderRadius: 6,
                width: 28,
                height: 18,
                cursor: "pointer",
                color: "var(--sidebar-text)",
                fontSize: 12,
                lineHeight: 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                transition: "background var(--t-fast)",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.16)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.08)")}
              aria-label="Expandir sidebar"
            >
              ›
            </button>
          )}
        </div>
      ) : (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 16px",
            minHeight: 68,
            borderBottom: "1px solid var(--sidebar-border)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 10,
                background: "#FF6B00",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 18,
                fontWeight: 900,
                color: "#fff",
                flexShrink: 0,
              }}
            >
              N
            </div>
            <div>
              <div
                style={{
                  fontSize: 18,
                  fontWeight: 900,
                  color: "#fff",
                  letterSpacing: "-0.5px",
                  lineHeight: 1.2,
                }}
              >
                NEXO
              </div>
              <div style={{ fontSize: 10, color: "var(--sidebar-text)", marginTop: 1 }}>
                AI Marketing
              </div>
            </div>
          </div>
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
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.12)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.06)")}
              aria-label="Colapsar sidebar"
            >
              ‹
            </button>
          )}
        </div>
      )}

      {/* ── Marca activa ── */}
      {!collapsed && marcas.length > 0 && (
        <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--sidebar-border)" }}>
          {marcas.length === 1 ? (
            <div
              style={{
                fontSize: 13,
                color: "#fff",
                fontWeight: 600,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
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
              {marcas.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.nombre}
                </option>
              ))}
            </select>
          )}
          <div style={{ marginTop: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
              <span style={{ fontSize: 10, color: "var(--sidebar-text)", fontWeight: 600 }}>
                PERFIL DE MARCA
              </span>
              <span
                style={{
                  fontSize: 10,
                  color: completitud >= 100 ? "#34D399" : "var(--primary)",
                  fontWeight: 700,
                }}
              >
                {completitud}%
              </span>
            </div>
            <div
              style={{
                height: 4,
                background: "rgba(255,255,255,0.08)",
                borderRadius: 999,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${completitud}%`,
                  background:
                    completitud >= 100 ? "#10B981" : "linear-gradient(90deg, #FF6B2B, #F5A623)",
                  borderRadius: 999,
                  transition: "width var(--t-slow)",
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* ── Navegación ── */}
      <nav
        style={{
          flex: 1,
          overflowY: "auto",
          overflowX: "hidden",
          padding: collapsed ? "6px 0" : "8px 8px",
          minHeight: 0,
        }}
      >
        {visibleSections.map((sec, secIdx) => (
          <div key={sec.title}>
            {collapsed ? (
              secIdx > 0 && (
                <div
                  style={{ height: 1, background: "rgba(255,255,255,0.07)", margin: "6px 12px" }}
                />
              )
            ) : (
              <div
                onClick={() => toggleSection(sec.title)}
                style={{
                  fontSize: 9,
                  fontWeight: 700,
                  color: "var(--sidebar-section)",
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                  padding: "14px 8px 6px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  userSelect: "none",
                }}
              >
                <span>{sec.title}</span>
                <span
                  style={{
                    fontSize: 9,
                    transition: "transform var(--t-fast)",
                    transform: openSections[sec.title] ? "rotate(0)" : "rotate(-90deg)",
                    color: "var(--sidebar-text)",
                  }}
                >
                  ▾
                </span>
              </div>
            )}

            {(collapsed || openSections[sec.title]) &&
              sec.items.map((item) => {
                const active =
                  pathname === item.path ||
                  (item.path !== "/dashboard" && pathname.startsWith(item.path));
                const isSA = user?.rol === "superadmin";
                const disabled = item.v2 && !isSA;

                if (collapsed) {
                  return (
                    <Tooltip
                      key={item.path}
                      text={item.v2 ? `${item.label} (V2)` : item.label}
                      delay={250}
                      placement="right"
                    >
                      <Link
                        to={disabled ? "#" : item.path}
                        onClick={disabled ? (e) => e.preventDefault() : handleLinkClick}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          width: 40,
                          height: 40,
                          margin: "2px auto",
                          borderRadius: 10,
                          fontSize: 20,
                          color: active ? "#fff" : "var(--sidebar-text)",
                          background: active ? "var(--sidebar-active)" : "transparent",
                          border: active
                            ? "1px solid rgba(255,107,43,0.35)"
                            : "1px solid transparent",
                          cursor: disabled ? "default" : "pointer",
                          transition: "all var(--t-fast)",
                          textDecoration: "none",
                          position: "relative",
                          flexShrink: 0,
                          opacity: disabled ? 0.4 : 1,
                          pointerEvents: disabled ? "none" : "auto",
                        }}
                        onMouseEnter={(e) => {
                          if (!active) {
                            e.currentTarget.style.background = "var(--sidebar-hover)";
                            e.currentTarget.style.color = "#fff";
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (!active) {
                            e.currentTarget.style.background = "transparent";
                            e.currentTarget.style.color = "var(--sidebar-text)";
                          }
                        }}
                        title=""
                      >
                        {item.icon}
                      </Link>
                    </Tooltip>
                  );
                }

                return (
                  <Link
                    key={item.path}
                    to={disabled ? "#" : item.path}
                    onClick={disabled ? (e) => e.preventDefault() : handleLinkClick}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      padding: "9px 10px",
                      borderRadius: 8,
                      fontSize: 13,
                      fontWeight: active ? 600 : 400,
                      color: active ? "var(--sidebar-text-active)" : "var(--sidebar-text)",
                      background: active ? "var(--sidebar-active)" : "transparent",
                      cursor: disabled ? "default" : "pointer",
                      transition: "all var(--t-fast)",
                      marginBottom: 2,
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textDecoration: "none",
                      position: "relative",
                      opacity: disabled ? 0.4 : 1,
                      pointerEvents: disabled ? "none" : "auto",
                    }}
                    onMouseEnter={(e) => {
                      if (!active) {
                        e.currentTarget.style.background = "var(--sidebar-hover)";
                        e.currentTarget.style.color = "#fff";
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!active) {
                        e.currentTarget.style.background = "transparent";
                        e.currentTarget.style.color = "var(--sidebar-text)";
                      }
                    }}
                  >
                    {active && (
                      <span
                        style={{
                          position: "absolute",
                          left: 0,
                          top: "50%",
                          transform: "translateY(-50%)",
                          width: 3,
                          height: 16,
                          background: "var(--primary)",
                          borderRadius: "0 2px 2px 0",
                        }}
                      />
                    )}
                    <span style={{ fontSize: 13, flexShrink: 0, lineHeight: 1 }}>{item.icon}</span>
                    <span style={{ flex: 1 }}>{item.label}</span>
                    {item.badge && pendientesCount > 0 && (
                      <span
                        style={{
                          background: "#EF4444",
                          color: "#fff",
                          fontSize: 9,
                          fontWeight: 700,
                          padding: "2px 5px",
                          borderRadius: 9,
                          minWidth: 16,
                          textAlign: "center",
                        }}
                      >
                        {pendientesCount}
                      </span>
                    )}
                  </Link>
                );
              })}
          </div>
        ))}
      </nav>

      {/* ── User box ── */}
      <div
        style={{
          borderTop: "1px solid var(--sidebar-border)",
          padding: collapsed ? "12px 0" : "12px 12px",
          display: "flex",
          alignItems: "center",
          justifyContent: collapsed ? "center" : "flex-start",
        }}
      >
        {collapsed ? (
          <Tooltip text={user?.nombre || "Usuario"} delay={200} placement="right">
            <div
              style={{
                width: 38,
                height: 38,
                borderRadius: "50%",
                background: "linear-gradient(135deg, #FF6B2B, #F5A623)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#fff",
                fontSize: 13,
                fontWeight: 700,
                cursor: "default",
                flexShrink: 0,
              }}
            >
              {initials}
            </div>
          </Tooltip>
        ) : (
          <div style={{ display: "flex", alignItems: "center", gap: 10, width: "100%" }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: "50%",
                flexShrink: 0,
                background: "linear-gradient(135deg, #FF6B2B, #F5A623)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#fff",
                fontSize: 12,
                fontWeight: 700,
              }}
            >
              {initials}
            </div>
            <div style={{ minWidth: 0, flex: 1 }}>
              <div
                style={{
                  fontSize: 13,
                  color: "#fff",
                  fontWeight: 600,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {user?.nombre || "Usuario"}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 5, marginTop: 2 }}>
                {user?.rol === "superadmin" ? (
                  <span
                    style={{
                      fontSize: 9,
                      fontWeight: 700,
                      color: "#F5A623",
                      background: "rgba(245,166,35,0.18)",
                      padding: "1px 6px",
                      borderRadius: 4,
                      letterSpacing: "0.06em",
                    }}
                  >
                    SUPERADMIN
                  </span>
                ) : (
                  <span
                    style={{
                      fontSize: 9,
                      fontWeight: 700,
                      color: plan === "Premium" ? "#A78BFA" : "rgba(255,255,255,0.60)",
                      background:
                        plan === "Premium" ? "rgba(139,92,246,0.2)" : "rgba(255,255,255,0.08)",
                      padding: "1px 6px",
                      borderRadius: 4,
                      letterSpacing: "0.06em",
                    }}
                  >
                    {plan?.toUpperCase()}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={handleLogout}
              style={{
                background: "rgba(255,255,255,0.06)",
                border: "none",
                borderRadius: 8,
                padding: "7px 8px",
                color: "rgba(255,255,255,0.65)",
                fontSize: 11,
                cursor: "pointer",
                flexShrink: 0,
                transition: "background var(--t-fast)",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(239,68,68,0.2)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.06)")}
              title="Cerrar sesión"
            >
              ↪
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
