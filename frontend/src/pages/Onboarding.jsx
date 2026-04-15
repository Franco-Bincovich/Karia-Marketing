import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 24, marginBottom: 16 };
const inputStyle = { width: "100%", padding: "12px 14px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 8 };
const textareaStyle = { ...inputStyle, minHeight: 80, resize: "vertical" };
const selectStyle = { ...inputStyle, appearance: "auto", background: "#fff" };
const btnPrimary = { padding: "10px 24px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSecondary = { ...btnPrimary, background: "#fff", color: "#0F172A", border: "1px solid #E2E8F0" };
const btnSuccess = { ...btnPrimary, background: "#10B981" };
const btnIA = { padding: "6px 14px", background: "#EDE9FE", color: "#6D28D9", border: "1px solid #C4B5FD", borderRadius: 8, fontSize: 12, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 4 };
const btnAutocompletar = { ...btnIA, background: "#DBEAFE", color: "#1D4ED8", borderColor: "#93C5FD" };

const SECCIONES = {
  "Marca": { color: "#F97316", icon: "🏢" },
  "Audiencia": { color: "#3B82F6", icon: "🎯" },
  "Contenido": { color: "#8B5CF6", icon: "✍️" },
  "Identidad": { color: "#EC4899", icon: "🎨" },
  "Operación": { color: "#10B981", icon: "⚙️" },
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

  // Auto-save debounced
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

  if (loading) return <Layout title="Onboarding"><p style={{ color: "#94A3B8" }}>Cargando...</p></Layout>;

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
    <Layout title="Onboarding">
      {/* Progress bar */}
      <div style={card}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <div>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 2 }}>Configuración de Marca</h3>
            <span style={{ fontSize: 12, color: "#94A3B8" }}>
              Plan {plan} — {respondidas}/{total} preguntas
              {isPremium && <span style={{ color: "#6D28D9", marginLeft: 8 }}>con asistencia IA</span>}
            </span>
          </div>
          <span style={{ fontSize: 24, fontWeight: 800, color: comp >= 100 ? "#10B981" : "#F97316" }}>{comp}%</span>
        </div>
        <div style={{ height: 8, background: "#F1F5F9", borderRadius: 4, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${comp}%`, background: comp >= 100 ? "#10B981" : "#F97316", borderRadius: 4, transition: "width 300ms" }} />
        </div>
        {/* Autocompletar button for Premium */}
        {isPremium && !isCompleted && respondidas < 5 && (
          <div style={{ marginTop: 12 }}>
            <button style={btnAutocompletar} onClick={autocompletarPerfil} disabled={autocompleting}>
              {autocompleting ? "Investigando marca..." : "Autocompletar con IA (busca info pública de tu marca)"}
            </button>
          </div>
        )}
      </div>

      {/* Messages */}
      {msg && (
        <div style={{ ...card, borderColor: "#10B981", background: "#F0FDF4" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: "#15803D", marginBottom: 4 }}>{msg}</div>
              <span style={{ fontSize: 12, color: "#475569" }}>Todos los agentes de IA ya tienen el contexto de tu marca.</span>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button style={btnPrimary} onClick={() => navigate("/dashboard")}>Ir al Dashboard</button>
              <button style={btnSecondary} onClick={() => navigate("/marca/perfil")}>Ver Perfil</button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div style={{ ...card, borderColor: "#EF4444", background: "#FEF2F2", padding: 12 }}>
          <span style={{ color: "#B91C1C", fontSize: 13 }}>{error}</span>
          <button onClick={() => setError("")} style={{ marginLeft: 8, background: "none", border: "none", cursor: "pointer", color: "#B91C1C", fontWeight: 600 }}>x</button>
        </div>
      )}

      {/* Section tabs */}
      <div style={{ display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap" }}>
        {secciones.map(sec => {
          const info = SECCIONES[sec.nombre] || { color: "#94A3B8", icon: "📋" };
          const isActive = preguntaActual?.seccion === sec.nombre;
          return (
            <button key={sec.nombre} onClick={() => setPasoActivo(sec.inicio)} style={{
              padding: "6px 14px", borderRadius: 8, fontSize: 12, fontWeight: 600,
              border: isActive ? `2px solid ${info.color}` : "1px solid #E2E8F0",
              background: isActive ? `${info.color}10` : "#fff",
              color: isActive ? info.color : "#475569",
              cursor: "pointer", display: "flex", alignItems: "center", gap: 4,
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
              <span style={{ background: "#F97316", color: "#fff", fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 6 }}>
                {pasoActivo + 1}/{total}
              </span>
              <span style={{ fontSize: 11, color: "#94A3B8", textTransform: "uppercase", fontWeight: 600 }}>
                {preguntaActual.seccion}
              </span>
              {preguntaActual.obligatoria && (
                <span style={{ fontSize: 10, color: "#B45309", background: "#FEF3C7", padding: "1px 6px", borderRadius: 4, fontWeight: 600 }}>Obligatoria</span>
              )}
            </div>
            {/* IA Suggest button — Premium only */}
            {isPremium && preguntaActual.tipo !== "select" && (
              <button style={btnIA} onClick={pedirSugerencia} disabled={suggesting}>
                {suggesting ? "Pensando..." : "Ayuda IA"}
              </button>
            )}
          </div>

          <h3 style={{ fontSize: 16, fontWeight: 600, color: "#0F172A", marginBottom: 16, lineHeight: 1.4 }}>
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
              <button style={btnSecondary} onClick={() => setPasoActivo(pasoActivo - 1)}>Anterior</button>
            )}
            {pasoActivo < total - 1 ? (
              <button style={btnPrimary} onClick={guardarYSiguiente} disabled={saving}>
                {saving ? "Guardando..." : "Siguiente"}
              </button>
            ) : (
              <button style={btnSuccess} onClick={completarOnboarding} disabled={completing}>
                {completing ? "Finalizando..." : "Completar Onboarding"}
              </button>
            )}
          </div>

          <p style={{ fontSize: 11, color: "#94A3B8", marginTop: 12 }}>
            Tu progreso se guarda automáticamente. Podés salir y retomar en cualquier momento.
          </p>
        </div>
      )}

      {/* Question list */}
      {!isCompleted && (
        <div style={card}>
          <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12 }}>Preguntas</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {preguntas.map((p, i) => {
              const answered = !!respuestas[String(p.id)];
              const active = i === pasoActivo;
              return (
                <button key={p.id} onClick={() => setPasoActivo(i)} style={{
                  display: "flex", alignItems: "center", gap: 8,
                  padding: "8px 10px", borderRadius: 8, textAlign: "left",
                  border: active ? "1.5px solid #F97316" : "1px solid transparent",
                  background: active ? "#FFF7ED" : "transparent",
                  cursor: "pointer", fontSize: 13,
                  color: answered ? "#15803D" : active ? "#F97316" : "#475569",
                  fontWeight: active ? 600 : 400,
                }}>
                  <span style={{ fontSize: 14, width: 18, textAlign: "center" }}>
                    {answered ? "✓" : `${p.id}`}
                  </span>
                  <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {p.pregunta}
                  </span>
                  {p.obligatoria && !answered && (
                    <span style={{ fontSize: 9, color: "#B45309", flexShrink: 0 }}>*</span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Completed state */}
      {isCompleted && !msg && (
        <div style={{ ...card, borderColor: "#10B981" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <h3 style={{ fontSize: 15, fontWeight: 700, color: "#15803D", marginBottom: 4 }}>Onboarding completo</h3>
              <span style={{ fontSize: 13, color: "#475569" }}>Tu perfil de marca está configurado.</span>
            </div>
            <button style={btnPrimary} onClick={() => navigate("/marca/perfil")}>Ver Perfil de Marca</button>
          </div>
        </div>
      )}
    </Layout>
  );
}
