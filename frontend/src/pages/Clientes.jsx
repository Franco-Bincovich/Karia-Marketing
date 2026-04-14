import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 12 };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const th = { textAlign: "left", fontSize: 10, color: "#94A3B8", textTransform: "uppercase", padding: "8px 12px", borderBottom: "1px solid #E2E8F0" };
const td = { padding: "10px 12px", fontSize: 13, borderBottom: "1px solid #F1F5F9", color: "#475569" };

export default function Clientes() {
  const { get, post } = useApi();
  const [clientes, setClientes] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ nombre: "", email_admin: "", pais: "AR" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => { get(ENDPOINTS.CLIENTES).then(({ data }) => setClientes(data)).catch(() => {}); }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.nombre || !form.email_admin) { setError("Completá todos los campos"); return; }
    setSaving(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.CLIENTES, form);
      setClientes(prev => [...prev, data]);
      setShowForm(false); setForm({ nombre: "", email_admin: "", pais: "AR" });
    } catch (err) { setError(err.response?.data?.message || "Error al crear cliente"); }
    finally { setSaving(false); }
  }

  return (
    <Layout title="Clientes">
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
        <button style={btn} onClick={() => setShowForm(v => !v)}>{showForm ? "Cancelar" : "+ Nuevo cliente"}</button>
      </div>
      {showForm && (
        <form style={card} onSubmit={handleSubmit}>
          {error && <p style={{ color: "#EF4444", fontSize: 13, marginBottom: 8 }}>{error}</p>}
          <input style={input} placeholder="Nombre" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} />
          <input style={input} placeholder="Email admin" type="email" value={form.email_admin} onChange={e => setForm({ ...form, email_admin: e.target.value })} />
          <input style={input} placeholder="País (AR)" value={form.pais} onChange={e => setForm({ ...form, pais: e.target.value })} />
          <button style={btn} type="submit" disabled={saving}>{saving ? "Guardando..." : "Crear cliente"}</button>
        </form>
      )}
      <div style={card}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead><tr><th style={th}>Nombre</th><th style={th}>Email</th><th style={th}>País</th><th style={th}>Estado</th></tr></thead>
          <tbody>{clientes.map(c => (
            <tr key={c.id}><td style={td}>{c.nombre}</td><td style={td}>{c.email_admin}</td><td style={td}>{c.pais}</td>
              <td style={td}><span style={{ background: c.activo ? "#DCFCE7" : "#FEE2E2", color: c.activo ? "#15803D" : "#B91C1C", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{c.activo ? "Activo" : "Inactivo"}</span></td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </Layout>
  );
}
