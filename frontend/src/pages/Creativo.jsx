import { useState } from "react";
import Layout from "../components/Layout";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 12 };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };

const FORMATOS = ["post", "story", "banner", "carousel"];
const REDES = ["instagram", "facebook", "linkedin", "tiktok"];

export default function Creativo() {
  const [form, setForm] = useState({ descripcion: "", formato: "post", red_social: "instagram", colores: "" });
  const [generado, setGenerado] = useState(false);

  function generar() {
    if (!form.descripcion.trim()) return;
    setGenerado(true);
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <Layout title="Creativo IA">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Generar Imagen</h3>
          <label style={{ fontSize: 12, color: "#94A3B8" }}>Descripción de la imagen</label>
          <textarea style={{ ...input, minHeight: 80, resize: "vertical" }} value={form.descripcion} onChange={set("descripcion")} placeholder="Describí la imagen que querés generar..." />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <label style={{ fontSize: 12, color: "#94A3B8" }}>Formato</label>
              <select style={{ ...input, appearance: "auto" }} value={form.formato} onChange={set("formato")}>
                {FORMATOS.map(f => <option key={f}>{f}</option>)}
              </select>
            </div>
            <div>
              <label style={{ fontSize: 12, color: "#94A3B8" }}>Red social</label>
              <select style={{ ...input, appearance: "auto" }} value={form.red_social} onChange={set("red_social")}>
                {REDES.map(r => <option key={r}>{r}</option>)}
              </select>
            </div>
          </div>
          <label style={{ fontSize: 12, color: "#94A3B8" }}>Colores de marca</label>
          <input style={input} value={form.colores} onChange={set("colores")} placeholder="Ej: #F97316, #0F172A" />
          <button style={btn} onClick={generar}>Generar Imagen</button>
        </div>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Preview</h3>
          {generado ? (
            <div style={{ background: "#F1F5F9", borderRadius: 10, padding: 40, textAlign: "center" }}>
              <div style={{ fontSize: 40, marginBottom: 12 }}>🎨</div>
              <div style={{ fontSize: 14, fontWeight: 600, color: "#0F172A", marginBottom: 4 }}>Imagen generada</div>
              <div style={{ fontSize: 12, color: "#94A3B8", marginBottom: 16 }}>Conecta con DALL-E 3 o Canva API para generar imágenes reales</div>
              <div style={{ display: "inline-flex", gap: 8 }}>
                <span style={{ background: "#DBEAFE", color: "#1D4ED8", padding: "4px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{form.formato}</span>
                <span style={{ background: "#EDE9FE", color: "#6D28D9", padding: "4px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{form.red_social}</span>
              </div>
            </div>
          ) : (
            <div style={{ background: "#F8FAFC", borderRadius: 10, padding: 40, textAlign: "center" }}>
              <div style={{ fontSize: 40, marginBottom: 8 }}>🖼️</div>
              <div style={{ fontSize: 13, color: "#94A3B8" }}>Configurá y generá una imagen</div>
            </div>
          )}
        </div>
      </div>
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Galería</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
          {[1, 2, 3, 4].map(i => (
            <div key={i} style={{ background: "#F1F5F9", borderRadius: 10, height: 140, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <span style={{ fontSize: 13, color: "#94A3B8" }}>Sin imágenes</span>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}
