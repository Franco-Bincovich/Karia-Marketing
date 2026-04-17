import { useNavigate } from "react-router-dom";
import Tooltip from "./Tooltip";

/**
 * PlanGate — wrapper que bloquea contenido si el usuario no tiene el plan requerido.
 *
 * Uso:
 *   <PlanGate required="Premium" userPlan={plan}>
 *     <SomeComponent />
 *   </PlanGate>
 *
 *   <PlanGate comingSoon label="Email Marketing">
 *     <SomeComponent />
 *   </PlanGate>
 */
export default function PlanGate({ children, required, userPlan, comingSoon, label }) {
  const navigate = useNavigate();

  // Funcionalidad próximamente
  if (comingSoon) {
    return (
      <div style={{ position: "relative" }}>
        <div style={{ pointerEvents: "none", userSelect: "none", opacity: 0.45 }}>
          {children}
        </div>
        <div className="plan-gate-overlay">
          <span className="plan-gate-icon">🔜</span>
          <span className="plan-gate-text">
            {label || "Próximamente"}
          </span>
          <span className="badge-soon">PRÓXIMAMENTE</span>
        </div>
      </div>
    );
  }

  // Funcionalidad bloqueada por plan
  const isBlocked = required && userPlan && userPlan !== required && userPlan !== "Premium";
  if (!isBlocked) return children;

  return (
    <Tooltip text={`Disponible en ${required}`} delay={200}>
      <div style={{ position: "relative" }}>
        <div style={{ pointerEvents: "none", userSelect: "none", opacity: 0.35 }}>
          {children}
        </div>
        <div
          className="plan-gate-overlay"
          onClick={() => navigate("/onboarding")}
          style={{ cursor: "pointer" }}
        >
          <span className="plan-gate-icon">🔒</span>
          <span className="plan-gate-text">Disponible en {required}</span>
          <button className="btn btn-primary btn-sm" style={{ marginTop: 4 }}>
            Upgradear
          </button>
        </div>
      </div>
    </Tooltip>
  );
}
