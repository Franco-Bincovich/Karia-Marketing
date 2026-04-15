import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box" };
const select = { ...input, appearance: "auto" };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSuccess = { ...btn, background: "#10B981" };
const btnDanger = { ...btn, background: "#EF4444" };
const btnSmall = { padding: "6px 14px", border: "1px solid #E2E8F0", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "#fff", color: "#475569" };
const btnAutopilot = { ...btn, background: "#6D28D9" };

const estadoBadge = (e) => {
  const map = {
    aprobado: { bg: "#DCFCE7", c: "#15803D" }, publicado: { bg: "#DBEAFE", c: "#1D4ED8" },
    pendiente_aprobacion: { bg: "#FEF3C7", c: "#B45309" }, rechazado: { bg: "#FEE2E2", c: "#B91C1C" },
    borrador: { bg: "#F1F5F9", c: "#475569" },
  };
  const s = map[e] || map.borrador;
  return { background: s.bg, color: s.c, padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 };
};

export default function Contenido() {
  const { get, post } = useApi();
  const { user } = useAuth();
  const [form, setForm] = useState({ red_social: "instagram", formato: "post", objetivo: "", tono: "profesional", tema: "" });
  const [resultado, setResultado] = useState(null);
  const [lista, setLista] = useState([]);
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [rechazoMotivo, setRechazoMotivo] = useState("");
  const [error, setError] = useState("");
  const [pubMsg, setPubMsg] = useState("");
  const [actionId, setActionId] = useState(null);
  const [scheduleDate, setScheduleDate] = useState("");
  const [filtro, setFiltro] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [savingKey, setSavingKey] = useState(false);

  const isSuperadmin = user?.rol === "superadmin";
  const canAutopilot = usage?.autopilot_enabled || isSuperadmin;

  useEffect(() => {
    loadData();
    get(ENDPOINTS.CONTENIDO_USAGE).then(r => setUsage(r.data)).catch(() => {});
  }, []);

  function loadData() {
    const url = filtro ? `${ENDPOINTS.CONTENIDO}?estado=${filtro}` : ENDPOINTS.CONTENIDO;
    get(url).then(r => setLista(r.data.data || [])).catch(() => {});
  }

  useEffect(() => { loadData(); }, [filtro]);

  async function generar(modo = "copilot") {
    if (!form.tema) return;
    setLoading(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.CONTENIDO_GENERAR, { ...form, modo });
      setResultado(data);
      get(ENDPOINTS.CONTENIDO_USAGE).then(r => setUsage(r.data)).catch(() => {});
    } catch (e) { setError(e.response?.data?.message || "Error generando"); }
    finally { setLoading(false); }
  }

  async function aprobar(variante) {
    if (!resultado?.id) return;
    await post(ENDPOINTS.CONTENIDO_APROBAR(resultado.id), { variante });
    setResultado(null);
    loadData();
  }

  async function publicarDirecto(variante) {
    if (!resultado?.id) return;
    setActionId("pub_directo");
    try {
      await post(ENDPOINTS.CONTENIDO_PUBLICAR_DIRECTO(resultado.id), { variante });
      setPubMsg("Generado y publicado correctamente");
      setResultado(null);
      loadData();
    } catch (e) { setError(e.response?.data?.message || "Error al publicar"); }
    finally { setActionId(null); }
  }

  async function rechazar() {
    if (!resultado?.id || !rechazoMotivo) return;
    try {
      const { data } = await post(ENDPOINTS.CONTENIDO_RECHAZAR(resultado.id), { comentario: rechazoMotivo });
      setResultado(data);
      setRechazoMotivo("");
    } catch {}
  }

  async function publicarAhora(c) {
    setActionId(c.id + "_pub");
    setPubMsg("");
    const copyText = c[`copy_${c.variante_seleccionada || "a"}`] || c.copy_a || "";
    try {
      await post(ENDPOINTS.SOCIAL_PUBLICAR, {
        red_social: c.red_social, copy_text: copyText, contenido_id: c.id,
      });
      setPubMsg("Publicado correctamente");
      loadData();
    } catch (e) { setPubMsg(e.response?.data?.message || "Error al publicar"); }
    finally { setActionId(null); }
  }

  async function programar(c) {
    if (!scheduleDate) { setPubMsg("Seleccioná fecha y hora"); return; }
    setActionId(c.id + "_sched");
    const copyText = c[`copy_${c.variante_seleccionada || "a"}`] || c.copy_a || "";
    try {
      await post(ENDPOINTS.SOCIAL_PROGRAMAR, {
        red_social: c.red_social, copy_text: copyText, contenido_id: c.id,
        programado_para: new Date(scheduleDate).toISOString(),
      });
      setPubMsg("Programado correctamente");
      setScheduleDate("");
    } catch (e) { setPubMsg(e.response?.data?.message || "Error"); }
    finally { setActionId(null); }
  }

  async function generarImagen(c) {
    setActionId(c.id + "_img");
    try {
      await post(ENDPOINTS.IMAGENES_PARA_CONTENIDO(c.id), { tamano: "1024x1024", estilo: "vivid" });
      setPubMsg("Imagen generada para el contenido");
      loadData();
    } catch (e) { setPubMsg(e.response?.data?.message || "Error al generar imagen"); }
    finally { setActionId(null); }
  }

  async function guardarApiKey() {
    if (!apiKey) return;
    setSavingKey(true);
    try {
      await post(ENDPOINTS.CONTENIDO_API_KEY, { api_key: apiKey });
      setApiKey("");
      get(ENDPOINTS.CONTENIDO_USAGE).then(r => setUsage(r.data)).catch(() => {});
      setPubMsg("API key guardada");
    } catch (e) { setError(e.response?.data?.message || "Error"); }
    finally { setSavingKey(false); }
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <Layout title="Generar Contenido">
      {/* Usage bar for Basic */}
      {usage && usage.limite && (
        <div style={{ ...card, padding: 14, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 13, color: "#475569" }}>
            Posts este mes: <strong>{usage.posts_mes}/{usage.limite}</strong>
          </span>
          <div style={{ width: 120, height: 6, background: "#F1F5F9", borderRadius: 3, overflow: "hidden" }}>
            <div style={{ height: "100%", width: `${Math.min(100, usage.posts_mes / usage.limite * 100)}%`, background: usage.posts_mes >= usage.limite ? "#EF4444" : "#F97316", borderRadius: 3 }} />
          </div>
        </div>
      )}

      {/* Config */}
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Configuración</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 12 }}>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Red Social</label><select style={select} value={form.red_social} onChange={set("red_social")}><option>instagram</option><option>facebook</option><option>linkedin</option><option>tiktok</option><option>twitter</option></select></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Formato</label><select style={select} value={form.formato} onChange={set("formato")}><option>post</option><option>reel</option><option>story</option><option>carrusel</option></select></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Tono</label><select style={select} value={form.tono} onChange={set("tono")}><option>profesional</option><option>cercano</option><option>inspirador</option><option>humoristico</option></select></div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Objetivo</label><input style={input} value={form.objetivo} onChange={set("objetivo")} placeholder="Ej: aumentar awareness" /></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Tema</label><input style={input} value={form.tema} onChange={set("tema")} placeholder="Ej: lanzamiento producto" /></div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button style={btn} onClick={() => generar("copilot")} disabled={loading}>
            {loading ? "Generando..." : "Generar 3 Variantes"}
          </button>
          {canAutopilot && (
            <button style={btnAutopilot} onClick={() => generar("autopilot")} disabled={loading}>
              Generar y aprobar (Autopilot)
            </button>
          )}
        </div>
        {error && <p style={{ color: "#EF4444", fontSize: 13, marginTop: 8 }}>{error}</p>}
      </div>

      {/* 3 Variantes */}
      {resultado && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 16 }}>
            {["a", "b", "c"].map(v => (
              <div key={v} style={{ ...card, borderColor: "#F97316", borderWidth: 2, marginBottom: 0 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                  <span style={{ fontSize: 13, fontWeight: 700, color: "#F97316" }}>Variante {v.toUpperCase()}</span>
                </div>
                <p style={{ fontSize: 13, color: "#475569", lineHeight: 1.6, whiteSpace: "pre-wrap", marginBottom: 8 }}>
                  {resultado[`copy_${v}`] || "—"}
                </p>
                {resultado[`hashtags_${v}`] && <p style={{ fontSize: 11, color: "#94A3B8", marginBottom: 4 }}>{resultado[`hashtags_${v}`]}</p>}
                {resultado[`cta_${v}`] && <p style={{ fontSize: 12, color: "#6D28D9", fontWeight: 600 }}>CTA: {resultado[`cta_${v}`]}</p>}
                <div style={{ display: "flex", gap: 6, marginTop: 10, flexWrap: "wrap" }}>
                  <button style={{ ...btnSmall, borderColor: "#10B981", color: "#15803D" }} onClick={() => aprobar(v)}>Aprobar</button>
                  {canAutopilot && (
                    <button
                      style={{ ...btnSmall, borderColor: "#6D28D9", color: "#6D28D9" }}
                      onClick={() => publicarDirecto(v)}
                      disabled={actionId === "pub_directo"}
                    >Publicar ya</button>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div style={card}>
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <input style={{ ...input, flex: 1, marginBottom: 0 }} placeholder="Motivo del rechazo..." value={rechazoMotivo} onChange={e => setRechazoMotivo(e.target.value)} />
              <button style={btnDanger} onClick={rechazar}>Rechazar y regenerar</button>
            </div>
          </div>
        </>
      )}

      {/* Messages */}
      {pubMsg && (
        <div style={{ ...card, borderColor: pubMsg.includes("Error") ? "#EF4444" : "#10B981", background: pubMsg.includes("Error") ? "#FEF2F2" : "#F0FDF4", padding: 12, fontSize: 13, color: pubMsg.includes("Error") ? "#B91C1C" : "#15803D" }}>
          {pubMsg}
          <button onClick={() => setPubMsg("")} style={{ marginLeft: 12, background: "none", border: "none", cursor: "pointer", color: "inherit", fontWeight: 600 }}>x</button>
        </div>
      )}

      {/* Filter + list */}
      <div style={card}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700 }}>Contenido ({lista.length})</h3>
          <select style={{ ...select, width: "auto", padding: "6px 10px", fontSize: 12 }} value={filtro} onChange={e => setFiltro(e.target.value)}>
            <option value="">Todos</option>
            <option value="pendiente_aprobacion">Pendientes</option>
            <option value="aprobado">Aprobados</option>
            <option value="publicado">Publicados</option>
            <option value="rechazado">Rechazados</option>
          </select>
        </div>
        {lista.length === 0 && <p style={{ color: "#94A3B8", fontSize: 13 }}>No hay contenido</p>}
        {lista.map(c => (
          <div key={c.id} style={{ padding: "12px 0", borderBottom: "1px solid #F1F5F9" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
              <span style={{ fontSize: 13, color: "#475569", fontWeight: 500 }}>{c.tema || c.red_social} — {c.formato}</span>
              <span style={estadoBadge(c.estado)}>{c.estado.replace("_", " ")}</span>
            </div>
            <p style={{ fontSize: 12, color: "#94A3B8", marginBottom: 6, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 500 }}>
              {c[`copy_${c.variante_seleccionada || "a"}`] || c.copy_a || ""}
            </p>
            {c.imagen_url && (
              <div style={{ marginBottom: 6 }}>
                <img src={c.imagen_url} alt="" style={{ height: 48, borderRadius: 6, objectFit: "cover" }} onError={e => { e.target.style.display = "none"; }} />
              </div>
            )}
            {c.estado === "aprobado" && (
              <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap" }}>
                <button style={{ ...btnSmall, borderColor: "#10B981", color: "#15803D" }} onClick={() => publicarAhora(c)} disabled={actionId === c.id + "_pub"}>
                  {actionId === c.id + "_pub" ? "..." : "Publicar ahora"}
                </button>
                <input type="datetime-local" style={{ ...input, width: "auto", marginBottom: 0, padding: "4px 8px", fontSize: 11 }} value={scheduleDate} onChange={e => setScheduleDate(e.target.value)} />
                <button style={{ ...btnSmall, borderColor: "#3B82F6", color: "#1D4ED8" }} onClick={() => programar(c)} disabled={actionId === c.id + "_sched"}>
                  {actionId === c.id + "_sched" ? "..." : "Programar"}
                </button>
                {!c.imagen_url && (
                  <button
                    style={{ ...btnSmall, borderColor: "#EC4899", color: "#BE185D" }}
                    onClick={() => generarImagen(c)}
                    disabled={actionId === c.id + "_img"}
                  >
                    {actionId === c.id + "_img" ? "Generando..." : "Generar imagen"}
                  </button>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Premium: API key propia */}
      {usage?.plan === "Premium" && (
        <div style={card}>
          <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>API Key propia de Anthropic</h3>
          <p style={{ fontSize: 12, color: "#94A3B8", marginBottom: 10 }}>
            {usage.has_custom_key ? "Ya tenés una API key configurada." : "Conectá tu propia key para usar tu cuota de Claude directamente."}
          </p>
          <div style={{ display: "flex", gap: 8 }}>
            <input style={{ ...input, flex: 1, marginBottom: 0 }} type="password" placeholder="sk-ant-..." value={apiKey} onChange={e => setApiKey(e.target.value)} />
            <button style={btnSmall} onClick={guardarApiKey} disabled={savingKey}>{savingKey ? "..." : "Guardar"}</button>
          </div>
        </div>
      )}
    </Layout>
  );
}
