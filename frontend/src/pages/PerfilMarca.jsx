import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import SkeletonLoader from "../components/ui/SkeletonLoader";
import EmptyState from "../components/ui/EmptyState";
import api from "../hooks/useApi";

const card        = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, padding: 20, marginBottom: 16 };
const sectionTitle= { fontSize: 14, fontWeight: 700, color: "var(--text)", marginBottom: 12 };
const fieldWrap   = { marginBottom: 12 };
const labelStyle  = { fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600, marginBottom: 4 };
const valueStyle  = { fontSize: 14, color: "var(--text)", lineHeight: 1.5 };
const tag         = { display: "inline-block", background: "var(--surface-2)", color: "var(--text)", padding: "3px 10px", borderRadius: 6, fontSize: 12, marginRight: 6, marginBottom: 4 };
const btnPrimary  = { padding: "8px 18px", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 9, fontSize: 13, fontWeight: 600, cursor: "pointer" };
const btnSmall    = { padding: "6px 14px", border: "1px solid var(--border)", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "var(--surface)", color: "var(--text-secondary)" };
const btnDanger   = { ...btnSmall, borderColor: "var(--danger)", color: "var(--danger-text)" };

function Field({ label: l, children }) {
  if (!children || (typeof children === "string" && !children.trim())) return null;
  return <div style={fieldWrap}><div style={labelStyle}>{l}</div><div style={valueStyle}>{children}</div></div>;
}

function Tags({ items }) {
  if (!items || !items.length) return <span style={{ color: "var(--text-muted)", fontSize: 13 }}>—</span>;
  return <div>{items.map((t, i) => <span key={i} style={tag}>{t}</span>)}</div>;
}

function ColorSwatches({ items }) {
  if (!items || !items.length) return <span style={{ color: "var(--text-muted)", fontSize: 13 }}>—</span>;
  // items can be an array of strings — join them and extract all hex codes
  const raw = Array.isArray(items) ? items.join(" ") : String(items);
  const hexCodes = raw.match(/#[0-9A-Fa-f]{6}/g);
  if (!hexCodes || !hexCodes.length) {
    // No hex codes found — show as text
    return <span style={{ fontSize: 13, color: "var(--text)" }}>{raw}</span>;
  }
  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
      {hexCodes.map((hex, i) => (
        <div key={i} title={hex} style={{
          width: 28, height: 28, borderRadius: "50%", backgroundColor: hex,
          border: "2px solid var(--border)", cursor: "default", flexShrink: 0,
        }} />
      ))}
      <span style={{ fontSize: 11, color: "var(--text-muted)", marginLeft: 4 }}>
        {hexCodes.join(", ")}
      </span>
    </div>
  );
}

function JsonField({ data }) {
  if (!data) return <span style={{ color: "var(--text-muted)", fontSize: 13 }}>—</span>;
  if (typeof data === "string") return <span style={{ color: "var(--text)", fontSize: 14 }}>{data}</span>;
  if (data.respuesta) return <span style={{ color: "var(--text)", fontSize: 14 }}>{data.respuesta}</span>;
  return <pre style={{ fontSize: 12, color: "var(--text)", whiteSpace: "pre-wrap" }}>{JSON.stringify(data, null, 2)}</pre>;
}

const ACCEPTED = ".pdf,.docx,.doc,.txt";
const MAX_MB = 10;
const tipoIcon = { pdf: "📄", docx: "📝", doc: "📝", txt: "📃" };

function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("es-AR", { day: "2-digit", month: "short", year: "numeric" });
}

export default function PerfilMarca() {
  const { get } = useApi();
  const navigate = useNavigate();
  const [perfil, setPerfil] = useState(null);
  const [loading, setLoading] = useState(true);
  const [docs, setDocs] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [docError, setDocError] = useState("");
  const fileRef = useRef(null);

  useEffect(() => {
    get(ENDPOINTS.MARCA_PERFIL).then(r => setPerfil(r.data)).catch(() => {}).finally(() => setLoading(false));
    get(ENDPOINTS.MARCA_DOCUMENTOS).then(r => setDocs(r.data.data || [])).catch(() => {});
  }, []);

  async function handleUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setDocError("");

    const ext = file.name.split(".").pop().toLowerCase();
    if (!["pdf", "docx", "doc", "txt"].includes(ext)) {
      setDocError("Formato no soportado. Usá PDF, DOCX o TXT.");
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      setDocError(`El archivo excede el límite de ${MAX_MB}MB.`);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      await api.post(ENDPOINTS.MARCA_DOCUMENTOS_SUBIR, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      get(ENDPOINTS.MARCA_DOCUMENTOS).then(r => setDocs(r.data.data || []));
    } catch (err) {
      setDocError(err.response?.data?.message || "Error al subir documento");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function handleDelete(docId) {
    try {
      await api.delete(ENDPOINTS.MARCA_DOCUMENTOS_ELIMINAR(docId));
      setDocs(prev => prev.filter(d => d.id !== docId));
    } catch {}
  }

  if (loading) return <Layout title="Perfil de Marca"><SkeletonLoader type="card" count={3} /></Layout>;
  if (!perfil) return <Layout title="Perfil de Marca"><p style={{ color: "var(--text-muted)" }}>No se pudo cargar el perfil.</p></Layout>;

  return (
    <Layout title="Perfil de Marca">
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
        <button style={btnPrimary} onClick={() => navigate("/onboarding")}>Editar Onboarding</button>
      </div>

      {/* Marca */}
      <div style={card}>
        <h3 style={sectionTitle}>Marca</h3>
        <Field label="Nombre">{perfil.nombre_marca}</Field>
        <Field label="Descripción">{perfil.descripcion}</Field>
        <Field label="Industria">{perfil.industria}</Field>
        <Field label="Sitio Web">{perfil.sitio_web}</Field>
        <Field label="Propuesta de Valor">{perfil.propuesta_valor}</Field>
        <div style={fieldWrap}><div style={labelStyle}>Diferenciadores</div><Tags items={perfil.diferenciadores} /></div>
        <div style={fieldWrap}><div style={labelStyle}>Productos / Servicios</div><JsonField data={perfil.productos_servicios} /></div>
        <div style={fieldWrap}><div style={labelStyle}>Competidores</div><JsonField data={perfil.competidores} /></div>
      </div>

      {/* Audiencia */}
      <div style={card}>
        <h3 style={sectionTitle}>Audiencia</h3>
        <Field label="Público Objetivo">{perfil.publico_objetivo}</Field>
        <Field label="ICP">{perfil.icp_descripcion}</Field>
      </div>

      {/* Identidad */}
      <div style={card}>
        <h3 style={sectionTitle}>Identidad Visual & Tono</h3>
        <Field label="Tono de Voz">
          <span style={{ background: "var(--purple-bg)", color: "var(--purple-text)", padding: "3px 10px", borderRadius: 6, fontSize: 13, fontWeight: 600 }}>{perfil.tono_voz}</span>
        </Field>
        <div style={fieldWrap}><div style={labelStyle}>Colores de Marca</div><ColorSwatches items={perfil.colores_marca} /></div>
        <Field label="Tipografía">{perfil.tipografia}</Field>
        <div style={fieldWrap}><div style={labelStyle}>Palabras Clave</div><Tags items={perfil.palabras_clave} /></div>
        <div style={fieldWrap}>
          <div style={labelStyle}>Palabras Prohibidas</div>
          {perfil.palabras_prohibidas?.length > 0 ? (
            <div>{perfil.palabras_prohibidas.map((t, i) => (
              <span key={i} style={{ ...tag, background: "var(--danger-bg)", color: "var(--danger-text)" }}>{t}</span>
            ))}</div>
          ) : <span style={{ color: "var(--text-muted)", fontSize: 13 }}>—</span>}
        </div>
      </div>

      {/* Contenido */}
      <div style={card}>
        <h3 style={sectionTitle}>Contenido</h3>
        <div style={fieldWrap}><div style={labelStyle}>Ejemplos de contenido aprobado</div><Tags items={perfil.ejemplos_contenido_aprobado} /></div>
        <Field label="Política de contenido">{perfil.politica_respuestas}</Field>
        <div style={fieldWrap}><div style={labelStyle}>Objetivos del período</div><JsonField data={perfil.objetivos_periodo} /></div>
      </div>

      {/* Documentos de marca */}
      <div style={card}>
        <h3 style={sectionTitle}>Documentos de marca</h3>
        <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 12 }}>
          Subí briefs, manuales de marca o cualquier documento para dar más contexto a los agentes de IA.
        </p>

        {docError && (
          <div className="msg-error" style={{ marginBottom: 12, borderRadius: 8 }}>
            <span style={{ flex: 1 }}>{docError}</span>
            <button className="msg-dismiss" onClick={() => setDocError("")}>×</button>
          </div>
        )}

        {/* Upload area */}
        <div
          style={{
            border: "2px dashed var(--border)", borderRadius: 10, padding: 20,
            textAlign: "center", marginBottom: 16, cursor: "pointer",
            background: "var(--surface-2)", transition: "border-color var(--t-fast)",
          }}
          onClick={() => fileRef.current?.click()}
          onDragOver={e => { e.preventDefault(); e.currentTarget.style.borderColor = "var(--primary)"; }}
          onDragLeave={e => { e.currentTarget.style.borderColor = "var(--border)"; }}
          onDrop={e => {
            e.preventDefault();
            e.currentTarget.style.borderColor = "var(--border)";
            const file = e.dataTransfer.files?.[0];
            if (file && fileRef.current) {
              const dt = new DataTransfer();
              dt.items.add(file);
              fileRef.current.files = dt.files;
              handleUpload({ target: { files: [file] } });
            }
          }}
        >
          <input ref={fileRef} type="file" accept={ACCEPTED} onChange={handleUpload} style={{ display: "none" }} />
          {uploading ? (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
              <span className="spinner" />
              <span style={{ color: "var(--text-secondary)", fontSize: 13 }}>Subiendo documento...</span>
            </div>
          ) : (
            <>
              <div style={{ fontSize: 28, marginBottom: 6 }}>📎</div>
              <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 4 }}>
                Arrastrá un archivo o hacé click para seleccionar
              </div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                PDF, DOCX o TXT — máximo {MAX_MB}MB
              </div>
            </>
          )}
        </div>

        {/* Document list */}
        {docs.length === 0 ? (
          <EmptyState icon="📎" title="Sin documentos" description="Subí tu primer documento de marca" />
        ) : (
          <div>
            {docs.map(d => (
              <div key={d.id} style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "10px 0", borderBottom: "1px solid var(--border-subtle)",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: 20 }}>{tipoIcon[d.tipo] || "📄"}</span>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text)" }}>{d.nombre_archivo}</div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                      {d.tipo.toUpperCase()} — {d.chars_extraidos > 0 ? `${d.chars_extraidos.toLocaleString()} chars extraídos` : "Sin texto extraído"} — {formatDate(d.created_at)}
                    </div>
                  </div>
                </div>
                <button style={btnDanger} onClick={() => handleDelete(d.id)}>Eliminar</button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={{ textAlign: "center", padding: "8px 0", color: "var(--text-muted)", fontSize: 12 }}>
        Plan: {perfil.plan} — Última actualización: {perfil.updated_at ? new Date(perfil.updated_at).toLocaleDateString("es-AR") : "—"}
      </div>
    </Layout>
  );
}
