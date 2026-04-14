import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const th = { textAlign: "left", fontSize: 10, color: "#94A3B8", textTransform: "uppercase", padding: "8px 12px", borderBottom: "1px solid #E2E8F0" };
const td = { padding: "10px 12px", fontSize: 13, borderBottom: "1px solid #F1F5F9", color: "#475569" };

export default function Reporting() {
  const { get, post, patch } = useApi();
  const [reportes, setReportes] = useState([]);
  const [config, setConfig] = useState({});
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    Promise.all([
      get(ENDPOINTS.ANALYTICS_REPORTES).then(r => setReportes(r.data.data || [])),
      get(ENDPOINTS.ANALYTICS_CONFIG).then(r => setConfig(r.data || {})),
    ]).catch(() => {}).finally(() => setLoading(false));
  }, []);

  async function generar() {
    setGenerating(true);
    try {
      await post(ENDPOINTS.ANALYTICS_GENERAR_REPORTE, { tipo: config.frecuencia || "semanal" });
      const { data } = await get(ENDPOINTS.ANALYTICS_REPORTES);
      setReportes(data.data || []);
    } catch {}
    finally { setGenerating(false); }
  }

  async function actualizarConfig(campo, valor) {
    const updated = { [campo]: valor };
    try {
      const { data } = await patch(ENDPOINTS.ANALYTICS_CONFIG, updated);
      setConfig(data);
    } catch {}
  }

  const ultimo = reportes[0];

  if (loading) return <Layout title="Reporting"><p style={{ color: "#94A3B8" }}>Cargando...</p></Layout>;

  return (
    <Layout title="Reporting">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Configuración</h3>
          <label style={{ fontSize: 12, color: "#94A3B8" }}>Frecuencia</label>
          <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
            {["diario", "semanal", "mensual"].map(f => (
              <button key={f} onClick={() => actualizarConfig("frecuencia", f)} style={{
                padding: "6px 16px", borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: "pointer",
                border: config.frecuencia === f ? "2px solid #F97316" : "1px solid #E2E8F0",
                background: config.frecuencia === f ? "#FFF7ED" : "#fff",
                color: config.frecuencia === f ? "#F97316" : "#475569",
              }}>{f}</button>
            ))}
          </div>
          <label style={{ fontSize: 12, color: "#94A3B8" }}>Canal de notificación</label>
          <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
            {["panel", "email", "whatsapp"].map(c => (
              <button key={c} onClick={() => actualizarConfig("canal_notificacion", c)} style={{
                padding: "6px 16px", borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: "pointer",
                border: config.canal_notificacion === c ? "2px solid #F97316" : "1px solid #E2E8F0",
                background: config.canal_notificacion === c ? "#FFF7ED" : "#fff",
                color: config.canal_notificacion === c ? "#F97316" : "#475569",
              }}>{c}</button>
            ))}
          </div>
          <button style={btn} onClick={generar} disabled={generating}>{generating ? "Generando..." : "Generar Reporte Ahora"}</button>
        </div>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Último Reporte</h3>
          {ultimo ? (
            <div>
              <div style={{ fontSize: 13, color: "#475569", marginBottom: 8 }}>
                <strong>Tipo:</strong> {ultimo.tipo} — <strong>Período:</strong> {ultimo.periodo_inicio} a {ultimo.periodo_fin}
              </div>
              <div style={{ fontSize: 13, color: "#475569", marginBottom: 8 }}>
                <strong>Formato:</strong> {ultimo.formato} — <strong>Estado:</strong>{" "}
                <span style={{ background: ultimo.enviado ? "#DCFCE7" : "#FEF3C7", color: ultimo.enviado ? "#15803D" : "#B45309", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{ultimo.enviado ? "Enviado" : "Pendiente"}</span>
              </div>
              {ultimo.contenido?.totales && (
                <div style={{ background: "#F8FAFC", borderRadius: 8, padding: 12, marginTop: 8 }}>
                  {Object.entries(ultimo.contenido.totales).map(([k, v]) => (
                    <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", fontSize: 13 }}>
                      <span style={{ color: "#94A3B8", textTransform: "capitalize" }}>{k.replace(/_/g, " ")}</span>
                      <span style={{ fontWeight: 600 }}>{typeof v === "number" ? v.toLocaleString() : v}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : <p style={{ color: "#94A3B8", fontSize: 13 }}>Sin reportes generados</p>}
        </div>
      </div>
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Historial de Reportes ({reportes.length})</h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead><tr><th style={th}>Tipo</th><th style={th}>Período</th><th style={th}>Formato</th><th style={th}>Estado</th><th style={th}>Fecha</th></tr></thead>
          <tbody>{reportes.map(r => (
            <tr key={r.id}>
              <td style={td}>{r.tipo}</td>
              <td style={td}>{r.periodo_inicio} a {r.periodo_fin}</td>
              <td style={td}>{r.formato}</td>
              <td style={td}><span style={{ background: r.enviado ? "#DCFCE7" : "#FEF3C7", color: r.enviado ? "#15803D" : "#B45309", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{r.enviado ? "Enviado" : "Pendiente"}</span></td>
              <td style={td}>{r.created_at?.split("T")[0]}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </Layout>
  );
}
