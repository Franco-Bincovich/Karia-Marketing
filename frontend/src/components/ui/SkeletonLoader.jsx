/**
 * SkeletonLoader — imita la forma del contenido mientras carga.
 *
 * Uso:
 *   <SkeletonLoader />           → texto genérico
 *   <SkeletonLoader type="card" count={4} />
 *   <SkeletonLoader type="list" count={6} />
 *   <SkeletonLoader type="metric" count={4} />
 */

function SkeletonCard() {
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div className="skeleton" style={{ height: 18, width: "60%" }} />
      <div className="skeleton" style={{ height: 36 }} />
      <div className="skeleton" style={{ height: 13, width: "40%" }} />
    </div>
  );
}

function SkeletonMetric() {
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div
          className="skeleton skeleton-circle"
          style={{ width: 36, height: 36, borderRadius: 10 }}
        />
        <div className="skeleton" style={{ height: 13, flex: 1, maxWidth: 100 }} />
      </div>
      <div className="skeleton" style={{ height: 28, width: "50%" }} />
    </div>
  );
}

function SkeletonList() {
  return (
    <div
      style={{
        padding: "12px 0",
        borderBottom: "1px solid var(--border-subtle)",
        display: "flex",
        alignItems: "center",
        gap: 12,
      }}
    >
      <div className="skeleton skeleton-circle" style={{ width: 32, height: 32, flexShrink: 0 }} />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 6 }}>
        <div className="skeleton" style={{ height: 13, width: "55%" }} />
        <div className="skeleton" style={{ height: 11, width: "35%" }} />
      </div>
    </div>
  );
}

function SkeletonText() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <div className="skeleton" style={{ height: 16, width: "80%" }} />
      <div className="skeleton" style={{ height: 14, width: "65%" }} />
      <div className="skeleton" style={{ height: 14, width: "50%" }} />
    </div>
  );
}

export default function SkeletonLoader({ type = "text", count = 1, style = {} }) {
  const items = Array.from({ length: count });

  if (type === "card") {
    return (
      <div className="grid-4" style={style}>
        {items.map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (type === "metric") {
    return (
      <div className="grid-4" style={style}>
        {items.map((_, i) => (
          <SkeletonMetric key={i} />
        ))}
      </div>
    );
  }

  if (type === "list") {
    return (
      <div style={style}>
        {items.map((_, i) => (
          <SkeletonList key={i} />
        ))}
      </div>
    );
  }

  return (
    <div style={style}>
      {items.map((_, i) => (
        <SkeletonText key={i} />
      ))}
    </div>
  );
}
