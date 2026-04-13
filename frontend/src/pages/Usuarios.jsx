/**
 * Página de gestión de subusuarios y permisos.
 */

import { useEffect, useState } from "react";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const ROLES = ["admin", "subusuario"];

const s = {
  page: { padding: "var(--spacing-8)", fontFamily: "var(--font-sans)" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--spacing-6)" },
  title: { fontSize: "var(--font-size-2xl)", fontWeight: 700 },
  btn: { background: "var(--color-primary)", color: "#fff", border: "none", padding: "10px 20px", borderRadius: "var(--radius-md)", cursor: "pointer", fontWeight: 600 },
  form: { background: "var(--color-surface)", padding: "var(--spacing-6)", borderRadius: "var(--radius-md)", boxShadow: "var(--shadow-md)", marginBottom: "var(--spacing-6)" },
  input: { display: "block", width: "100%", padding: "10px 12px", borderRadius: "var(--radius-md)", border: "1px solid var(--color-border)", marginBottom: "var(--spacing-4)", boxSizing: "border-box" },
  select: { display: "block", width: "100%", padding: "10px 12px", borderRadius: "var(--radius-md)", border: "1px solid var(--color-border)", marginBottom: "var(--spacing-4)", boxSizing: "border-box", background: "#fff" },
  table: { width: "100%", borderCollapse: "collapse", background: "var(--color-surface)", borderRadius: "var(--radius-md)", overflow: "hidden", boxShadow: "var(--shadow-sm)" },
  th: { background: "var(--color-bg)", padding: "12px 16px", textAlign: "left", fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", fontWeight: 600 },
  td: { padding: "12px 16px", borderTop: "1px solid var(--color-border)", fontSize: "var(--font-size-sm)" },
  error: { color: "var(--color-error)", fontSize: "var(--font-size-sm)", marginBottom: "var(--spacing-3)" },
};

export default function Usuarios() {
  const { user } = useAuth();
  const { get, post } = useApi();
  const [usuarios, setUsuarios] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ email: "", password: "", nombre: "", rol: "subusuario" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const clienteId = user?.cliente_id;

  useEffect(() => {
    if (!clienteId) return;
    get(ENDPOINTS.USUARIOS, { cliente_id: clienteId }).then(({ data }) => setUsuarios(data)).catch(() => {});
  }, [get, clienteId]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.email || !form.password || !form.nombre) { setError("Completá todos los campos"); return; }
    setSaving(true); setError("");
    try {
      const payload = { ...form, cliente_id: clienteId };
      const { data } = await post(ENDPOINTS.USUARIOS, payload);
      setUsuarios((prev) => [...prev, data]);
      setShowForm(false);
      setForm({ email: "", password: "", nombre: "", rol: "subusuario" });
    } catch (err) {
      setError(err.response?.data?.message || "Error al crear usuario");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>Usuarios</h1>
        <button style={s.btn} onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancelar" : "+ Nuevo usuario"}
        </button>
      </div>

      {showForm && (
        <form style={s.form} onSubmit={handleSubmit}>
          {error && <p style={s.error}>{error}</p>}
          <input style={s.input} placeholder="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
          <input style={s.input} placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input style={s.input} placeholder="Contraseña" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <select style={s.select} value={form.rol} onChange={(e) => setForm({ ...form, rol: e.target.value })}>
            {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
          <button style={s.btn} type="submit" disabled={saving}>{saving ? "Guardando..." : "Crear usuario"}</button>
        </form>
      )}

      <table style={s.table}>
        <thead>
          <tr>
            <th style={s.th}>Nombre</th>
            <th style={s.th}>Email</th>
            <th style={s.th}>Rol</th>
            <th style={s.th}>Estado</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map((u) => (
            <tr key={u.id}>
              <td style={s.td}>{u.nombre}</td>
              <td style={s.td}>{u.email}</td>
              <td style={s.td}>{u.rol}</td>
              <td style={s.td}>{u.activo ? "Activo" : "Inactivo"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
