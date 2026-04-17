import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import EmptyState from "../components/ui/EmptyState";

const card       = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 12, padding: 20, marginBottom: 16 };
const btn        = { padding: "10px 20px", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSmall   = { padding: "6px 14px", border: "1px solid var(--border)", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "var(--surface)", color: "var(--text-secondary)" };
const selectStyle= { padding: "10px 12px", border: "1.5px solid var(--border)", borderRadius: 9, fontSize: 14, outline: "none", appearance: "auto", background: "var(--surface)", color: "var(--text)" };

const prioBadge = (p) => {
  const map = {
    alta:  ["var(--danger-bg)",  "var(--danger-text)" ],
    media: ["var(--warning-bg)", "var(--warning-text)"],
    baja:  ["var(--success-bg)", "var(--success-text)"],
  };
  const [bg, c] = map[p] || ["var(--surface-2)", "var(--text-secondary)"];
  return { background: bg, color: c, padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 };
};

export default function Estrategia() {
  const { get, post, patch } = useApi();
  const [tab, setTab] = useState("competencia");
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState("");
  const [analisis, setAnalisis] = useState(null);
  const [periodo, setPeriodo] = useState("semanal");
  const [plan, setPlan] = useState(null);
  const [sugerencias, setSugerencias] = useState([]);

  useEffect(() => {
    get(ENDPOINTS.ESTRATEGIA_SUGERENCIAS).then(r => setSugerencias(r.data.data || [])).catch(() => {});
  }, []);

  async function analizarCompetencia() {
    setLoading("comp"); setError(""); setAnalisis(null);
    try {
      const { data } = await post(ENDPOINTS.ESTRATEGIA_COMPETENCIA);
      setAnalisis(data.contenido || data);
    } catch (e) { setError(e.response?.data?.message || "Error al analizar"); }
    finally { setLoading(null); }
  }

  async function generarPlan() {
    setLoading("plan"); setError(""); setPlan(null);
    try {
      const { data } = await post(ENDPOINTS.ESTRATEGIA_PLAN, { periodo });
      setPlan(data.contenido || data);
    } catch (e) { setError(e.response?.data?.message || "Error al generar plan"); }
    finally { setLoading(null); }
  }

  async function generarSugerencias() {
    setLoading("sug"); setError("");
    try {
      const { data } = await post(ENDPOINTS.ESTRATEGIA_SUGERENCIAS);
      setSugerencias(prev => [data, ...prev]);
    } catch (e) { setError(e.response?.data?.message || "Error"); }
    finally { setLoading(null); }
  }

  async function implementar(id) {
    try {
      await patch(ENDPOINTS.ESTRATEGIA_IMPLEMENTAR(id));
      setSugerencias(prev => prev.map(s => s.id === id ? { ...s, implementada: true } : s));
    } catch {}
  }

  const tabs = [
    { key: "competencia",  label: "Competencia" },
    { key: "plan",         label: "Plan de Contenido" },
    { key: "sugerencias",  label: `Sugerencias (${sugerencias.length})` },
  ];

  return (
    <Layout title="Estrategia">
      {error && (
        <div className="msg-error" style={{ marginBottom: 16, borderRadius: 12 }}>
          <span style={{ flex: 1 }}>{error}</span>
          <button className="msg-dismiss" onClick={() => setError("")}>×</button>
        </div>
      )}

      <div className="tabs" style={{ marginBottom: 16 }}>
        {tabs.map(t => (
          <button key={t.key} className={`tab ${tab === t.key ? "active" : ""}`} onClick={() => setTab(t.key)}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Competencia */}
      {tab === "competencia" && (
        <div>
          <div style={card}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 8, color: "var(--text)" }}>Análisis de Competencia</h3>
            <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 16 }}>Analiza los competidores de tu perfil de marca con IA + búsqueda web.</p>
            <button style={btn} onClick={analizarCompetencia} disabled={loading === "comp"}>
              {loading === "comp" ? "Analizando..." : "Analizar Competencia"}
            </button>
          </div>
          {analisis && (
            <div style={card}>
              {analisis.resumen && <p style={{ fontSize: 14, color: "var(--text)", marginBottom: 16, lineHeight: 1.6 }}>{analisis.resumen}</p>}
              {(analisis.competidores || []).map((c, i) => (
                <div key={i} style={{ padding: "12px 0", borderBottom: "1px solid var(--border-subtle)" }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text)", marginBottom: 4 }}>{c.nombre}</div>
                  {c.contenido  && <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 4 }}>Contenido: {c.contenido}</p>}
                  {c.frecuencia && <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 4 }}>Frecuencia: {c.frecuencia}</p>}
                  <div style={{ display: "flex", gap: 16, fontSize: 12 }}>
                    {c.fortalezas  && <div><span style={{ color: "var(--success-text)", fontWeight: 600 }}>Fortalezas:</span> {c.fortalezas.join(", ")}</div>}
                    {c.debilidades && <div><span style={{ color: "var(--danger-text)", fontWeight: 600 }}>Debilidades:</span> {c.debilidades.join(", ")}</div>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Plan */}
      {tab === "plan" && (
        <div>
          <div style={card}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>Generar Plan de Contenido</h3>
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <select style={selectStyle} value={periodo} onChange={e => setPeriodo(e.target.value)}>
                <option value="diario">Diario (7 días)</option>
                <option value="semanal">Semanal (7 días)</option>
                <option value="mensual">Mensual (30 días)</option>
              </select>
              <button style={btn} onClick={generarPlan} disabled={loading === "plan"}>
                {loading === "plan" ? "Generando..." : "Generar Plan"}
              </button>
            </div>
          </div>
          {plan && (
            <div style={card}>
              {plan.resumen && <p style={{ fontSize: 14, color: "var(--text)", marginBottom: 16 }}>{plan.resumen}</p>}
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 600 }}>
                  <thead>
                    <tr>
                      {["Día","Red","Formato","Tema","Copy"].map(h => (
                        <th key={h} style={{ textAlign: "left", fontSize: 10, color: "var(--text-muted)", padding: "8px 12px", borderBottom: "1px solid var(--border)", fontWeight: 700, textTransform: "uppercase" }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(plan.plan || []).map((p, i) => (
                      <tr key={i}>
                        <td style={{ padding: "10px 12px", fontSize: 13, borderBottom: "1px solid var(--border-subtle)", fontWeight: 600, color: "var(--text)" }}>Día {p.dia}</td>
                        <td style={{ padding: "10px 12px", fontSize: 13, borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)" }}>{p.red_social}</td>
                        <td style={{ padding: "10px 12px", fontSize: 13, borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)" }}>{p.formato}</td>
                        <td style={{ padding: "10px 12px", fontSize: 13, borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)" }}>{p.tema}</td>
                        <td style={{ padding: "10px 12px", fontSize: 12, borderBottom: "1px solid var(--border-subtle)", color: "var(--text-muted)", maxWidth: 200 }}>{p.copy_sugerido}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sugerencias */}
      {tab === "sugerencias" && (
        <div>
          <div style={{ ...card, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: "var(--text)" }}>Sugerencias Estratégicas</h3>
            <button style={btn} onClick={generarSugerencias} disabled={loading === "sug"}>
              {loading === "sug" ? "Generando..." : "Generar Sugerencias"}
            </button>
          </div>
          {sugerencias.length === 0 ? (
            <div style={card}><EmptyState icon="💡" title="Sin sugerencias" description="Generá sugerencias estratégicas basadas en tu perfil de marca" /></div>
          ) : sugerencias.map(s => {
            const items = s.contenido?.sugerencias || [];
            return (
              <div key={s.id} style={card}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 8 }}>
                  {s.created_at ? new Date(s.created_at).toLocaleDateString("es-AR") : ""}
                  {s.implementada && <span style={{ marginLeft: 8, background: "var(--success-bg)", color: "var(--success-text)", padding: "2px 8px", borderRadius: 6, fontSize: 10, fontWeight: 600 }}>Implementada</span>}
                </div>
                {items.map((item, i) => (
                  <div key={i} style={{ padding: "8px 0", borderBottom: "1px solid var(--border-subtle)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontSize: 14, fontWeight: 600, color: "var(--text)" }}>{item.titulo}</span>
                      {item.prioridad && <span style={prioBadge(item.prioridad)}>{item.prioridad}</span>}
                    </div>
                    <p style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 4 }}>{item.descripcion}</p>
                    {item.plazo && <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Plazo: {item.plazo}</span>}
                  </div>
                ))}
                {!s.implementada && (
                  <button style={{ ...btnSmall, marginTop: 8, borderColor: "var(--success)", color: "var(--success-text)" }} onClick={() => implementar(s.id)}>
                    Marcar implementada
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Layout>
  );
}
