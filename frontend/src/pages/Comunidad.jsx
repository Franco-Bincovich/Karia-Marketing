import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box" };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const sentBadge = (s) => {
  const map = { positivo: ["#DCFCE7", "#15803D"], negativo: ["#FEE2E2", "#B91C1C"], neutro: ["#F1F5F9", "#475569"], mixto: ["#EDE9FE", "#6D28D9"] };
  const [bg, c] = map[s] || ["#F1F5F9", "#475569"];
  return { background: bg, color: c, padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 };
};

export default function Comunidad() {
  const { get, post } = useApi();
  const [pendientes, setPendientes] = useState([]);
  const [leads, setLeads] = useState([]);
  const [urgentes, setUrgentes] = useState([]);
  const [sentimiento, setSentimiento] = useState(null);
  const [respuestas, setRespuestas] = useState({});

  useEffect(() => {
    get(ENDPOINTS.COMUNIDAD_PENDIENTES).then(r => setPendientes(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.COMUNIDAD_LEADS).then(r => setLeads(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.COMUNIDAD_URGENTES).then(r => setUrgentes(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.COMUNIDAD_SENTIMIENTO).then(r => setSentimiento(r.data)).catch(() => {});
  }, []);

  async function responder(id) {
    const resp = respuestas[id];
    if (!resp) return;
    await post(ENDPOINTS.COMUNIDAD_RESPONDER(id), { respuesta: resp });
    setPendientes(prev => prev.filter(m => m.id !== id));
    setRespuestas(prev => { const n = { ...prev }; delete n[id]; return n; });
  }

  return (
    <Layout title="Comunidad">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        {sentimiento && (
          <div style={card}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Sentimiento de Marca</h3>
            <div style={{ display: "flex", gap: 16 }}>
              {Object.entries(sentimiento.porcentajes || {}).map(([k, v]) => (
                <div key={k} style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 22, fontWeight: 800 }}>{v}%</div>
                  <div style={{ fontSize: 11, color: "#94A3B8", textTransform: "capitalize" }}>{k}</div>
                </div>
              ))}
            </div>
            <div style={{ fontSize: 12, color: "#94A3B8", marginTop: 8 }}>{sentimiento.total} menciones analizadas</div>
          </div>
        )}
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Menciones Urgentes ({urgentes.length})</h3>
          {urgentes.length === 0 ? <p style={{ color: "#94A3B8", fontSize: 13 }}>Sin menciones urgentes</p> : urgentes.slice(0, 5).map(m => (
            <div key={m.id} style={{ padding: "8px 0", borderBottom: "1px solid #F1F5F9", fontSize: 13 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "#475569" }}>{m.contenido?.slice(0, 80)}...</span>
                <span style={sentBadge(m.sentimiento)}>{m.sentimiento}</span>
              </div>
              <div style={{ fontSize: 11, color: "#94A3B8" }}>{m.fuente} — alcance: {m.alcance_estimado}</div>
            </div>
          ))}
        </div>
      </div>
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Mensajes Pendientes ({pendientes.length})</h3>
        {pendientes.length === 0 ? <p style={{ color: "#94A3B8", fontSize: 13 }}>Bandeja vacía</p> : pendientes.map(m => (
          <div key={m.id} style={{ padding: 12, border: "1px solid #F1F5F9", borderRadius: 10, marginBottom: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <span style={{ fontWeight: 600, fontSize: 13 }}>{m.autor_username || "Anónimo"}</span>
                <span style={{ fontSize: 11, color: "#94A3B8" }}>{m.red_social} — {m.tipo}</span>
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                <span style={sentBadge(m.sentimiento)}>{m.sentimiento}</span>
                <span style={{ background: "#DBEAFE", color: "#1D4ED8", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{m.clasificacion}</span>
              </div>
            </div>
            <p style={{ fontSize: 13, color: "#475569", marginBottom: 8 }}>{m.contenido}</p>
            {m.respuesta_sugerida && <p style={{ fontSize: 12, color: "#F97316", fontStyle: "italic", marginBottom: 8 }}>Sugerida: {m.respuesta_sugerida}</p>}
            <div style={{ display: "flex", gap: 8 }}>
              <input style={{ ...input, flex: 1, marginBottom: 0 }} placeholder="Respuesta..." value={respuestas[m.id] || ""} onChange={e => setRespuestas({ ...respuestas, [m.id]: e.target.value })} />
              <button style={btn} onClick={() => responder(m.id)}>Enviar</button>
            </div>
          </div>
        ))}
      </div>
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Leads Detectados ({leads.length})</h3>
        {leads.map(l => (
          <div key={l.id} style={{ padding: "8px 0", borderBottom: "1px solid #F1F5F9", fontSize: 13, display: "flex", justifyContent: "space-between" }}>
            <span style={{ color: "#475569" }}>{l.autor_username} — {l.red_social}</span>
            <span style={{ background: "#DCFCE7", color: "#15803D", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>Lead</span>
          </div>
        ))}
      </div>
    </Layout>
  );
}
