import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const card = { background: "#fff", border: "1px solid #E2E8F0", borderRadius: 14, padding: 16 };

export default function FeatureFlags() {
  const { user } = useAuth();
  const { get, patch } = useApi();
  const [flags, setFlags] = useState([]);
  const clienteId = user?.cliente_id;

  useEffect(() => {
    if (!clienteId) return;
    get(ENDPOINTS.FEATURE_FLAGS, { cliente_id: clienteId }).then(({ data }) => setFlags(data)).catch(() => {});
  }, [clienteId]);

  async function toggleFlag(flag) {
    try {
      const { data } = await patch(`${ENDPOINTS.FEATURE_FLAG(flag.feature)}?cliente_id=${clienteId}`, { habilitado: !flag.habilitado, modo: flag.modo });
      setFlags(prev => prev.map(f => f.id === flag.id ? data : f));
    } catch {}
  }

  async function changeModo(flag, modo) {
    try {
      const { data } = await patch(`${ENDPOINTS.FEATURE_FLAG(flag.feature)}?cliente_id=${clienteId}`, { habilitado: flag.habilitado, modo });
      setFlags(prev => prev.map(f => f.id === flag.id ? data : f));
    } catch {}
  }

  return (
    <Layout title="Feature Flags">
      {!flags.length ? <p style={{ color: "#94A3B8", fontSize: 13 }}>No hay feature flags configurados.</p> : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(300px,1fr))", gap: 16 }}>
          {flags.map(flag => (
            <div key={flag.id} style={card}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <span style={{ fontWeight: 700, fontSize: 14 }}>{flag.feature}</span>
                <button onClick={() => toggleFlag(flag)} style={{
                  padding: "4px 14px", borderRadius: 20, border: "none", fontWeight: 600, fontSize: 12, cursor: "pointer",
                  background: flag.habilitado ? "#10B981" : "#E2E8F0",
                  color: flag.habilitado ? "#fff" : "#94A3B8",
                }}>{flag.habilitado ? "ON" : "OFF"}</button>
              </div>
              <select value={flag.modo} onChange={e => changeModo(flag, e.target.value)} disabled={!flag.habilitado}
                style={{ padding: "6px 10px", borderRadius: 9, border: "1px solid #E2E8F0", fontSize: 13, background: "#fff", width: "100%" }}>
                {["ia", "manual", "autopilot", "copilot"].map(m => <option key={m}>{m}</option>)}
              </select>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
