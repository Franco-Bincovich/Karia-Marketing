import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import EmptyState from "../components/ui/EmptyState";

const card       = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 12, padding: 20, marginBottom: 16 };
const btn        = { padding: "10px 20px", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSmall   = { padding: "6px 14px", border: "1px solid var(--border)", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "var(--surface)", color: "var(--text-secondary)" };
const selectStyle= { padding: "10px 12px", border: "1.5px solid var(--border)", borderRadius: 9, fontSize: 14, outline: "none", appearance: "auto", background: "var(--surface)", color: "var(--text)" };

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

  if (loading) return <Layout title="Reporting"><p style={{ color: "var(--text-muted)" }}>Cargando...</p></Layout>;

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
        <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{reportes.length} reportes generados</span>
      </div>

      {/* Detalle */}
      {detalle && (
        <div>
          <div style={{ ...card, borderColor: "var(--primary)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h3 style={{ fontSize: 15, fontWeight: 700, color: "var(--text)" }}>Reporte {detalle.tipo}</h3>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{detalle.periodo_inicio} a {detalle.periodo_fin}</span>
            </div>

            {detalle.resumen_ejecutivo && (
              <div style={{ background: "var(--primary-light)", borderRadius: 10, padding: 16, marginBottom: 16, borderLeft: "4px solid var(--primary)" }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "var(--primary)", marginBottom: 6 }}>Resumen Ejecutivo (IA)</div>
                <p style={{ fontSize: 14, color: "var(--text)", lineHeight: 1.6 }}>{detalle.resumen_ejecutivo}</p>
              </div>
            )}

            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
              {[
                ["Alcance",     totales.alcance],
                ["Impresiones", totales.impresiones],
                ["Engagement",  totales.engagement],
                ["Clicks",      totales.clicks],
              ].map(([label, val]) => (
                <div key={label} style={{ background: "var(--surface-2)", borderRadius: 10, padding: 14, textAlign: "center" }}>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>{label}</div>
                  <div style={{ fontSize: 22, fontWeight: 800, color: "var(--text)" }}>{(val || 0).toLocaleString()}</div>
                </div>
              ))}
            </div>

            {detalle.contenido?.comparacion && (
              <div style={{ marginTop: 16 }}>
                <h4 style={{ fontSize: 13, fontWeight: 700, marginBottom: 8, color: "var(--text)" }}>vs Período anterior</h4>
                <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                  {Object.entries(detalle.contenido.comparacion.variaciones || {}).map(([k, v]) => (
                    <span key={k} style={{
                      padding: "4px 10px", borderRadius: 6, fontSize: 12, fontWeight: 600,
                      background: v > 0 ? "var(--success-bg)" : v < 0 ? "var(--danger-bg)" : "var(--surface-2)",
                      color: v > 0 ? "var(--success-text)" : v < 0 ? "var(--danger-text)" : "var(--text-secondary)",
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

      {/* Historial */}
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>Historial ({reportes.length})</h3>
        {reportes.length === 0 ? (
          <EmptyState icon="📋" title="Sin reportes" description="Generá tu primer reporte de performance" action={{ label: "Generar reporte", onClick: generar }} />
        ) : reportes.map(r => (
          <div key={r.id} style={{ padding: "10px 0", borderBottom: "1px solid var(--border-subtle)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span style={{ fontSize: 13, fontWeight: 500, color: "var(--text)" }}>{r.tipo}</span>
              <span style={{ fontSize: 12, color: "var(--text-muted)", marginLeft: 8 }}>{r.periodo_inicio} a {r.periodo_fin}</span>
            </div>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <span style={{
                background: r.enviado ? "var(--success-bg)" : "var(--warning-bg)",
                color: r.enviado ? "var(--success-text)" : "var(--warning-text)",
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
