import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import EmptyState from "../components/ui/EmptyState";

const card  = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid var(--border)", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", background: "var(--surface)", color: "var(--text)" };
const btn   = { padding: "10px 20px", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const th    = { textAlign: "left", fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", padding: "8px 12px", borderBottom: "1px solid var(--border)", fontWeight: 600 };
const td    = { padding: "10px 12px", fontSize: 13, borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)" };

const severidadBadge = (s) => {
  const map = {
    critico: ["var(--danger-bg)",  "var(--danger-text)" ],
    alto:    ["var(--warning-bg)", "var(--warning-text)"],
    medio:   ["var(--blue-bg)",    "var(--blue-text)"   ],
    bajo:    ["var(--success-bg)", "var(--success-text)"],
  };
  const [bg, c] = map[s] || ["var(--surface-2)", "var(--text-secondary)"];
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
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>Investigar Keywords</h3>
        <div style={{ display: "flex", gap: 12 }}>
          <input style={{ ...input, flex: 1 }} placeholder="Buscar keywords..." value={query} onChange={e => setQuery(e.target.value)} />
          <button style={btn} onClick={investigar} disabled={loading === "kw"}>{loading === "kw" ? "..." : "Investigar"}</button>
        </div>
      </div>

      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>Keywords Monitoreadas ({keywords.length})</h3>
        {keywords.length === 0 ? (
          <EmptyState icon="🔍" title="Sin keywords" description="Investigá keywords para empezar a monitorearlas" />
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={th}>Keyword</th><th style={th}>Volumen</th><th style={th}>Dificultad</th>
                  <th style={th}>Posición</th><th style={th}>Intención</th><th style={th}>Estado</th>
                </tr>
              </thead>
              <tbody>
                {keywords.slice(0, 20).map(k => (
                  <tr key={k.id}>
                    <td style={{ ...td, fontWeight: 500, color: "var(--text)" }}>{k.keyword}</td>
                    <td style={td}>{k.volumen_mensual}</td>
                    <td style={td}>{k.dificultad}</td>
                    <td style={td}>
                      {k.posicion_actual || "—"}
                      {k.posicion_anterior && k.posicion_actual && k.posicion_actual < k.posicion_anterior
                        ? <span style={{ color: "var(--success-text)", marginLeft: 4 }}>↑</span>
                        : k.posicion_anterior && k.posicion_actual > k.posicion_anterior
                        ? <span style={{ color: "var(--danger-text)", marginLeft: 4 }}>↓</span>
                        : null}
                    </td>
                    <td style={td}>{k.intencion}</td>
                    <td style={td}>
                      <span style={{ background: "var(--blue-bg)", color: "var(--blue-text)", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{k.estado}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>Auditoría Técnica</h3>
          <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
            <input style={{ ...input, flex: 1 }} placeholder="URL a auditar" value={url} onChange={e => setUrl(e.target.value)} />
            <button style={btn} onClick={auditar} disabled={loading === "audit"}>Auditar</button>
          </div>
          {auditoria.length === 0 ? (
            <EmptyState icon="🔧" title="Sin auditorías" description="Ingresá una URL para auditar" />
          ) : auditoria.slice(0, 5).map(a => (
            <div key={a.id} style={{ padding: "8px 0", borderBottom: "1px solid var(--border-subtle)", fontSize: 13 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>{a.descripcion}</span>
                <span style={severidadBadge(a.severidad)}>{a.severidad}</span>
              </div>
              <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>{a.recomendacion}</div>
            </div>
          ))}
        </div>

        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>Briefs SEO</h3>
          <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
            <input style={{ ...input, flex: 1 }} placeholder="Keyword principal" value={briefKw} onChange={e => setBriefKw(e.target.value)} />
            <button style={btn} onClick={generarBrief} disabled={loading === "brief"}>Generar</button>
          </div>
          {briefs.length === 0 ? (
            <EmptyState icon="📝" title="Sin briefs" description="Generá un brief para optimizar contenido" />
          ) : briefs.slice(0, 5).map(b => (
            <div key={b.id} style={{ padding: "8px 0", borderBottom: "1px solid var(--border-subtle)", fontSize: 13 }}>
              <div style={{ fontWeight: 600, color: "var(--text)" }}>{b.keyword_principal}</div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{b.meta_title || "Sin title"}</div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}
