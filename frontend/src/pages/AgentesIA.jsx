import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20 };

const agentes = [
  { nombre: "Agente Contenido", rol: "Genera copies y variantes A/B", icon: "✍️", activo: true },
  { nombre: "Agente Social Media", rol: "Publica y monitorea redes", icon: "📱", activo: true },
  { nombre: "Agente Prospección", rol: "Busca leads con IA", icon: "🎯", activo: true },
  { nombre: "Agente Comunidad", rol: "Responde mensajes y DMs", icon: "💬", activo: true },
  { nombre: "Agente Ads", rol: "Gestiona campañas pagadas", icon: "📣", activo: true },
  { nombre: "Agente SEO", rol: "Investiga keywords y audita", icon: "🔍", activo: true },
  { nombre: "Agente Analytics", rol: "Consolida métricas y KPIs", icon: "📈", activo: true },
  { nombre: "Agente Reporting", rol: "Genera reportes periódicos", icon: "📊", activo: true },
  { nombre: "Agente Listening", rol: "Monitorea menciones y crisis", icon: "👂", activo: true },
  { nombre: "Agente Estrategia", rol: "Planifica y analiza competidores", icon: "🧠", activo: true },
  { nombre: "Agente Creativo", rol: "Genera imágenes con IA", icon: "🎨", activo: false },
  { nombre: "Agente Orquestador", rol: "Coordina todos los agentes", icon: "🎭", activo: true },
];

export default function AgentesIA() {
  const { modo } = useAuth();

  return (
    <Layout title="Agentes IA">
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16 }}>
        {agentes.map(a => (
          <div key={a.nombre} style={{ ...card, opacity: a.activo ? 1 : 0.6 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <span style={{ width: 42, height: 42, borderRadius: 12, background: "#F1F5F9", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>{a.icon}</span>
              <div>
                <div style={{ fontSize: 14, fontWeight: 700, color: "#0F172A" }}>{a.nombre}</div>
                <div style={{ fontSize: 12, color: "#94A3B8" }}>{a.rol}</div>
              </div>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{
                background: a.activo ? "#DCFCE7" : "#FEE2E2",
                color: a.activo ? "#15803D" : "#B91C1C",
                padding: "3px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
              }}>{a.activo ? "Activo" : "Inactivo"}</span>
              <span style={{
                background: modo === "autopilot" ? "#DCFCE7" : "#EDE9FE",
                color: modo === "autopilot" ? "#15803D" : "#6D28D9",
                padding: "3px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
              }}>{modo === "autopilot" ? "Autopilot" : "Copilot"}</span>
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
