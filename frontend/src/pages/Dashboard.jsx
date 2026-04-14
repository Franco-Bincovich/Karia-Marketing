import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = {
  background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20,
};
const metricVal = { fontSize: 26, fontWeight: 800, color: "#0F172A" };
const metricLabel = { fontSize: 13, color: "#94A3B8", marginTop: 4 };
const grid4 = { display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 24 };
const grid2 = { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 };

const metricas = [
  { label: "Alcance Total", key: "alcance", icon: "👁️", color: "#DBEAFE" },
  { label: "Leads Generados", key: "leads", icon: "🎯", color: "#DCFCE7" },
  { label: "Engagement Rate", key: "engagement", icon: "💬", color: "#EDE9FE", suffix: "%" },
  { label: "Gasto Ads", key: "gasto", icon: "📣", color: "#FEF3C7", prefix: "$" },
];

export default function Dashboard() {
  const { get } = useApi();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    get(ENDPOINTS.ANALYTICS_DASHBOARD).then(r => setData(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const vals = { alcance: data?.metricas_30d?.alcance || 0, leads: 0, engagement: 0, gasto: 0 };

  return (
    <Layout title="Dashboard">
      {loading ? <p style={{ color: "#94A3B8" }}>Cargando...</p> : (
        <>
          <div style={grid4}>
            {metricas.map(m => (
              <div key={m.key} style={card}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                  <span style={{ width: 36, height: 36, borderRadius: 10, background: m.color,
                    display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>{m.icon}</span>
                  <span style={metricLabel}>{m.label}</span>
                </div>
                <div style={metricVal}>
                  {m.prefix || ""}{(vals[m.key] || 0).toLocaleString()}{m.suffix || ""}
                </div>
              </div>
            ))}
          </div>
          <div style={grid2}>
            <div style={card}>
              <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Actividad Reciente</h3>
              {["Campaña Meta creada", "Brief SEO generado", "3 leads detectados", "Contenido aprobado"].map((t, i) => (
                <div key={i} style={{ padding: "10px 0", borderBottom: "1px solid #F1F5F9", fontSize: 13, color: "#475569" }}>
                  <span style={{ marginRight: 8 }}>•</span>{t}
                </div>
              ))}
            </div>
            <div style={card}>
              <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Agentes Activos</h3>
              {["Contenido IA", "Prospección", "SEO", "Comunidad", "Ads", "Analytics"].map((a, i) => (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0",
                  borderBottom: "1px solid #F1F5F9", fontSize: 13 }}>
                  <span style={{ color: "#475569" }}>{a}</span>
                  <span style={{ background: "#DCFCE7", color: "#15803D", padding: "2px 8px",
                    borderRadius: 6, fontSize: 11, fontWeight: 600 }}>Activo</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </Layout>
  );
}
