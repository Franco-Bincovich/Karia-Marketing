/**
 * Panel de feature flags por marca/cliente.
 */

import { useEffect, useState } from "react";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const MODOS = ["ia", "manual", "autopilot", "copilot"];

const s = {
  page: { padding: "var(--spacing-8)", fontFamily: "var(--font-sans)" },
  title: { fontSize: "var(--font-size-2xl)", fontWeight: 700, marginBottom: "var(--spacing-6)" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "var(--spacing-4)" },
  card: { background: "var(--color-surface)", borderRadius: "var(--radius-md)", padding: "var(--spacing-4)", boxShadow: "var(--shadow-sm)" },
  cardHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--spacing-3)" },
  featureName: { fontWeight: 700, fontSize: "var(--font-size-base)" },
  toggle: { cursor: "pointer", padding: "4px 12px", borderRadius: "var(--radius-full)", border: "none", fontWeight: 600, fontSize: "var(--font-size-xs)" },
  toggleOn: { background: "var(--color-success)", color: "#fff" },
  toggleOff: { background: "var(--color-border)", color: "var(--color-text-muted)" },
  select: { padding: "6px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--color-border)", fontSize: "var(--font-size-sm)", background: "#fff" },
  empty: { color: "var(--color-text-muted)", textAlign: "center", padding: "var(--spacing-12)" },
};

export default function FeatureFlags() {
  const { user } = useAuth();
  const { get, patch } = useApi();
  const [flags, setFlags] = useState([]);

  const clienteId = user?.cliente_id;

  useEffect(() => {
    if (!clienteId) return;
    get(ENDPOINTS.FEATURE_FLAGS, { cliente_id: clienteId }).then(({ data }) => setFlags(data)).catch(() => {});
  }, [get, clienteId]);

  async function toggleFlag(flag) {
    const updated = { habilitado: !flag.habilitado, modo: flag.modo };
    try {
      const { data } = await patch(`${ENDPOINTS.FEATURE_FLAG(flag.feature)}?cliente_id=${clienteId}`, updated);
      setFlags((prev) => prev.map((f) => (f.id === flag.id ? data : f)));
    } catch {}
  }

  async function changeModo(flag, modo) {
    try {
      const { data } = await patch(`${ENDPOINTS.FEATURE_FLAG(flag.feature)}?cliente_id=${clienteId}`, { habilitado: flag.habilitado, modo });
      setFlags((prev) => prev.map((f) => (f.id === flag.id ? data : f)));
    } catch {}
  }

  if (!flags.length) {
    return (
      <div style={s.page}>
        <h1 style={s.title}>Feature Flags</h1>
        <p style={s.empty}>No hay feature flags configurados para este cliente.</p>
      </div>
    );
  }

  return (
    <div style={s.page}>
      <h1 style={s.title}>Feature Flags</h1>
      <div style={s.grid}>
        {flags.map((flag) => (
          <div key={flag.id} style={s.card}>
            <div style={s.cardHeader}>
              <span style={s.featureName}>{flag.feature}</span>
              <button
                style={{ ...s.toggle, ...(flag.habilitado ? s.toggleOn : s.toggleOff) }}
                onClick={() => toggleFlag(flag)}
              >
                {flag.habilitado ? "ON" : "OFF"}
              </button>
            </div>
            <select
              style={s.select}
              value={flag.modo}
              onChange={(e) => changeModo(flag, e.target.value)}
              disabled={!flag.habilitado}
            >
              {MODOS.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
}
