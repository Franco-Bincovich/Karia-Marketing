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
const selectStyle = { ...inputStyle, appearance: "auto" };
const btnPrimary = {
  padding: "10px 20px",
  background: "var(--primary)",
  color: "#fff",
  border: "none",
  borderRadius: 9,
  fontSize: 14,
  fontWeight: 600,
  cursor: "pointer",
};
const btnSecondary = {
  padding: "10px 20px",
  background: "var(--surface)",
  color: "var(--text-secondary)",
  border: "1.5px solid var(--border)",
  borderRadius: 9,
  fontSize: 14,
  fontWeight: 500,
  cursor: "pointer",
};
const th = {
  textAlign: "left",
  fontSize: 10,
  color: "var(--text-muted)",
  textTransform: "uppercase",
  padding: "8px 12px",
  borderBottom: "1px solid var(--border)",
  fontWeight: 600,
  letterSpacing: "0.06em",
};
const td = {
  padding: "10px 12px",
  fontSize: 13,
  borderBottom: "1px solid var(--border-subtle)",
  color: "var(--text-secondary)",
};

const redIcons = { instagram: "📷", facebook: "📘", linkedin: "💼", tiktok: "🎵", twitter: "🐦" };

const estadoBadge = (estado) => {
  const map = {
    publicado: { bg: "var(--success-bg)", color: "var(--success-text)" },
    programado: { bg: "var(--blue-bg)", color: "var(--blue-text)" },
    fallido: { bg: "var(--danger-bg)", color: "var(--danger-text)" },
    publicando: { bg: "var(--warning-bg)", color: "var(--warning-text)" },
  };
  const s = map[estado] || map.fallido;
  return {
    background: s.bg,
    color: s.color,
    padding: "2px 8px",
    borderRadius: 6,
    fontSize: 11,
    fontWeight: 600,
  };
};

function formatDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString("es-AR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function SocialMedia() {
  const { get, post, delete: del } = useApi();
  const [cuentas, setCuentas] = useState([]);
  const [pubs, setPubs] = useState([]);
  const [connecting, setConnecting] = useState(false);
  const [connectPlatform, setConnectPlatform] = useState("instagram");
  const [error, setError] = useState("");

  useEffect(() => {
    get(ENDPOINTS.SOCIAL_CUENTAS)
      .then((r) => setCuentas(r.data.data || []))
      .catch(() => {});
    get(ENDPOINTS.SOCIAL_PUBLICACIONES)
      .then((r) => setPubs(r.data.data || []))
      .catch(() => {});
  }, []);

  async function conectarCuenta() {
    setConnecting(true);
    setError("");
    try {
      const callbackUrl = `${window.location.origin}/social-media?oauth=callback`;
      const { data } = await post(ENDPOINTS.SOCIAL_CONECTAR, {
        platform: connectPlatform,
        callback_url: callbackUrl,
      });
      if (data.auth_url) window.open(data.auth_url, "_blank", "width=600,height=700");
    } catch (err) {
      setError(err.response?.data?.message || "Error al iniciar conexión");
    } finally {
      setConnecting(false);
    }
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const state = params.get("state");
    if (code && state) {
      post(ENDPOINTS.SOCIAL_CONECTAR_CALLBACK, { code, state })
        .then(() => {
          get(ENDPOINTS.SOCIAL_CUENTAS).then((r) => setCuentas(r.data.data || []));
          window.history.replaceState({}, "", "/social-media");
        })
        .catch(() => {});
    }
  }, []);

  async function desconectar(cuentaId) {
    try {
      await del(`/api/social/cuentas/${cuentaId}`);
      setCuentas((prev) => prev.map((c) => (c.id === cuentaId ? { ...c, activa: false } : c)));
    } catch {}
  }

  return (
    <Layout title="Redes Sociales">
      {/* Cuentas conectadas */}
      <div style={card}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 16,
          }}
        >
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "var(--text)" }}>
            Cuentas Conectadas
          </h3>
        </div>
        {cuentas.filter((c) => c.activa).length === 0 ? (
          <EmptyState
            icon="📱"
            title="Sin cuentas conectadas"
            description="Conectá tu primera red social abajo"
          />
        ) : (
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            {cuentas
              .filter((c) => c.activa)
              .map((c) => (
                <div
                  key={c.id}
                  style={{
                    border: "1px solid var(--border)",
                    borderRadius: 10,
                    padding: "12px 16px",
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    background: "var(--surface-2)",
                  }}
                >
                  <span style={{ fontSize: 20 }}>{redIcons[c.red_social] || "🌐"}</span>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text)" }}>
                      {c.nombre_cuenta}
                    </div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{c.red_social}</div>
                  </div>
                  <span
                    style={{
                      background: "var(--success-bg)",
                      color: "var(--success-text)",
                      padding: "2px 8px",
                      borderRadius: 6,
                      fontSize: 10,
                      fontWeight: 600,
                    }}
                  >
                    Activa
                  </span>
                  <button
                    onClick={() => desconectar(c.id)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "var(--text-muted)",
                      fontSize: 16,
                      cursor: "pointer",
                      padding: "0 4px",
                    }}
                    title="Desconectar"
                  >
                    ×
                  </button>
                </div>
              ))}
          </div>
        )}
      </div>

      {/* Conectar nueva */}
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>
          Conectar Cuenta
        </h3>
        {error && (
          <div className="msg-error" style={{ marginBottom: 12, borderRadius: 8 }}>
            {error}
          </div>
        )}
        <div style={{ display: "flex", gap: 12, alignItems: "end" }}>
          <div style={{ flex: 1 }}>
            <label className="field-label-sm">Plataforma</label>
            <select
              style={selectStyle}
              value={connectPlatform}
              onChange={(e) => setConnectPlatform(e.target.value)}
            >
              <option value="instagram">Instagram</option>
              <option value="facebook">Facebook</option>
            </select>
          </div>
          <button style={btnPrimary} onClick={conectarCuenta} disabled={connecting}>
            {connecting ? "Conectando..." : "Conectar via OAuth"}
          </button>
        </div>
        <p style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 8 }}>
          Plan Basic: Instagram (30 posts/mes). Premium: Instagram + Facebook sin límite.
        </p>
      </div>

      {/* Historial */}
      <div style={{ ...card, overflowX: "auto" }}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>
          Historial de Publicaciones ({pubs.length})
        </h3>
        <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 700 }}>
          <thead>
            <tr>
              <th style={th}>Red</th>
              <th style={th}>Copy</th>
              <th style={th}>Estado</th>
              <th style={th}>Fecha</th>
              <th style={th}>Likes</th>
              <th style={th}>Comentarios</th>
            </tr>
          </thead>
          <tbody>
            {pubs.length === 0 && (
              <tr>
                <td colSpan={6} style={{ ...td, textAlign: "center", color: "var(--text-muted)" }}>
                  Sin publicaciones
                </td>
              </tr>
            )}
            {pubs.map((p) => (
              <tr key={p.id}>
                <td style={td}>
                  <span style={{ fontSize: 16, marginRight: 4 }}>
                    {redIcons[p.red_social] || "🌐"}
                  </span>
                  {p.red_social}
                </td>
                <td
                  style={{
                    ...td,
                    maxWidth: 280,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {p.copy_publicado || "—"}
                </td>
                <td style={td}>
                  <span style={estadoBadge(p.estado)}>{p.estado}</span>
                </td>
                <td style={td}>
                  {p.estado === "programado"
                    ? formatDate(p.programado_para)
                    : formatDate(p.publicado_at)}
                </td>
                <td style={td}>{p.likes_2hs}</td>
                <td style={td}>{p.comentarios_2hs}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
