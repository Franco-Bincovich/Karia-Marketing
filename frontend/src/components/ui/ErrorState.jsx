/**
 * ErrorState — estado de error amigable con botón de reintentar.
 *
 * Uso:
 *   <ErrorState onRetry={loadData} />
 *   <ErrorState message="No se pudo cargar el reporte" onRetry={loadData} />
 */
export default function ErrorState({ message, onRetry, style = {} }) {
  return (
    <div className="error-state" style={style}>
      <div className="error-state-icon">⚠️</div>
      <h3 className="error-state-title">Algo salió mal</h3>
      <p className="error-state-desc">
        {message || "No pudimos cargar esta sección. Intentá de nuevo."}
      </p>
      {onRetry && (
        <button className="btn btn-ghost btn-sm" style={{ marginTop: 8 }} onClick={onRetry}>
          Reintentar
        </button>
      )}
    </div>
  );
}
