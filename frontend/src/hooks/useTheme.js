import { useState, useEffect } from "react";

/**
 * Hook para manejar el modo oscuro/claro de NEXO.
 * Persiste en localStorage bajo la clave "nexo-theme".
 * Dark mode es el default.
 */
export function useTheme() {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem("nexo-theme");
    // Si no hay nada guardado o está en "dark", activar dark mode
    return saved !== "light";
  });

  useEffect(() => {
    document.body.classList.toggle("dark-mode", isDark);
    localStorage.setItem("nexo-theme", isDark ? "dark" : "light");
  }, [isDark]);

  function toggle() {
    setIsDark((prev) => !prev);
  }

  return { isDark, toggle };
}
