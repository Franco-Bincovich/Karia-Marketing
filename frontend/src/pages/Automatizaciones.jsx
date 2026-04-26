import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import SkeletonLoader from "../components/ui/SkeletonLoader";

const card = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 12,
  padding: 20,
  marginBottom: 0,
};
const btn = {
  padding: "8px 18px",
  background: "var(--primary)",
  color: "#fff",
  border: "none",
  borderRadius: 9,
  fontSize: 13,
  fontWeight: 600,
  cursor: "pointer",
};
const btnSmall = {
  padding: "6px 14px",
  border: "1px solid var(--border)",
  borderRadius: 7,
  fontSize: 12,
  fontWeight: 500,
  cursor: "pointer",
  background: "var(--surface)",
  color: "var(--text-secondary)",
};

const tipoIcon = {
  vencimientos: "📅",
  listening: "👂",
  reporte: "📊",
  publicacion: "📱",
  orquestador: "🎭",
};

function formatDate(iso) {
  if (!iso) return "Nunca";
  return new Date(iso).toLocaleString("es-AR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function Automatizaciones() {
  const { get, patch, post } = useApi();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    get(ENDPOINTS.AUTOMATIZACIONES)
      .then((r) => setItems(r.data.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function toggle(item) {
    const endpoint = item.activa
      ? ENDPOINTS.AUTOMATIZACION_DESACTIVAR(item.tipo)
      : ENDPOINTS.AUTOMATIZACION_ACTIVAR(item.tipo);
    try {
      const { data } = await patch(endpoint);
      setItems((prev) => prev.map((a) => (a.tipo === item.tipo ? data : a)));
    } catch {}
  }

  async function ejecutar(tipo) {
    setExecuting(tipo);
    setMsg("");
    try {
      const { data } = await post(ENDPOINTS.AUTOMATIZACION_EJECUTAR(tipo));
      setMsg(`${tipo}: ${data.resultado}`);
      get(ENDPOINTS.AUTOMATIZACIONES).then((r) => setItems(r.data.data || []));
    } catch (e) {
      setMsg(e.response?.data?.message || "Error al ejecutar");
    } finally {
      setExecuting(null);
    }
  }

  if (loading)
    return (
      <Layout title="Automatizaciones">
        <SkeletonLoader type="card" count={4} />
      </Layout>
    );

  return (
    <Layout title="Automatizaciones">
      {msg && (
        <div
          className={msg.includes("Error") ? "msg-error" : "msg-success"}
          style={{ marginBottom: 16, borderRadius: 12 }}
        >
          <span style={{ flex: 1 }}>{msg}</span>
          <button className="msg-dismiss" onClick={() => setMsg("")}>
            ×
          </button>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {items.map((a) => (
          <div key={a.tipo} style={{ ...card, opacity: a.activa ? 1 : 0.7 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                marginBottom: 12,
              }}
            >
              <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                <span
                  style={{
                    width: 42,
                    height: 42,
                    borderRadius: 12,
                    background: "var(--surface-2)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 20,
                  }}
                >
                  {tipoIcon[a.tipo] || "⚙️"}
                </span>
                <div>
                  <div style={{ fontSize: 15, fontWeight: 700, color: "var(--text)" }}>
                    {a.nombre}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{a.descripcion}</div>
                </div>
              </div>
              <button
                onClick={() => toggle(a)}
                style={{
                  padding: "4px 12px",
                  borderRadius: 6,
                  fontSize: 11,
                  fontWeight: 600,
                  border: "none",
                  cursor: "pointer",
                  background: a.activa ? "var(--success-bg)" : "var(--surface-2)",
                  color: a.activa ? "var(--success-text)" : "var(--text-muted)",
                }}
              >
                {a.activa ? "Activa" : "Inactiva"}
              </button>
            </div>

            <div
              style={{
                display: "flex",
                gap: 16,
                fontSize: 12,
                color: "var(--text-muted)",
                marginBottom: 12,
                flexWrap: "wrap",
              }}
            >
              <div>
                <span style={{ fontWeight: 600 }}>Última:</span> {formatDate(a.ultima_ejecucion)}
              </div>
              <div>
                <span style={{ fontWeight: 600 }}>Próxima:</span> {formatDate(a.proxima_ejecucion)}
              </div>
              <div>
                <span style={{ fontWeight: 600 }}>Intervalo:</span>{" "}
                {a.intervalo_horas >= 1
                  ? `${a.intervalo_horas}h`
                  : `${Math.round(a.intervalo_horas * 60)}min`}
              </div>
            </div>

            <button
              style={a.activa ? btn : { ...btnSmall, opacity: 0.5 }}
              onClick={() => a.activa && ejecutar(a.tipo)}
              disabled={!a.activa || executing === a.tipo}
            >
              {executing === a.tipo ? "Ejecutando..." : "Ejecutar ahora"}
            </button>
          </div>
        ))}
      </div>
    </Layout>
  );
}
