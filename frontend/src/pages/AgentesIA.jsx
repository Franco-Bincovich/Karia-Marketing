import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20 };
const btnSmall = { padding: "6px 14px", border: "1px solid #E2E8F0", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "#fff", color: "#475569" };
const btnPrimary = { padding: "8px 18px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 13, fontWeight: 600, cursor: "pointer" };
const inputStyle = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box" };

const estadoBadge = (estado) => {
  const map = {
    disponible: { bg: "#DCFCE7", c: "#15803D", text: "Disponible" },
    bloqueado_v1: { bg: "#FEE2E2", c: "#B91C1C", text: "Próximamente" },
    solo_premium: { bg: "#EDE9FE", c: "#6D28D9", text: "Solo Premium" },
  };
  const s = map[estado] || map.disponible;
  return { style: { background: s.bg, color: s.c, padding: "3px 10px", borderRadius: 6, fontSize: 10, fontWeight: 600 }, text: s.text };
};

export default function AgentesIA() {
  const { get, patch, post } = useApi();
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

  async function ejecutar(agente) {
    setExecuting(agente.nombre);
    setResultado(null);
    try {
      const { data } = await post(ENDPOINTS.AGENTE_EJECUTAR(agente.nombre));
      setResultado(data);
    } catch (e) { setResultado({ agente: agente.nombre, resultado: e.response?.data?.message || "Error al ejecutar" }); }
    finally { setExecuting(null); }
  }

  if (loading) return <Layout title="Agentes IA"><p style={{ color: "#94A3B8" }}>Cargando...</p></Layout>;

  const bloqueado = (a) => a.estado === "bloqueado_v1" || a.estado === "solo_premium";

  return (
    <Layout title="Agentes IA">
      {/* Resultado de ejecución */}
      {resultado && (
        <div style={{ ...card, marginBottom: 16, borderColor: "#F97316" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <h3 style={{ fontSize: 14, fontWeight: 700 }}>Resultado — {resultado.agente}</h3>
            <button onClick={() => setResultado(null)} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 16, color: "#94A3B8" }}>x</button>
          </div>
          <pre style={{ fontSize: 13, color: "#475569", whiteSpace: "pre-wrap", lineHeight: 1.6, maxHeight: 400, overflow: "auto" }}>
            {resultado.resultado}
          </pre>
        </div>
      )}

      {/* Grid de agentes */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 16 }}>
        {agentes.map(a => {
          const isBlocked = bloqueado(a);
          const badge = estadoBadge(a.estado);
          return (
            <div key={a.nombre} style={{ ...card, opacity: isBlocked ? 0.55 : 1, position: "relative" }}>
              {/* Header */}
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
                <span style={{ width: 42, height: 42, borderRadius: 12, background: "#F1F5F9", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>
                  {a.icon}
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: "#0F172A" }}>{a.label}</div>
                  <div style={{ fontSize: 12, color: "#94A3B8" }}>{a.rol}</div>
                </div>
              </div>

              {/* Status row */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                {/* Active toggle */}
                {!isBlocked ? (
                  <button
                    onClick={() => toggleActivo(a)}
                    style={{
                      padding: "3px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
                      border: "none", cursor: "pointer",
                      background: a.activo ? "#DCFCE7" : "#F1F5F9",
                      color: a.activo ? "#15803D" : "#94A3B8",
                    }}
                  >
                    {a.activo ? "Activo" : "Inactivo"}
                  </button>
                ) : (
                  <span style={badge.style}>{badge.text}</span>
                )}

                {/* Mode toggle */}
                {!isBlocked && a.activo && (
                  <button
                    onClick={() => a.autopilot_disponible ? toggleModo(a) : null}
                    style={{
                      padding: "3px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
                      border: "none", cursor: a.autopilot_disponible ? "pointer" : "default",
                      background: a.modo === "autopilot" ? "#DCFCE7" : "#EDE9FE",
                      color: a.modo === "autopilot" ? "#15803D" : "#6D28D9",
                      opacity: a.autopilot_disponible ? 1 : 0.5,
                    }}
                    title={a.autopilot_disponible ? "Click para cambiar modo" : "Autopilot solo disponible en Premium"}
                  >
                    {a.modo === "autopilot" ? "Autopilot" : "Copilot"}
                  </button>
                )}
              </div>

              {/* Actions */}
              {!isBlocked && (
                <div style={{ display: "flex", gap: 6 }}>
                  <button style={btnSmall} onClick={() => abrirConfig(a)}>Configurar</button>
                  {a.activo && (
                    <button
                      style={{ ...btnSmall, borderColor: "#F97316", color: "#F97316" }}
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

      {/* Config drawer/modal */}
      {configOpen && (
        <>
          <div onClick={() => setConfigOpen(null)} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,.4)", zIndex: 200 }} />
          <div style={{
            position: "fixed", top: 0, right: 0, width: 480, height: "100vh",
            background: "#fff", zIndex: 201, padding: 24, overflowY: "auto",
            boxShadow: "-4px 0 20px rgba(0,0,0,.1)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <h2 style={{ fontSize: 18, fontWeight: 700 }}>
                {configOpen.icon} {configOpen.label}
              </h2>
              <button onClick={() => setConfigOpen(null)} style={{ background: "none", border: "none", fontSize: 20, cursor: "pointer", color: "#94A3B8" }}>x</button>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label style={{ fontSize: 12, color: "#94A3B8", display: "block", marginBottom: 6 }}>System Prompt</label>
              <textarea
                style={{ ...inputStyle, minHeight: 200, resize: "vertical", fontFamily: "monospace", fontSize: 13 }}
                value={promptEdit}
                onChange={e => setPromptEdit(e.target.value)}
              />
              <p style={{ fontSize: 11, color: "#94A3B8", marginTop: 4 }}>
                Este prompt se usa como instrucción base del agente. Podés personalizarlo.
              </p>
            </div>

            <div style={{ display: "flex", gap: 8 }}>
              <button style={btnPrimary} onClick={guardarPrompt} disabled={saving}>
                {saving ? "Guardando..." : "Guardar"}
              </button>
              <button
                style={btnSmall}
                onClick={() => setPromptEdit(configOpen.system_prompt_default || "")}
              >
                Restaurar default
              </button>
            </div>
          </div>
        </>
      )}
    </Layout>
  );
}
