import { memo, useState } from "react";

const STATUS_COLORS = {
  disponible: "var(--success)",
  bloqueado_v1: "var(--text-muted)",
  solo_premium: "var(--purple-text)",
};
const STATUS_LABELS = { bloqueado_v1: "Próximamente", solo_premium: "Premium" };

function HoverTooltip({ node }) {
  const deps =
    node.dependencias?.length > 0 ? ` — Depende de: ${node.dependencias.join(", ")}` : "";
  return (
    <div
      style={{
        marginTop: 16,
        padding: "12px 16px",
        background: "var(--surface)",
        border: `1px solid ${node.area_color}`,
        borderRadius: 10,
        maxWidth: 420,
        width: "100%",
      }}
    >
      <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text)", marginBottom: 4 }}>
        {node.icon} {node.label}
      </div>
      <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 4 }}>
        {node.rol}
      </div>
      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
        Área: {node.area} — Reporta a: {node.reporta_a || "—"}
        {deps}
      </div>
    </div>
  );
}

function AgentCard({ node, onHover }) {
  const active = node.activo;
  const border = active ? node.area_color : "var(--border)";
  return (
    <div
      onMouseEnter={() => onHover(node)}
      onMouseLeave={() => onHover(null)}
      style={{
        minWidth: 180,
        borderRadius: 10,
        border: `2px solid ${border}`,
        background: "var(--surface)",
        padding: "10px 12px",
        display: "flex",
        flexDirection: "column",
        gap: 6,
        cursor: "default",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ fontSize: 18, flexShrink: 0 }}>{node.icon}</span>
        <span style={{ fontSize: 13, fontWeight: 700, color: "var(--text)" }}>{node.label}</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        {node.estado === "disponible" ? (
          <span
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: active ? "var(--success-text)" : "var(--text-muted)",
            }}
          >
            {active ? "Activo" : "Inactivo"}
          </span>
        ) : (
          <span
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: STATUS_COLORS[node.estado] || "var(--text-muted)",
            }}
          >
            {STATUS_LABELS[node.estado] || node.estado}
          </span>
        )}
        {active && (
          <span
            style={{
              fontSize: 10,
              fontWeight: 600,
              padding: "1px 7px",
              borderRadius: 4,
              background: node.modo === "autopilot" ? "var(--primary)" : "var(--surface-2)",
              color: node.modo === "autopilot" ? "#fff" : "var(--text-secondary)",
            }}
          >
            {node.modo === "autopilot" ? "Auto" : "Copilot"}
          </span>
        )}
      </div>
    </div>
  );
}

function CollabCard({ node, onHover }) {
  return (
    <div
      onMouseEnter={() => onHover(node)}
      onMouseLeave={() => onHover(null)}
      style={{
        minWidth: 140,
        borderRadius: 8,
        border: `1.5px dashed ${node.area_color}60`,
        background: "var(--surface)",
        padding: "6px 10px",
        cursor: "default",
      }}
    >
      <div
        style={{
          fontSize: 9,
          fontWeight: 600,
          color: "var(--text-muted)",
          textTransform: "uppercase",
          letterSpacing: 0.5,
          marginBottom: 2,
        }}
      >
        Colaborador
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <span style={{ fontSize: 13 }}>{node.icon}</span>
        <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text)" }}>{node.label}</span>
      </div>
    </div>
  );
}

function CollabGroup({ collabs, color, onHover }) {
  if (!collabs.length) return null;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginTop: 4 }}>
      <div style={{ width: 1, height: 16, borderLeft: `1.5px dashed ${color}50` }} />
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, justifyContent: "center" }}>
        {collabs.map((c) => (
          <CollabCard key={c.nombre} node={c} onHover={onHover} />
        ))}
      </div>
    </div>
  );
}

function AreaColumn({ name, color, agents, collabsByParent, onHover }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 10,
        flex: "1 1 180px",
        minWidth: 180,
      }}
    >
      <div
        style={{ width: 10, height: 10, borderRadius: "50%", background: color, flexShrink: 0 }}
      />
      <div
        style={{
          fontSize: 11,
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: 1,
          color,
          textAlign: "center",
          padding: "4px 12px",
          border: `1px solid ${color}40`,
          borderRadius: 6,
          background: `${color}10`,
        }}
      >
        {name}
      </div>
      {agents.map((a) => (
        <div
          key={a.nombre}
          style={{ display: "flex", flexDirection: "column", alignItems: "center" }}
        >
          <AgentCard node={a} onHover={onHover} />
          <CollabGroup collabs={collabsByParent[a.nombre] || []} color={color} onHover={onHover} />
        </div>
      ))}
    </div>
  );
}

const OrgChart = memo(function OrgChart({ nodos, areas }) {
  const [hovered, setHovered] = useState(null);
  if (!nodos || !Object.keys(nodos).length) return null;

  const orq = nodos.orquestador;
  const areaOrder = Object.entries(areas)
    .filter(([k]) => k !== "Dirección")
    .sort((a, b) => a[1].orden - b[1].orden);

  // Separate agents from collaborators, group collabs by reporta_a
  const grouped = {};
  const collabsByParent = {};
  for (const [k, v] of Object.entries(nodos)) {
    if (k === "orquestador") continue;
    if (v.es_colaborador) {
      const parent = v.reporta_a || "_none";
      if (!collabsByParent[parent]) collabsByParent[parent] = [];
      collabsByParent[parent].push(v);
    } else {
      if (!grouped[v.area]) grouped[v.area] = [];
      grouped[v.area].push(v);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 0 }}>
      {orq && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            marginBottom: 8,
          }}
        >
          <AgentCard node={orq} onHover={setHovered} />
        </div>
      )}
      <div style={{ width: 2, height: 28, background: "#FF6B0050" }} />
      <div style={{ width: "80%", maxWidth: 900, height: 2, background: "var(--border)" }} />
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: 20,
          width: "100%",
        }}
      >
        {areaOrder.map(([name, info]) => {
          const agents = grouped[name] || [];
          if (!agents.length) return null;
          return (
            <AreaColumn
              key={name}
              name={name}
              color={info.color}
              agents={agents}
              collabsByParent={collabsByParent}
              onHover={setHovered}
            />
          );
        })}
      </div>
      {hovered && <HoverTooltip node={hovered} />}
    </div>
  );
});
export default OrgChart;
