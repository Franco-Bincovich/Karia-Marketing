/**
 * Página de login con validación de formulario.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "var(--color-bg)",
    fontFamily: "var(--font-sans)",
  },
  card: {
    background: "var(--color-surface)",
    borderRadius: "var(--radius-lg)",
    boxShadow: "var(--shadow-lg)",
    padding: "var(--spacing-8)",
    width: "100%",
    maxWidth: "400px",
  },
  title: { fontSize: "var(--font-size-2xl)", fontWeight: 700, color: "var(--color-text)", marginBottom: "var(--spacing-6)" },
  label: { display: "block", fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", marginBottom: "var(--spacing-1)" },
  input: {
    width: "100%", padding: "10px 12px", borderRadius: "var(--radius-md)",
    border: "1px solid var(--color-border)", fontSize: "var(--font-size-base)",
    marginBottom: "var(--spacing-4)", boxSizing: "border-box",
  },
  button: {
    width: "100%", padding: "12px", background: "var(--color-primary)",
    color: "#fff", border: "none", borderRadius: "var(--radius-md)",
    fontSize: "var(--font-size-base)", fontWeight: 600, cursor: "pointer",
  },
  error: { color: "var(--color-error)", fontSize: "var(--font-size-sm)", marginBottom: "var(--spacing-4)" },
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
    if (!email || !password) {
      setError("Completá todos los campos");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.message || "Error al iniciar sesión");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>KarIA Marketing</h1>
        <form onSubmit={handleSubmit}>
          {error && <p style={styles.error}>{error}</p>}
          <label style={styles.label}>Email</label>
          <input
            style={styles.input}
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            placeholder="admin@empresa.com"
          />
          <label style={styles.label}>Contraseña</label>
          <input
            style={styles.input}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
          <button style={styles.button} type="submit" disabled={loading}>
            {loading ? "Ingresando..." : "Ingresar"}
          </button>
        </form>
      </div>
    </div>
  );
}
