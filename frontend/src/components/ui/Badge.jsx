/**
 * Badge — etiqueta de estado con variantes de color.
 *
 * Variantes: success | warning | danger | purple | blue | gray | primary | soon
 *
 * Uso:
 *   <Badge variant="success">Activo</Badge>
 *   <Badge variant="soon">Próximamente</Badge>
 */
export default function Badge({ variant = "gray", children, style = {} }) {
  const cls = variant === "soon" ? "badge-soon" : `badge badge-${variant}`;
  return (
    <span className={cls} style={style}>
      {children}
    </span>
  );
}
