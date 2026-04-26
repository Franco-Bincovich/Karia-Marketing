import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const card = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 12,
  padding: 20,
  marginBottom: 16,
};
const inputStyle = {
  width: "100%",
  padding: "10px 12px",
  border: "1.5px solid var(--border)",
  borderRadius: 9,
  fontSize: 14,
  outline: "none",
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
const btnApprove = { ...btn, background: "var(--success)" };
const btnPause = { ...btn, background: "var(--danger)", fontSize: 12, padding: "6px 12px" };
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

const estadoBadge = (e) => {
  const map = {
    activa: ["var(--success-bg)", "var(--success-text)"],
    pendiente_aprobacion: ["var(--warning-bg)", "var(--warning-text)"],
    pausada: ["var(--danger-bg)", "var(--danger-text)"],
    borrador: ["var(--surface-2)", "var(--text-secondary)"],
  };
  const [bg, color] = map[e] || ["var(--surface-2)", "var(--text-secondary)"];
  return {
    background: bg,
    color,
    padding: "2px 8px",
    borderRadius: 6,
    fontSize: 11,
    fontWeight: 600,
  };
};

export default function Ads() {
  const { user } = useAuth();

  if (user?.rol !== "superadmin") {
    return (
      <Layout title="Campañas Ads">
        <div style={{ ...card, padding: 60, textAlign: "center" }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>⊕</div>
          <div style={{ display: "flex", justifyContent: "center", gap: 8, marginBottom: 12 }}>
            <h2 style={{ fontSize: 20, fontWeight: 700, color: "var(--text)" }}>Campañas Ads</h2>
            <span
              style={{
                background: "var(--purple-bg)",
                color: "var(--purple-text)",
                padding: "3px 10px",
                borderRadius: 6,
                fontSize: 11,
                fontWeight: 700,
                alignSelf: "center",
              }}
            >
              V2
            </span>
          </div>
          <p style={{ fontSize: 14, color: "var(--text-muted)", maxWidth: 400, margin: "0 auto" }}>
            Este módulo estará disponible en la próxima versión de NEXO.
          </p>
        </div>
      </Layout>
    );
  }

  return <AdsPanel />;
}

function AdsPanel() {
  const { get, post } = useApi();
  const [campanas, setCampanas] = useState([]);
  const [umbrales, setUmbrales] = useState({});
  const [form, setForm] = useState({
    nombre: "",
    plataforma: "meta",
    presupuesto_diario: "",
    objetivo: "",
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    cargar();
  }, []);

  function cargar() {
    get(ENDPOINTS.ADS_CAMPANAS)
      .then((r) => setCampanas(r.data.data || []))
      .catch(() => {});
    get(ENDPOINTS.ADS_UMBRALES)
      .then((r) => setUmbrales(r.data || {}))
      .catch(() => {});
  }

  async function crear() {
    if (!form.nombre || !form.presupuesto_diario) return;
    setLoading(true);
    await post(ENDPOINTS.ADS_CAMPANAS, {
      ...form,
      presupuesto_diario: Number(form.presupuesto_diario),
    });
    setForm({ nombre: "", plataforma: "meta", presupuesto_diario: "", objetivo: "" });
    cargar();
    setLoading(false);
  }

  async function aprobar(id) {
    await post(ENDPOINTS.ADS_APROBAR(id), {});
    cargar();
  }
  async function pausar(id) {
    await post(ENDPOINTS.ADS_PAUSAR(id), { motivo: "manual" });
    cargar();
  }

  return (
    <Layout title="Campañas Ads">
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>
          Nueva Campaña
        </h3>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr 1fr auto",
            gap: 12,
            alignItems: "end",
          }}
        >
          <div>
            <label style={{ fontSize: 12, color: "var(--text-muted)" }}>Nombre</label>
            <input
              style={inputStyle}
              value={form.nombre}
              onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            />
          </div>
          <div>
            <label style={{ fontSize: 12, color: "var(--text-muted)" }}>Plataforma</label>
            <select
              style={{ ...inputStyle, appearance: "auto" }}
              value={form.plataforma}
              onChange={(e) => setForm({ ...form, plataforma: e.target.value })}
            >
              <option>meta</option>
              <option>google</option>
            </select>
          </div>
          <div>
            <label style={{ fontSize: 12, color: "var(--text-muted)" }}>Presupuesto/día ($)</label>
            <input
              style={inputStyle}
              type="number"
              value={form.presupuesto_diario}
              onChange={(e) => setForm({ ...form, presupuesto_diario: e.target.value })}
            />
          </div>
          <div>
            <label style={{ fontSize: 12, color: "var(--text-muted)" }}>Objetivo</label>
            <input
              style={inputStyle}
              value={form.objetivo}
              onChange={(e) => setForm({ ...form, objetivo: e.target.value })}
            />
          </div>
          <button style={btn} onClick={crear} disabled={loading}>
            Crear
          </button>
        </div>
      </div>

      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>
          Campañas ({campanas.length})
        </h3>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Nombre</th>
                <th style={th}>Plataforma</th>
                <th style={th}>Presupuesto/día</th>
                <th style={th}>Estado</th>
                <th style={th}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {campanas.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    style={{ ...td, textAlign: "center", color: "var(--text-muted)" }}
                  >
                    No hay campañas
                  </td>
                </tr>
              )}
              {campanas.map((c) => (
                <tr key={c.id}>
                  <td style={{ ...td, fontWeight: 500, color: "var(--text)" }}>{c.nombre}</td>
                  <td style={td}>{c.plataforma}</td>
                  <td style={td}>${c.presupuesto_diario}</td>
                  <td style={td}>
                    <span style={estadoBadge(c.estado)}>{c.estado}</span>
                  </td>
                  <td style={td}>
                    {c.estado === "pendiente_aprobacion" && (
                      <button style={btnApprove} onClick={() => aprobar(c.id)}>
                        Aprobar
                      </button>
                    )}
                    {c.estado === "activa" && (
                      <button style={btnPause} onClick={() => pausar(c.id)}>
                        Pausar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
        {[
          ["CPA Máximo", umbrales.cpa_maximo],
          ["ROAS Mínimo", umbrales.roas_minimo],
          ["Gasto Diario Máx", umbrales.gasto_diario_maximo],
        ].map(([label, val]) => (
          <div key={label} style={card}>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 26, fontWeight: 800, color: "var(--text)" }}>
              {val != null ? `$${val}` : "--"}
            </div>
            {val == null && (
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                Sin configurar
              </div>
            )}
          </div>
        ))}
      </div>
    </Layout>
  );
}
