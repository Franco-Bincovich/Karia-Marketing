/**
 * EmptyState — estado vacío con ícono, título y CTA opcional.
 *
 * Uso:
 *   <EmptyState
 *     icon="✍️"
 *     title="Todavía no generaste contenido"
 *     description="Generá tu primer post en segundos"
 *     action={{ label: "Generar contenido", onClick: () => navigate("/contenido") }}
 *   />
 */
export default function EmptyState({ icon, title, description, action, style = {} }) {
  return (
    <div className="empty-state" style={style}>
      {icon && <div className="empty-state-icon">{icon}</div>}
      {title && <h3 className="empty-state-title">{title}</h3>}
      {description && <p className="empty-state-desc">{description}</p>}
      {action && (
        <button
          className="btn btn-primary"
          style={{ marginTop: 8 }}
          onClick={action.onClick}
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
