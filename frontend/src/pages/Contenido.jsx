import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box" };
const select = { ...input, appearance: "auto" };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSuccess = { ...btn, background: "#10B981" };
const btnDanger = { ...btn, background: "#EF4444" };
const btnBlue = { ...btn, background: "#3B82F6" };
const btnSmall = { padding: "6px 14px", border: "1px solid #E2E8F0", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "#fff", color: "#475569" };

export default function Contenido() {
  const { get, post } = useApi();
  const [form, setForm] = useState({ red_social: "instagram", formato: "post", objetivo: "", tono: "profesional", tema: "" });
  const [resultado, setResultado] = useState(null);
  const [lista, setLista] = useState([]);
  const [loading, setLoading] = useState(false);
  const [rechazoMotivo, setRechazoMotivo] = useState("");
  const [error, setError] = useState("");

  // Publicar/programar state
  const [publishing, setPublishing] = useState(null);
  const [scheduling, setScheduling] = useState(null);
  const [scheduleDate, setScheduleDate] = useState("");
  const [pubMsg, setPubMsg] = useState("");

  useEffect(() => { get(ENDPOINTS.CONTENIDO).then(r => setLista(r.data.data || [])).catch(() => {}); }, []);

  async function generar() {
    if (!form.tema) return;
    setLoading(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.CONTENIDO_GENERAR, form);
      setResultado(data);
    } catch (e) { setError(e.response?.data?.message || "Error generando"); }
    finally { setLoading(false); }
  }

  async function aprobar(variante) {
    if (!resultado?.id) return;
    await post(ENDPOINTS.CONTENIDO_APROBAR(resultado.id), { variante });
    setResultado(null);
    get(ENDPOINTS.CONTENIDO).then(r => setLista(r.data.data || []));
  }

  async function rechazar() {
    if (!resultado?.id || !rechazoMotivo) return;
    await post(ENDPOINTS.CONTENIDO_RECHAZAR(resultado.id), { motivo: rechazoMotivo });
    setRechazoMotivo(""); setResultado(null);
  }

  async function publicarAhora(contenido) {
    setPublishing(contenido.id);
    setPubMsg("");
    try {
      await post(ENDPOINTS.SOCIAL_PUBLICAR, {
        red_social: contenido.red_social || "instagram",
        copy_text: contenido.copy_aprobado || contenido.copy_a || "",
        contenido_id: contenido.id,
        imagen_url: contenido.imagen_url || null,
      });
      setPubMsg("Publicado correctamente");
    } catch (err) {
      setPubMsg(err.response?.data?.message || "Error al publicar");
    } finally {
      setPublishing(null);
    }
  }

  async function programarPost(contenido) {
    if (!scheduleDate) { setPubMsg("Seleccioná fecha y hora"); return; }
    setScheduling(contenido.id);
    setPubMsg("");
    try {
      await post(ENDPOINTS.SOCIAL_PROGRAMAR, {
        red_social: contenido.red_social || "instagram",
        copy_text: contenido.copy_aprobado || contenido.copy_a || "",
        contenido_id: contenido.id,
        imagen_url: contenido.imagen_url || null,
        programado_para: new Date(scheduleDate).toISOString(),
      });
      setPubMsg("Programado correctamente");
      setScheduleDate("");
    } catch (err) {
      setPubMsg(err.response?.data?.message || "Error al programar");
    } finally {
      setScheduling(null);
    }
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <Layout title="Generar Contenido">
      {/* Configuración */}
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Configuración</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 12 }}>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Red Social</label><select style={select} value={form.red_social} onChange={set("red_social")}><option>instagram</option><option>facebook</option><option>linkedin</option><option>tiktok</option><option>twitter</option></select></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Formato</label><select style={select} value={form.formato} onChange={set("formato")}><option>post</option><option>reel</option><option>story</option><option>carousel</option></select></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Tono</label><select style={select} value={form.tono} onChange={set("tono")}><option>profesional</option><option>cercano</option><option>inspirador</option><option>humoristico</option></select></div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Objetivo</label><input style={input} value={form.objetivo} onChange={set("objetivo")} placeholder="Ej: aumentar awareness" /></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Tema</label><input style={input} value={form.tema} onChange={set("tema")} placeholder="Ej: lanzamiento producto" /></div>
        </div>
        <button style={btn} onClick={generar} disabled={loading}>{loading ? "Generando..." : "Generar Variantes A/B"}</button>
        {error && <p style={{ color: "#EF4444", fontSize: 13, marginTop: 8 }}>{error}</p>}
      </div>

      {/* Variantes A/B */}
      {resultado && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
          {["a", "b"].map(v => (
            <div key={v} style={{ ...card, borderColor: "#F97316", borderWidth: 2 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
                <span style={{ fontSize: 13, fontWeight: 700, color: "#F97316" }}>Variante {v.toUpperCase()}</span>
                <button style={btnSuccess} onClick={() => aprobar(v)}>Aprobar {v.toUpperCase()}</button>
              </div>
              <p style={{ fontSize: 13, color: "#475569", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{resultado[`copy_${v}`] || "—"}</p>
              {resultado[`hashtags_${v}`] && <p style={{ fontSize: 12, color: "#94A3B8", marginTop: 8 }}>{resultado[`hashtags_${v}`]}</p>}
            </div>
          ))}
          <div style={{ ...card, gridColumn: "1/-1" }}>
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <input style={{ ...input, flex: 1, marginBottom: 0 }} placeholder="Motivo del rechazo..." value={rechazoMotivo} onChange={e => setRechazoMotivo(e.target.value)} />
              <button style={btnDanger} onClick={rechazar}>Rechazar</button>
            </div>
          </div>
        </div>
      )}

      {/* Feedback de publicación */}
      {pubMsg && (
        <div style={{
          ...card,
          borderColor: pubMsg.includes("Error") ? "#EF4444" : "#10B981",
          background: pubMsg.includes("Error") ? "#FEF2F2" : "#F0FDF4",
          padding: 12, fontSize: 13,
          color: pubMsg.includes("Error") ? "#B91C1C" : "#15803D",
        }}>
          {pubMsg}
          <button onClick={() => setPubMsg("")} style={{ marginLeft: 12, background: "none", border: "none", cursor: "pointer", color: "inherit", fontWeight: 600 }}>x</button>
        </div>
      )}

      {/* Contenido Generado con acciones de publicación */}
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Contenido Generado ({lista.length})</h3>
        {lista.length === 0 && <p style={{ color: "#94A3B8", fontSize: 13 }}>No hay contenido generado</p>}
        {lista.map(c => (
          <div key={c.id} style={{ padding: "12px 0", borderBottom: "1px solid #F1F5F9" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <span style={{ fontSize: 13, color: "#475569" }}>{c.tema || c.red_social} — {c.formato}</span>
              <span style={{
                background: c.estado === "aprobado" ? "#DCFCE7" : "#FEF3C7",
                color: c.estado === "aprobado" ? "#15803D" : "#B45309",
                padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600,
              }}>{c.estado}</span>
            </div>
            {c.estado === "aprobado" && (
              <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 8 }}>
                <button
                  style={{ ...btnSmall, borderColor: "#10B981", color: "#15803D" }}
                  onClick={() => publicarAhora(c)}
                  disabled={publishing === c.id}
                >
                  {publishing === c.id ? "Publicando..." : "Publicar ahora"}
                </button>
                <input
                  type="datetime-local"
                  style={{ ...input, width: "auto", marginBottom: 0, padding: "5px 8px", fontSize: 12 }}
                  value={scheduleDate}
                  onChange={e => setScheduleDate(e.target.value)}
                />
                <button
                  style={{ ...btnSmall, borderColor: "#3B82F6", color: "#1D4ED8" }}
                  onClick={() => programarPost(c)}
                  disabled={scheduling === c.id}
                >
                  {scheduling === c.id ? "Programando..." : "Programar"}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </Layout>
  );
}
