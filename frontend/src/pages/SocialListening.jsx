import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSmall = { padding: "6px 14px", border: "1px solid #E2E8F0", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "#fff", color: "#475569" };
const selectStyle = { padding: "8px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 13, outline: "none", appearance: "auto", background: "#fff" };

const sentBadge = (s) => {
  const map = { positivo: ["#DCFCE7", "#15803D"], negativo: ["#FEE2E2", "#B91C1C"], neutro: ["#F1F5F9", "#475569"], mixto: ["#EDE9FE", "#6D28D9"] };
  const [bg, c] = map[s] || ["#F1F5F9", "#475569"];
  return { background: bg, color: c, padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 };
};

const platIcon = { instagram: "📷", facebook: "📘", twitter: "🐦", linkedin: "💼", web: "🌐", foro: "💬" };

function ScoreBar({ score }) {
  const color = score < 30 ? "#EF4444" : score < 60 ? "#F59E0B" : "#10B981";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <div style={{ width: 50, height: 6, background: "#F1F5F9", borderRadius: 3, overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${score}%`, background: color, borderRadius: 3 }} />
      </div>
      <span style={{ fontSize: 11, color: "#94A3B8" }}>{score}</span>
    </div>
  );
}

export default function SocialListening() {
  const { get, post, patch } = useApi();
  const [resumen, setResumen] = useState(null);
  const [menciones, setMenciones] = useState([]);
  const [alertas, setAlertas] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [filtroSent, setFiltroSent] = useState("");
  const [filtroPlat, setFiltroPlat] = useState("");

  function loadData() {
    get(ENDPOINTS.LISTENING_RESUMEN).then(r => setResumen(r.data)).catch(() => {});
    const params = new URLSearchParams();
    if (filtroSent) params.set("sentimiento", filtroSent);
    if (filtroPlat) params.set("plataforma", filtroPlat);
    const url = `${ENDPOINTS.LISTENING_MENCIONES}${params.toString() ? "?" + params.toString() : ""}`;
    get(url).then(r => setMenciones(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.LISTENING_ALERTAS).then(r => setAlertas(r.data.data || [])).catch(() => {});
  }

  useEffect(() => { loadData(); }, [filtroSent, filtroPlat]);

  async function escanear() {
    setScanning(true);
    try {
      await post(ENDPOINTS.LISTENING_ESCANEAR);
      loadData();
    } catch {}
    finally { setScanning(false); }
  }

  async function procesar(id) {
    try {
      await patch(ENDPOINTS.LISTENING_PROCESAR(id));
      setMenciones(prev => prev.map(m => m.id === id ? { ...m, procesado: true } : m));
    } catch {}
  }

  const pct = resumen?.porcentajes || {};

  return (
    <Layout title="Social Listening">
      {/* Alertas */}
      {alertas.filter(a => !a.leida).length > 0 && (
        <div style={{ ...card, borderColor: "#EF4444", background: "#FEF2F2" }}>
          <h3 style={{ fontSize: 14, fontWeight: 700, color: "#B91C1C", marginBottom: 8 }}>
            Alertas activas ({alertas.filter(a => !a.leida).length})
          </h3>
          {alertas.filter(a => !a.leida).slice(0, 3).map(a => (
            <div key={a.id} style={{ padding: "6px 0", fontSize: 13, color: "#B91C1C", borderBottom: "1px solid #FEE2E2" }}>
              {a.mensaje}
            </div>
          ))}
        </div>
      )}

      {/* Métricas */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 16 }}>
        <div style={card}>
          <div style={{ fontSize: 11, color: "#94A3B8", marginBottom: 4 }}>Total menciones</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#0F172A" }}>{resumen?.total || 0}</div>
        </div>
        <div style={card}>
          <div style={{ fontSize: 11, color: "#94A3B8", marginBottom: 4 }}>Positivas</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#15803D" }}>{pct.positivo || 0}%</div>
          <div style={{ fontSize: 11, color: "#94A3B8" }}>{resumen?.positivos || 0} menciones</div>
        </div>
        <div style={card}>
          <div style={{ fontSize: 11, color: "#94A3B8", marginBottom: 4 }}>Negativas</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#B91C1C" }}>{pct.negativo || 0}%</div>
          <div style={{ fontSize: 11, color: "#94A3B8" }}>{resumen?.negativos || 0} menciones</div>
        </div>
        <div style={card}>
          <div style={{ fontSize: 11, color: "#94A3B8", marginBottom: 4 }}>Neutras</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#475569" }}>{pct.neutro || 0}%</div>
          <div style={{ fontSize: 11, color: "#94A3B8" }}>{resumen?.neutros || 0} menciones</div>
        </div>
      </div>

      {/* Sentimiento visual */}
      {resumen && resumen.total > 0 && (
        <div style={{ ...card, padding: 16 }}>
          <div style={{ display: "flex", height: 24, borderRadius: 6, overflow: "hidden" }}>
            {pct.positivo > 0 && <div style={{ width: `${pct.positivo}%`, background: "#10B981" }} title={`Positivo ${pct.positivo}%`} />}
            {pct.neutro > 0 && <div style={{ width: `${pct.neutro}%`, background: "#94A3B8" }} title={`Neutro ${pct.neutro}%`} />}
            {pct.mixto > 0 && <div style={{ width: `${pct.mixto}%`, background: "#8B5CF6" }} title={`Mixto ${pct.mixto}%`} />}
            {pct.negativo > 0 && <div style={{ width: `${pct.negativo}%`, background: "#EF4444" }} title={`Negativo ${pct.negativo}%`} />}
          </div>
          <div style={{ display: "flex", gap: 16, marginTop: 8, fontSize: 11, color: "#94A3B8" }}>
            <span style={{ display: "flex", alignItems: "center", gap: 4 }}><span style={{ width: 8, height: 8, borderRadius: 2, background: "#10B981" }} /> Positivo</span>
            <span style={{ display: "flex", alignItems: "center", gap: 4 }}><span style={{ width: 8, height: 8, borderRadius: 2, background: "#94A3B8" }} /> Neutro</span>
            <span style={{ display: "flex", alignItems: "center", gap: 4 }}><span style={{ width: 8, height: 8, borderRadius: 2, background: "#EF4444" }} /> Negativo</span>
          </div>
        </div>
      )}

      {/* Filtros + Escanear */}
      <div style={{ ...card, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <select style={selectStyle} value={filtroSent} onChange={e => setFiltroSent(e.target.value)}>
            <option value="">Todos los sentimientos</option>
            <option value="positivo">Positivo</option>
            <option value="neutro">Neutro</option>
            <option value="negativo">Negativo</option>
          </select>
          <select style={selectStyle} value={filtroPlat} onChange={e => setFiltroPlat(e.target.value)}>
            <option value="">Todas las plataformas</option>
            <option value="instagram">Instagram</option>
            <option value="facebook">Facebook</option>
            <option value="twitter">Twitter</option>
            <option value="linkedin">LinkedIn</option>
            <option value="web">Web</option>
          </select>
        </div>
        <button style={btn} onClick={escanear} disabled={scanning}>
          {scanning ? "Escaneando..." : "Escanear ahora"}
        </button>
      </div>

      {/* Menciones */}
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Menciones ({menciones.length})</h3>
        {menciones.length === 0 ? (
          <p style={{ color: "#94A3B8", fontSize: 13 }}>Sin menciones. Ejecutá un escaneo.</p>
        ) : menciones.map(m => (
          <div key={m.id} style={{ padding: "10px 0", borderBottom: "1px solid #F1F5F9", opacity: m.procesado ? 0.5 : 1 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <span style={{ fontSize: 16 }}>{platIcon[m.fuente] || "🌐"}</span>
                <span style={{ fontSize: 13, fontWeight: 600 }}>{m.autor || "Desconocido"}</span>
                <span style={{ fontSize: 11, color: "#94A3B8" }}>{m.fuente}</span>
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <ScoreBar score={m.score_sentimiento || 50} />
                <span style={sentBadge(m.sentimiento)}>{m.sentimiento}</span>
              </div>
            </div>
            <p style={{ fontSize: 13, color: "#475569", marginBottom: 6, lineHeight: 1.5 }}>
              {m.contenido}
            </p>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              {m.url && <a href={m.url} target="_blank" rel="noreferrer" style={{ fontSize: 11, color: "#3B82F6" }}>Ver original</a>}
              {!m.procesado && (
                <button style={btnSmall} onClick={() => procesar(m.id)}>Marcar procesada</button>
              )}
              {m.urgente && !m.procesado && (
                <span style={{ fontSize: 10, color: "#B91C1C", fontWeight: 600 }}>URGENTE</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
