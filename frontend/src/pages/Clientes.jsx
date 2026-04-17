import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import EmptyState from "../components/ui/EmptyState";

const card        = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 12, padding: 20, marginBottom: 16 };
const inputStyle  = { width: "100%", padding: "10px 12px", border: "1.5px solid var(--border)", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 12, background: "var(--surface)", color: "var(--text)" };
const selectStyle = { ...inputStyle, appearance: "auto" };
const btnPrimary  = { padding: "10px 20px", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSecondary= { padding: "10px 20px", background: "var(--surface)", color: "var(--text-secondary)", border: "1.5px solid var(--border)", borderRadius: 9, fontSize: 14, fontWeight: 500, cursor: "pointer" };
const th          = { textAlign: "left", fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", padding: "8px 12px", borderBottom: "1px solid var(--border)", fontWeight: 600 };
const td          = { padding: "10px 12px", fontSize: 13, borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)" };
const planBadge   = (plan) => ({
  background: plan === "Premium" ? "var(--purple-bg)" : "var(--surface-2)",
  color: plan === "Premium" ? "var(--purple-text)" : "var(--text-secondary)",
  padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600,
});
const actionBtn   = { padding: "5px 12px", border: "1px solid var(--border)", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "var(--surface)", color: "var(--text-secondary)" };
const renewBtn    = { ...actionBtn, borderColor: "var(--success)", color: "var(--success-text)" };

const estadoBadge = (estado) => {
  const map = {
    activo:     { bg: "var(--success-bg)", color: "var(--success-text)" },
    por_vencer: { bg: "var(--warning-bg)", color: "var(--warning-text)" },
    vencido:    { bg: "var(--danger-bg)",  color: "var(--danger-text)"  },
  };
  const s = map[estado] || map.vencido;
  return { background: s.bg, color: s.color, padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 };
};

const estadoLabel = (estado) => ({ activo: "Activo", por_vencer: "Por vencer", vencido: "Vencido" }[estado] || "Vencido");

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("es-AR", { day: "2-digit", month: "short", year: "numeric" });
}

export default function Clientes() {
  const { get, post, patch } = useApi();
  const [clientes, setClientes] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ nombre: "", email_admin: "", plan: "Basic" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [actionId, setActionId] = useState(null);
  const [createdCliente, setCreatedCliente] = useState(null);

  useEffect(() => {
    get(ENDPOINTS.CLIENTES).then(({ data }) => setClientes(Array.isArray(data) ? data : [])).catch(() => {});
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.nombre || !form.email_admin) { setError("Completá nombre y email"); return; }
    setSaving(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.CLIENTES, form);
      setClientes(prev => [data, ...prev]);
      setCreatedCliente(data);
      setShowForm(false);
      setForm({ nombre: "", email_admin: "", plan: "Basic" });
    } catch (err) { setError(err.response?.data?.message || "Error al crear cliente"); }
    finally { setSaving(false); }
  }

  async function toggleEstado(cliente) {
    setActionId(cliente.id + "_estado");
    try {
      const { data } = await patch(ENDPOINTS.CLIENTE_ESTADO(cliente.id), { activo: !cliente.activo });
      setClientes(prev => prev.map(c => c.id === cliente.id ? data : c));
    } catch {}
    finally { setActionId(null); }
  }

  async function renovar(cliente) {
    setActionId(cliente.id + "_renovar");
    try {
      const { data } = await post(ENDPOINTS.CLIENTE_RENOVAR(cliente.id));
      setClientes(prev => prev.map(c => c.id === cliente.id ? data : c));
    } catch {}
    finally { setActionId(null); }
  }

  return (
    <Layout title="Clientes">
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
        <button style={btnPrimary} onClick={() => { setShowForm(v => !v); setCreatedCliente(null); }}>
          {showForm ? "Cancelar" : "+ Nuevo cliente"}
        </button>
      </div>

      {createdCliente && !showForm && (
        <div style={{ ...card, borderColor: "var(--success)", background: "var(--success-bg)" }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: "var(--success-text)", marginBottom: 8 }}>Cliente creado correctamente</div>
          <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            <strong>{createdCliente.nombre}</strong> — {createdCliente.email_admin}
          </div>
          <div style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 4 }}>
            Plan: <strong>{createdCliente.plan}</strong> · Vencimiento: <strong>{formatDate(createdCliente.fecha_vencimiento)}</strong> ({createdCliente.dias_restantes} días)
          </div>
          <button style={{ ...btnSecondary, marginTop: 12, fontSize: 12, padding: "6px 14px" }} onClick={() => setCreatedCliente(null)}>Cerrar</button>
        </div>
      )}

      {showForm && (
        <form style={card} onSubmit={handleSubmit}>
          {error && <div className="msg-error" style={{ marginBottom: 12, borderRadius: 8 }}>{error}</div>}
          <input style={inputStyle} placeholder="Nombre del cliente" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} />
          <input style={inputStyle} placeholder="Email del administrador" type="email" value={form.email_admin} onChange={e => setForm({ ...form, email_admin: e.target.value })} />
          <select style={selectStyle} value={form.plan} onChange={e => setForm({ ...form, plan: e.target.value })}>
            <option value="Basic">Basic — USD 100/mes</option>
            <option value="Premium">Premium — USD 250/mes</option>
          </select>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 12 }}>
            El primer ciclo de 30 días queda incluido en la membresía de acceso.
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button style={btnPrimary} type="submit" disabled={saving}>{saving ? "Creando..." : "Crear cliente"}</button>
            <button style={btnSecondary} type="button" onClick={() => setShowForm(false)}>Cancelar</button>
          </div>
        </form>
      )}

      <div style={{ ...card, overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 800 }}>
          <thead>
            <tr>
              <th style={th}>Nombre</th><th style={th}>Email</th><th style={th}>Plan</th>
              <th style={th}>Estado</th><th style={th}>Vencimiento</th><th style={th}>Días rest.</th>
              <th style={th}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {clientes.length === 0 && (
              <tr><td colSpan={7} style={{ ...td, textAlign: "center", color: "var(--text-muted)" }}>No hay clientes registrados</td></tr>
            )}
            {clientes.map(c => (
              <tr key={c.id}>
                <td style={{ ...td, fontWeight: 500, color: "var(--text)" }}>{c.nombre}</td>
                <td style={td}>{c.email_admin}</td>
                <td style={td}><span style={planBadge(c.plan)}>{c.plan}</span></td>
                <td style={td}><span style={estadoBadge(c.estado_vencimiento)}>{estadoLabel(c.estado_vencimiento)}</span></td>
                <td style={td}>{formatDate(c.fecha_vencimiento)}</td>
                <td style={{ ...td, fontWeight: 600, color: c.dias_restantes <= 7 ? "var(--warning-text)" : "var(--text-secondary)" }}>{c.dias_restantes}d</td>
                <td style={td}>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    <button style={renewBtn} onClick={() => renovar(c)} disabled={actionId === c.id + "_renovar"}>
                      {actionId === c.id + "_renovar" ? "..." : "Renovar"}
                    </button>
                    <button style={actionBtn} onClick={() => toggleEstado(c)} disabled={actionId === c.id + "_estado"}>
                      {actionId === c.id + "_estado" ? "..." : c.activo ? "Pausar" : "Reactivar"}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
