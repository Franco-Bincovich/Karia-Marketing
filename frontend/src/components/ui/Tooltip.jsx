import { useState, useRef } from "react";

/**
 * Tooltip — aparece al hacer hover con 500ms de delay.
 *
 * Uso:
 *   <Tooltip text="Ver detalles del reporte">
 *     <button>Ver</button>
 *   </Tooltip>
 */
export default function Tooltip({ text, children, delay = 500 }) {
  const [visible, setVisible] = useState(false);
  const timer = useRef(null);

  function handleEnter() {
    timer.current = setTimeout(() => setVisible(true), delay);
  }

  function handleLeave() {
    clearTimeout(timer.current);
    setVisible(false);
  }

  return (
    <span
      className="tooltip-wrap"
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
    >
      {children}
      {visible && text && (
        <span className="tooltip-box">{text}</span>
      )}
    </span>
  );
}
