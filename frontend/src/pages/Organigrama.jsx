import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import OrgChart from "../components/OrgChart";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import SkeletonLoader from "../components/ui/SkeletonLoader";

const card = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, padding: 20, marginBottom: 16 };

export default function Organigrama() {
  const { get } = useApi();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    get(ENDPOINTS.ORGANIGRAMA)
      .then(r => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Layout title="Organigrama"><SkeletonLoader type="card" count={2} /></Layout>;

  const nodos = data?.nodos || {};
  const areas = data?.areas || {};
  const totalActivos = Object.values(nodos).filter(n => n.activo).length;
  const totalAgentes = Object.keys(nodos).length;

  return (
    <Layout title="Organigrama de la Agencia">
      {/* Header */}
      <div style={card}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
          <div>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: "var(--text)", marginBottom: 4 }}>Equipo NEXO</h3>
            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
              {totalActivos} de {totalAgentes} agentes activos — {Object.keys(areas).length} áreas
            </span>
          </div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {Object.entries(areas).filter(([k]) => k !== "Dirección").map(([name, info]) => (
              <span key={name} style={{
                fontSize: 11, fontWeight: 600, padding: "3px 10px", borderRadius: 6,
                border: `1px solid ${info.color}30`, color: info.color, background: `${info.color}12`,
              }}>{name}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div style={{ ...card, padding: 24 }}>
        <OrgChart nodos={nodos} areas={areas} />
      </div>

      {/* Legend */}
      <div style={card}>
        <h4 style={{ fontSize: 13, fontWeight: 700, color: "var(--text)", marginBottom: 10 }}>Leyenda</h4>
        <div style={{ display: "flex", alignItems: "center", gap: 24, flexWrap: "wrap", fontSize: 12, color: "var(--text-secondary)" }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><span style={{ color: "var(--success-text)" }}>●</span> Activo</span>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><span style={{ color: "var(--text-muted)" }}>●</span> Inactivo</span>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><span style={{ background: "var(--primary)", color: "#fff", fontSize: 10, padding: "1px 6px", borderRadius: 4 }}>Auto</span> Autopilot</span>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><span style={{ background: "var(--surface-2)", color: "var(--text-secondary)", fontSize: 10, padding: "1px 6px", borderRadius: 4 }}>Copilot</span> Manual</span>
        </div>
      </div>
    </Layout>
  );
}
