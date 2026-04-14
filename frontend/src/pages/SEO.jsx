import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box" };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const th = { textAlign: "left", fontSize: 10, color: "#94A3B8", textTransform: "uppercase", padding: "8px 12px", borderBottom: "1px solid #E2E8F0" };
const td = { padding: "10px 12px", fontSize: 13, borderBottom: "1px solid #F1F5F9", color: "#475569" };
const severidadBadge = (s) => {
  const map = { critico: ["#FEE2E2", "#B91C1C"], alto: ["#FEF3C7", "#B45309"], medio: ["#DBEAFE", "#1D4ED8"], bajo: ["#DCFCE7", "#15803D"] };
  const [bg, c] = map[s] || ["#F1F5F9", "#475569"];
  return { background: bg, color: c, padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 };
};

export default function SEO() {
  const { get, post } = useApi();
  const [keywords, setKeywords] = useState([]);
  const [auditoria, setAuditoria] = useState([]);
  const [briefs, setBriefs] = useState([]);
  const [query, setQuery] = useState("");
  const [url, setUrl] = useState("");
  const [briefKw, setBriefKw] = useState("");
  const [loading, setLoading] = useState("");

  useEffect(() => {
    get(ENDPOINTS.SEO_KEYWORDS).then(r => setKeywords(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.SEO_AUDITORIA).then(r => setAuditoria(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.SEO_BRIEFS).then(r => setBriefs(r.data.data || [])).catch(() => {});
  }, []);

  async function investigar() {
    if (!query) return; setLoading("kw");
    await post(ENDPOINTS.SEO_INVESTIGAR, { query });
    get(ENDPOINTS.SEO_KEYWORDS).then(r => setKeywords(r.data.data || []));
    setQuery(""); setLoading("");
  }

  async function auditar() {
    if (!url) return; setLoading("audit");
    await post(ENDPOINTS.SEO_AUDITORIA, { url });
    get(ENDPOINTS.SEO_AUDITORIA).then(r => setAuditoria(r.data.data || []));
    setUrl(""); setLoading("");
  }

  async function generarBrief() {
    if (!briefKw) return; setLoading("brief");
    await post(ENDPOINTS.SEO_BRIEFS, { keyword_principal: briefKw });
    get(ENDPOINTS.SEO_BRIEFS).then(r => setBriefs(r.data.data || []));
    setBriefKw(""); setLoading("");
  }

  return (
    <Layout title="SEO">
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Investigar Keywords</h3>
        <div style={{ display: "flex", gap: 12 }}>
          <input style={{ ...input, flex: 1 }} placeholder="Buscar keywords..." value={query} onChange={e => setQuery(e.target.value)} />
          <button style={btn} onClick={investigar} disabled={loading === "kw"}>{loading === "kw" ? "..." : "Investigar"}</button>
        </div>
      </div>
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Keywords Monitoreadas ({keywords.length})</h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead><tr><th style={th}>Keyword</th><th style={th}>Volumen</th><th style={th}>Dificultad</th><th style={th}>Posición</th><th style={th}>Intención</th><th style={th}>Estado</th></tr></thead>
          <tbody>{keywords.slice(0, 20).map(k => (
            <tr key={k.id}><td style={td}>{k.keyword}</td><td style={td}>{k.volumen_mensual}</td><td style={td}>{k.dificultad}</td>
              <td style={td}>{k.posicion_actual || "—"}{k.posicion_anterior && k.posicion_actual && k.posicion_actual < k.posicion_anterior ? <span style={{ color: "#10B981", marginLeft: 4 }}>↑</span> : k.posicion_anterior && k.posicion_actual > k.posicion_anterior ? <span style={{ color: "#EF4444", marginLeft: 4 }}>↓</span> : null}</td>
              <td style={td}>{k.intencion}</td><td style={td}><span style={{ background: "#DBEAFE", color: "#1D4ED8", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{k.estado}</span></td></tr>
          ))}</tbody>
        </table>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Auditoría Técnica</h3>
          <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
            <input style={{ ...input, flex: 1 }} placeholder="URL a auditar" value={url} onChange={e => setUrl(e.target.value)} />
            <button style={btn} onClick={auditar} disabled={loading === "audit"}>Auditar</button>
          </div>
          {auditoria.slice(0, 5).map(a => (
            <div key={a.id} style={{ padding: "8px 0", borderBottom: "1px solid #F1F5F9", fontSize: 13 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "#475569" }}>{a.descripcion}</span>
                <span style={severidadBadge(a.severidad)}>{a.severidad}</span>
              </div>
              <div style={{ fontSize: 12, color: "#94A3B8", marginTop: 2 }}>{a.recomendacion}</div>
            </div>
          ))}
        </div>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Briefs SEO</h3>
          <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
            <input style={{ ...input, flex: 1 }} placeholder="Keyword principal" value={briefKw} onChange={e => setBriefKw(e.target.value)} />
            <button style={btn} onClick={generarBrief} disabled={loading === "brief"}>Generar</button>
          </div>
          {briefs.slice(0, 5).map(b => (
            <div key={b.id} style={{ padding: "8px 0", borderBottom: "1px solid #F1F5F9", fontSize: 13 }}>
              <div style={{ fontWeight: 600, color: "#0F172A" }}>{b.keyword_principal}</div>
              <div style={{ fontSize: 12, color: "#94A3B8" }}>{b.meta_title || "Sin title"}</div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}
