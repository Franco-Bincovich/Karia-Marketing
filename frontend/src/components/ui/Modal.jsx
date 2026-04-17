import { useEffect } from "react";

/**
 * Modal — diálogo con backdrop y animación suave.
 *
 * Uso:
 *   <Modal open={open} onClose={() => setOpen(false)} title="Confirmar acción">
 *     <p>¿Estás seguro?</p>
 *     <div className="modal-footer">
 *       <button className="btn btn-secondary" onClick={() => setOpen(false)}>Cancelar</button>
 *       <button className="btn btn-danger" onClick={confirm}>Confirmar</button>
 *     </div>
 *   </Modal>
 */
export default function Modal({ open, onClose, title, children, size = "default" }) {
  // Cerrar con Escape
  useEffect(() => {
    if (!open) return;
    function handleKey(e) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  // Bloquear scroll del body
  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  if (!open) return null;

  return (
    <div className="modal-backdrop" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className={`modal ${size === "lg" ? "modal-lg" : ""}`}>
        {(title || onClose) && (
          <div className="modal-header">
            {title && <h2 className="modal-title">{title}</h2>}
            <button className="modal-close" onClick={onClose} aria-label="Cerrar">×</button>
          </div>
        )}
        {children}
      </div>
    </div>
  );
}

/** Confirmación destructiva rápida */
export function ConfirmModal({ open, onClose, onConfirm, title, message, confirmLabel = "Confirmar", dangerous = false }) {
  return (
    <Modal open={open} onClose={onClose} title={title || "Confirmar acción"}>
      <p style={{ fontSize: "var(--text-base)", color: "var(--text-secondary)", lineHeight: 1.5 }}>
        {message || "¿Estás seguro? Esta acción no se puede deshacer."}
      </p>
      <div className="modal-footer">
        <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
        <button
          className={`btn ${dangerous ? "btn-danger" : "btn-primary"}`}
          onClick={() => { onConfirm(); onClose(); }}
        >
          {confirmLabel}
        </button>
      </div>
    </Modal>
  );
}
