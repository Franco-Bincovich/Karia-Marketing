import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box" };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnApprove = { ...btn, background: "#10B981" };
const btnPause = { ...btn, background: "#EF4444", fontSize: 12, padding: "6px 12px" };
const th = { textAlign: "left", fontSize: 10, color: "#94A3B8", textTransform: "uppercase", padding: "8px 12px", borderBottom: "1px solid #E2E8F0" };
const td = { padding: "10px 12px", fontSize: 13, borderBottom: "1px solid #F1F5F9", color: "#475569" };

const estadoBadge = (e) => {
  const map = { activa: ["#DCFCE7", "#15803D"], pendiente_aprobacion: ["#FEF3C7", "#B45309"], pausada: ["#FEE2E2", "#B91C1C"], borrador: ["#F1F5F9", "#475569"] };
  const [bg, color] = map[e] || ["#F1F5F9", "#475569"];
  return { background: bg, color, padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 };
};

export default function Ads() {
  const { get, post, patch } = useApi();
  const [campanas, setCampanas] = useState([]);
  const [umbrales, setUmbrales] = useState({});
  const [form, setForm] = useState({ nombre: "", plataforma: "meta", presupuesto_diario: "", objetivo: "" });
  const [loading, setLoading] = useState(false);

  useEffect(() => { cargar(); }, []);

  function cargar() {
    get(ENDPOINTS.ADS_CAMPANAS).then(r => setCampanas(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.ADS_UMBRALES).then(r => setUmbrales(r.data || {})).catch(() => {});
  }

  async function crear() {
    if (!form.nombre || !form.presupuesto_diario) return;
    setLoading(true);
    await post(ENDPOINTS.ADS_CAMPANAS, { ...form, presupuesto_diario: Number(form.presupuesto_diario) });
    setForm({ nombre: "", plataforma: "meta", presupuesto_diario: "", objetivo: "" });
    cargar(); setLoading(false);
  }

  async function aprobar(id) { await post(ENDPOINTS.ADS_APROBAR(id), {}); cargar(); }
  async function pausar(id) { await post(ENDPOINTS.ADS_PAUSAR(id), { motivo: "manual" }); cargar(); }

  return (
    <Layout title="Campañas Ads">
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Nueva Campaña</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr auto", gap: 12, alignItems: "end" }}>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Nombre</label><input style={input} value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} /></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Plataforma</label><select style={{ ...input, appearance: "auto" }} value={form.plataforma} onChange={e => setForm({ ...form, plataforma: e.target.value })}><option>meta</option><option>google</option></select></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Presupuesto/día ($)</label><input style={input} type="number" value={form.presupuesto_diario} onChange={e => setForm({ ...form, presupuesto_diario: e.target.value })} /></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Objetivo</label><input style={input} value={form.objetivo} onChange={e => setForm({ ...form, objetivo: e.target.value })} /></div>
          <button style={btn} onClick={crear} disabled={loading}>Crear</button>
        </div>
      </div>
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Campañas ({campanas.length})</h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead><tr><th style={th}>Nombre</th><th style={th}>Plataforma</th><th style={th}>Presupuesto/día</th><th style={th}>Estado</th><th style={th}>Acciones</th></tr></thead>
          <tbody>{campanas.map(c => (
            <tr key={c.id}>
              <td style={td}>{c.nombre}</td><td style={td}>{c.plataforma}</td>
              <td style={td}>${c.presupuesto_diario}</td>
              <td style={td}><span style={estadoBadge(c.estado)}>{c.estado}</span></td>
              <td style={td}>
                {c.estado === "pendiente_aprobacion" && <button style={btnApprove} onClick={() => aprobar(c.id)}>Aprobar</button>}
                {c.estado === "activa" && <button style={btnPause} onClick={() => pausar(c.id)}>Pausar</button>}
              </td>
            </tr>
          ))}</tbody>
        </table>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
        {[["CPA Máximo", umbrales.cpa_maximo], ["ROAS Mínimo", umbrales.roas_minimo], ["Gasto Diario Máx", umbrales.gasto_diario_maximo]].map(([label, val]) => (
          <div key={label} style={card}>
            <div style={{ fontSize: 12, color: "#94A3B8", marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 26, fontWeight: 800 }}>${val || 0}</div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
