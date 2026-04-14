import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 12 };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };

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
  }, [clienteId]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.nombre) { setError("El nombre es requerido"); return; }
    setSaving(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.CLIENTE_MARCAS(clienteId), form);
      setMarcas(prev => [...prev, data]);
      setShowForm(false); setForm({ nombre: "", industria: "", sitio_web: "" });
    } catch (err) { setError(err.response?.data?.message || "Error al crear marca"); }
    finally { setSaving(false); }
  }

  return (
    <Layout title="Marcas">
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
        <button style={btn} onClick={() => setShowForm(v => !v)}>{showForm ? "Cancelar" : "+ Nueva marca"}</button>
      </div>
      {showForm && (
        <form style={card} onSubmit={handleSubmit}>
          {error && <p style={{ color: "#EF4444", fontSize: 13, marginBottom: 8 }}>{error}</p>}
          <input style={input} placeholder="Nombre *" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} />
          <input style={input} placeholder="Industria" value={form.industria} onChange={e => setForm({ ...form, industria: e.target.value })} />
          <input style={input} placeholder="Sitio web" value={form.sitio_web} onChange={e => setForm({ ...form, sitio_web: e.target.value })} />
          <button style={btn} type="submit" disabled={saving}>{saving ? "Guardando..." : "Crear marca"}</button>
        </form>
      )}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(280px,1fr))", gap: 16 }}>
        {marcas.map(m => (
          <div key={m.id} style={card}>
            <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>{m.nombre}</div>
            {m.industria && <div style={{ fontSize: 13, color: "#94A3B8" }}>{m.industria}</div>}
          </div>
        ))}
      </div>
    </Layout>
  );
}
