import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const inputStyle = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box" };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSmall = { padding: "6px 14px", border: "1px solid #E2E8F0", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "#fff", color: "#475569" };
const th = { textAlign: "left", fontSize: 10, color: "#94A3B8", textTransform: "uppercase", padding: "8px 12px", borderBottom: "1px solid #E2E8F0" };
const td = { padding: "10px 12px", fontSize: 13, borderBottom: "1px solid #F1F5F9", color: "#475569" };

const sentBadge = (s) => {
  const map = { positivo: ["#DCFCE7", "#15803D"], negativo: ["#FEE2E2", "#B91C1C"], neutro: ["#F1F5F9", "#475569"], mixto: ["#EDE9FE", "#6D28D9"] };
  const [bg, c] = map[s] || ["#F1F5F9", "#475569"];
  return { background: bg, color: c, padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 };
};

const redIcon = { instagram: "📷", facebook: "📘", linkedin: "💼", tiktok: "🎵", twitter: "🐦" };

export default function Comunidad() {
  const { get, post } = useApi();
  const [tab, setTab] = useState("pendientes");
  const [pendientes, setPendientes] = useState([]);
  const [historial, setHistorial] = useState([]);
  const [leads, setLeads] = useState([]);
  const [respuestas, setRespuestas] = useState({});
  const [actionId, setActionId] = useState(null);

  useEffect(() => {
    get(ENDPOINTS.COMUNIDAD_PENDIENTES).then(r => setPendientes(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.COMUNIDAD_HISTORIAL).then(r => setHistorial(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.COMUNIDAD_LEADS).then(r => setLeads(r.data.data || [])).catch(() => {});
  }, []);

  async function responder(id) {
    const resp = respuestas[id];
    if (!resp) return;
    setActionId(id);
    try {
      await post(ENDPOINTS.COMUNIDAD_RESPONDER(id), { respuesta: resp });
      setPendientes(prev => prev.filter(m => m.id !== id));
      setRespuestas(prev => { const n = { ...prev }; delete n[id]; return n; });
      get(ENDPOINTS.COMUNIDAD_HISTORIAL).then(r => setHistorial(r.data.data || []));
    } catch {}
    finally { setActionId(null); }
  }

  function usarSugerencia(id, sugerencia) {
    setRespuestas(prev => ({ ...prev, [id]: sugerencia }));
  }

  const tabs = [
    { key: "pendientes", label: `Pendientes (${pendientes.length})` },
    { key: "historial", label: `Historial (${historial.length})` },
    { key: "leads", label: `Leads (${leads.length})` },
  ];

  return (
    <Layout title="Comunidad">
      {/* Tabs */}
      <div style={{ display: "flex", gap: 4, marginBottom: 16 }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)} style={{
            padding: "8px 18px", borderRadius: 8, fontSize: 13, fontWeight: 600,
            border: tab === t.key ? "2px solid #F97316" : "1px solid #E2E8F0",
            background: tab === t.key ? "#FFF7ED" : "#fff",
            color: tab === t.key ? "#F97316" : "#475569", cursor: "pointer",
          }}>{t.label}</button>
        ))}
      </div>

      {/* Pendientes */}
      {tab === "pendientes" && (
        <div>
          {pendientes.length === 0 ? (
            <div style={card}><p style={{ color: "#94A3B8", fontSize: 13 }}>Bandeja vacía</p></div>
          ) : pendientes.map(m => (
            <div key={m.id} style={card}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <span style={{ fontSize: 16 }}>{redIcon[m.red_social] || "🌐"}</span>
                  <span style={{ fontWeight: 600, fontSize: 13 }}>{m.autor_username || "Anónimo"}</span>
                  <span style={{ fontSize: 11, color: "#94A3B8" }}>{m.tipo}</span>
                </div>
                <div style={{ display: "flex", gap: 6 }}>
                  <span style={sentBadge(m.sentimiento)}>{m.sentimiento}</span>
                  <span style={{ background: "#DBEAFE", color: "#1D4ED8", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{m.clasificacion}</span>
                </div>
              </div>
              <p style={{ fontSize: 14, color: "#0F172A", marginBottom: 10, lineHeight: 1.5 }}>{m.contenido}</p>
              {m.respuesta_sugerida && (
                <div style={{ background: "#FFF7ED", borderRadius: 8, padding: "8px 12px", marginBottom: 10, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <p style={{ fontSize: 13, color: "#F97316", fontStyle: "italic", flex: 1 }}>IA sugiere: {m.respuesta_sugerida}</p>
                  <button style={{ ...btnSmall, borderColor: "#F97316", color: "#F97316" }} onClick={() => usarSugerencia(m.id, m.respuesta_sugerida)}>Usar</button>
                </div>
              )}
              <div style={{ display: "flex", gap: 8 }}>
                <input style={{ ...inputStyle, flex: 1, marginBottom: 0 }} placeholder="Escribí tu respuesta..." value={respuestas[m.id] || ""} onChange={e => setRespuestas({ ...respuestas, [m.id]: e.target.value })} />
                <button style={btn} onClick={() => responder(m.id)} disabled={actionId === m.id}>
                  {actionId === m.id ? "..." : "Enviar"}
                </button>
                <button style={btnSmall} onClick={() => { setPendientes(prev => prev.filter(x => x.id !== m.id)); }}>Ignorar</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Historial */}
      {tab === "historial" && (
        <div style={{ ...card, overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 600 }}>
            <thead>
              <tr>
                <th style={th}>Red</th>
                <th style={th}>Usuario</th>
                <th style={th}>Mensaje</th>
                <th style={th}>Respuesta</th>
                <th style={th}>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {historial.length === 0 && (
                <tr><td colSpan={5} style={{ ...td, textAlign: "center", color: "#94A3B8" }}>Sin historial</td></tr>
              )}
              {historial.map(m => (
                <tr key={m.id}>
                  <td style={td}>{redIcon[m.red_social] || "🌐"} {m.red_social}</td>
                  <td style={{ ...td, fontWeight: 500 }}>{m.autor_username || "—"}</td>
                  <td style={{ ...td, maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{m.contenido}</td>
                  <td style={{ ...td, maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", color: "#15803D" }}>{m.respuesta || "—"}</td>
                  <td style={{ ...td, fontSize: 11, color: "#94A3B8" }}>{m.respondido_at ? new Date(m.respondido_at).toLocaleDateString("es-AR") : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Leads */}
      {tab === "leads" && (
        <div style={card}>
          {leads.length === 0 ? <p style={{ color: "#94A3B8", fontSize: 13 }}>Sin leads detectados</p> : leads.map(l => (
            <div key={l.id} style={{ padding: "10px 0", borderBottom: "1px solid #F1F5F9", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <span style={{ fontSize: 13, fontWeight: 600 }}>{l.autor_username || "Anónimo"}</span>
                <span style={{ fontSize: 11, color: "#94A3B8", marginLeft: 8 }}>{l.red_social}</span>
                <p style={{ fontSize: 12, color: "#475569", marginTop: 2 }}>{l.contenido?.slice(0, 100)}</p>
              </div>
              <span style={{ background: "#DCFCE7", color: "#15803D", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>Lead</span>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
