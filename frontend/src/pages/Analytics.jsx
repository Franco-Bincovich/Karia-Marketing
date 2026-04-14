import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };

export default function Analytics() {
  const { get, post, patch } = useApi();
  const [dashboard, setDashboard] = useState(null);
  const [alertas, setAlertas] = useState([]);
  const [reportes, setReportes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      get(ENDPOINTS.ANALYTICS_DASHBOARD).then(r => setDashboard(r.data)),
      get(ENDPOINTS.ANALYTICS_ALERTAS).then(r => setAlertas(r.data.data || [])),
      get(ENDPOINTS.ANALYTICS_REPORTES).then(r => setReportes(r.data.data || [])),
    ]).catch(() => {}).finally(() => setLoading(false));
  }, []);

  async function generarReporte() {
    await post(ENDPOINTS.ANALYTICS_GENERAR_REPORTE, { tipo: "semanal" });
    get(ENDPOINTS.ANALYTICS_REPORTES).then(r => setReportes(r.data.data || []));
  }

  async function leerAlerta(id) {
    await patch(`/api/analytics/alertas/${id}/leer`, {});
    setAlertas(prev => prev.map(a => a.id === id ? { ...a, leida: true } : a));
  }

  if (loading) return <Layout title="Analytics"><p style={{ color: "#94A3B8" }}>Cargando...</p></Layout>;

  const kpis = dashboard?.kpis || [];
  const metricas = dashboard?.metricas_30d || {};

  return (
    <Layout title="Analytics">
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 16 }}>
        {[["Alcance", metricas.alcance], ["Impresiones", metricas.impresiones], ["Engagement", metricas.engagement], ["Clicks", metricas.clicks]].map(([l, v]) => (
          <div key={l} style={card}>
            <div style={{ fontSize: 12, color: "#94A3B8", marginBottom: 4 }}>{l}</div>
            <div style={{ fontSize: 26, fontWeight: 800 }}>{(v || 0).toLocaleString()}</div>
          </div>
        ))}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>KPIs — Progreso</h3>
          {kpis.length === 0 ? <p style={{ color: "#94A3B8", fontSize: 13 }}>Sin KPIs activos</p> : kpis.map(k => (
            <div key={k.kpi} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
                <span style={{ color: "#475569" }}>{k.kpi}</span>
                <span style={{ fontWeight: 600 }}>{k.progreso_pct || 0}%</span>
              </div>
              <div style={{ height: 8, background: "#F1F5F9", borderRadius: 4, overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${Math.min(k.progreso_pct || 0, 100)}%`, background: "#F97316", borderRadius: 4, transition: "width 300ms" }} />
              </div>
            </div>
          ))}
        </div>
        <div style={card}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <h3 style={{ fontSize: 15, fontWeight: 700 }}>Alertas ({alertas.filter(a => !a.leida).length})</h3>
          </div>
          {alertas.slice(0, 5).map(a => (
            <div key={a.id} style={{ padding: "8px 0", borderBottom: "1px solid #F1F5F9", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 13, color: a.leida ? "#94A3B8" : "#0F172A", fontWeight: a.leida ? 400 : 600 }}>{a.mensaje}</div>
                <div style={{ fontSize: 11, color: "#94A3B8" }}>{a.tipo}</div>
              </div>
              {!a.leida && <button onClick={() => leerAlerta(a.id)} style={{ fontSize: 11, background: "#F1F5F9", border: "none", padding: "4px 8px", borderRadius: 6, cursor: "pointer", color: "#475569" }}>Leída</button>}
            </div>
          ))}
        </div>
      </div>
      <div style={card}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700 }}>Reportes ({reportes.length})</h3>
          <button style={btn} onClick={generarReporte}>Generar Reporte</button>
        </div>
        {reportes.map(r => (
          <div key={r.id} style={{ padding: "10px 0", borderBottom: "1px solid #F1F5F9", display: "flex", justifyContent: "space-between", fontSize: 13 }}>
            <span style={{ color: "#475569" }}>{r.tipo} — {r.periodo_inicio} a {r.periodo_fin}</span>
            <span style={{ background: r.enviado ? "#DCFCE7" : "#FEF3C7", color: r.enviado ? "#15803D" : "#B45309", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{r.enviado ? "Enviado" : "Pendiente"}</span>
          </div>
        ))}
      </div>
    </Layout>
  );
}
