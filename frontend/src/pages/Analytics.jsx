import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };

export default function Analytics() {
  const { get } = useApi();
  const { user } = useAuth();
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

  if (loading) return <Layout title="Analytics"><p style={{ color: "#94A3B8" }}>Cargando...</p></Layout>;

  if (denied) {
    return (
      <Layout title="Analytics">
        <div style={{ ...card, textAlign: "center", padding: 60 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📈</div>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: "#0F172A", marginBottom: 8 }}>Solo disponible en Premium</h2>
          <p style={{ fontSize: 14, color: "#94A3B8", maxWidth: 400, margin: "0 auto" }}>
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
      {/* KPI cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 16 }}>
        {[
          ["Alcance total", metricas.alcance, "📡"],
          ["Impresiones", metricas.impresiones, "👁️"],
          ["Engagement", metricas.engagement, "💬"],
          ["Clicks", metricas.clicks, "🔗"],
          ["Nuevos seguidores", metricas.nuevos_seguidores, "👥"],
          ["Videos vistos", metricas.reproducciones_video, "🎬"],
        ].map(([label, val, icon]) => (
          <div key={label} style={card}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 11, color: "#94A3B8", marginBottom: 4 }}>{label}</div>
                <div style={{ fontSize: 24, fontWeight: 800, color: "#0F172A" }}>{(val || 0).toLocaleString()}</div>
              </div>
              <span style={{ fontSize: 24 }}>{icon}</span>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16, marginBottom: 16 }}>
        {/* Tendencias chart */}
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Tendencia de Engagement (30 días)</h3>
          {tendData.length === 0 ? (
            <p style={{ color: "#94A3B8", fontSize: 13 }}>Sin datos</p>
          ) : (
            <div style={{ display: "flex", alignItems: "flex-end", gap: 2, height: 120 }}>
              {tendData.slice(-30).map((d, i) => (
                <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center" }}>
                  <div style={{ width: "100%", height: Math.max(4, (d.engagement / maxEng) * 100), background: "#F97316", borderRadius: 2, minWidth: 3 }} title={`${d.fecha}: ${d.engagement}`} />
                </div>
              ))}
            </div>
          )}
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6, fontSize: 10, color: "#94A3B8" }}>
            <span>{tendData[0]?.fecha || ""}</span>
            <span>{tendData[tendData.length - 1]?.fecha || ""}</span>
          </div>
        </div>

        {/* KPIs */}
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>KPIs</h3>
          {kpis.length === 0 ? <p style={{ color: "#94A3B8", fontSize: 13 }}>Sin KPIs</p> : kpis.map(k => (
            <div key={k.kpi} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
                <span style={{ color: "#475569" }}>{k.kpi}</span>
                <span style={{ fontWeight: 600 }}>{k.progreso_pct || 0}%</span>
              </div>
              <div style={{ height: 6, background: "#F1F5F9", borderRadius: 3, overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${Math.min(k.progreso_pct || 0, 100)}%`, background: (k.progreso_pct || 0) >= 80 ? "#10B981" : "#F97316", borderRadius: 3 }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top 5 */}
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Top 5 Contenidos</h3>
        {topContenido.length === 0 ? (
          <p style={{ color: "#94A3B8", fontSize: 13 }}>Sin publicaciones</p>
        ) : topContenido.map((p, i) => (
          <div key={p.id} style={{ padding: "10px 0", borderBottom: "1px solid #F1F5F9", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <span style={{ fontSize: 16, fontWeight: 800, color: i < 3 ? "#F97316" : "#94A3B8", width: 24 }}>#{i + 1}</span>
              <div>
                <div style={{ fontSize: 13, color: "#0F172A", fontWeight: 500 }}>{p.red_social} — {(p.copy_publicado || "").slice(0, 60)}</div>
                <div style={{ fontSize: 11, color: "#94A3B8" }}>{p.publicado_at?.split("T")[0]}</div>
              </div>
            </div>
            <div style={{ display: "flex", gap: 12, fontSize: 13 }}>
              <span style={{ color: "#15803D", fontWeight: 600 }}>{p.likes_2hs} likes</span>
              <span style={{ color: "#3B82F6", fontWeight: 600 }}>{p.comentarios_2hs} cmts</span>
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
