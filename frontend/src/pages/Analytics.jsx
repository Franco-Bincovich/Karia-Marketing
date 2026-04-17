import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import SkeletonLoader from "../components/ui/SkeletonLoader";
import EmptyState from "../components/ui/EmptyState";

const card = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 12, padding: 20, marginBottom: 16 };

export default function Analytics() {
  const { get } = useApi();
  const [dashboard, setDashboard] = useState(null);
  const [tendencias, setTendencias] = useState(null);
  const [topContenido, setTopContenido] = useState([]);
  const [loading, setLoading] = useState(true);
  const [denied, setDenied] = useState(false);

  useEffect(() => {
    get(ENDPOINTS.ANALYTICS_DASHBOARD).then(r => {
      setDashboard(r.data);
      return Promise.all([
        get(ENDPOINTS.ANALYTICS_TENDENCIAS).then(r => setTendencias(r.data)),
        get(ENDPOINTS.ANALYTICS_TOP_CONTENIDO).then(r => setTopContenido(r.data.data || [])),
      ]);
    }).catch(e => {
      if (e.response?.status === 403) setDenied(true);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <Layout title="Analytics"><SkeletonLoader type="metric" count={6} /></Layout>;

  if (denied) {
    return (
      <Layout title="Analytics">
        <div style={{ ...card, textAlign: "center", padding: 60 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📈</div>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: "var(--text)", marginBottom: 8 }}>Solo disponible en Premium</h2>
          <p style={{ fontSize: 14, color: "var(--text-muted)", maxWidth: 400, margin: "0 auto" }}>
            El dashboard de Analytics con KPIs, tendencias y top contenido está disponible en el plan Premium.
          </p>
        </div>
      </Layout>
    );
  }

  const metricas = dashboard?.metricas_30d || {};
  const kpis = dashboard?.kpis || [];
  const tendData = tendencias?.data || [];
  const maxEng = Math.max(...tendData.map(d => d.engagement || 0), 1);

  return (
    <Layout title="Analytics">
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 16 }}>
        {[
          ["Alcance total",      metricas.alcance,               "📡"],
          ["Impresiones",        metricas.impresiones,            "👁️"],
          ["Engagement",         metricas.engagement,             "💬"],
          ["Clicks",             metricas.clicks,                 "🔗"],
          ["Nuevos seguidores",  metricas.nuevos_seguidores,      "👥"],
          ["Videos vistos",      metricas.reproducciones_video,   "🎬"],
        ].map(([label, val, icon]) => (
          <div key={label} style={card}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>{label}</div>
                <div style={{ fontSize: 24, fontWeight: 800, color: "var(--text)" }}>{(val || 0).toLocaleString()}</div>
              </div>
              <span style={{ fontSize: 24 }}>{icon}</span>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16, marginBottom: 16 }}>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>Tendencia de Engagement (30 días)</h3>
          {tendData.length === 0 ? (
            <EmptyState icon="📊" title="Sin datos" description="Publicá contenido para ver tendencias" />
          ) : (
            <div style={{ display: "flex", alignItems: "flex-end", gap: 2, height: 120 }}>
              {tendData.slice(-30).map((d, i) => (
                <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center" }}>
                  <div style={{
                    width: "100%",
                    height: Math.max(4, (d.engagement / maxEng) * 100),
                    background: "var(--primary)",
                    borderRadius: "2px 2px 0 0",
                    minWidth: 3,
                    opacity: 0.8,
                  }} title={`${d.fecha}: ${d.engagement}`} />
                </div>
              ))}
            </div>
          )}
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6, fontSize: 10, color: "var(--text-muted)" }}>
            <span>{tendData[0]?.fecha || ""}</span>
            <span>{tendData[tendData.length - 1]?.fecha || ""}</span>
          </div>
        </div>

        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>KPIs</h3>
          {kpis.length === 0 ? (
            <p style={{ color: "var(--text-muted)", fontSize: 13 }}>Sin KPIs configurados</p>
          ) : kpis.map(k => (
            <div key={k.kpi} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
                <span style={{ color: "var(--text-secondary)" }}>{k.kpi}</span>
                <span style={{ fontWeight: 600, color: "var(--text)" }}>{k.progreso_pct || 0}%</span>
              </div>
              <div className="progress-track">
                <div
                  className={`progress-fill ${(k.progreso_pct || 0) >= 80 ? "success" : ""}`}
                  style={{ width: `${Math.min(k.progreso_pct || 0, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>Top 5 Contenidos</h3>
        {topContenido.length === 0 ? (
          <EmptyState icon="🏆" title="Sin publicaciones" description="Publicá contenido para ver el top" />
        ) : topContenido.map((p, i) => (
          <div key={p.id} style={{ padding: "10px 0", borderBottom: "1px solid var(--border-subtle)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <span style={{ fontSize: 16, fontWeight: 800, color: i < 3 ? "var(--primary)" : "var(--text-muted)", width: 24 }}>#{i + 1}</span>
              <div>
                <div style={{ fontSize: 13, color: "var(--text)", fontWeight: 500 }}>{p.red_social} — {(p.copy_publicado || "").slice(0, 60)}</div>
                <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{p.publicado_at?.split("T")[0]}</div>
              </div>
            </div>
            <div style={{ display: "flex", gap: 12, fontSize: 13 }}>
              <span style={{ color: "var(--success-text)", fontWeight: 600 }}>{p.likes_2hs} likes</span>
              <span style={{ color: "var(--blue-text)", fontWeight: 600 }}>{p.comentarios_2hs} cmts</span>
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
