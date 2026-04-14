import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box" };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const th = { textAlign: "left", fontSize: 10, color: "#94A3B8", textTransform: "uppercase", padding: "8px 12px", borderBottom: "1px solid #E2E8F0" };
const td = { padding: "10px 12px", fontSize: 13, borderBottom: "1px solid #F1F5F9", color: "#475569" };

export default function SocialMedia() {
  const { get, post, delete: del } = useApi();
  const [cuentas, setCuentas] = useState([]);
  const [pubs, setPubs] = useState([]);
  const [form, setForm] = useState({ red: "instagram", nombre_cuenta: "", access_token: "mock" });

  useEffect(() => {
    get(ENDPOINTS.SOCIAL_CUENTAS).then(r => setCuentas(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.SOCIAL_PUBLICACIONES).then(r => setPubs(r.data.data || [])).catch(() => {});
  }, []);

  async function conectar() {
    if (!form.nombre_cuenta) return;
    await post(`/api/social/cuentas/${form.red}`, { nombre_cuenta: form.nombre_cuenta, access_token: form.access_token });
    setForm({ red: "instagram", nombre_cuenta: "", access_token: "mock" });
    get(ENDPOINTS.SOCIAL_CUENTAS).then(r => setCuentas(r.data.data || []));
  }

  return (
    <Layout title="Redes Sociales">
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Cuentas Conectadas</h3>
        {cuentas.length === 0 ? <p style={{ color: "#94A3B8", fontSize: 13 }}>Sin cuentas conectadas</p> : (
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            {cuentas.map(c => (
              <div key={c.id} style={{ border: "1px solid #E2E8F0", borderRadius: 10, padding: "12px 16px", display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontSize: 20 }}>{c.red_social === "instagram" ? "📷" : c.red_social === "facebook" ? "📘" : "💼"}</span>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>{c.nombre_cuenta}</div>
                  <div style={{ fontSize: 11, color: "#94A3B8" }}>{c.red_social}</div>
                </div>
                <span style={{ background: c.activa ? "#DCFCE7" : "#FEE2E2", color: c.activa ? "#15803D" : "#B91C1C", padding: "2px 8px", borderRadius: 6, fontSize: 10, fontWeight: 600 }}>{c.activa ? "Activa" : "Inactiva"}</span>
              </div>
            ))}
          </div>
        )}
      </div>
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Conectar Cuenta</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr auto", gap: 12, alignItems: "end" }}>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Red</label><select style={{ ...input, appearance: "auto" }} value={form.red} onChange={e => setForm({ ...form, red: e.target.value })}><option>instagram</option><option>facebook</option><option>linkedin</option></select></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Nombre</label><input style={input} value={form.nombre_cuenta} onChange={e => setForm({ ...form, nombre_cuenta: e.target.value })} placeholder="@cuenta" /></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Token</label><input style={input} value={form.access_token} onChange={e => setForm({ ...form, access_token: e.target.value })} /></div>
          <button style={btn} onClick={conectar}>Conectar</button>
        </div>
      </div>
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Publicaciones Recientes</h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead><tr><th style={th}>Red</th><th style={th}>Copy</th><th style={th}>Estado</th><th style={th}>Likes</th><th style={th}>Comentarios</th></tr></thead>
          <tbody>{pubs.map(p => (
            <tr key={p.id}><td style={td}>{p.red_social}</td><td style={{ ...td, maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{p.copy_publicado || "—"}</td><td style={td}>{p.estado}</td><td style={td}>{p.likes_2hs}</td><td style={td}>{p.comentarios_2hs}</td></tr>
          ))}</tbody>
        </table>
      </div>
    </Layout>
  );
}
