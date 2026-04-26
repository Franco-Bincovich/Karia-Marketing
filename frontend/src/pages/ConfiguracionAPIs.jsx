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
const btnPrimary = {
  padding: "8px 18px",
  background: "var(--primary)",
  color: "#fff",
  border: "none",
  borderRadius: 9,
  fontSize: 13,
  fontWeight: 600,
  cursor: "pointer",
};
const btnDanger = {
  padding: "6px 14px",
  border: "1px solid var(--danger)",
  borderRadius: 7,
  fontSize: 12,
  fontWeight: 500,
  cursor: "pointer",
  background: "var(--surface)",
  color: "var(--danger-text)",
};

const SERVICIO_META = {
  anthropic: {
    label: "Claude (Anthropic)",
    icon: "🧠",
    desc: "Generación de contenido, estrategia, onboarding IA",
  },
  openai: { label: "OpenAI (GPT Image)", icon: "🎨", desc: "Generación de imágenes con IA" },
  canva: { label: "Canva", icon: "🖌️", desc: "Diseño y templates" },
  zernio: { label: "Zernio", icon: "📱", desc: "Publicación en redes sociales" },
};

export default function ConfiguracionAPIs() {
  const { get, post } = useApi();
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inputs, setInputs] = useState({});
  const [saving, setSaving] = useState(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    get(ENDPOINTS.CONFIG_API_KEYS)
      .then((r) => setKeys(r.data.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function guardar(servicio) {
    const val = inputs[servicio];
    if (!val) return;
    setSaving(servicio);
    try {
      await post(ENDPOINTS.CONFIG_API_KEY(servicio), { api_key: val });
      setInputs((prev) => ({ ...prev, [servicio]: "" }));
      setMsg(`API key de ${servicio} guardada correctamente`);
      get(ENDPOINTS.CONFIG_API_KEYS).then((r) => setKeys(r.data.data || []));
    } catch (e) {
      setMsg(e.response?.data?.message || "Error al guardar");
    } finally {
      setSaving(null);
    }
  }

  async function eliminar(servicio) {
    try {
      await fetch(`/api/config/api-keys/${servicio}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
      });
      setMsg(`API key de ${servicio} eliminada`);
      get(ENDPOINTS.CONFIG_API_KEYS).then((r) => setKeys(r.data.data || []));
    } catch {}
  }

  if (loading)
    return (
      <Layout title="Configuración de APIs">
        <SkeletonLoader type="card" count={4} />
      </Layout>
    );

  return (
    <Layout title="Configuración de APIs">
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

      <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 20 }}>
        Gestioná las API keys de los servicios conectados a NEXO. Las keys se almacenan encriptadas.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {keys.map((k) => {
          const meta = SERVICIO_META[k.servicio] || { label: k.servicio, icon: "🔑", desc: "" };
          return (
            <div key={k.servicio} style={card}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
                <span style={{ fontSize: 24 }}>{meta.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 15, fontWeight: 700, color: "var(--text)" }}>
                    {meta.label}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{meta.desc}</div>
                </div>
                {k.configurada ? (
                  <span
                    style={{
                      background: "var(--success-bg)",
                      color: "var(--success-text)",
                      padding: "3px 10px",
                      borderRadius: 6,
                      fontSize: 11,
                      fontWeight: 600,
                    }}
                  >
                    {k.origen === "env" ? "Configurada vía sistema" : "Configurada"}
                  </span>
                ) : (
                  <span
                    style={{
                      background: "var(--surface-2)",
                      color: "var(--text-muted)",
                      padding: "3px 10px",
                      borderRadius: 6,
                      fontSize: 11,
                      fontWeight: 600,
                    }}
                  >
                    Sin configurar
                  </span>
                )}
              </div>

              {k.editable ? (
                <div>
                  <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
                    <input
                      style={{ ...inputStyle, flex: 1, marginBottom: 0 }}
                      type="password"
                      placeholder={
                        k.configurada ? "••••••••••••••" : `Ingresá tu ${meta.label} API key...`
                      }
                      value={inputs[k.servicio] || ""}
                      onChange={(e) =>
                        setInputs((prev) => ({ ...prev, [k.servicio]: e.target.value }))
                      }
                    />
                    <button
                      style={btnPrimary}
                      onClick={() => guardar(k.servicio)}
                      disabled={saving === k.servicio || !inputs[k.servicio]}
                    >
                      {saving === k.servicio ? "..." : "Guardar"}
                    </button>
                  </div>
                  {k.configurada && k.origen === "db" && (
                    <button style={btnDanger} onClick={() => eliminar(k.servicio)}>
                      Eliminar key
                    </button>
                  )}
                  {k.updated_at && (
                    <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 6 }}>
                      Última actualización: {new Date(k.updated_at).toLocaleDateString("es-AR")}
                    </div>
                  )}
                </div>
              ) : (
                <div style={{ fontSize: 12, color: "var(--text-muted)", fontStyle: "italic" }}>
                  Esta key se gestiona desde la configuración del sistema y no puede modificarse
                  desde aquí.
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Layout>
  );
}
