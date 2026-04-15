import { useAuth } from "../context/AuthContext";

const s = {
  header: {
    height: 58, background: "#fff", borderBottom: "1px solid #E2E8F0",
    display: "flex", alignItems: "center", justifyContent: "space-between",
    padding: "0 28px", position: "sticky", top: 0, zIndex: 50,
  },
  left: { display: "flex", alignItems: "center", gap: 12 },
  menuBtn: {
    background: "none", border: "1px solid #E2E8F0", borderRadius: 8,
    padding: "6px 8px", cursor: "pointer", display: "flex", alignItems: "center",
    justifyContent: "center", color: "#475569", fontSize: 18, lineHeight: 1,
  },
  title: { fontSize: 18, fontWeight: 700, color: "#0F172A" },
  right: { display: "flex", alignItems: "center", gap: 14 },
  toggle: {
    display: "flex", borderRadius: 8, overflow: "hidden", border: "1px solid #E2E8F0",
  },
  toggleBtn: (active, mode) => ({
    padding: "6px 14px", fontSize: 12, fontWeight: 600, border: "none", cursor: "pointer",
    background: active
      ? (mode === "autopilot" ? "#DCFCE7" : "#EDE9FE")
      : "#fff",
    color: active
      ? (mode === "autopilot" ? "#15803D" : "#6D28D9")
      : "#94A3B8",
    transition: "all 150ms",
  }),
  avatar: {
    width: 32, height: 32, borderRadius: "50%", display: "flex", alignItems: "center",
    justifyContent: "center", background: "linear-gradient(135deg,#F97316,#FB923C)",
    color: "#fff", fontSize: 12, fontWeight: 700,
  },
};

export default function Header({ title, onMenuClick, showMenu }) {
  const { user, modo, setModo } = useAuth();
  const initials = user?.nombre?.split(" ").map(n => n[0]).join("").slice(0, 2) || "?";

  return (
    <header style={s.header}>
      <div style={s.left}>
        {showMenu && (
          <button style={s.menuBtn} onClick={onMenuClick} aria-label="Menu">
            &#9776;
          </button>
        )}
        <h1 style={s.title}>{title}</h1>
      </div>
      <div style={s.right}>
        <div style={s.toggle}>
          <button
            style={s.toggleBtn(modo === "copilot", "copilot")}
            onClick={() => setModo("copilot")}
          >Copilot</button>
          <button
            style={s.toggleBtn(modo === "autopilot", "autopilot")}
            onClick={() => setModo("autopilot")}
          >Autopilot</button>
        </div>
        <div style={s.avatar}>{initials}</div>
      </div>
    </header>
  );
}
