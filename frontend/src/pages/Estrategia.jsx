import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import EmptyState from "../components/ui/EmptyState";

const card = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 12,
  padding: 20,
  marginBottom: 16,
};
const btn = {
  padding: "10px 20px",
  background: "var(--primary)",
  color: "#fff",
  border: "none",
  borderRadius: 9,
  fontSize: 14,
  fontWeight: 600,
  cursor: "pointer",
};
const btnSmall = {
  padding: "6px 14px",
  border: "1px solid var(--border)",
  borderRadius: 7,
  fontSize: 12,
  fontWeight: 500,
  cursor: "pointer",
  background: "var(--surface)",
  color: "var(--text-secondary)",
};
const selectStyle = {
  padding: "10px 12px",
  border: "1.5px solid var(--border)",
  borderRadius: 9,
  fontSize: 14,
  outline: "none",
  appearance: "auto",
  background: "var(--surface)",
  color: "var(--text)",
};

const prioBadge = (p) => {
  const map = {
    alta: ["var(--danger-bg)", "var(--danger-text)"],
    media: ["var(--warning-bg)", "var(--warning-text)"],
    baja: ["var(--success-bg)", "var(--success-text)"],
  };
  const [bg, c] = map[p] || ["var(--surface-2)", "var(--text-secondary)"];
  return {
    background: bg,
    color: c,
    padding: "2px 8px",
    borderRadius: 6,
    fontSize: 11,
    fontWeight: 600,
  };
};

export default function Estrategia() {
  const { get, post, patch } = useApi();
  const [tab, setTab] = useState("competencia");
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState("");
  const [analisis, setAnalisis] = useState(null);
  const [periodo, setPeriodo] = useState("semanal");
  const [redSocial, setRedSocial] = useState("todas");
  const [formatos, setFormatos] = useState(["post", "carrusel", "reel", "story"]);
  const [plan, setPlan] = useState(null);
  const [planId, setPlanId] = useState(null);
  const [planSaved, setPlanSaved] = useState(false);
  const [sugerencias, setSugerencias] = useState([]);

  useEffect(() => {
    get(ENDPOINTS.ESTRATEGIA_SUGERENCIAS)
      .then((r) => setSugerencias(r.data.data || []))
      .catch(() => {});
  }, []);

  async function analizarCompetencia() {
    setLoading("comp");
    setError("");
    setAnalisis(null);
    try {
      const { data } = await post(ENDPOINTS.ESTRATEGIA_COMPETENCIA);
      setAnalisis(data.contenido || data);
    } catch (e) {
      setError(e.response?.data?.message || "Error al analizar");
    } finally {
      setLoading(null);
    }
  }

  function toggleFormato(f) {
    setFormatos((prev) => (prev.includes(f) ? prev.filter((x) => x !== f) : [...prev, f]));
  }

  async function generarPlan() {
    if (formatos.length === 0) {
      setError("Seleccioná al menos un formato");
      return;
    }
    setLoading("plan");
    setError("");
    setPlan(null);
    setPlanSaved(false);
    try {
      const { data } = await post(ENDPOINTS.ESTRATEGIA_PLAN, {
        periodo,
        red_social: redSocial,
        formatos,
      });
      setPlan(data.contenido || data);
      setPlanId(data.id || null);
    } catch (e) {
      setError(e.response?.data?.message || "Error al generar plan");
    } finally {
      setLoading(null);
    }
  }

  async function guardarPlan() {
    if (!planId) return;
    try {
      await post(ENDPOINTS.ESTRATEGIA_PLAN_ACTIVAR(planId));
      setPlanSaved(true);
    } catch (e) {
      setError(e.response?.data?.message || "Error al guardar plan");
    }
  }

  async function generarSugerencias() {
    setLoading("sug");
    setError("");
    try {
      const { data } = await post(ENDPOINTS.ESTRATEGIA_SUGERENCIAS);
      setSugerencias((prev) => [data, ...prev]);
    } catch (e) {
      setError(e.response?.data?.message || "Error");
    } finally {
      setLoading(null);
    }
  }

  async function implementar(id) {
    try {
      await patch(ENDPOINTS.ESTRATEGIA_IMPLEMENTAR(id));
      setSugerencias((prev) => prev.map((s) => (s.id === id ? { ...s, implementada: true } : s)));
    } catch {}
  }

  const tabs = [
    { key: "competencia", label: "Competencia" },
    { key: "plan", label: "Plan de Contenido" },
    { key: "sugerencias", label: `Sugerencias (${sugerencias.length})` },
  ];

  return (
    <Layout title="Estrategia">
      {error && (
        <div className="msg-error" style={{ marginBottom: 16, borderRadius: 12 }}>
          <span style={{ flex: 1 }}>{error}</span>
          <button className="msg-dismiss" onClick={() => setError("")}>
            ×
          </button>
        </div>
      )}

      <div className="tabs" style={{ marginBottom: 16 }}>
        {tabs.map((t) => (
          <button
            key={t.key}
            className={`tab ${tab === t.key ? "active" : ""}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Competencia */}
      {tab === "competencia" && (
        <div>
          <div style={card}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 8, color: "var(--text)" }}>
              Análisis de Competencia
            </h3>
            <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 16 }}>
              Analiza los competidores de tu perfil de marca con IA + búsqueda web.
            </p>
            <button style={btn} onClick={analizarCompetencia} disabled={loading === "comp"}>
              {loading === "comp" ? "Analizando..." : "Analizar Competencia"}
            </button>
          </div>
          {analisis && (
            <div style={card}>
              {analisis.resumen && (
                <p
                  style={{ fontSize: 14, color: "var(--text)", marginBottom: 16, lineHeight: 1.6 }}
                >
                  {analisis.resumen}
                </p>
              )}
              {(analisis.competidores || []).map((c, i) => (
                <div
                  key={i}
                  style={{ padding: "12px 0", borderBottom: "1px solid var(--border-subtle)" }}
                >
                  <div
                    style={{ fontSize: 14, fontWeight: 700, color: "var(--text)", marginBottom: 4 }}
                  >
                    {c.nombre}
                  </div>
                  {c.contenido && (
                    <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 4 }}>
                      Contenido: {c.contenido}
                    </p>
                  )}
                  {c.frecuencia && (
                    <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 4 }}>
                      Frecuencia: {c.frecuencia}
                    </p>
                  )}
                  <div style={{ display: "flex", gap: 16, fontSize: 12 }}>
                    {c.fortalezas && (
                      <div>
                        <span style={{ color: "var(--success-text)", fontWeight: 600 }}>
                          Fortalezas:
                        </span>{" "}
                        {c.fortalezas.join(", ")}
                      </div>
                    )}
                    {c.debilidades && (
                      <div>
                        <span style={{ color: "var(--danger-text)", fontWeight: 600 }}>
                          Debilidades:
                        </span>{" "}
                        {c.debilidades.join(", ")}
                      </div>
                    )}
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
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>
              Generar Plan de Contenido
            </h3>
            <div
              style={{
                display: "flex",
                gap: 12,
                alignItems: "center",
                marginBottom: 12,
                flexWrap: "wrap",
              }}
            >
              <select
                style={selectStyle}
                value={periodo}
                onChange={(e) => setPeriodo(e.target.value)}
              >
                <option value="diario">Diario (7 días)</option>
                <option value="semanal">Semanal (7 días)</option>
                <option value="mensual">Mensual (30 días)</option>
              </select>
              <select
                style={selectStyle}
                value={redSocial}
                onChange={(e) => setRedSocial(e.target.value)}
              >
                <option value="todas">Todas las redes</option>
                <option value="instagram">Solo Instagram</option>
                <option value="facebook">Solo Facebook</option>
              </select>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label
                style={{
                  fontSize: 12,
                  color: "var(--text-muted)",
                  display: "block",
                  marginBottom: 6,
                }}
              >
                Formatos a incluir
              </label>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {[
                  ["post", "Post"],
                  ["carrusel", "Carrusel"],
                  ["reel", "Reel"],
                  ["story", "Historia"],
                ].map(([val, label]) => (
                  <label
                    key={val}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      padding: "6px 12px",
                      borderRadius: 8,
                      cursor: "pointer",
                      fontSize: 13,
                      border: formatos.includes(val)
                        ? "2px solid var(--primary)"
                        : "1px solid var(--border)",
                      background: formatos.includes(val)
                        ? "var(--primary-light)"
                        : "var(--surface)",
                      color: formatos.includes(val) ? "var(--primary)" : "var(--text-secondary)",
                      fontWeight: formatos.includes(val) ? 600 : 400,
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={formatos.includes(val)}
                      onChange={() => toggleFormato(val)}
                      style={{ display: "none" }}
                    />
                    {label}
                  </label>
                ))}
              </div>
            </div>
            <button style={btn} onClick={generarPlan} disabled={loading === "plan"}>
              {loading === "plan" ? "Generando..." : "Generar Plan"}
            </button>
          </div>

          {planSaved && (
            <div className="msg-success" style={{ marginBottom: 16, borderRadius: 12 }}>
              <span style={{ flex: 1 }}>
                Plan guardado — el sistema lo usará para las próximas publicaciones.
              </span>
              <button className="msg-dismiss" onClick={() => setPlanSaved(false)}>
                ×
              </button>
            </div>
          )}

          {plan && (
            <div style={card}>
              {(plan.plan || []).some((p) =>
                (p.copy_sugerido || "").includes(
                  "[PENDIENTE — el cliente debe proveer testimonio real]"
                )
              ) && (
                <div
                  style={{
                    background: "var(--warning-bg)",
                    color: "var(--warning-text)",
                    borderRadius: 8,
                    padding: "10px 14px",
                    marginBottom: 16,
                    fontSize: 13,
                    lineHeight: 1.6,
                  }}
                >
                  ⚠️ Tu marca no tiene testimonios cargados. El plan marcó contenido testimonial
                  como pendiente. →{" "}
                  <Link
                    to="/onboarding"
                    style={{ color: "inherit", fontWeight: 700, textDecoration: "underline" }}
                  >
                    Completá tu perfil de marca
                  </Link>{" "}
                  para desbloquearlo.
                </div>
              )}
              {plan.resumen && (
                <p style={{ fontSize: 14, color: "var(--text)", marginBottom: 16 }}>
                  {plan.resumen}
                </p>
              )}
              {plan.impacto_esperado && (
                <div
                  style={{
                    background: "var(--surface-2)",
                    borderLeft: "3px solid var(--primary)",
                    borderRadius: 6,
                    padding: "10px 14px",
                    marginBottom: 16,
                    fontSize: 13,
                    color: "var(--text-secondary)",
                    fontStyle: "italic",
                  }}
                >
                  🎯 {plan.impacto_esperado}
                </div>
              )}
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 600 }}>
                  <thead>
                    <tr>
                      {["Día", "Red", "Formato", "Tema", "Copy", "Agente NEXO"].map((h) => (
                        <th
                          key={h}
                          style={{
                            textAlign: "left",
                            fontSize: 10,
                            color: "var(--text-muted)",
                            padding: "8px 12px",
                            borderBottom: "1px solid var(--border)",
                            fontWeight: 700,
                            textTransform: "uppercase",
                          }}
                        >
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(plan.plan || []).map((p, i) => (
                      <tr key={i}>
                        <td
                          style={{
                            padding: "10px 12px",
                            fontSize: 13,
                            borderBottom: "1px solid var(--border-subtle)",
                            fontWeight: 600,
                            color: "var(--text)",
                          }}
                        >
                          Día {p.dia}
                        </td>
                        <td
                          style={{
                            padding: "10px 12px",
                            fontSize: 13,
                            borderBottom: "1px solid var(--border-subtle)",
                            color: "var(--text-secondary)",
                          }}
                        >
                          {p.red_social}
                        </td>
                        <td
                          style={{
                            padding: "10px 12px",
                            fontSize: 13,
                            borderBottom: "1px solid var(--border-subtle)",
                            color: "var(--text-secondary)",
                          }}
                        >
                          {p.formato}
                        </td>
                        <td
                          style={{
                            padding: "10px 12px",
                            fontSize: 13,
                            borderBottom: "1px solid var(--border-subtle)",
                            color: "var(--text-secondary)",
                          }}
                        >
                          {p.tema}
                        </td>
                        <td
                          style={{
                            padding: "10px 12px",
                            fontSize: 12,
                            borderBottom: "1px solid var(--border-subtle)",
                            color: "var(--text-muted)",
                            maxWidth: 200,
                          }}
                        >
                          {p.copy_sugerido}
                        </td>
                        <td
                          style={{
                            padding: "10px 12px",
                            borderBottom: "1px solid var(--border-subtle)",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {p.agente && (
                            <span
                              style={{
                                background: "var(--surface-2)",
                                color: "var(--primary)",
                                padding: "2px 8px",
                                borderRadius: 6,
                                fontSize: 11,
                                fontWeight: 600,
                              }}
                            >
                              {p.agente}
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {planId && !planSaved && (
                <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
                  <button style={{ ...btn, background: "var(--success)" }} onClick={guardarPlan}>
                    Guardar plan
                  </button>
                  <span style={{ fontSize: 12, color: "var(--text-muted)", alignSelf: "center" }}>
                    Al guardar, este plan se usará como referencia para las publicaciones
                    automáticas.
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Sugerencias */}
      {tab === "sugerencias" && (
        <div>
          <div
            style={{
              ...card,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <h3 style={{ fontSize: 15, fontWeight: 700, color: "var(--text)" }}>
              Sugerencias Estratégicas
            </h3>
            <button style={btn} onClick={generarSugerencias} disabled={loading === "sug"}>
              {loading === "sug" ? "Generando..." : "Generar Sugerencias"}
            </button>
          </div>
          {sugerencias.length === 0 ? (
            <div style={card}>
              <EmptyState
                icon="💡"
                title="Sin sugerencias"
                description="Generá sugerencias estratégicas basadas en tu perfil de marca"
              />
            </div>
          ) : (
            sugerencias.map((s) => {
              const items = s.contenido?.sugerencias || [];
              return (
                <div key={s.id} style={card}>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 8 }}>
                    {s.created_at ? new Date(s.created_at).toLocaleDateString("es-AR") : ""}
                    {s.implementada && (
                      <span
                        style={{
                          marginLeft: 8,
                          background: "var(--success-bg)",
                          color: "var(--success-text)",
                          padding: "2px 8px",
                          borderRadius: 6,
                          fontSize: 10,
                          fontWeight: 600,
                        }}
                      >
                        Implementada
                      </span>
                    )}
                  </div>
                  {items.map((item, i) => (
                    <div
                      key={i}
                      style={{ padding: "8px 0", borderBottom: "1px solid var(--border-subtle)" }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <span style={{ fontSize: 14, fontWeight: 600, color: "var(--text)" }}>
                          {item.titulo}
                        </span>
                        {item.prioridad && (
                          <span style={prioBadge(item.prioridad)}>{item.prioridad}</span>
                        )}
                      </div>
                      <p style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 4 }}>
                        {item.descripcion}
                      </p>
                      {item.plazo && (
                        <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
                          Plazo: {item.plazo}
                        </span>
                      )}
                      {item.agente && (
                        <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>
                          Ejecuta: {item.agente}
                        </p>
                      )}
                    </div>
                  ))}
                  {!s.implementada && (
                    <button
                      style={{
                        ...btnSmall,
                        marginTop: 8,
                        borderColor: "var(--success)",
                        color: "var(--success-text)",
                      }}
                      onClick={() => implementar(s.id)}
                    >
                      Marcar implementada
                    </button>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}
    </Layout>
  );
}
