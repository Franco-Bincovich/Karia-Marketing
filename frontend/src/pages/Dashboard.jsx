import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 12,
  padding: 20,
};
const metricVal = { fontSize: 26, fontWeight: 800, color: "var(--text)" };
const metricLabel = { fontSize: 13, color: "var(--text-muted)", marginTop: 4 };
const grid4 = { display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 24 };
const grid2 = { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 };

const metricas = [
  { label: "Alcance Total", key: "alcance", icon: "👁️", color: "var(--blue-bg)" },
  { label: "Engagement", key: "engagement", icon: "💬", color: "var(--purple-bg)" },
  { label: "Impresiones", key: "impresiones", icon: "📊", color: "var(--success-bg)" },
  { label: "Clicks", key: "clicks", icon: "🔗", color: "var(--warning-bg)" },
];

const agentesV1 = [
  { nombre: "Contenido IA", icon: "✍️" },
  { nombre: "Creativo", icon: "🎨" },
  { nombre: "Social Media", icon: "📱" },
  { nombre: "Comunidad", icon: "💬" },
  { nombre: "Estrategia", icon: "🧠" },
  { nombre: "Reporting", icon: "📊" },
  { nombre: "Orquestador", icon: "🎭" },
  { nombre: "Social Listening", icon: "👂" },
];

function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("es-AR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function Dashboard() {
  const { get } = useApi();
  const [data, setData] = useState(null);
  const [actividad, setActividad] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    get(ENDPOINTS.ANALYTICS_DASHBOARD)
      .then((r) => setData(r.data))
      .catch(() => {});

    // Fetch actividad reciente real de múltiples fuentes
    Promise.all([
      get(ENDPOINTS.CONTENIDO + "?estado=aprobado").catch(() => ({ data: { data: [] } })),
      get(ENDPOINTS.CONTENIDO + "?estado=publicado").catch(() => ({ data: { data: [] } })),
      get(ENDPOINTS.SOCIAL_PUBLICACIONES).catch(() => ({ data: { data: [] } })),
    ])
      .then(([aprobados, publicados, pubs]) => {
        const items = [];
        for (const c of (aprobados.data.data || []).slice(0, 3)) {
          items.push({
            texto: `Contenido aprobado: ${c.tema || c.red_social} — ${c.formato}`,
            fecha: c.updated_at || c.created_at,
          });
        }
        for (const c of (publicados.data.data || []).slice(0, 3)) {
          items.push({
            texto: `Contenido publicado: ${c.tema || c.red_social}`,
            fecha: c.updated_at || c.created_at,
          });
        }
        for (const p of (pubs.data.data || []).slice(0, 3)) {
          items.push({
            texto: `Post ${p.estado} en ${p.red_social}`,
            fecha: p.publicado_at || p.created_at,
          });
        }
        items.sort((a, b) => (b.fecha || "").localeCompare(a.fecha || ""));
        setActividad(items.slice(0, 6));
      })
      .finally(() => setLoading(false));
  }, []);

  const m30 = data?.metricas_30d || {};
  const vals = {
    alcance: m30.alcance || 0,
    engagement: m30.engagement || 0,
    impresiones: m30.impresiones || 0,
    clicks: m30.clicks || 0,
  };

  return (
    <Layout title="Dashboard">
      {loading ? (
        <p style={{ color: "var(--text-muted)" }}>Cargando...</p>
      ) : (
        <>
          <div style={grid4}>
            {metricas.map((m) => (
              <div key={m.key} style={card}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                  <span
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: 10,
                      background: m.color,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 18,
                    }}
                  >
                    {m.icon}
                  </span>
                  <span style={metricLabel}>{m.label}</span>
                </div>
                <div style={metricVal}>{(vals[m.key] || 0).toLocaleString()}</div>
              </div>
            ))}
          </div>
          <div style={grid2}>
            <div style={card}>
              <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>
                Actividad Reciente
              </h3>
              {actividad.length === 0 ? (
                <p style={{ color: "var(--text-muted)", fontSize: 13 }}>Sin actividad reciente</p>
              ) : (
                actividad.map((a, i) => (
                  <div
                    key={i}
                    style={{
                      padding: "10px 0",
                      borderBottom: "1px solid var(--border-subtle)",
                      fontSize: 13,
                      color: "var(--text-secondary)",
                      display: "flex",
                      justifyContent: "space-between",
                    }}
                  >
                    <span>
                      <span style={{ marginRight: 8 }}>•</span>
                      {a.texto}
                    </span>
                    <span
                      style={{
                        fontSize: 11,
                        color: "var(--text-muted)",
                        flexShrink: 0,
                        marginLeft: 8,
                      }}
                    >
                      {formatDate(a.fecha)}
                    </span>
                  </div>
                ))
              )}
            </div>
            <div style={card}>
              <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>
                Agentes V1
              </h3>
              {agentesV1.map((a, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    padding: "8px 0",
                    borderBottom: "1px solid var(--border-subtle)",
                    fontSize: 13,
                  }}
                >
                  <span style={{ color: "var(--text-secondary)" }}>
                    {a.icon} {a.nombre}
                  </span>
                  <span
                    style={{
                      background: "var(--success-bg)",
                      color: "var(--success-text)",
                      padding: "2px 8px",
                      borderRadius: 6,
                      fontSize: 11,
                      fontWeight: 600,
                    }}
                  >
                    Activo
                  </span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </Layout>
  );
}
