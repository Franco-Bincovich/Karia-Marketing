import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

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
  ]},
];

const s = {
  sidebar: {
    width: 224, minHeight: "100vh", background: "#0F172A", display: "flex",
    flexDirection: "column", padding: "20px 12px", position: "fixed", top: 0, left: 0, zIndex: 100,
  },
  logoBox: { padding: "0 8px", marginBottom: 16 },
  logo: { fontSize: 22, fontWeight: 800, color: "#F97316", lineHeight: 1.2 },
  sub: { fontSize: 11, color: "#475569", marginTop: 2 },
  marcaBox: { padding: "0 8px", marginBottom: 16 },
  marcaSelect: {
    width: "100%", padding: "7px 8px", borderRadius: 8, border: "1px solid rgba(255,255,255,.1)",
    background: "rgba(255,255,255,.05)", color: "#E2E8F0", fontSize: 12, outline: "none",
  },
  profileBar: {
    padding: "8px 8px 0", marginBottom: 12,
  },
  profileLabel: { fontSize: 10, color: "#475569", marginBottom: 4, fontWeight: 600 },
  barTrack: { height: 6, background: "rgba(255,255,255,.08)", borderRadius: 3, overflow: "hidden" },
  barFill: (pct) => ({
    height: "100%", width: `${pct}%`, background: pct >= 80 ? "#10B981" : "#F97316",
    borderRadius: 3, transition: "width 300ms",
  }),
  barPct: { fontSize: 10, color: "#94A3B8", marginTop: 3, textAlign: "right" },
  section: { fontSize: 10, fontWeight: 700, color: "#334155", textTransform: "uppercase",
    letterSpacing: "0.05em", padding: "16px 8px 6px" },
  link: (active) => ({
    display: "flex", alignItems: "center", gap: 10, padding: "9px 10px",
    borderRadius: 8, fontSize: 13, color: active ? "#F97316" : "#94A3B8",
    background: active ? "rgba(249,115,22,.18)" : "transparent",
    fontWeight: active ? 600 : 400, cursor: "pointer", transition: "all 150ms", marginBottom: 2,
  }),
  badge: {
    background: "#EF4444", color: "#fff", fontSize: 10, fontWeight: 700,
    padding: "1px 6px", borderRadius: 9, marginLeft: "auto",
  },
  userBox: {
    marginTop: "auto", padding: "12px 8px", borderTop: "1px solid rgba(255,255,255,.08)",
    display: "flex", alignItems: "center", gap: 10,
  },
  avatar: {
    width: 34, height: 34, borderRadius: "50%", display: "flex", alignItems: "center",
    justifyContent: "center", background: "linear-gradient(135deg,#F97316,#FB923C)",
    color: "#fff", fontSize: 13, fontWeight: 700,
  },
  userName: { fontSize: 13, color: "#E2E8F0", fontWeight: 500 },
  userRole: { fontSize: 11, color: "#64748B" },
};

export default function Sidebar() {
  const { user, marcas, marcaActiva, setMarcaActiva, completitud } = useAuth();
  const { pathname } = useLocation();
  const initials = user?.nombre?.split(" ").map(n => n[0]).join("").slice(0, 2) || "?";

  function handleMarcaChange(e) {
    const marca = marcas.find(m => m.id === e.target.value);
    if (marca) setMarcaActiva(marca);
  }

  return (
    <aside style={s.sidebar}>
      <div style={s.logoBox}>
        <div style={s.logo}>KarIA</div>
        <div style={s.sub}>Marketing Platform</div>
      </div>
      {marcas.length > 0 && (
        <div style={s.marcaBox}>
          {marcas.length === 1 ? (
            <div style={{ fontSize: 12, color: "#E2E8F0", padding: "4px 0", fontWeight: 500 }}>{marcaActiva?.nombre}</div>
          ) : (
            <select style={s.marcaSelect} value={marcaActiva?.id || ""} onChange={handleMarcaChange}>
              {marcas.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
            </select>
          )}
        </div>
      )}
      <div style={s.profileBar}>
        <div style={s.profileLabel}>Perfil de marca</div>
        <div style={s.barTrack}><div style={s.barFill(completitud)} /></div>
        <div style={s.barPct}>{completitud}%</div>
      </div>
      <nav style={{ flex: 1, overflowY: "auto" }}>
        {sections.map((sec) => (
          <div key={sec.title}>
            <div style={s.section}>{sec.title}</div>
            {sec.items.map((item) => (
              <Link key={item.path} to={item.path} style={s.link(pathname === item.path)}>
                <span>{item.icon}</span>
                <span>{item.label}</span>
                {item.badge && <span style={s.badge}>3</span>}
              </Link>
            ))}
          </div>
        ))}
      </nav>
      <div style={s.userBox}>
        <div style={s.avatar}>{initials}</div>
        <div>
          <div style={s.userName}>{user?.nombre || "Usuario"}</div>
          <div style={s.userRole}>{user?.rol || "—"}</div>
        </div>
      </div>
    </aside>
  );
}
