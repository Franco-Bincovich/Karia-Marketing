import { useState } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 12 };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };

export default function Estrategia() {
  const { post } = useApi();
  const [objetivos, setObjetivos] = useState(["Aumentar engagement 20%", "Generar 50 leads", "Mejorar ROAS a 3x"]);
  const [nuevoObj, setNuevoObj] = useState("");
  const [competidor, setCompetidor] = useState("");
  const [analisis, setAnalisis] = useState(null);
  const [loading, setLoading] = useState(false);

  function agregarObjetivo() {
    if (!nuevoObj.trim()) return;
    setObjetivos(prev => [...prev, nuevoObj.trim()]);
    setNuevoObj("");
  }

  async function analizarCompetidor() {
    if (!competidor.trim()) return;
    setLoading(true);
    try {
      const { data } = await post(ENDPOINTS.SEO_COMPETIDOR, { dominio: competidor.trim() });
      setAnalisis(data);
    } catch {}
    finally { setLoading(false); }
  }

  return (
    <Layout title="Estrategia">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Plan del Mes</h3>
          {objetivos.map((o, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: "1px solid #F1F5F9" }}>
              <span style={{ width: 22, height: 22, borderRadius: 6, background: "#DCFCE7", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, color: "#15803D" }}>✓</span>
              <span style={{ fontSize: 13, color: "#475569" }}>{o}</span>
              <button onClick={() => setObjetivos(prev => prev.filter((_, j) => j !== i))} style={{ marginLeft: "auto", background: "none", border: "none", color: "#94A3B8", cursor: "pointer", fontSize: 14 }}>×</button>
            </div>
          ))}
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <input style={{ ...input, flex: 1, marginBottom: 0 }} placeholder="Nuevo objetivo..." value={nuevoObj} onChange={e => setNuevoObj(e.target.value)} />
            <button style={btn} onClick={agregarObjetivo}>Agregar</button>
          </div>
        </div>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Tendencias del Sector</h3>
          {["IA generativa en marketing", "Video corto como formato principal", "Social commerce en crecimiento", "Personalización con datos first-party"].map((t, i) => (
            <div key={i} style={{ padding: "8px 0", borderBottom: "1px solid #F1F5F9", fontSize: 13, color: "#475569", display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#F97316", flexShrink: 0 }} />
              {t}
            </div>
          ))}
        </div>
      </div>
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Análisis de Competidores</h3>
        <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
          <input style={{ ...input, flex: 1, marginBottom: 0 }} placeholder="Dominio del competidor (ej: competidor.com)" value={competidor} onChange={e => setCompetidor(e.target.value)} />
          <button style={btn} onClick={analizarCompetidor} disabled={loading}>{loading ? "Analizando..." : "Analizar"}</button>
        </div>
        {analisis && (
          <div>
            <div style={{ fontSize: 13, color: "#475569", marginBottom: 8 }}>
              <strong>Dominio:</strong> {analisis.dominio} — <strong>Keywords exclusivas:</strong> {analisis.keywords_exclusivas?.length || 0}
            </div>
            {(analisis.keywords_exclusivas || []).map((k, i) => (
              <div key={i} style={{ padding: "6px 0", borderBottom: "1px solid #F1F5F9", fontSize: 13, color: "#475569", display: "flex", justifyContent: "space-between" }}>
                <span>{k.keyword}</span>
                <span style={{ color: "#94A3B8" }}>Vol: {k.volumen_mensual} — Pos: {k.posicion}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
