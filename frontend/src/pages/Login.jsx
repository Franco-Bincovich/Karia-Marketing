import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const s = {
  container: {
    minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
    background: "#F1F5F9", fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  card: {
    background: "#fff", borderRadius: 14, border: "1px solid #E2E8F0",
    padding: 32, width: "100%", maxWidth: 400, boxShadow: "0 4px 12px rgba(0,0,0,.08)",
  },
  logo: { fontSize: 22, fontWeight: 800, color: "#F97316", marginBottom: 4 },
  sub: { fontSize: 13, color: "#475569", marginBottom: 28 },
  label: { display: "block", fontSize: 12, color: "#94A3B8", marginBottom: 4 },
  input: {
    width: "100%", padding: "10px 12px", borderRadius: 9,
    border: "1.5px solid #E2E8F0", fontSize: 14, marginBottom: 16,
    boxSizing: "border-box", outline: "none",
  },
  btn: {
    width: "100%", padding: 12, background: "#F97316", color: "#fff", border: "none",
    borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer",
  },
  error: { color: "#EF4444", fontSize: 13, marginBottom: 12 },
};

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email || !password) { setError("Completá todos los campos"); return; }
    setLoading(true); setError("");
    try { await login(email, password); navigate("/dashboard"); }
    catch (err) { setError(err.response?.data?.message || "Error al iniciar sesión"); }
    finally { setLoading(false); }
  }

  return (
    <div style={s.container}>
      <div style={s.card}>
        <div style={s.logo}>KarIA</div>
        <div style={s.sub}>Marketing Platform</div>
        <form onSubmit={handleSubmit}>
          {error && <p style={s.error}>{error}</p>}
          <label style={s.label}>Email</label>
          <input style={s.input} type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="admin@empresa.com" autoComplete="email" />
          <label style={s.label}>Contraseña</label>
          <input style={s.input} type="password" value={password} onChange={e => setPassword(e.target.value)} autoComplete="current-password" />
          <button style={s.btn} type="submit" disabled={loading}>{loading ? "Ingresando..." : "Ingresar"}</button>
        </form>
      </div>
    </div>
  );
}
