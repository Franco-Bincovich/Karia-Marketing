import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 12 };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSec = { ...btn, background: "#fff", color: "#0F172A", border: "1px solid #E2E8F0" };

const PASOS = [
  { n: 1, key: "paso_1_info_basica", title: "Info Básica", fields: ["nombre_marca", "industria", "descripcion", "sitio_web"] },
  { n: 2, key: "paso_2_identidad_marca", title: "Identidad de Marca", fields: ["propuesta_valor", "tipografia"] },
  { n: 3, key: "paso_3_tono_voz", title: "Tono de Voz", fields: ["tono_voz"] },
  { n: 4, key: "paso_4_audiencia", title: "Audiencia", fields: ["publico_objetivo", "icp_descripcion"] },
  { n: 5, key: "paso_5_competidores", title: "Competidores", fields: [] },
  { n: 6, key: "paso_6_productos", title: "Productos/Servicios", fields: [] },
  { n: 7, key: "paso_7_objetivos", title: "Objetivos", fields: [] },
  { n: 8, key: "paso_8_integraciones", title: "Integraciones", fields: [] },
  { n: 9, key: "paso_9_notificaciones", title: "Notificaciones", fields: [] },
  { n: 10, key: "paso_10_subusuarios", title: "Subusuarios", fields: [] },
];

const textareas = new Set(["descripcion", "publico_objetivo", "icp_descripcion", "propuesta_valor"]);

export default function Onboarding() {
  const { get, post } = useApi();
  const { setCompletitud } = useAuth();
  const navigate = useNavigate();
  const [estado, setEstado] = useState(null);
  const [pasoActivo, setPasoActivo] = useState(1);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    get(ENDPOINTS.ONBOARDING_ESTADO).then(r => {
      setEstado(r.data);
      if (r.data.memoria) setForm(r.data.memoria);
      setCompletitud(r.data.completitud || 0);
    }).catch(() => {
      post(ENDPOINTS.ONBOARDING_INICIAR).then(r => setEstado(r.data)).catch(() => {});
    }).finally(() => setLoading(false));
  }, []);

  async function guardarPaso() {
    const paso = PASOS[pasoActivo - 1];
    const datos = {};
    paso.fields.forEach(f => { if (form[f] !== undefined) datos[f] = form[f]; });
    setSaving(true); setMsg("");
    try {
      const { data } = await post(ENDPOINTS.ONBOARDING_PASO(pasoActivo), { datos });
      const newComp = data.completitud || 0;
      setEstado(prev => ({ ...prev, ...data }));
      setCompletitud(newComp);
      if (newComp >= 80 && (estado?.completitud || 0) < 80) {
        setMsg("¡Tu marca está lista para usar KarIA!");
      }
      if (pasoActivo < 10) setPasoActivo(pasoActivo + 1);
    } catch {}
    finally { setSaving(false); }
  }

  const comp = estado?.completitud || 0;
  const pasos = estado?.pasos || {};

  if (loading) return <Layout title="Configuración"><p style={{ color: "#94A3B8" }}>Cargando...</p></Layout>;

  return (
    <Layout title="Configuración — Onboarding">
      <div style={card}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700 }}>Progreso del Onboarding</h3>
          <span style={{ fontSize: 22, fontWeight: 800, color: comp >= 80 ? "#10B981" : "#F97316" }}>{comp}%</span>
        </div>
        <div style={{ height: 10, background: "#F1F5F9", borderRadius: 5, overflow: "hidden", marginBottom: 16 }}>
          <div style={{ height: "100%", width: `${comp}%`, background: comp >= 80 ? "#10B981" : "#F97316", borderRadius: 5, transition: "width 300ms" }} />
        </div>
        {msg && (
          <div style={{ background: "#DCFCE7", color: "#15803D", padding: "10px 14px", borderRadius: 9, fontSize: 13, fontWeight: 600, marginBottom: 12, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>{msg}</span>
            <button style={{ ...btn, background: "#10B981", padding: "6px 16px", fontSize: 13 }} onClick={() => navigate("/dashboard")}>Ir al Dashboard</button>
          </div>
        )}
        <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
          {PASOS.map(p => {
            const done = pasos[p.key] || false;
            return (
              <button key={p.n} onClick={() => setPasoActivo(p.n)} style={{
                padding: "6px 12px", borderRadius: 8, fontSize: 12,
                fontWeight: pasoActivo === p.n ? 700 : 400,
                border: pasoActivo === p.n ? "2px solid #F97316" : "1px solid #E2E8F0",
                cursor: "pointer",
                background: done ? "#DCFCE7" : pasoActivo === p.n ? "#FFF7ED" : "#fff",
                color: done ? "#15803D" : pasoActivo === p.n ? "#F97316" : "#475569",
                display: "flex", alignItems: "center", gap: 4,
              }}>
                {done && <span style={{ fontSize: 14 }}>✓</span>}
                {p.n}. {p.title}
              </button>
            );
          })}
        </div>
      </div>
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>
          Paso {pasoActivo}: {PASOS[pasoActivo - 1].title}
        </h3>
        {PASOS[pasoActivo - 1].fields.length > 0 ? (
          PASOS[pasoActivo - 1].fields.map(f => (
            <div key={f}>
              <label style={{ fontSize: 12, color: "#94A3B8", textTransform: "capitalize" }}>{f.replace(/_/g, " ")}</label>
              {f === "tono_voz" ? (
                <select style={{ ...input, appearance: "auto" }} value={form[f] || "profesional"} onChange={e => setForm({ ...form, [f]: e.target.value })}>
                  <option>profesional</option><option>cercano</option><option>inspirador</option>
                  <option>humoristico</option><option>informativo</option><option>urgente</option>
                </select>
              ) : textareas.has(f) ? (
                <textarea style={{ ...input, minHeight: 60, resize: "vertical" }} value={form[f] || ""} onChange={e => setForm({ ...form, [f]: e.target.value })} />
              ) : (
                <input style={input} value={form[f] || ""} onChange={e => setForm({ ...form, [f]: e.target.value })} />
              )}
            </div>
          ))
        ) : (
          <p style={{ color: "#94A3B8", fontSize: 13, marginBottom: 12 }}>
            Este paso se configura desde el módulo correspondiente. Hacé click en "Guardar y Continuar" para marcarlo como completado.
          </p>
        )}
        <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
          {pasoActivo > 1 && <button style={btnSec} onClick={() => setPasoActivo(pasoActivo - 1)}>Anterior</button>}
          <button style={btn} onClick={guardarPaso} disabled={saving}>
            {saving ? "Guardando..." : pasoActivo === 10 ? "Finalizar" : "Guardar y Continuar"}
          </button>
        </div>
      </div>
    </Layout>
  );
}
