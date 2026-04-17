import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";
import EmptyState from "../components/ui/EmptyState";

const card  = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid var(--border)", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 12, background: "var(--surface)", color: "var(--text)" };
const btn   = { padding: "10px 20px", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };

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
          {error && (
            <div className="msg-error" style={{ marginBottom: 12, borderRadius: 8 }}>
              <span style={{ flex: 1 }}>{error}</span>
              <button type="button" className="msg-dismiss" onClick={() => setError("")}>×</button>
            </div>
          )}
          <input style={input} placeholder="Nombre *" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} />
          <input style={input} placeholder="Industria" value={form.industria} onChange={e => setForm({ ...form, industria: e.target.value })} />
          <input style={input} placeholder="Sitio web" value={form.sitio_web} onChange={e => setForm({ ...form, sitio_web: e.target.value })} />
          <button style={btn} type="submit" disabled={saving}>{saving ? "Guardando..." : "Crear marca"}</button>
        </form>
      )}

      {marcas.length === 0 && !showForm ? (
        <EmptyState icon="🏢" title="Sin marcas" description="Creá tu primera marca para empezar" action={{ label: "+ Nueva marca", onClick: () => setShowForm(true) }} />
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(280px,1fr))", gap: 16 }}>
          {marcas.map(m => (
            <div key={m.id} style={card}>
              <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4, color: "var(--text)" }}>{m.nombre}</div>
              {m.industria && <div style={{ fontSize: 13, color: "var(--text-muted)" }}>{m.industria}</div>}
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
