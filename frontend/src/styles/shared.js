/**
 * Estilos compartidos del design system NEXO.
 * Importar en vez de redefinir en cada componente.
 */

export const cardStyle = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 12,
  padding: 20,
  marginBottom: 16,
};

export const inputStyle = {
  width: "100%",
  padding: "10px 12px",
  border: "1.5px solid var(--border)",
  borderRadius: 9,
  fontSize: 14,
  outline: "none",
  boxSizing: "border-box",
  background: "var(--surface)",
  color: "var(--text)",
};

export const selectStyle = { ...inputStyle, appearance: "auto" };

export const textareaStyle = { ...inputStyle, minHeight: 80, resize: "vertical" };

export const btnPrimary = {
  padding: "10px 20px",
  background: "var(--primary)",
  color: "#fff",
  border: "none",
  borderRadius: 9,
  fontSize: 14,
  fontWeight: 600,
  cursor: "pointer",
};

export const btnSecondary = {
  ...btnPrimary,
  background: "var(--surface)",
  color: "var(--text)",
  border: "1px solid var(--border)",
};

export const btnSuccess = { ...btnPrimary, background: "var(--success)" };
export const btnDanger = { ...btnPrimary, background: "var(--danger)" };

export const btnSmall = {
  padding: "6px 14px",
  border: "1px solid var(--border)",
  borderRadius: 7,
  fontSize: 12,
  fontWeight: 500,
  cursor: "pointer",
  background: "var(--surface)",
  color: "var(--text-secondary)",
};

export const labelStyle = {
  fontSize: 11,
  color: "var(--text-muted)",
  textTransform: "uppercase",
  fontWeight: 600,
  marginBottom: 4,
};

export const sectionTitle = {
  fontSize: 14,
  fontWeight: 700,
  color: "var(--text)",
  marginBottom: 12,
};
