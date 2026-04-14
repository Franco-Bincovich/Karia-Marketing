import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20 };
const input = { width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box" };
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const colors = { instagram: "#E1306C", facebook: "#1877F2", linkedin: "#0A66C2", tiktok: "#000", twitter: "#1DA1F2" };

export default function Calendario() {
  const { get, post } = useApi();
  const [eventos, setEventos] = useState([]);
  const [mes, setMes] = useState(new Date().getMonth() + 1);
  const [anio, setAnio] = useState(new Date().getFullYear());
  const [form, setForm] = useState({ titulo: "", descripcion: "", red_social: "instagram", formato: "post", fecha_programada: "" });

  useEffect(() => { cargar(); }, [mes, anio]);

  function cargar() {
    get(ENDPOINTS.CALENDARIO, { mes, anio }).then(r => setEventos(r.data.data || [])).catch(() => {});
  }

  async function crear() {
    if (!form.titulo || !form.fecha_programada) return;
    await post(ENDPOINTS.CALENDARIO, form);
    setForm({ titulo: "", descripcion: "", red_social: "instagram", formato: "post", fecha_programada: "" });
    cargar();
  }

  const dias = new Date(anio, mes, 0).getDate();
  const primerDia = new Date(anio, mes - 1, 1).getDay();
  const celdas = Array.from({ length: 42 }, (_, i) => {
    const d = i - primerDia + 1;
    return d > 0 && d <= dias ? d : null;
  });

  function eventosDelDia(d) {
    return eventos.filter(e => {
      const fecha = new Date(e.fecha_programada);
      return fecha.getDate() === d && fecha.getMonth() + 1 === mes;
    });
  }

  return (
    <Layout title="Calendario Editorial">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 16 }}>
        <div style={card}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <button style={{ ...btn, background: "#fff", color: "#0F172A", border: "1px solid #E2E8F0" }} onClick={() => { mes === 1 ? (setMes(12), setAnio(anio - 1)) : setMes(mes - 1); }}>←</button>
            <h3 style={{ fontSize: 16, fontWeight: 700 }}>{new Date(anio, mes - 1).toLocaleString("es-AR", { month: "long", year: "numeric" })}</h3>
            <button style={{ ...btn, background: "#fff", color: "#0F172A", border: "1px solid #E2E8F0" }} onClick={() => { mes === 12 ? (setMes(1), setAnio(anio + 1)) : setMes(mes + 1); }}>→</button>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 2 }}>
            {["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"].map(d => (
              <div key={d} style={{ textAlign: "center", fontSize: 10, color: "#94A3B8", padding: 6, textTransform: "uppercase" }}>{d}</div>
            ))}
            {celdas.map((d, i) => (
              <div key={i} style={{ minHeight: 70, border: "1px solid #F1F5F9", borderRadius: 6, padding: 4, background: d ? "#fff" : "#F8FAFC" }}>
                {d && <div style={{ fontSize: 12, color: "#475569", marginBottom: 2 }}>{d}</div>}
                {d && eventosDelDia(d).map(e => (
                  <div key={e.id} style={{ background: colors[e.red_social] || "#94A3B8", color: "#fff", fontSize: 9, padding: "2px 4px", borderRadius: 3, marginBottom: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{e.titulo}</div>
                ))}
              </div>
            ))}
          </div>
        </div>
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Nuevo Evento</h3>
          <label style={{ fontSize: 12, color: "#94A3B8" }}>Título</label>
          <input style={{ ...input, marginBottom: 12 }} value={form.titulo} onChange={e => setForm({ ...form, titulo: e.target.value })} />
          <label style={{ fontSize: 12, color: "#94A3B8" }}>Red Social</label>
          <select style={{ ...input, marginBottom: 12, appearance: "auto" }} value={form.red_social} onChange={e => setForm({ ...form, red_social: e.target.value })}>
            <option>instagram</option><option>facebook</option><option>linkedin</option><option>tiktok</option>
          </select>
          <label style={{ fontSize: 12, color: "#94A3B8" }}>Fecha</label>
          <input style={{ ...input, marginBottom: 12 }} type="datetime-local" value={form.fecha_programada} onChange={e => setForm({ ...form, fecha_programada: e.target.value })} />
          <label style={{ fontSize: 12, color: "#94A3B8" }}>Descripción</label>
          <textarea style={{ ...input, marginBottom: 16, minHeight: 60, resize: "vertical" }} value={form.descripcion} onChange={e => setForm({ ...form, descripcion: e.target.value })} />
          <button style={{ ...btn, width: "100%" }} onClick={crear}>Crear Evento</button>
        </div>
      </div>
    </Layout>
  );
}
