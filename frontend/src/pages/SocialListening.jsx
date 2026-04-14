import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 12 };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const sentBadge = (s) => {
  const map = { positivo: ["#DCFCE7", "#15803D"], negativo: ["#FEE2E2", "#B91C1C"], neutro: ["#F1F5F9", "#475569"], mixto: ["#EDE9FE", "#6D28D9"] };
  const [bg, c] = map[s] || ["#F1F5F9", "#475569"];
  return { background: bg, color: c, padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 };
};

export default function SocialListening() {
  const { get, post, patch } = useApi();
  const [menciones, setMenciones] = useState([]);
  const [urgentes, setUrgentes] = useState([]);
  const [sentimiento, setSentimiento] = useState(null);
  const [config, setConfig] = useState({});
  const [filtro, setFiltro] = useState("todos");
  const [monitoring, setMonitoring] = useState(false);

  useEffect(() => {
    get(ENDPOINTS.COMUNIDAD_MENCIONES).then(r => setMenciones(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.COMUNIDAD_URGENTES).then(r => setUrgentes(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.COMUNIDAD_SENTIMIENTO).then(r => setSentimiento(r.data)).catch(() => {});
    get(ENDPOINTS.COMUNIDAD_LISTENING).then(r => setConfig(r.data || {})).catch(() => {});
  }, []);

  async function monitorear() {
    setMonitoring(true);
    try {
      await post(ENDPOINTS.COMUNIDAD_MONITOREAR, {});
      const [m, u, s] = await Promise.all([
        get(ENDPOINTS.COMUNIDAD_MENCIONES), get(ENDPOINTS.COMUNIDAD_URGENTES), get(ENDPOINTS.COMUNIDAD_SENTIMIENTO),
      ]);
      setMenciones(m.data.data || []); setUrgentes(u.data.data || []); setSentimiento(s.data);
    } catch {}
    finally { setMonitoring(false); }
  }

  const filtradas = filtro === "todos" ? menciones : menciones.filter(m => m.tipo === filtro);

  return (
    <Layout title="Social Listening">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 16 }}>
        {sentimiento && Object.entries(sentimiento.porcentajes || {}).map(([k, v]) => (
          <div key={k} style={card}>
            <div style={{ fontSize: 12, color: "#94A3B8", textTransform: "capitalize", marginBottom: 4 }}>{k}</div>
            <div style={{ fontSize: 26, fontWeight: 800 }}>{v}%</div>
          </div>
        ))}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16, marginBottom: 16 }}>
        <div style={card}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <h3 style={{ fontSize: 15, fontWeight: 700 }}>Menciones ({filtradas.length})</h3>
            <div style={{ display: "flex", gap: 8 }}>
              {["todos", "marca", "competidor", "sector"].map(f => (
                <button key={f} onClick={() => setFiltro(f)} style={{
                  padding: "4px 12px", borderRadius: 6, fontSize: 12, fontWeight: filtro === f ? 600 : 400,
                  border: filtro === f ? "1.5px solid #F97316" : "1px solid #E2E8F0", cursor: "pointer",
                  background: filtro === f ? "#FFF7ED" : "#fff", color: filtro === f ? "#F97316" : "#475569",
                }}>{f}</button>
              ))}
            </div>
          </div>
          {filtradas.slice(0, 10).map(m => (
            <div key={m.id} style={{ padding: "10px 0", borderBottom: "1px solid #F1F5F9" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontSize: 13, color: "#475569" }}>{m.contenido?.slice(0, 100)}{m.contenido?.length > 100 ? "..." : ""}</span>
                <span style={sentBadge(m.sentimiento)}>{m.sentimiento}</span>
              </div>
              <div style={{ fontSize: 11, color: "#94A3B8", display: "flex", gap: 12 }}>
                <span>{m.fuente}</span><span>Alcance: {m.alcance_estimado}</span>
                <span style={{ background: "#DBEAFE", color: "#1D4ED8", padding: "1px 6px", borderRadius: 4, fontSize: 10 }}>{m.tipo}</span>
              </div>
            </div>
          ))}
        </div>
        <div>
          <div style={{ ...card, borderColor: urgentes.length > 0 ? "#EF4444" : "#E2E8F0" }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: urgentes.length > 0 ? "#B91C1C" : "#0F172A" }}>
              Urgentes ({urgentes.length})
            </h3>
            {urgentes.length === 0 ? <p style={{ color: "#94A3B8", fontSize: 13 }}>Sin alertas</p> : urgentes.slice(0, 5).map(u => (
              <div key={u.id} style={{ padding: "8px 0", borderBottom: "1px solid #FEE2E2", fontSize: 12, color: "#B91C1C" }}>
                {u.contenido?.slice(0, 60)}...
                <div style={{ fontSize: 11, color: "#94A3B8" }}>Alcance: {u.alcance_estimado}</div>
              </div>
            ))}
          </div>
          <div style={card}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Monitoreo</h3>
            <button style={{ ...btn, width: "100%", marginBottom: 12 }} onClick={monitorear} disabled={monitoring}>
              {monitoring ? "Monitoreando..." : "Ejecutar Monitoreo"}
            </button>
            <div style={{ fontSize: 12, color: "#94A3B8" }}>
              Términos marca: {(config.terminos_marca || []).join(", ") || "Sin configurar"}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
