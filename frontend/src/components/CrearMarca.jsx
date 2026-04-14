import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const s = {
  container: {
    minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
    background: "#F1F5F9", fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  card: {
    background: "#fff", borderRadius: 14, border: "1px solid #E2E8F0",
    padding: 32, width: "100%", maxWidth: 480, boxShadow: "0 4px 12px rgba(0,0,0,.08)",
  },
  logo: { fontSize: 22, fontWeight: 800, color: "#F97316", marginBottom: 4 },
  title: { fontSize: 20, fontWeight: 700, color: "#0F172A", marginBottom: 4 },
  sub: { fontSize: 14, color: "#475569", marginBottom: 28 },
  label: { display: "block", fontSize: 12, color: "#94A3B8", marginBottom: 4 },
  input: {
    width: "100%", padding: "10px 12px", borderRadius: 9,
    border: "1.5px solid #E2E8F0", fontSize: 14, marginBottom: 16,
    boxSizing: "border-box", outline: "none",
  },
  textarea: {
    width: "100%", padding: "10px 12px", borderRadius: 9,
    border: "1.5px solid #E2E8F0", fontSize: 14, marginBottom: 16,
    boxSizing: "border-box", outline: "none", minHeight: 80, resize: "vertical",
  },
  btn: {
    width: "100%", padding: 12, background: "#F97316", color: "#fff", border: "none",
    borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer",
  },
  error: { color: "#EF4444", fontSize: 13, marginBottom: 12 },
};

export default function CrearMarca() {
  const { user, addMarca } = useAuth();
  const { post } = useApi();
  const navigate = useNavigate();
  const [nombre, setNombre] = useState("");
  const [industria, setIndustria] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!nombre.trim()) { setError("El nombre de la marca es obligatorio"); return; }
    setLoading(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.CLIENTE_MARCAS(user.cliente_id), {
        nombre: nombre.trim(), industria: industria.trim() || undefined,
        descripcion: descripcion.trim() || undefined,
      });
      addMarca(data);
      navigate("/onboarding");
    } catch (err) {
      setError(err.response?.data?.message || "Error al crear la marca");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={s.container}>
      <div style={s.card}>
        <div style={s.logo}>KarIA</div>
        <h1 style={s.title}>Creá tu primera marca</h1>
        <p style={s.sub}>Configurá la marca que vas a gestionar con KarIA</p>
        <form onSubmit={handleSubmit}>
          {error && <p style={s.error}>{error}</p>}
          <label style={s.label}>Nombre de la marca *</label>
          <input style={s.input} value={nombre} onChange={e => setNombre(e.target.value)} placeholder="Ej: Mi Empresa" />
          <label style={s.label}>Industria</label>
          <input style={s.input} value={industria} onChange={e => setIndustria(e.target.value)} placeholder="Ej: Tecnología, Gastronomía..." />
          <label style={s.label}>Descripción breve</label>
          <textarea style={s.textarea} value={descripcion} onChange={e => setDescripcion(e.target.value)} placeholder="¿A qué se dedica tu marca?" />
          <button style={s.btn} type="submit" disabled={loading}>
            {loading ? "Creando..." : "Crear marca"}
          </button>
        </form>
      </div>
    </div>
  );
}
