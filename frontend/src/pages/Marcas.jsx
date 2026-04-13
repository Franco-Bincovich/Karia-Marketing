/**
 * Página de gestión de marcas por cliente.
 */

import { useEffect, useState } from "react";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const s = {
  page: { padding: "var(--spacing-8)", fontFamily: "var(--font-sans)" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--spacing-6)" },
  title: { fontSize: "var(--font-size-2xl)", fontWeight: 700 },
  btn: { background: "var(--color-primary)", color: "#fff", border: "none", padding: "10px 20px", borderRadius: "var(--radius-md)", cursor: "pointer", fontWeight: 600 },
  form: { background: "var(--color-surface)", padding: "var(--spacing-6)", borderRadius: "var(--radius-md)", boxShadow: "var(--shadow-md)", marginBottom: "var(--spacing-6)" },
  input: { display: "block", width: "100%", padding: "10px 12px", borderRadius: "var(--radius-md)", border: "1px solid var(--color-border)", marginBottom: "var(--spacing-4)", boxSizing: "border-box" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "var(--spacing-4)" },
  card: { background: "var(--color-surface)", borderRadius: "var(--radius-md)", padding: "var(--spacing-4)", boxShadow: "var(--shadow-sm)" },
  cardTitle: { fontWeight: 700, marginBottom: "4px" },
  error: { color: "var(--color-error)", fontSize: "var(--font-size-sm)", marginBottom: "var(--spacing-3)" },
};

export default function Marcas() {
  const { user } = useAuth();
  const { get, post } = useApi();
  const [marcas, setMarcas] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ nombre: "", industria: "", sitio_web: "" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const clienteId = user?.cliente_id;

  useEffect(() => {
    if (!clienteId) return;
    get(ENDPOINTS.CLIENTE_MARCAS(clienteId)).then(({ data }) => setMarcas(data)).catch(() => {});
  }, [get, clienteId]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.nombre) { setError("El nombre es requerido"); return; }
    setSaving(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.CLIENTE_MARCAS(clienteId), form);
      setMarcas((prev) => [...prev, data]);
      setShowForm(false);
      setForm({ nombre: "", industria: "", sitio_web: "" });
    } catch (err) {
      setError(err.response?.data?.message || "Error al crear marca");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>Marcas</h1>
        <button style={s.btn} onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancelar" : "+ Nueva marca"}
        </button>
      </div>

      {showForm && (
        <form style={s.form} onSubmit={handleSubmit}>
          {error && <p style={s.error}>{error}</p>}
          <input style={s.input} placeholder="Nombre *" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
          <input style={s.input} placeholder="Industria" value={form.industria} onChange={(e) => setForm({ ...form, industria: e.target.value })} />
          <input style={s.input} placeholder="Sitio web" value={form.sitio_web} onChange={(e) => setForm({ ...form, sitio_web: e.target.value })} />
          <button style={s.btn} type="submit" disabled={saving}>{saving ? "Guardando..." : "Crear marca"}</button>
        </form>
      )}

      <div style={s.grid}>
        {marcas.map((m) => (
          <div key={m.id} style={s.card}>
            <div style={s.cardTitle}>{m.nombre}</div>
            {m.industria && <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)" }}>{m.industria}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
