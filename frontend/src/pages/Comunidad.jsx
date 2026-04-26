import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import EmptyState from "../components/ui/EmptyState";

const card = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 12,
  padding: 20,
  marginBottom: 16,
};
const inputStyle = {
  width: "100%",
  padding: "10px 12px",
  border: "1.5px solid var(--border)",
  borderRadius: 9,
  fontSize: 14,
  outline: "none",
  boxSizing: "border-box",
  background: "var(--surface)",
  color: "var(--text)",
};
const btn = {
  padding: "10px 20px",
  background: "var(--primary)",
  color: "#fff",
  border: "none",
  borderRadius: 9,
  fontSize: 14,
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
const th = {
  textAlign: "left",
  fontSize: 10,
  color: "var(--text-muted)",
  textTransform: "uppercase",
  padding: "8px 12px",
  borderBottom: "1px solid var(--border)",
  fontWeight: 600,
};
const td = {
  padding: "10px 12px",
  fontSize: 13,
  borderBottom: "1px solid var(--border-subtle)",
  color: "var(--text-secondary)",
};

const sentBadge = (s) => {
  const map = {
    positivo: ["var(--success-bg)", "var(--success-text)"],
    negativo: ["var(--danger-bg)", "var(--danger-text)"],
    neutro: ["var(--surface-2)", "var(--text-secondary)"],
    mixto: ["var(--purple-bg)", "var(--purple-text)"],
  };
  const [bg, c] = map[s] || ["var(--surface-2)", "var(--text-secondary)"];
  return {
    background: bg,
    color: c,
    padding: "2px 8px",
    borderRadius: 6,
    fontSize: 11,
    fontWeight: 600,
  };
};

const redIcon = { instagram: "📷", facebook: "📘", linkedin: "💼", tiktok: "🎵", twitter: "🐦" };

export default function Comunidad() {
  const { get, post } = useApi();
  const [tab, setTab] = useState("pendientes");
  const [pendientes, setPendientes] = useState([]);
  const [historial, setHistorial] = useState([]);
  const [leads, setLeads] = useState([]);
  const [respuestas, setRespuestas] = useState({});
  const [actionId, setActionId] = useState(null);

  useEffect(() => {
    get(ENDPOINTS.COMUNIDAD_PENDIENTES)
      .then((r) => setPendientes(r.data.data || []))
      .catch(() => {});
    get(ENDPOINTS.COMUNIDAD_HISTORIAL)
      .then((r) => setHistorial(r.data.data || []))
      .catch(() => {});
    get(ENDPOINTS.COMUNIDAD_LEADS)
      .then((r) => setLeads(r.data.data || []))
      .catch(() => {});
  }, []);

  async function responder(id) {
    const resp = respuestas[id];
    if (!resp) return;
    setActionId(id);
    try {
      await post(ENDPOINTS.COMUNIDAD_RESPONDER(id), { respuesta: resp });
      setPendientes((prev) => prev.filter((m) => m.id !== id));
      setRespuestas((prev) => {
        const n = { ...prev };
        delete n[id];
        return n;
      });
      get(ENDPOINTS.COMUNIDAD_HISTORIAL).then((r) => setHistorial(r.data.data || []));
    } catch {
    } finally {
      setActionId(null);
    }
  }

  function usarSugerencia(id, sugerencia) {
    setRespuestas((prev) => ({ ...prev, [id]: sugerencia }));
  }

  const tabs = [
    { key: "pendientes", label: `Pendientes (${pendientes.length})` },
    { key: "historial", label: `Historial (${historial.length})` },
    { key: "leads", label: `Leads (${leads.length})` },
  ];

  return (
    <Layout title="Comunidad">
      {/* Tabs */}
      <div className="tabs" style={{ marginBottom: 16 }}>
        {tabs.map((t) => (
          <button
            key={t.key}
            className={`tab ${tab === t.key ? "active" : ""}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Pendientes */}
      {tab === "pendientes" && (
        <div>
          {pendientes.length === 0 ? (
            <div style={card}>
              <EmptyState
                icon="💬"
                title="Bandeja vacía"
                description="No hay mensajes pendientes de respuesta"
              />
            </div>
          ) : (
            pendientes.map((m) => (
              <div key={m.id} style={card}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <span style={{ fontSize: 16 }}>{redIcon[m.red_social] || "🌐"}</span>
                    <span style={{ fontWeight: 600, fontSize: 13, color: "var(--text)" }}>
                      {m.autor_username || "Anónimo"}
                    </span>
                    <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{m.tipo}</span>
                  </div>
                  <div style={{ display: "flex", gap: 6 }}>
                    <span style={sentBadge(m.sentimiento)}>{m.sentimiento}</span>
                    <span
                      style={{
                        background: "var(--blue-bg)",
                        color: "var(--blue-text)",
                        padding: "2px 8px",
                        borderRadius: 6,
                        fontSize: 11,
                        fontWeight: 600,
                      }}
                    >
                      {m.clasificacion}
                    </span>
                  </div>
                </div>
                <p
                  style={{ fontSize: 14, color: "var(--text)", marginBottom: 10, lineHeight: 1.5 }}
                >
                  {m.contenido}
                </p>
                {m.respuesta_sugerida && (
                  <div
                    style={{
                      background: "var(--primary-light)",
                      borderRadius: 8,
                      padding: "8px 12px",
                      marginBottom: 10,
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <p
                      style={{
                        fontSize: 13,
                        color: "var(--primary)",
                        fontStyle: "italic",
                        flex: 1,
                      }}
                    >
                      IA sugiere: {m.respuesta_sugerida}
                    </p>
                    <button
                      style={{
                        ...btnSmall,
                        borderColor: "var(--primary)",
                        color: "var(--primary)",
                      }}
                      onClick={() => usarSugerencia(m.id, m.respuesta_sugerida)}
                    >
                      Usar
                    </button>
                  </div>
                )}
                <div style={{ display: "flex", gap: 8 }}>
                  <input
                    style={{ ...inputStyle, flex: 1 }}
                    placeholder="Escribí tu respuesta..."
                    value={respuestas[m.id] || ""}
                    onChange={(e) => setRespuestas({ ...respuestas, [m.id]: e.target.value })}
                  />
                  <button style={btn} onClick={() => responder(m.id)} disabled={actionId === m.id}>
                    {actionId === m.id ? "..." : "Enviar"}
                  </button>
                  <button
                    style={btnSmall}
                    onClick={() => setPendientes((prev) => prev.filter((x) => x.id !== m.id))}
                  >
                    Ignorar
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Historial */}
      {tab === "historial" && (
        <div style={{ ...card, overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 600 }}>
            <thead>
              <tr>
                <th style={th}>Red</th>
                <th style={th}>Usuario</th>
                <th style={th}>Mensaje</th>
                <th style={th}>Respuesta</th>
                <th style={th}>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {historial.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    style={{ ...td, textAlign: "center", color: "var(--text-muted)" }}
                  >
                    Sin historial
                  </td>
                </tr>
              )}
              {historial.map((m) => (
                <tr key={m.id}>
                  <td style={td}>
                    {redIcon[m.red_social] || "🌐"} {m.red_social}
                  </td>
                  <td style={{ ...td, fontWeight: 500, color: "var(--text)" }}>
                    {m.autor_username || "—"}
                  </td>
                  <td
                    style={{
                      ...td,
                      maxWidth: 200,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {m.contenido}
                  </td>
                  <td
                    style={{
                      ...td,
                      maxWidth: 200,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                      color: "var(--success-text)",
                    }}
                  >
                    {m.respuesta || "—"}
                  </td>
                  <td style={{ ...td, fontSize: 11, color: "var(--text-muted)" }}>
                    {m.respondido_at ? new Date(m.respondido_at).toLocaleDateString("es-AR") : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Leads */}
      {tab === "leads" && (
        <div style={card}>
          {leads.length === 0 ? (
            <EmptyState
              icon="🎯"
              title="Sin leads detectados"
              description="Los leads aparecen cuando detectamos interés de compra en comentarios"
            />
          ) : (
            leads.map((l) => (
              <div
                key={l.id}
                style={{
                  padding: "10px 0",
                  borderBottom: "1px solid var(--border-subtle)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text)" }}>
                    {l.autor_username || "Anónimo"}
                  </span>
                  <span style={{ fontSize: 11, color: "var(--text-muted)", marginLeft: 8 }}>
                    {l.red_social}
                  </span>
                  <p style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
                    {l.contenido?.slice(0, 100)}
                  </p>
                </div>
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
                  Lead
                </span>
              </div>
            ))
          )}
        </div>
      )}
    </Layout>
  );
}
