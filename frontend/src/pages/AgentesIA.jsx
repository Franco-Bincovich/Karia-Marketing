import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import Badge from "../components/ui/Badge";
import SkeletonLoader from "../components/ui/SkeletonLoader";

const card     = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 12, padding: 20 };
const btnSmall = { padding: "6px 14px", border: "1px solid var(--border)", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "var(--surface)", color: "var(--text-secondary)" };
const btnPrimary = { padding: "8px 18px", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 9, fontSize: 13, fontWeight: 600, cursor: "pointer" };
const inputStyle = { width: "100%", padding: "10px 12px", border: "1.5px solid var(--border)", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", background: "var(--surface)", color: "var(--text)" };

const estadoBadge = (estado) => {
  const map = {
    disponible:     { bg: "var(--success-bg)", c: "var(--success-text)", text: "Disponible" },
    bloqueado_v1:   { bg: "var(--danger-bg)",  c: "var(--danger-text)",  text: "Próximamente" },
    solo_premium:   { bg: "var(--purple-bg)",  c: "var(--purple-text)",  text: "Solo Premium" },
  };
  const s = map[estado] || map.disponible;
  return { style: { background: s.bg, color: s.c, padding: "3px 10px", borderRadius: 6, fontSize: 10, fontWeight: 600 }, text: s.text };
};

export default function AgentesIA() {
  const { get, patch, post } = useApi();
  const navigate = useNavigate();
  const [agentes, setAgentes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [configOpen, setConfigOpen] = useState(null);
  const [promptEdit, setPromptEdit] = useState("");
  const [executing, setExecuting] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    get(ENDPOINTS.AGENTES).then(r => setAgentes(r.data.data || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  async function toggleActivo(agente) {
    try {
      const { data } = await patch(ENDPOINTS.AGENTE_CONFIG(agente.nombre), { activo: !agente.activo });
      setAgentes(prev => prev.map(a => a.nombre === agente.nombre ? data : a));
    } catch {}
  }

  async function toggleModo(agente) {
    const nuevoModo = agente.modo === "copilot" ? "autopilot" : "copilot";
    try {
      const { data } = await patch(ENDPOINTS.AGENTE_CONFIG(agente.nombre), { modo: nuevoModo });
      setAgentes(prev => prev.map(a => a.nombre === agente.nombre ? data : a));
    } catch {}
  }

  function abrirConfig(agente) {
    setConfigOpen(agente);
    setPromptEdit(agente.system_prompt || "");
  }

  async function guardarPrompt() {
    if (!configOpen) return;
    setSaving(true);
    try {
      const { data } = await patch(ENDPOINTS.AGENTE_CONFIG(configOpen.nombre), { system_prompt: promptEdit });
      setAgentes(prev => prev.map(a => a.nombre === configOpen.nombre ? data : a));
      setConfigOpen(null);
    } catch {}
    finally { setSaving(false); }
  }

  function ejecutar(agente) {
    if (agente.nombre === "creativo")  { navigate("/creativo");  return; }
    if (agente.nombre === "comunidad") { navigate("/comunidad"); return; }
    if (agente.nombre === "estrategia"){ navigate("/estrategia");return; }
    ejecutarRemoto(agente);
  }

  async function ejecutarRemoto(agente) {
    setExecuting(agente.nombre);
    setResultado(null);
    try {
      const { data } = await post(ENDPOINTS.AGENTE_EJECUTAR(agente.nombre));
      setResultado(data);
    } catch (e) {
      setResultado({ agente: agente.nombre, resultado: e.response?.data?.message || "Error al ejecutar" });
    } finally { setExecuting(null); }
  }

  if (loading) return <Layout title="Agentes IA"><SkeletonLoader type="card" count={6} /></Layout>;

  const bloqueado = (a) => a.estado === "bloqueado_v1" || a.estado === "solo_premium";

  return (
    <Layout title="Agentes IA">
      {resultado && (
        <div style={{ ...card, marginBottom: 16, borderColor: "var(--primary)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <h3 style={{ fontSize: 14, fontWeight: 700, color: "var(--text)" }}>Resultado — {resultado.agente}</h3>
            <button onClick={() => setResultado(null)} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 16, color: "var(--text-muted)" }}>×</button>
          </div>
          <pre style={{ fontSize: 13, color: "var(--text-secondary)", whiteSpace: "pre-wrap", lineHeight: 1.6, maxHeight: 400, overflow: "auto" }}>
            {resultado.resultado}
          </pre>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 16 }}>
        {agentes.map(a => {
          const isBlocked = bloqueado(a);
          const badge = estadoBadge(a.estado);
          return (
            <div key={a.nombre} style={{ ...card, opacity: isBlocked ? 0.55 : 1, position: "relative" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
                <span style={{ width: 42, height: 42, borderRadius: 12, background: "var(--surface-2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>
                  {a.icon}
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text)" }}>{a.label}</div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{a.rol}</div>
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                {!isBlocked ? (
                  <button
                    onClick={() => toggleActivo(a)}
                    style={{
                      padding: "3px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
                      border: "none", cursor: "pointer",
                      background: a.activo ? "var(--success-bg)" : "var(--surface-2)",
                      color: a.activo ? "var(--success-text)" : "var(--text-muted)",
                    }}
                  >
                    {a.activo ? "Activo" : "Inactivo"}
                  </button>
                ) : (
                  <span style={badge.style}>{badge.text}</span>
                )}

                {!isBlocked && a.activo && (
                  <button
                    onClick={() => a.autopilot_disponible ? toggleModo(a) : null}
                    style={{
                      padding: "3px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
                      border: "none", cursor: a.autopilot_disponible ? "pointer" : "default",
                      background: a.modo === "autopilot" ? "var(--success-bg)" : "var(--purple-bg)",
                      color: a.modo === "autopilot" ? "var(--success-text)" : "var(--purple-text)",
                      opacity: a.autopilot_disponible ? 1 : 0.5,
                    }}
                    title={a.autopilot_disponible ? "Click para cambiar modo" : "Autopilot solo disponible en Premium"}
                  >
                    {a.modo === "autopilot" ? "Autopilot" : "Copilot"}
                  </button>
                )}
              </div>

              {!isBlocked && (
                <div style={{ display: "flex", gap: 6 }}>
                  <button style={btnSmall} onClick={() => abrirConfig(a)}>Configurar</button>
                  {a.activo && (
                    <button
                      style={{ ...btnSmall, borderColor: "var(--primary)", color: "var(--primary)" }}
                      onClick={() => ejecutar(a)}
                      disabled={executing === a.nombre}
                    >
                      {executing === a.nombre ? "Ejecutando..." : "Ejecutar"}
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Drawer de configuración */}
      {configOpen && (
        <>
          <div onClick={() => setConfigOpen(null)} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,.45)", zIndex: 200 }} />
          <div className="drawer">
            <div className="drawer-header">
              <h2 className="drawer-title">{configOpen.icon} {configOpen.label}</h2>
              <button onClick={() => setConfigOpen(null)} className="modal-close">×</button>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label className="field-label-sm" style={{ marginBottom: 6 }}>System Prompt</label>
              <textarea
                style={{ ...inputStyle, minHeight: 200, resize: "vertical", fontFamily: "monospace", fontSize: 13 }}
                value={promptEdit}
                onChange={e => setPromptEdit(e.target.value)}
              />
              <p style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
                Este prompt se usa como instrucción base del agente. Podés personalizarlo.
              </p>
            </div>

            <div style={{ display: "flex", gap: 8 }}>
              <button style={btnPrimary} onClick={guardarPrompt} disabled={saving}>
                {saving ? "Guardando..." : "Guardar"}
              </button>
              <button style={btnSmall} onClick={() => setPromptEdit(configOpen.system_prompt_default || "")}>
                Restaurar default
              </button>
            </div>
          </div>
        </>
      )}
    </Layout>
  );
}
