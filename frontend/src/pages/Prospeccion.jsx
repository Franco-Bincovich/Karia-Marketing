import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 20, marginBottom: 16 };
const input = {
  width: "100%", padding: "10px 12px", border: "1.5px solid #E2E8F0", borderRadius: 9,
  fontSize: 14, outline: "none", marginBottom: 12, boxSizing: "border-box",
};
const btn = { padding: "10px 20px", background: "#F97316", color: "#fff", border: "none",
  borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnSec = { ...btn, background: "#fff", color: "#0F172A", border: "1px solid #E2E8F0" };
const th = { textAlign: "left", fontSize: 10, color: "#94A3B8", textTransform: "uppercase",
  padding: "8px 12px", borderBottom: "1px solid #E2E8F0" };
const td = { padding: "10px 12px", fontSize: 13, borderBottom: "1px solid #F1F5F9", color: "#475569" };

export default function Prospeccion() {
  const { get, post } = useApi();
  const [rubro, setRubro] = useState("");
  const [ubicacion, setUbicacion] = useState("");
  const [cantidad, setCantidad] = useState(10);
  const [resultados, setResultados] = useState([]);
  const [contactos, setContactos] = useState([]);
  const [seleccionados, setSeleccionados] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { get(ENDPOINTS.CONTACTOS).then(r => setContactos(r.data.data || [])).catch(() => {}); }, []);

  async function buscar() {
    if (!rubro) return;
    setLoading(true); setError("");
    try {
      const { data } = await post(ENDPOINTS.CONTACTOS_BUSCAR, { rubro, ubicacion, cantidad: Number(cantidad) });
      setResultados(data.data || data || []);
    } catch (e) { setError(e.response?.data?.message || "Error en búsqueda"); }
    finally { setLoading(false); }
  }

  async function guardar() {
    const items = resultados.filter((_, i) => seleccionados.has(i));
    if (!items.length) return;
    try {
      await post(ENDPOINTS.CONTACTOS_GUARDAR, { contactos: items });
      setSeleccionados(new Set());
      const { data } = await get(ENDPOINTS.CONTACTOS);
      setContactos(data.data || []);
    } catch {}
  }

  function toggle(i) {
    const s = new Set(seleccionados);
    s.has(i) ? s.delete(i) : s.add(i);
    setSeleccionados(s);
  }

  return (
    <Layout title="Prospección IA">
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Buscar Prospectos</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto auto", gap: 12, alignItems: "end" }}>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Rubro</label><input style={input} value={rubro} onChange={e => setRubro(e.target.value)} placeholder="Ej: tecnología" /></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Ubicación</label><input style={input} value={ubicacion} onChange={e => setUbicacion(e.target.value)} placeholder="Ej: Buenos Aires" /></div>
          <div><label style={{ fontSize: 12, color: "#94A3B8" }}>Cantidad</label><input style={{...input, width: 80}} type="number" value={cantidad} onChange={e => setCantidad(e.target.value)} /></div>
          <button style={btn} onClick={buscar} disabled={loading}>{loading ? "Buscando..." : "Buscar con IA"}</button>
        </div>
        {error && <p style={{ color: "#EF4444", fontSize: 13, marginTop: 8 }}>{error}</p>}
      </div>
      {resultados.length > 0 && (
        <div style={card}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
            <h3 style={{ fontSize: 15, fontWeight: 700 }}>Resultados ({resultados.length})</h3>
            <button style={btn} onClick={guardar}>Guardar selección ({seleccionados.size})</button>
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th style={th}></th><th style={th}>Nombre</th><th style={th}>Empresa</th><th style={th}>Email</th><th style={th}>Cargo</th><th style={th}>Confianza</th></tr></thead>
            <tbody>{resultados.map((c, i) => (
              <tr key={i} style={{ background: seleccionados.has(i) ? "#FFF7ED" : "transparent" }}>
                <td style={td}><input type="checkbox" checked={seleccionados.has(i)} onChange={() => toggle(i)} /></td>
                <td style={td}>{c.nombre}</td><td style={td}>{c.empresa}</td>
                <td style={td}>{c.email_empresarial}</td><td style={td}>{c.cargo}</td>
                <td style={td}><span style={{ background: c.confianza > 0.7 ? "#DCFCE7" : "#FEF3C7", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600, color: c.confianza > 0.7 ? "#15803D" : "#B45309" }}>{Math.round((c.confianza || 0) * 100)}%</span></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      )}
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Contactos Guardados ({contactos.length})</h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead><tr><th style={th}>Nombre</th><th style={th}>Empresa</th><th style={th}>Email</th><th style={th}>Score</th><th style={th}>Estado</th></tr></thead>
          <tbody>{contactos.map(c => (
            <tr key={c.id}><td style={td}>{c.nombre}</td><td style={td}>{c.empresa}</td>
              <td style={td}>{c.email_empresarial}</td><td style={td}>{c.score}</td>
              <td style={td}><span style={{ background: "#DBEAFE", color: "#1D4ED8", padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{c.estado}</span></td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </Layout>
  );
}
