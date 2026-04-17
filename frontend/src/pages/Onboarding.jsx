import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";
import SkeletonLoader from "../components/ui/SkeletonLoader";

const card         = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 12, padding: 24, marginBottom: 16 };
const inputStyle   = { width: "100%", padding: "12px 14px", border: "1.5px solid var(--border)", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 8, background: "var(--surface)", color: "var(--text)" };
const textareaStyle= { ...inputStyle, minHeight: 80, resize: "vertical" };
const selectStyle  = { ...inputStyle, appearance: "auto" };
const btnPrimary   = { padding: "10px 24px", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSecondary = { ...btnPrimary, background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)" };
const btnSuccess   = { ...btnPrimary, background: "var(--success)" };
const btnIA        = { padding: "6px 14px", background: "var(--purple-bg)", color: "var(--purple-text)", border: "1px solid var(--purple-bg)", borderRadius: 8, fontSize: 12, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 4 };
const btnAutocompletar = { ...btnIA, background: "var(--blue-bg)", color: "var(--blue-text)", borderColor: "var(--blue-bg)" };

const SECCIONES = {
  "Marca":     { color: "var(--primary)", icon: "🏢" },
  "Audiencia": { color: "var(--blue)",    icon: "🎯" },
  "Contenido": { color: "var(--purple)",  icon: "✍️" },
  "Identidad": { color: "#EC4899",        icon: "🎨" },
  "Operación": { color: "var(--success)", icon: "⚙️" },
};

export default function Onboarding() {
  const { get, post } = useApi();
  const { setCompletitud } = useAuth();
  const navigate = useNavigate();
  const [estado, setEstado] = useState(null);
  const [preguntas, setPreguntas] = useState([]);
  const [respuestas, setRespuestas] = useState({});
  const [pasoActivo, setPasoActivo] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [suggesting, setSuggesting] = useState(false);
  const [autocompleting, setAutocompleting] = useState(false);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const autoSaveTimer = useRef(null);

  const isPremium = estado?.ia_enabled || false;

  useEffect(() => {
    get(ENDPOINTS.ONBOARDING_ESTADO).then(r => {
      setEstado(r.data);
      setPreguntas(r.data.preguntas || []);
      setRespuestas(r.data.respuestas || {});
      setCompletitud(r.data.completitud || 0);
      const resp = r.data.respuestas || {};
      const first = (r.data.preguntas || []).findIndex(p => !resp[String(p.id)]);
      setPasoActivo(first >= 0 ? first : 0);
    }).catch(() => {
      post(ENDPOINTS.ONBOARDING_INICIAR).then(r => setEstado(r.data)).catch(() => {});
    }).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!preguntas.length || loading) return;
    if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
    autoSaveTimer.current = setTimeout(() => guardarParcial(), 2000);
    return () => { if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current); };
  }, [respuestas]);

  async function guardarParcial() {
    try {
      const { data } = await post(ENDPOINTS.ONBOARDING_GUARDAR, { respuestas });
      setCompletitud(data.completitud || 0);
      setEstado(prev => ({ ...prev, ...data }));
    } catch {}
  }

  async function guardarYSiguiente() {
    setSaving(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.ONBOARDING_GUARDAR, { respuestas });
      setCompletitud(data.completitud || 0);
      setEstado(prev => ({ ...prev, ...data }));
      if (pasoActivo < preguntas.length - 1) setPasoActivo(pasoActivo + 1);
    } catch (err) { setError(err.response?.data?.message || "Error al guardar"); }
    finally { setSaving(false); }
  }

  async function completarOnboarding() {
    setCompleting(true); setError("");
    try {
      await post(ENDPOINTS.ONBOARDING_GUARDAR, { respuestas });
      const { data } = await post(ENDPOINTS.ONBOARDING_COMPLETAR);
      setCompletitud(100);
      setEstado(prev => ({ ...prev, ...data }));
      setMsg("Onboarding completado. Tu perfil de marca está listo.");
    } catch (err) { setError(err.response?.data?.message || "Error al completar"); }
    finally { setCompleting(false); }
  }

  async function pedirSugerencia() {
    const preguntaActual = preguntas[pasoActivo];
    if (!preguntaActual) return;
    setSuggesting(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.ONBOARDING_SUGERIR, { pregunta_id: preguntaActual.id });
      if (data.sugerencia) {
        setRespuestas(prev => ({ ...prev, [String(preguntaActual.id)]: data.sugerencia }));
      }
    } catch (err) { setError(err.response?.data?.message || "Error al sugerir"); }
    finally { setSuggesting(false); }
  }

  async function autocompletarPerfil() {
    const nombre = respuestas["1"];
    if (!nombre) { setError("Primero completá el nombre de tu marca (pregunta 1)"); return; }
    setAutocompleting(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.ONBOARDING_AUTOCOMPLETAR, { nombre_marca: nombre });
      setRespuestas(data.respuestas || {});
      setEstado(prev => ({ ...prev, ...data }));
      setCompletitud(data.completitud || 0);
      setMsg("Perfil autocompletado con información pública. Revisá y ajustá las respuestas.");
    } catch (err) { setError(err.response?.data?.message || "Error al autocompletar"); }
    finally { setAutocompleting(false); }
  }

  function setRespuesta(id, valor) {
    setRespuestas(prev => ({ ...prev, [String(id)]: valor }));
  }

  if (loading) return <Layout title="Configuración"><SkeletonLoader type="card" count={2} /></Layout>;

  const preguntaActual = preguntas[pasoActivo];
  const comp = estado?.completitud || 0;
  const plan = estado?.plan || "Basic";
  const total = preguntas.length;
  const respondidas = estado?.respondidas || 0;
  const isCompleted = estado?.completado;

  const secciones = [];
  const seen = new Set();
  preguntas.forEach((p, i) => {
    if (!seen.has(p.seccion)) { seen.add(p.seccion); secciones.push({ nombre: p.seccion, inicio: i }); }
  });

  return (
    <Layout title="Configuración de Marca">
      {/* Progress */}
      <div style={card}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <div>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 2, color: "var(--text)" }}>Perfil de Marca</h3>
            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
              Plan {plan} — {respondidas}/{total} preguntas
              {isPremium && <span style={{ color: "var(--purple-text)", marginLeft: 8 }}>con asistencia IA</span>}
            </span>
          </div>
          <span style={{ fontSize: 24, fontWeight: 800, color: comp >= 100 ? "var(--success-text)" : "var(--primary)" }}>{comp}%</span>
        </div>
        <div className="progress-track">
          <div className={`progress-fill ${comp >= 100 ? "success" : ""}`} style={{ width: `${comp}%` }} />
        </div>
        {isPremium && !isCompleted && respondidas < 5 && (
          <div style={{ marginTop: 12 }}>
            <button style={btnAutocompletar} onClick={autocompletarPerfil} disabled={autocompleting}>
              {autocompleting ? "Investigando marca..." : "🔍 Autocompletar con IA (info pública de tu marca)"}
            </button>
          </div>
        )}
      </div>

      {/* Messages */}
      {msg && (
        <div style={{ ...card, borderColor: "var(--success)", background: "var(--success-bg)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: "var(--success-text)", marginBottom: 4 }}>{msg}</div>
              <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>Todos los agentes de IA ya tienen el contexto de tu marca.</span>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button style={btnPrimary} onClick={() => navigate("/dashboard")}>Ir al Dashboard</button>
              <button style={btnSecondary} onClick={() => navigate("/marca/perfil")}>Ver Perfil</button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="msg-error" style={{ marginBottom: 16, borderRadius: 12 }}>
          <span style={{ flex: 1 }}>{error}</span>
          <button className="msg-dismiss" onClick={() => setError("")}>×</button>
        </div>
      )}

      {/* Section tabs */}
      <div style={{ display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap" }}>
        {secciones.map(sec => {
          const info = SECCIONES[sec.nombre] || { color: "var(--text-muted)", icon: "📋" };
          const isActive = preguntaActual?.seccion === sec.nombre;
          return (
            <button key={sec.nombre} onClick={() => setPasoActivo(sec.inicio)} style={{
              padding: "6px 14px", borderRadius: 8, fontSize: 12, fontWeight: 600,
              border: isActive ? `2px solid ${info.color}` : "1px solid var(--border)",
              background: isActive ? `${info.color}18` : "var(--surface)",
              color: isActive ? info.color : "var(--text-secondary)",
              cursor: "pointer", display: "flex", alignItems: "center", gap: 4,
              transition: "all var(--t-fast)",
            }}>
              <span>{info.icon}</span> {sec.nombre}
            </button>
          );
        })}
      </div>

      {/* Question card */}
      {preguntaActual && !isCompleted && (
        <div style={card}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ background: "var(--primary)", color: "#fff", fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 6 }}>
                {pasoActivo + 1}/{total}
              </span>
              <span style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                {preguntaActual.seccion}
              </span>
              {preguntaActual.obligatoria && (
                <span style={{ fontSize: 10, color: "var(--warning-text)", background: "var(--warning-bg)", padding: "1px 6px", borderRadius: 4, fontWeight: 600 }}>Obligatoria</span>
              )}
            </div>
            {isPremium && preguntaActual.tipo !== "select" && (
              <button style={btnIA} onClick={pedirSugerencia} disabled={suggesting}>
                {suggesting ? "Pensando..." : "✦ Ayuda IA"}
              </button>
            )}
          </div>

          <h3 style={{ fontSize: 16, fontWeight: 600, color: "var(--text)", marginBottom: 16, lineHeight: 1.4 }}>
            {preguntaActual.pregunta}
          </h3>

          {preguntaActual.tipo === "select" ? (
            <select style={selectStyle} value={respuestas[String(preguntaActual.id)] || ""} onChange={e => setRespuesta(preguntaActual.id, e.target.value)}>
              <option value="">Seleccioná una opción</option>
              {(preguntaActual.opciones || []).map(op => <option key={op} value={op}>{op}</option>)}
            </select>
          ) : (
            <textarea
              style={textareaStyle}
              value={respuestas[String(preguntaActual.id)] || ""}
              onChange={e => setRespuesta(preguntaActual.id, e.target.value)}
              placeholder="Escribí tu respuesta..."
            />
          )}

          <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
            {pasoActivo > 0 && (
              <button style={btnSecondary} onClick={() => setPasoActivo(pasoActivo - 1)}>← Anterior</button>
            )}
            {pasoActivo < total - 1 ? (
              <button style={btnPrimary} onClick={guardarYSiguiente} disabled={saving}>
                {saving ? "Guardando..." : "Siguiente →"}
              </button>
            ) : (
              <button style={btnSuccess} onClick={completarOnboarding} disabled={completing}>
                {completing ? "Finalizando..." : "Completar Onboarding"}
              </button>
            )}
          </div>

          <p style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 12 }}>
            Tu progreso se guarda automáticamente.
          </p>
        </div>
      )}

      {/* Question list */}
      {!isCompleted && (
        <div style={card}>
          <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>Preguntas</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {preguntas.map((p, i) => {
              const answered = !!respuestas[String(p.id)];
              const active = i === pasoActivo;
              return (
                <button key={p.id} onClick={() => setPasoActivo(i)} style={{
                  display: "flex", alignItems: "center", gap: 8,
                  padding: "8px 10px", borderRadius: 8, textAlign: "left",
                  border: active ? "1.5px solid var(--primary)" : "1px solid transparent",
                  background: active ? "var(--primary-light)" : "transparent",
                  cursor: "pointer", fontSize: 13,
                  color: answered ? "var(--success-text)" : active ? "var(--primary)" : "var(--text-secondary)",
                  fontWeight: active ? 600 : 400,
                  transition: "all var(--t-fast)",
                }}>
                  <span style={{ fontSize: 14, width: 18, textAlign: "center" }}>
                    {answered ? "✓" : `${p.id}`}
                  </span>
                  <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {p.pregunta}
                  </span>
                  {p.obligatoria && !answered && (
                    <span style={{ fontSize: 9, color: "var(--warning-text)", flexShrink: 0 }}>*</span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {isCompleted && !msg && (
        <div style={{ ...card, borderColor: "var(--success)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <h3 style={{ fontSize: 15, fontWeight: 700, color: "var(--success-text)", marginBottom: 4 }}>✓ Onboarding completo</h3>
              <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>Tu perfil de marca está configurado.</span>
            </div>
            <button style={btnPrimary} onClick={() => navigate("/marca/perfil")}>Ver Perfil de Marca</button>
          </div>
        </div>
      )}
    </Layout>
  );
}
