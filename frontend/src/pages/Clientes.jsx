/**
 * Página de gestión de clientes — solo superadmin.
 */

import { useEffect, useState } from "react";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const s = {
  page: { padding: "var(--spacing-8)", fontFamily: "var(--font-sans)" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--spacing-6)" },
  title: { fontSize: "var(--font-size-2xl)", fontWeight: 700, color: "var(--color-text)" },
  btn: {
    background: "var(--color-primary)", color: "#fff", border: "none",
    padding: "10px 20px", borderRadius: "var(--radius-md)", cursor: "pointer", fontWeight: 600,
  },
  table: { width: "100%", borderCollapse: "collapse", background: "var(--color-surface)", borderRadius: "var(--radius-md)", overflow: "hidden", boxShadow: "var(--shadow-sm)" },
  th: { background: "var(--color-bg)", padding: "12px 16px", textAlign: "left", fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", fontWeight: 600 },
  td: { padding: "12px 16px", borderTop: "1px solid var(--color-border)", fontSize: "var(--font-size-sm)" },
  form: { background: "var(--color-surface)", padding: "var(--spacing-6)", borderRadius: "var(--radius-md)", boxShadow: "var(--shadow-md)", marginBottom: "var(--spacing-6)" },
  input: { display: "block", width: "100%", padding: "10px 12px", borderRadius: "var(--radius-md)", border: "1px solid var(--color-border)", marginBottom: "var(--spacing-4)", boxSizing: "border-box" },
  error: { color: "var(--color-error)", fontSize: "var(--font-size-sm)", marginBottom: "var(--spacing-3)" },
};

export default function Clientes() {
  const { get, post } = useApi();
  const [clientes, setClientes] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ nombre: "", email_admin: "", pais: "AR" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    get(ENDPOINTS.CLIENTES).then(({ data }) => setClientes(data)).catch(() => {});
  }, [get]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.nombre || !form.email_admin) { setError("Completá todos los campos"); return; }
    setSaving(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.CLIENTES, form);
      setClientes((prev) => [...prev, data]);
      setShowForm(false);
      setForm({ nombre: "", email_admin: "", pais: "AR" });
    } catch (err) {
      setError(err.response?.data?.message || "Error al crear cliente");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>Clientes</h1>
        <button style={s.btn} onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancelar" : "+ Nuevo cliente"}
        </button>
      </div>

      {showForm && (
        <form style={s.form} onSubmit={handleSubmit}>
          {error && <p style={s.error}>{error}</p>}
          <input style={s.input} placeholder="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
          <input style={s.input} placeholder="Email admin" type="email" value={form.email_admin} onChange={(e) => setForm({ ...form, email_admin: e.target.value })} />
          <input style={s.input} placeholder="País (AR)" value={form.pais} onChange={(e) => setForm({ ...form, pais: e.target.value })} />
          <button style={s.btn} type="submit" disabled={saving}>{saving ? "Guardando..." : "Crear cliente"}</button>
        </form>
      )}

      <table style={s.table}>
        <thead>
          <tr>
            <th style={s.th}>Nombre</th>
            <th style={s.th}>Email admin</th>
            <th style={s.th}>País</th>
            <th style={s.th}>Estado</th>
          </tr>
        </thead>
        <tbody>
          {clientes.map((c) => (
            <tr key={c.id}>
              <td style={s.td}>{c.nombre}</td>
              <td style={s.td}>{c.email_admin}</td>
              <td style={s.td}>{c.pais}</td>
              <td style={s.td}>{c.activo ? "Activo" : "Inactivo"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
