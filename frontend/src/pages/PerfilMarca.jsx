import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import SkeletonLoader from "../components/ui/SkeletonLoader";

const card        = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, padding: 20, marginBottom: 16 };
const sectionTitle= { fontSize: 14, fontWeight: 700, color: "var(--text)", marginBottom: 12 };
const fieldWrap   = { marginBottom: 12 };
const labelStyle  = { fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600, marginBottom: 4 };
const valueStyle  = { fontSize: 14, color: "var(--text-secondary)", lineHeight: 1.5 };
const tag         = { display: "inline-block", background: "var(--surface-2)", color: "var(--text-secondary)", padding: "3px 10px", borderRadius: 6, fontSize: 12, marginRight: 6, marginBottom: 4 };
const btnPrimary  = { padding: "8px 18px", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 9, fontSize: 13, fontWeight: 600, cursor: "pointer" };

function Field({ label: l, children }) {
  if (!children || (typeof children === "string" && !children.trim())) return null;
  return (
    <div style={fieldWrap}>
      <div style={labelStyle}>{l}</div>
      <div style={valueStyle}>{children}</div>
    </div>
  );
}

function Tags({ items }) {
  if (!items || !items.length) return <span style={{ color: "var(--text-muted)", fontSize: 13 }}>—</span>;
  return <div>{items.map((t, i) => <span key={i} style={tag}>{t}</span>)}</div>;
}

function JsonField({ data }) {
  if (!data) return <span style={{ color: "var(--text-muted)", fontSize: 13 }}>—</span>;
  if (typeof data === "string") return <span>{data}</span>;
  if (data.respuesta) return <span>{data.respuesta}</span>;
  return <pre style={{ fontSize: 12, color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>{JSON.stringify(data, null, 2)}</pre>;
}

export default function PerfilMarca() {
  const { get } = useApi();
  const navigate = useNavigate();
  const [perfil, setPerfil] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    get(ENDPOINTS.MARCA_PERFIL).then(r => setPerfil(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

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
        <div style={fieldWrap}>
          <div style={labelStyle}>Diferenciadores</div>
          <Tags items={perfil.diferenciadores} />
        </div>
        <div style={fieldWrap}>
          <div style={labelStyle}>Productos / Servicios</div>
          <JsonField data={perfil.productos_servicios} />
        </div>
        <div style={fieldWrap}>
          <div style={labelStyle}>Competidores</div>
          <JsonField data={perfil.competidores} />
        </div>
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
          <span style={{
            background: "var(--purple-bg)", color: "var(--purple-text)", padding: "3px 10px",
            borderRadius: 6, fontSize: 13, fontWeight: 600,
          }}>{perfil.tono_voz}</span>
        </Field>
        <div style={fieldWrap}>
          <div style={labelStyle}>Colores de Marca</div>
          <Tags items={perfil.colores_marca} />
        </div>
        <Field label="Tipografía">{perfil.tipografia}</Field>
        <div style={fieldWrap}>
          <div style={labelStyle}>Palabras Clave</div>
          <Tags items={perfil.palabras_clave} />
        </div>
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
        <div style={fieldWrap}>
          <div style={labelStyle}>Ejemplos de contenido aprobado</div>
          <Tags items={perfil.ejemplos_contenido_aprobado} />
        </div>
        <Field label="Política de contenido">{perfil.politica_respuestas}</Field>
        <div style={fieldWrap}>
          <div style={labelStyle}>Objetivos del período</div>
          <JsonField data={perfil.objetivos_periodo} />
        </div>
      </div>

      <div style={{ textAlign: "center", padding: "8px 0", color: "var(--text-muted)", fontSize: 12 }}>
        Plan: {perfil.plan} — Última actualización: {perfil.updated_at ? new Date(perfil.updated_at).toLocaleDateString("es-AR") : "—"}
      </div>
    </Layout>
  );
}
