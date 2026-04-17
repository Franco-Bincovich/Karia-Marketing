import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);
  const { login } = useAuth();
  const navigate  = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email || !password) { setError("Completá todos los campos"); return; }
    setLoading(true); setError("");
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.message || "Email o contraseña incorrectos");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "var(--bg)",
      padding: 20,
    }}>
      <div className="card" style={{
        width: "100%",
        maxWidth: 420,
        padding: 36,
        boxShadow: "var(--shadow-xl)",
        animation: "slideUp 250ms ease",
      }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{
            display: "inline-flex",
            width: 52, height: 52,
            borderRadius: 14,
            background: "linear-gradient(135deg, #FF6B2B, #F5A623)",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 22,
            fontWeight: 900,
            color: "#fff",
            marginBottom: 14,
            boxShadow: "0 8px 24px rgba(255,107,43,0.35)",
          }}>N</div>
          <div style={{ fontSize: 22, fontWeight: 900, color: "var(--text)", letterSpacing: "-0.5px" }}>NEXO</div>
          <div style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 3 }}>Marketing AI Platform</div>
        </div>

        <form onSubmit={handleSubmit}>
          {error && (
            <div className="msg-error" style={{ marginBottom: 16, borderRadius: "var(--radius)" }}>
              {error}
            </div>
          )}

          <div style={{ marginBottom: 16 }}>
            <label className="field-label">Email</label>
            <input
              className="field-input"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="admin@empresa.com"
              autoComplete="email"
            />
          </div>

          <div style={{ marginBottom: 24 }}>
            <label className="field-label">Contraseña</label>
            <input
              className="field-input"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: "100%", padding: 12, fontSize: "var(--text-md)" }}
            disabled={loading}
          >
            {loading ? (
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
                <span className="spinner" />
                Ingresando...
              </span>
            ) : "Ingresar"}
          </button>
        </form>
      </div>
    </div>
  );
}
