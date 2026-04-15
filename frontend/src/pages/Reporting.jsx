import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSmall = { padding: "6px 14px", border: "1px solid #E2E8F0", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "#fff", color: "#475569" };
const selectStyle = { padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", appearance: "auto", background: "#fff" };

export default function Reporting() {
  const { get, post } = useApi();
  const [reportes, setReportes] = useState([]);
  const [periodo, setPeriodo] = useState("semanal");
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [detalle, setDetalle] = useState(null);

  useEffect(() => {
    get(ENDPOINTS.REPORTING).then(r => setReportes(r.data.data || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  async function generar() {
    setGenerating(true);
    try {
      const { data } = await post(ENDPOINTS.REPORTING_GENERAR, { periodo });
      setReportes(prev => [data, ...prev]);
      setDetalle(data);
    } catch {}
    finally { setGenerating(false); }
  }

  async function verDetalle(id) {
    try {
      const { data } = await get(ENDPOINTS.REPORTING_DETALLE(id));
      setDetalle(data);
    } catch {}
  }

  if (loading) return <Layout title="Reporting"><p style={{ color: "#94A3B8" }}>Cargando...</p></Layout>;

  const totales = detalle?.contenido?.totales || {};

  return (
    <Layout title="Reporting">
      {/* Generar */}
      <div style={{ ...card, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <select style={selectStyle} value={periodo} onChange={e => setPeriodo(e.target.value)}>
            <option value="semanal">Semanal</option>
            <option value="mensual">Mensual</option>
            <option value="diario">Diario</option>
          </select>
          <button style={btn} onClick={generar} disabled={generating}>
            {generating ? "Generando..." : "Generar Reporte"}
          </button>
        </div>
        <span style={{ fontSize: 12, color: "#94A3B8" }}>{reportes.length} reportes generados</span>
      </div>

      {/* Detalle del reporte */}
      {detalle && (
        <div>
          <div style={{ ...card, borderColor: "#F97316" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h3 style={{ fontSize: 15, fontWeight: 700 }}>Reporte {detalle.tipo}</h3>
              <span style={{ fontSize: 12, color: "#94A3B8" }}>
                {detalle.periodo_inicio} a {detalle.periodo_fin}
              </span>
            </div>

            {/* Resumen ejecutivo */}
            {detalle.resumen_ejecutivo && (
              <div style={{ background: "#FFF7ED", borderRadius: 10, padding: 16, marginBottom: 16, borderLeft: "4px solid #F97316" }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#F97316", marginBottom: 6 }}>Resumen Ejecutivo (IA)</div>
                <p style={{ fontSize: 14, color: "#0F172A", lineHeight: 1.6 }}>{detalle.resumen_ejecutivo}</p>
              </div>
            )}

            {/* Métricas en cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
              {[
                ["Alcance", totales.alcance],
                ["Impresiones", totales.impresiones],
                ["Engagement", totales.engagement],
                ["Clicks", totales.clicks],
              ].map(([label, val]) => (
                <div key={label} style={{ background: "#F8FAFC", borderRadius: 10, padding: 14, textAlign: "center" }}>
                  <div style={{ fontSize: 11, color: "#94A3B8", marginBottom: 4 }}>{label}</div>
                  <div style={{ fontSize: 22, fontWeight: 800 }}>{(val || 0).toLocaleString()}</div>
                </div>
              ))}
            </div>

            {/* Comparación */}
            {detalle.contenido?.comparacion && (
              <div style={{ marginTop: 16 }}>
                <h4 style={{ fontSize: 13, fontWeight: 700, marginBottom: 8 }}>vs Período anterior</h4>
                <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                  {Object.entries(detalle.contenido.comparacion.variaciones || {}).map(([k, v]) => (
                    <span key={k} style={{
                      padding: "4px 10px", borderRadius: 6, fontSize: 12, fontWeight: 600,
                      background: v > 0 ? "#DCFCE7" : v < 0 ? "#FEE2E2" : "#F1F5F9",
                      color: v > 0 ? "#15803D" : v < 0 ? "#B91C1C" : "#475569",
                    }}>
                      {k}: {v > 0 ? "+" : ""}{v}%
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
          <button style={btnSmall} onClick={() => setDetalle(null)}>Cerrar detalle</button>
        </div>
      )}

      {/* Lista de reportes */}
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Historial ({reportes.length})</h3>
        {reportes.length === 0 ? (
          <p style={{ color: "#94A3B8", fontSize: 13 }}>Sin reportes. Generá uno.</p>
        ) : reportes.map(r => (
          <div key={r.id} style={{ padding: "10px 0", borderBottom: "1px solid #F1F5F9", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span style={{ fontSize: 13, fontWeight: 500, color: "#0F172A" }}>{r.tipo}</span>
              <span style={{ fontSize: 12, color: "#94A3B8", marginLeft: 8 }}>{r.periodo_inicio} a {r.periodo_fin}</span>
            </div>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <span style={{
                background: r.enviado ? "#DCFCE7" : "#FEF3C7",
                color: r.enviado ? "#15803D" : "#B45309",
                padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600,
              }}>{r.enviado ? "Enviado" : "Generado"}</span>
              <button style={btnSmall} onClick={() => verDetalle(r.id)}>Ver</button>
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
