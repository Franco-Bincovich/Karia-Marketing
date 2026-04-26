import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";

const card = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 14,
  padding: 20,
  marginBottom: 16,
};
const input = {
  width: "100%",
  padding: "10px 12px",
  border: "1.5px solid var(--border)",
  borderRadius: 9,
  fontSize: 14,
  outline: "none",
  marginBottom: 12,
  boxSizing: "border-box",
  background: "var(--surface)",
  color: "var(--text)",
};
const btn = {
  padding: "10px 20px",
  background: "var(--primary)",
  color: "#fff",
  border: "none",
  borderRadius: 9,
  fontSize: 14,
  fontWeight: 600,
  cursor: "pointer",
};
const th = {
  textAlign: "left",
  fontSize: 10,
  color: "var(--text-muted)",
  textTransform: "uppercase",
  padding: "8px 12px",
  borderBottom: "1px solid var(--border)",
  fontWeight: 600,
};
const td = {
  padding: "10px 12px",
  fontSize: 13,
  borderBottom: "1px solid var(--border-subtle)",
  color: "var(--text-secondary)",
};

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

  useEffect(() => {
    get(ENDPOINTS.CONTACTOS)
      .then((r) => setContactos(r.data.data || []))
      .catch(() => {});
  }, []);

  async function buscar() {
    if (!rubro) return;
    setLoading(true);
    setError("");
    try {
      const { data } = await post(ENDPOINTS.CONTACTOS_BUSCAR, {
        rubro,
        ubicacion,
        cantidad: Number(cantidad),
      });
      setResultados(data.data || data || []);
    } catch (e) {
      setError(e.response?.data?.message || "Error en búsqueda");
    } finally {
      setLoading(false);
    }
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
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>
          Buscar Prospectos
        </h3>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr auto auto",
            gap: 12,
            alignItems: "end",
          }}
        >
          <div>
            <label style={{ fontSize: 12, color: "var(--text-muted)" }}>Rubro</label>
            <input
              style={input}
              value={rubro}
              onChange={(e) => setRubro(e.target.value)}
              placeholder="Ej: tecnología"
            />
          </div>
          <div>
            <label style={{ fontSize: 12, color: "var(--text-muted)" }}>Ubicación</label>
            <input
              style={input}
              value={ubicacion}
              onChange={(e) => setUbicacion(e.target.value)}
              placeholder="Ej: Buenos Aires"
            />
          </div>
          <div>
            <label style={{ fontSize: 12, color: "var(--text-muted)" }}>Cantidad</label>
            <input
              style={{ ...input, width: 80 }}
              type="number"
              value={cantidad}
              onChange={(e) => setCantidad(e.target.value)}
            />
          </div>
          <button style={btn} onClick={buscar} disabled={loading}>
            {loading ? "Buscando..." : "Buscar con IA"}
          </button>
        </div>
        {error && (
          <div className="msg-error" style={{ marginTop: 8, borderRadius: 8 }}>
            <span style={{ flex: 1 }}>{error}</span>
            <button className="msg-dismiss" onClick={() => setError("")}>
              ×
            </button>
          </div>
        )}
      </div>

      {resultados.length > 0 && (
        <div style={card}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: "var(--text)" }}>
              Resultados ({resultados.length})
            </h3>
            <button style={btn} onClick={guardar}>
              Guardar selección ({seleccionados.size})
            </button>
          </div>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={th}></th>
                  <th style={th}>Nombre</th>
                  <th style={th}>Empresa</th>
                  <th style={th}>Email</th>
                  <th style={th}>Cargo</th>
                  <th style={th}>Confianza</th>
                </tr>
              </thead>
              <tbody>
                {resultados.map((c, i) => (
                  <tr
                    key={i}
                    style={{
                      background: seleccionados.has(i) ? "var(--primary-light)" : "transparent",
                    }}
                  >
                    <td style={td}>
                      <input
                        type="checkbox"
                        checked={seleccionados.has(i)}
                        onChange={() => toggle(i)}
                      />
                    </td>
                    <td style={{ ...td, color: "var(--text)", fontWeight: 500 }}>{c.nombre}</td>
                    <td style={td}>{c.empresa}</td>
                    <td style={td}>{c.email_empresarial}</td>
                    <td style={td}>{c.cargo}</td>
                    <td style={td}>
                      <span
                        style={{
                          background: c.confianza > 0.7 ? "var(--success-bg)" : "var(--warning-bg)",
                          color: c.confianza > 0.7 ? "var(--success-text)" : "var(--warning-text)",
                          padding: "2px 8px",
                          borderRadius: 6,
                          fontSize: 11,
                          fontWeight: 600,
                        }}
                      >
                        {Math.round((c.confianza || 0) * 100)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>
          Contactos Guardados ({contactos.length})
        </h3>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Nombre</th>
                <th style={th}>Empresa</th>
                <th style={th}>Email</th>
                <th style={th}>Score</th>
                <th style={th}>Estado</th>
              </tr>
            </thead>
            <tbody>
              {contactos.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    style={{ ...td, textAlign: "center", color: "var(--text-muted)" }}
                  >
                    Sin contactos guardados
                  </td>
                </tr>
              )}
              {contactos.map((c) => (
                <tr key={c.id}>
                  <td style={{ ...td, color: "var(--text)", fontWeight: 500 }}>{c.nombre}</td>
                  <td style={td}>{c.empresa}</td>
                  <td style={td}>{c.email_empresarial}</td>
                  <td style={td}>{c.score}</td>
                  <td style={td}>
                    <span
                      style={{
                        background: "var(--blue-bg)",
                        color: "var(--blue-text)",
                        padding: "2px 8px",
                        borderRadius: 6,
                        fontSize: 11,
                        fontWeight: 600,
                      }}
                    >
                      {c.estado}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}
