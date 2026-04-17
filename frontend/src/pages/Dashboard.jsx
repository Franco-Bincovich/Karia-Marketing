import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import SkeletonLoader from "../components/ui/SkeletonLoader";
import EmptyState from "../components/ui/EmptyState";
import Badge from "../components/ui/Badge";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "Buenos días";
  if (h < 20) return "Buenas tardes";
  return "Buenas noches";
}

function MetricCard({ label, value, icon, color, suffix = "", prefix = "" }) {
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{
          width: 40, height: 40, borderRadius: 12,
          background: color || "var(--primary-light)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 18, flexShrink: 0,
        }}>{icon}</div>
        <span style={{ fontSize: "var(--text-sm)", color: "var(--text-muted)", fontWeight: 500 }}>{label}</span>
      </div>
      <div style={{ fontSize: 28, fontWeight: 800, color: "var(--text)", lineHeight: 1 }}>
        {prefix}{typeof value === "number" ? value.toLocaleString("es-AR") : (value || 0)}{suffix}
      </div>
    </div>
  );
}

function QuickAction({ icon, label, onClick, color }) {
  return (
    <button
      onClick={onClick}
      className="card"
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 12,
        padding: 20,
        cursor: "pointer",
        border: "1px solid var(--border)",
        background: "var(--surface)",
        borderRadius: "var(--radius-lg)",
        transition: "all var(--t-fast)",
        textAlign: "center",
        minHeight: 100,
      }}
      onMouseEnter={e => { e.currentTarget.style.borderColor = "var(--primary)"; e.currentTarget.style.background = "var(--primary-light)"; }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = "var(--border)"; e.currentTarget.style.background = "var(--surface)"; }}
    >
      <div style={{
        width: 44, height: 44, borderRadius: 12,
        background: color || "var(--primary-light)",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 20,
      }}>{icon}</div>
      <span style={{ fontSize: "var(--text-sm)", fontWeight: 600, color: "var(--text-secondary)" }}>{label}</span>
    </button>
  );
}

const ESTADO_MAP = {
  publicado:           { label: "Publicado",  variant: "blue" },
  aprobado:            { label: "Aprobado",   variant: "success" },
  pendiente_aprobacion:{ label: "Pendiente",  variant: "warning" },
  rechazado:           { label: "Rechazado",  variant: "danger" },
  borrador:            { label: "Borrador",   variant: "gray" },
};

export default function Dashboard() {
  const { get } = useApi();
  const { user, completitud, marcaActiva } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [contenido, setContenido] = useState([]);
  const [alertas, setAlertas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const today = new Date().toLocaleDateString("es-AR", { weekday: "long", day: "numeric", month: "long" });
  const firstName = user?.nombre?.split(" ")[0] || "Usuario";

  useEffect(() => {
    if (!marcaActiva) { setLoading(false); return; }
    Promise.all([
      get(ENDPOINTS.ANALYTICS_DASHBOARD).catch(() => null),
      get(ENDPOINTS.CONTENIDO).catch(() => null),
      get(ENDPOINTS.LISTENING_ALERTAS).catch(() => null),
    ]).then(([dash, cont, alerts]) => {
      if (dash) setData(dash.data);
      if (cont) setContenido((cont.data?.data || []).slice(0, 3));
      if (alerts) setAlertas((alerts.data?.data || []).filter(a => !a.leida).slice(0, 3));
    }).catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [marcaActiva?.id]);

  const metricas = data?.metricas_30d || {};
  const plan = user?.plan || "Basic";
  const isBasic = plan === "Basic";

  return (
    <Layout title="Dashboard">
      {/* ── Greeting ── */}
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: "var(--text-2xl)", fontWeight: 800, color: "var(--text)", lineHeight: 1.2, marginBottom: 4 }}>
          {getGreeting()}, {firstName} 👋
        </h2>
        <p style={{ fontSize: "var(--text-sm)", color: "var(--text-muted)", textTransform: "capitalize" }}>{today}</p>
      </div>

      {/* ── Onboarding progress ── */}
      {completitud < 100 && (
        <div style={{
          background: "linear-gradient(135deg, var(--primary-light) 0%, var(--gold-light) 100%)",
          border: "1px solid rgba(255,107,43,0.2)",
          borderRadius: "var(--radius-lg)",
          padding: "16px 20px",
          marginBottom: 24,
          display: "flex",
          alignItems: "center",
          gap: 16,
          flexWrap: "wrap",
        }}>
          <div style={{ flex: 1, minWidth: 200 }}>
            <div style={{ fontSize: "var(--text-sm)", fontWeight: 700, color: "var(--primary)", marginBottom: 8 }}>
              Completá tu perfil de marca — {completitud}%
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${completitud}%` }} />
            </div>
          </div>
          <button className="btn btn-primary btn-sm" onClick={() => navigate("/onboarding")}>
            Completar
          </button>
        </div>
      )}

      {/* ── Crisis alert ── */}
      {alertas.length > 0 && (
        <div className="msg-error" style={{ marginBottom: 20, borderRadius: "var(--radius-lg)" }}>
          <span style={{ fontSize: 18, flexShrink: 0 }}>🚨</span>
          <div style={{ flex: 1 }}>
            <strong>{alertas.length} alerta{alertas.length > 1 ? "s" : ""} activa{alertas.length > 1 ? "s" : ""}</strong>
            <span style={{ fontSize: 12, marginLeft: 8 }}>{alertas[0]?.mensaje}</span>
          </div>
          <button className="btn btn-sm" style={{ background: "var(--danger)", color: "#fff", border: "none" }} onClick={() => navigate("/social-listening")}>
            Ver ahora
          </button>
        </div>
      )}

      {/* ── Metric cards ── */}
      {loading ? (
        <SkeletonLoader type="metric" count={4} style={{ marginBottom: 24 }} />
      ) : (
        <div className="grid-4" style={{ marginBottom: 24 }}>
          <MetricCard label="Posts este mes"         value={metricas.posts_mes || 0}       icon="✎" color="var(--primary-light)" />
          <MetricCard label="Menciones hoy"          value={metricas.menciones_hoy || 0}   icon="◎" color="var(--blue-bg)" />
          <MetricCard label="Engagement promedio"    value={metricas.engagement || 0}       icon="◬" color="var(--purple-bg)" suffix="%" />
          <MetricCard label="Automatizaciones activas" value={metricas.automatizaciones || 0} icon="↻" color="var(--success-bg)" />
        </div>
      )}

      {/* ── Usage bar for Basic ── */}
      {isBasic && metricas.posts_mes !== undefined && (
        <div className="card card-sm" style={{ marginBottom: 24, display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
              <span style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)", fontWeight: 500 }}>
                {metricas.posts_mes || 0} / 30 posts este mes
              </span>
              {(metricas.posts_mes || 0) >= 24 && (
                <Badge variant="warning">Cercano al límite</Badge>
              )}
            </div>
            <div className="progress-track">
              <div
                className={`progress-fill ${(metricas.posts_mes || 0) >= 30 ? "danger" : (metricas.posts_mes || 0) >= 24 ? "warning" : ""}`}
                style={{ width: `${Math.min(100, ((metricas.posts_mes || 0) / 30) * 100)}%` }}
              />
            </div>
          </div>
          <button className="btn btn-sm" style={{ background: "var(--gold-light)", color: "var(--gold)", border: "1px solid rgba(245,166,35,0.3)", fontWeight: 700 }}>
            ✦ Upgrade
          </button>
        </div>
      )}

      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* ── Quick actions ── */}
        <div>
          <div className="section-label" style={{ marginBottom: 12 }}>Acciones rápidas</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <QuickAction icon="✎" label="Generar contenido"  color="var(--primary-light)" onClick={() => navigate("/contenido")} />
            <QuickAction icon="▦" label="Ver calendario"     color="var(--blue-bg)"       onClick={() => navigate("/calendario")} />
            <QuickAction icon="▤" label="Ver reportes"       color="var(--purple-bg)"     onClick={() => navigate("/reporting")} />
            <QuickAction icon="◌" label="Escanear menciones" color="var(--warning-bg)"    onClick={() => navigate("/social-listening")} />
          </div>
        </div>

        {/* ── Recent activity ── */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <h3 style={{ fontSize: "var(--text-md)", fontWeight: 700, color: "var(--text)" }}>Actividad reciente</h3>
            <button className="btn btn-ghost btn-xs" onClick={() => navigate("/contenido")}>Ver todo</button>
          </div>

          {loading ? (
            <SkeletonLoader type="list" count={3} />
          ) : contenido.length === 0 ? (
            <EmptyState
              icon="✎"
              title="Todavía no generaste contenido"
              description="Generá tu primer post en segundos"
              action={{ label: "Generar ahora", onClick: () => navigate("/contenido") }}
            />
          ) : (
            <div>
              {contenido.map(c => {
                const estado = ESTADO_MAP[c.estado] || ESTADO_MAP.borrador;
                const copy = c[`copy_${c.variante_seleccionada || "a"}`] || c.copy_a || "";
                return (
                  <div key={c.id} style={{
                    padding: "10px 0",
                    borderBottom: "1px solid var(--border-subtle)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: 10,
                  }}>
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div style={{ fontSize: "var(--text-sm)", fontWeight: 500, color: "var(--text)", marginBottom: 2 }}>
                        {c.tema || c.red_social} — {c.formato}
                      </div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {copy.slice(0, 60) || "—"}
                      </div>
                    </div>
                    <Badge variant={estado.variant}>{estado.label}</Badge>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* ── Upgrade banner for Basic ── */}
      {isBasic && (
        <div className="upgrade-banner">
          <div>
            <div className="upgrade-banner-title">✦ Pasá a Premium</div>
            <div className="upgrade-banner-text" style={{ marginTop: 4 }}>
              Desbloqueá posts ilimitados, Analytics avanzado, Automatizaciones y más IA.
            </div>
          </div>
          <button
            className="btn btn-primary"
            style={{ flexShrink: 0 }}
            onClick={() => navigate("/onboarding")}
          >
            Ver planes
          </button>
        </div>
      )}
    </Layout>
  );
}
