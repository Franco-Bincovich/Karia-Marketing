import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../hooks/useTheme";

export default function Header({ title, onMenuClick, showMenu }) {
  const { user, modo, setModo, logout } = useAuth();
  const { isDark, toggle } = useTheme();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropRef = useRef(null);

  const initials =
    user?.nombre
      ?.split(" ")
      .map((n) => n[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "?";

  // Cerrar dropdown al hacer click afuera
  useEffect(() => {
    function handle(e) {
      if (dropRef.current && !dropRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handle);
    return () => document.removeEventListener("mousedown", handle);
  }, []);

  async function handleLogout() {
    setDropdownOpen(false);
    await logout();
    navigate("/login");
  }

  return (
    <header
      style={{
        height: "var(--header-h)",
        background: "var(--header-bg)",
        borderBottom: "1px solid var(--header-border)",
        boxShadow: "var(--header-shadow)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 24px",
        position: "sticky",
        top: 0,
        zIndex: 50,
        transition: "background var(--t-slow), border-color var(--t-slow)",
        gap: 12,
      }}
    >
      {/* ── Left ── */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, minWidth: 0 }}>
        {showMenu && (
          <button
            onClick={onMenuClick}
            style={{
              background: "var(--surface-2)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius)",
              padding: "7px 9px",
              cursor: "pointer",
              color: "var(--text-secondary)",
              fontSize: 18,
              lineHeight: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
            aria-label="Abrir menú"
          >
            ≡
          </button>
        )}
        <h1
          style={{
            fontSize: "var(--text-lg)",
            fontWeight: 700,
            color: "var(--text)",
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {title}
        </h1>
      </div>

      {/* ── Right ── */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexShrink: 0 }}>
        {/* Copilot / Autopilot toggle */}
        <div
          style={{
            display: "flex",
            borderRadius: "var(--radius)",
            overflow: "hidden",
            border: "1px solid var(--border)",
            background: "var(--surface-2)",
          }}
        >
          {["copilot", "autopilot"].map((m) => {
            const active = modo === m;
            return (
              <button
                key={m}
                onClick={() => setModo(m)}
                style={{
                  padding: "5px 12px",
                  fontSize: 11,
                  fontWeight: 700,
                  border: "none",
                  cursor: "pointer",
                  background: active
                    ? m === "autopilot"
                      ? "var(--success-bg)"
                      : "var(--purple-bg)"
                    : "transparent",
                  color: active
                    ? m === "autopilot"
                      ? "var(--success-text)"
                      : "var(--purple-text)"
                    : "var(--text-muted)",
                  transition: "all var(--t-fast)",
                  textTransform: "capitalize",
                  letterSpacing: "0.02em",
                }}
              >
                {m}
              </button>
            );
          })}
        </div>

        {/* Dark/Light toggle */}
        <button
          onClick={toggle}
          title={isDark ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
          style={{
            width: 34,
            height: 34,
            borderRadius: "var(--radius)",
            border: "1px solid var(--border)",
            background: "var(--surface-2)",
            color: "var(--text-secondary)",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 15,
            transition: "background var(--t-fast)",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--surface-3)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "var(--surface-2)")}
        >
          {isDark ? "☀" : "☾"}
        </button>

        {/* Avatar + dropdown */}
        <div ref={dropRef} style={{ position: "relative" }}>
          <button
            onClick={() => setDropdownOpen((v) => !v)}
            style={{
              width: 34,
              height: 34,
              borderRadius: "50%",
              background: "linear-gradient(135deg, #FF6B2B, #F5A623)",
              color: "#fff",
              fontSize: 12,
              fontWeight: 700,
              border: "none",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              outline: dropdownOpen ? "2px solid var(--primary)" : "none",
              outlineOffset: 2,
            }}
            aria-label="Menú de usuario"
          >
            {initials}
          </button>

          {dropdownOpen && (
            <div
              style={{
                position: "absolute",
                top: "calc(100% + 8px)",
                right: 0,
                background: "var(--surface)",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-lg)",
                boxShadow: "var(--shadow-xl)",
                minWidth: 200,
                padding: 6,
                zIndex: 100,
                animation: "slideUp 150ms ease",
              }}
            >
              {/* User info */}
              <div
                style={{
                  padding: "10px 12px 8px",
                  borderBottom: "1px solid var(--border-subtle)",
                  marginBottom: 4,
                }}
              >
                <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text)" }}>
                  {user?.nombre || "Usuario"}
                </div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                  {user?.email || user?.rol}
                </div>
              </div>

              {[
                {
                  label: "Ver perfil de marca",
                  icon: "◫",
                  action: () => {
                    navigate("/marca/perfil");
                    setDropdownOpen(false);
                  },
                },
                {
                  label: "Configuración",
                  icon: "⊙",
                  action: () => {
                    navigate("/onboarding");
                    setDropdownOpen(false);
                  },
                },
                {
                  label: "Cambiar marca",
                  icon: "↔",
                  action: () => {
                    navigate("/marcas");
                    setDropdownOpen(false);
                  },
                  show: user?.rol !== "admin_cliente",
                },
              ]
                .filter((i) => i.show !== false)
                .map((item) => (
                  <button
                    key={item.label}
                    onClick={item.action}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      width: "100%",
                      padding: "8px 12px",
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      fontSize: 13,
                      color: "var(--text-secondary)",
                      borderRadius: 6,
                      textAlign: "left",
                      transition: "background var(--t-fast)",
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = "var(--surface-2)")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "none")}
                  >
                    <span style={{ fontSize: 14, opacity: 0.7 }}>{item.icon}</span>
                    {item.label}
                  </button>
                ))}

              <div
                style={{ borderTop: "1px solid var(--border-subtle)", marginTop: 4, paddingTop: 4 }}
              >
                <button
                  onClick={handleLogout}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    width: "100%",
                    padding: "8px 12px",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    fontSize: 13,
                    color: "var(--danger-text)",
                    borderRadius: 6,
                    textAlign: "left",
                    transition: "background var(--t-fast)",
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = "var(--danger-bg)")}
                  onMouseLeave={(e) => (e.currentTarget.style.background = "none")}
                >
                  <span>↪</span> Cerrar sesión
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
