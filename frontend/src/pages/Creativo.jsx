import { useState, useEffect, useRef } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import EmptyState from "../components/ui/EmptyState";
import api from "../hooks/useApi";

const card       = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, padding: 20, marginBottom: 16 };
const inputStyle = { width: "100%", padding: "10px 12px", border: "1.5px solid var(--border)", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 12, background: "var(--surface)", color: "var(--text)" };
const selectStyle= { ...inputStyle, appearance: "auto" };
const btn        = { padding: "10px 20px", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSmall   = { padding: "6px 14px", border: "1px solid var(--border)", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "var(--surface)", color: "var(--text-secondary)" };
const btnDanger  = { ...btnSmall, borderColor: "var(--danger)", color: "var(--danger-text)" };

const FORMATOS = [
  { value: "post", label: "Post (1080×1080)" },
  { value: "historia", label: "Historia (1080×1920)" },
  { value: "reel", label: "Reel (1080×1920)" },
  { value: "carrusel", label: "Carrusel (1080×1080)" },
  { value: "facebook_post", label: "Facebook Post (1200×630)" },
];

const ACCEPTED_IMG = ".jpg,.jpeg,.png,.webp,.gif";
const MAX_MB = 20;

function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("es-AR", { day: "2-digit", month: "short" });
}

export default function Creativo() {
  const { get, post } = useApi();
  const [tab, setTab] = useState("ia");
  const [form, setForm] = useState({ descripcion: "", formato: "post", estilo: "vivid", usar_perfil_marca: true, tipo: "elaborada" });
  const [generada, setGenerada] = useState(null);
  const [galeria, setGaleria] = useState([]);
  const [biblioteca, setBiblioteca] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const fileRef = useRef(null);

  useEffect(() => {
    get(ENDPOINTS.IMAGENES).then(r => setGaleria(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.IMAGENES_BIBLIOTECA).then(r => setBiblioteca(r.data.data || [])).catch(() => {});
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

  async function handleUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError("");

    const ext = file.name.split(".").pop().toLowerCase();
    if (!["jpg", "jpeg", "png", "webp", "gif"].includes(ext)) {
      setError("Formato no soportado. Usá JPG, PNG, WEBP o GIF.");
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      setError(`El archivo excede el límite de ${MAX_MB}MB.`);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setUploading(true);
    try {
      const { data } = await api.post(ENDPOINTS.IMAGENES_BIBLIOTECA_SUBIR, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setBiblioteca(prev => [data, ...prev]);
      setMsg("Imagen subida correctamente");
    } catch (err) {
      setError(err.response?.data?.message || "Error al subir imagen");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function handleDelete(id) {
    try {
      await api.delete(ENDPOINTS.IMAGENES_BIBLIOTECA_ELIMINAR(id));
      setBiblioteca(prev => prev.filter(i => i.id !== id));
    } catch {}
  }

  const set = (k) => (e) => setForm({ ...form, [k]: typeof e === "boolean" ? e : e.target.value });

  const tabs = [
    { key: "ia", label: "Generar con IA" },
    { key: "biblioteca", label: `Biblioteca (${biblioteca.length})` },
  ];

  return (
    <Layout title="Creativo IA">
      {msg && (
        <div className="msg-success" style={{ marginBottom: 16, borderRadius: 12 }}>
          <span style={{ flex: 1 }}>{msg}</span>
          <button className="msg-dismiss" onClick={() => setMsg("")}>×</button>
        </div>
      )}
      {error && (
        <div className="msg-error" style={{ marginBottom: 16, borderRadius: 12 }}>
          <span style={{ flex: 1 }}>{error}</span>
          <button className="msg-dismiss" onClick={() => setError("")}>×</button>
        </div>
      )}

      {/* Tabs */}
      <div className="tabs" style={{ marginBottom: 16 }}>
        {tabs.map(t => (
          <button key={t.key} className={`tab ${tab === t.key ? "active" : ""}`} onClick={() => setTab(t.key)}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab: Generar con IA */}
      {tab === "ia" && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div style={card}>
              <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>Generar Imagen</h3>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 12, color: "var(--text-muted)" }}>Tipo de imagen</label>
                <select style={selectStyle} value={form.tipo} onChange={set("tipo")}>
                  <option value="elaborada">Imagen elaborada (foto/ilustración)</option>
                  <option value="placa">Placa con texto (cartel minimalista)</option>
                </select>
              </div>
              <label style={{ fontSize: 12, color: "var(--text-muted)" }}>{form.tipo === "placa" ? "Texto principal de la placa" : "Descripción de la imagen"}</label>
              <textarea style={{ ...inputStyle, minHeight: 80, resize: "vertical" }} value={form.descripcion} onChange={set("descripcion")} placeholder={form.tipo === "placa" ? "Escribí el texto principal que querés mostrar en la placa..." : "Describí la imagen que querés generar..."} />
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div><label style={{ fontSize: 12, color: "var(--text-muted)" }}>Formato</label><select style={selectStyle} value={form.formato} onChange={set("formato")}>{FORMATOS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}</select></div>
                <div><label style={{ fontSize: 12, color: "var(--text-muted)" }}>Estilo</label><select style={selectStyle} value={form.estilo} onChange={set("estilo")}><option value="vivid">Vivid (vibrante)</option><option value="natural">Natural (realista)</option></select></div>
              </div>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: "var(--text-secondary)", marginBottom: 16, cursor: "pointer" }}>
                <input type="checkbox" checked={form.usar_perfil_marca} onChange={e => setForm({ ...form, usar_perfil_marca: e.target.checked })} />
                Usar perfil de marca
              </label>
              <button style={btn} onClick={generar} disabled={loading}>{loading ? "Generando..." : "Generar Imagen"}</button>
            </div>

            <div style={card}>
              <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>Preview</h3>
              {generada ? (
                <div>
                  <div style={{ borderRadius: 10, overflow: "hidden", marginBottom: 12, background: "var(--surface-2)" }}>
                    <img src={generada.imagen_url} alt="" style={{ width: "100%", height: "auto", display: "block" }} onError={e => { e.target.style.display = "none"; }} />
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button style={btnSmall} onClick={() => { setGenerada(null); generar(); }}>Regenerar</button>
                    {generada.imagen_url && <a href={generada.imagen_url} target="_blank" rel="noreferrer" style={{ ...btnSmall, textDecoration: "none" }}>Descargar</a>}
                  </div>
                </div>
              ) : (
                <div style={{ background: "var(--surface-2)", borderRadius: 10, padding: 40, textAlign: "center" }}>
                  <div style={{ fontSize: 40, marginBottom: 8 }}>🖼️</div>
                  <div style={{ fontSize: 13, color: "var(--text-muted)" }}>{loading ? "Generando imagen..." : "Configurá y generá una imagen"}</div>
                </div>
              )}
            </div>
          </div>

          {/* Galería IA */}
          <div style={card}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>Galería IA ({galeria.length})</h3>
            {galeria.length === 0 ? (
              <EmptyState icon="🖼️" title="Sin imágenes" description="Generá tu primera imagen con IA" />
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
                {galeria.map(img => (
                  <div key={img.id} style={{ borderRadius: 10, overflow: "hidden", border: "1px solid var(--border)", cursor: "pointer" }} onClick={() => setGenerada(img)}>
                    <img src={img.imagen_url} alt={img.prompt} style={{ width: "100%", height: 140, objectFit: "cover", display: "block" }} onError={e => { e.target.style.display = "none"; e.target.parentNode.style.background = "var(--surface-2)"; e.target.parentNode.style.height = "140px"; }} />
                    <div style={{ padding: "6px 8px", background: "var(--surface)" }}>
                      <p style={{ fontSize: 11, color: "var(--text-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{img.prompt}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </>
      )}

      {/* Tab: Biblioteca */}
      {tab === "biblioteca" && (
        <>
          {/* Upload zone */}
          <div style={card}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>Subir Imagen</h3>
            <div
              style={{
                border: "2px dashed var(--border)", borderRadius: 10, padding: 24,
                textAlign: "center", cursor: "pointer",
                background: "var(--surface-2)", transition: "border-color var(--t-fast)",
              }}
              onClick={() => fileRef.current?.click()}
              onDragOver={e => { e.preventDefault(); e.currentTarget.style.borderColor = "var(--primary)"; }}
              onDragLeave={e => { e.currentTarget.style.borderColor = "var(--border)"; }}
              onDrop={e => {
                e.preventDefault();
                e.currentTarget.style.borderColor = "var(--border)";
                const file = e.dataTransfer.files?.[0];
                if (file) handleUpload({ target: { files: [file] } });
              }}
            >
              <input ref={fileRef} type="file" accept={ACCEPTED_IMG} onChange={handleUpload} style={{ display: "none" }} />
              {uploading ? (
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
                  <span className="spinner" />
                  <span style={{ color: "var(--text-secondary)", fontSize: 13 }}>Subiendo imagen...</span>
                </div>
              ) : (
                <>
                  <div style={{ fontSize: 28, marginBottom: 6 }}>📷</div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 4 }}>
                    Arrastrá una imagen o hacé click para seleccionar
                  </div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                    JPG, PNG, WEBP o GIF — máximo {MAX_MB}MB
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Biblioteca grid */}
          <div style={card}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>Imágenes subidas ({biblioteca.length})</h3>
            {biblioteca.length === 0 ? (
              <EmptyState icon="📷" title="Biblioteca vacía" description="Subí tu primera imagen" />
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
                {biblioteca.map(img => (
                  <div key={img.id} style={{ borderRadius: 10, overflow: "hidden", border: "1px solid var(--border)", position: "relative" }}>
                    <img src={img.imagen_url} alt={img.prompt} style={{ width: "100%", height: 160, objectFit: "cover", display: "block" }} onError={e => { e.target.style.display = "none"; e.target.parentNode.style.background = "var(--surface-2)"; e.target.parentNode.style.height = "160px"; }} />
                    <div style={{ padding: "8px 10px", background: "var(--surface)" }}>
                      <p style={{ fontSize: 12, color: "var(--text)", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", marginBottom: 2 }}>{img.prompt}</p>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontSize: 10, color: "var(--text-muted)" }}>{formatDate(img.created_at)}</span>
                        <button style={{ ...btnDanger, padding: "3px 8px", fontSize: 11 }} onClick={() => handleDelete(img.id)}>Eliminar</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </Layout>
  );
}
