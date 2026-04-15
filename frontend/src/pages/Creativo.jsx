import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const inputStyle = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 12 };
const selectStyle = { ...inputStyle, appearance: "auto", background: "#fff" };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSmall = { padding: "6px 14px", border: "1px solid #E2E8F0", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "#fff", color: "#475569" };

const SIZES = [
  { value: "1024x1024", label: "Cuadrado (1024x1024)" },
  { value: "1792x1024", label: "Horizontal (1792x1024)" },
  { value: "1024x1792", label: "Vertical (1024x1792)" },
];

export default function Creativo() {
  const { get, post } = useApi();
  const { user } = useAuth();
  const [form, setForm] = useState({ descripcion: "", tamano: "1024x1024", estilo: "vivid", usar_perfil_marca: true });
  const [generada, setGenerada] = useState(null);
  const [galeria, setGaleria] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [savingKey, setSavingKey] = useState(false);

  const isPremiumOrSA = user?.rol === "superadmin";

  useEffect(() => {
    get(ENDPOINTS.IMAGENES).then(r => setGaleria(r.data.data || [])).catch(() => {});
  }, []);

  async function generar() {
    if (!form.descripcion.trim()) return;
    setLoading(true); setError(""); setGenerada(null);
    try {
      const { data } = await post(ENDPOINTS.IMAGENES_GENERAR, form);
      setGenerada(data);
      setGaleria(prev => [data, ...prev]);
    } catch (e) { setError(e.response?.data?.message || "Error al generar imagen"); }
    finally { setLoading(false); }
  }

  async function regenerar() {
    setGenerada(null);
    await generar();
  }

  async function guardarKey() {
    if (!apiKey) return;
    setSavingKey(true);
    try {
      await post(ENDPOINTS.IMAGENES_OPENAI_KEY, { api_key: apiKey });
      setApiKey(""); setMsg("OpenAI API key guardada");
    } catch (e) { setError(e.response?.data?.message || "Error"); }
    finally { setSavingKey(false); }
  }

  const set = (k) => (e) => setForm({ ...form, [k]: typeof e === "boolean" ? e : e.target.value });

  return (
    <Layout title="Creativo IA">
      {msg && (
        <div style={{ ...card, borderColor: "#10B981", background: "#F0FDF4", padding: 12, fontSize: 13, color: "#15803D" }}>
          {msg} <button onClick={() => setMsg("")} style={{ marginLeft: 8, background: "none", border: "none", cursor: "pointer", color: "inherit", fontWeight: 600 }}>x</button>
        </div>
      )}
      {error && (
        <div style={{ ...card, borderColor: "#EF4444", background: "#FEF2F2", padding: 12, fontSize: 13, color: "#B91C1C" }}>
          {error} <button onClick={() => setError("")} style={{ marginLeft: 8, background: "none", border: "none", cursor: "pointer", color: "inherit", fontWeight: 600 }}>x</button>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Form */}
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Generar Imagen</h3>
          <label style={{ fontSize: 12, color: "#94A3B8" }}>Descripción de la imagen</label>
          <textarea style={{ ...inputStyle, minHeight: 80, resize: "vertical" }} value={form.descripcion} onChange={set("descripcion")} placeholder="Describí la imagen que querés generar..." />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <label style={{ fontSize: 12, color: "#94A3B8" }}>Tamaño</label>
              <select style={selectStyle} value={form.tamano} onChange={set("tamano")}>
                {SIZES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
            <div>
              <label style={{ fontSize: 12, color: "#94A3B8" }}>Estilo</label>
              <select style={selectStyle} value={form.estilo} onChange={set("estilo")}>
                <option value="vivid">Vivid (vibrante)</option>
                <option value="natural">Natural (realista)</option>
              </select>
            </div>
          </div>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: "#475569", marginBottom: 16, cursor: "pointer" }}>
            <input type="checkbox" checked={form.usar_perfil_marca} onChange={e => setForm({ ...form, usar_perfil_marca: e.target.checked })} />
            Usar perfil de marca (colores, estética, industria)
          </label>
          <button style={btn} onClick={generar} disabled={loading}>
            {loading ? "Generando..." : "Generar Imagen"}
          </button>
        </div>

        {/* Preview */}
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Preview</h3>
          {generada ? (
            <div>
              <div style={{ borderRadius: 10, overflow: "hidden", marginBottom: 12, background: "#F1F5F9" }}>
                <img
                  src={generada.imagen_url}
                  alt={generada.prompt}
                  style={{ width: "100%", height: "auto", display: "block" }}
                  onError={e => { e.target.style.display = "none"; }}
                />
              </div>
              <p style={{ fontSize: 12, color: "#94A3B8", marginBottom: 12, lineHeight: 1.4 }}>
                {generada.prompt}
              </p>
              <div style={{ display: "flex", gap: 8 }}>
                <button style={btnSmall} onClick={regenerar}>Regenerar</button>
                {generada.imagen_url && (
                  <a href={generada.imagen_url} target="_blank" rel="noreferrer" style={{ ...btnSmall, textDecoration: "none", display: "inline-block" }}>
                    Descargar
                  </a>
                )}
              </div>
            </div>
          ) : (
            <div style={{ background: "#F8FAFC", borderRadius: 10, padding: 40, textAlign: "center" }}>
              <div style={{ fontSize: 40, marginBottom: 8 }}>🖼️</div>
              <div style={{ fontSize: 13, color: "#94A3B8" }}>
                {loading ? "Generando imagen..." : "Configurá y generá una imagen"}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Galería */}
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Galería ({galeria.length})</h3>
        {galeria.length === 0 ? (
          <p style={{ color: "#94A3B8", fontSize: 13 }}>No hay imágenes generadas</p>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
            {galeria.map(img => (
              <div key={img.id} style={{ borderRadius: 10, overflow: "hidden", border: "1px solid #E2E8F0", cursor: "pointer" }} onClick={() => setGenerada(img)}>
                <img
                  src={img.imagen_url}
                  alt={img.prompt}
                  style={{ width: "100%", height: 140, objectFit: "cover", display: "block" }}
                  onError={e => { e.target.style.display = "none"; e.target.parentNode.style.background = "#F1F5F9"; e.target.parentNode.style.height = "140px"; }}
                />
                <div style={{ padding: "6px 8px" }}>
                  <p style={{ fontSize: 11, color: "#94A3B8", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {img.prompt}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* OpenAI API key propia */}
      {isPremiumOrSA && (
        <div style={card}>
          <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>API Key propia de OpenAI</h3>
          <p style={{ fontSize: 12, color: "#94A3B8", marginBottom: 10 }}>
            Conectá tu propia key para generar imágenes con tu cuota.
          </p>
          <div style={{ display: "flex", gap: 8 }}>
            <input style={{ ...inputStyle, flex: 1, marginBottom: 0 }} type="password" placeholder="sk-..." value={apiKey} onChange={e => setApiKey(e.target.value)} />
            <button style={btnSmall} onClick={guardarKey} disabled={savingKey}>{savingKey ? "..." : "Guardar"}</button>
          </div>
        </div>
      )}
    </Layout>
  );
}
