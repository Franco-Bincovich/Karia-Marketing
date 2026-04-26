import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import EmptyState from "../components/ui/EmptyState";
import api from "../hooks/useApi";

const card = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 14,
  padding: 20,
};
const inputStyle = {
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
const selectEl = { ...inputStyle, appearance: "auto" };
const btn = {
  padding: "10px 20px",
  background: "var(--primary)",
  color: "#fff",
  border: "none",
  borderRadius: 9,
  fontSize: 14,
  fontWeight: 600,
  cursor: "pointer",
};
const btnNav = {
  ...btn,
  background: "var(--surface)",
  color: "var(--text)",
  border: "1px solid var(--border)",
  padding: "8px 14px",
};
const btnSmall = {
  padding: "6px 14px",
  border: "1px solid var(--border)",
  borderRadius: 7,
  fontSize: 12,
  fontWeight: 500,
  cursor: "pointer",
  background: "var(--surface)",
  color: "var(--text-secondary)",
};
const btnDanger = { ...btnSmall, borderColor: "var(--danger)", color: "var(--danger-text)" };
const colors = {
  instagram: "#E1306C",
  facebook: "#1877F2",
  linkedin: "#0A66C2",
  tiktok: "#333",
  twitter: "#1DA1F2",
};
const redIcon = { instagram: "📷", facebook: "📘", linkedin: "💼", tiktok: "🎵", twitter: "🐦" };
const formatoColors = {
  post: "#E53E3E",
  historia: "#3B82F6",
  story: "#3B82F6",
  carrusel: "#22C55E",
  reel: "#EAB308",
};

const estadoBadge = (e) => {
  const map = {
    programado: { bg: "var(--blue-bg)", c: "var(--blue-text)" },
    publicado: { bg: "var(--success-bg)", c: "var(--success-text)" },
    fallido: { bg: "var(--danger-bg)", c: "var(--danger-text)" },
    cancelado: { bg: "var(--surface-2)", c: "var(--text-muted)" },
    publicando: { bg: "var(--warning-bg)", c: "var(--warning-text)" },
    pendiente: { bg: "var(--warning-bg)", c: "var(--warning-text)" },
  };
  const s = map[e] || { bg: "var(--surface-2)", c: "var(--text-secondary)" };
  return {
    background: s.bg,
    color: s.c,
    padding: "2px 8px",
    borderRadius: 6,
    fontSize: 11,
    fontWeight: 600,
  };
};

function formatHora(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" });
}

export default function Calendario() {
  const { get, post, patch, delete: del } = useApi();
  const [eventos, setEventos] = useState([]);
  const [allPubs, setAllPubs] = useState([]);
  const [mes, setMes] = useState(new Date().getMonth() + 1);
  const [anio, setAnio] = useState(new Date().getFullYear());
  const [showModal, setShowModal] = useState(false);
  const [selectedDay, setSelectedDay] = useState(null);
  const [cuentas, setCuentas] = useState([]);
  const [imagenes, setImagenes] = useState([]);
  const [hoveredImgId, setHoveredImgId] = useState(null);
  const [form, setForm] = useState({
    red_social: "instagram",
    copy_text: "",
    fechaHora: "",
    formato: "post",
    imagen_url: "",
  });
  const [carruselUrls, setCarruselUrls] = useState([]);
  const [scheduling, setScheduling] = useState(false);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    cargar();
  }, [mes, anio]);

  function cargar() {
    get(ENDPOINTS.CALENDARIO, { mes, anio })
      .then((r) => {
        const data = r.data.data || [];
        console.log("[Calendario] eventos (primer item):", data[0] || "sin datos");
        console.log(
          "[Calendario] eventos formato values:",
          data.map((e) => e.formato)
        );
        setEventos(data);
      })
      .catch(() => {});
    get(ENDPOINTS.SOCIAL_PUBLICACIONES)
      .then((r) => {
        const data = r.data.data || [];
        console.log("[Calendario] publicaciones (primer item):", data[0] || "sin datos");
        console.log(
          "[Calendario] publicaciones formato values:",
          data.map((p) => p.formato)
        );
        setAllPubs(data);
      })
      .catch(() => {});
  }

  useEffect(() => {
    get(ENDPOINTS.SOCIAL_CUENTAS)
      .then((r) => {
        const activas = (r.data.data || []).filter((c) => c.activa);
        setCuentas(activas);
        if (activas.length > 0) setForm((f) => ({ ...f, red_social: activas[0].red_social }));
      })
      .catch(() => {});
    get(ENDPOINTS.IMAGENES_BIBLIOTECA)
      .then((r) => setImagenes(r.data.data || []))
      .catch(() => {});
    get(ENDPOINTS.IMAGENES)
      .then((r) => setImagenes((prev) => [...prev, ...(r.data.data || [])]))
      .catch(() => {});
  }, []);

  const isCarrusel = form.formato === "carrusel";

  function toggleCarruselImg(url) {
    setCarruselUrls((prev) => {
      if (prev.includes(url)) return prev.filter((u) => u !== url);
      if (prev.length >= 10) return prev;
      return [...prev, url];
    });
  }
  function moveCarruselImg(idx, dir) {
    setCarruselUrls((prev) => {
      const a = [...prev];
      const n = idx + dir;
      if (n < 0 || n >= a.length) return a;
      [a[idx], a[n]] = [a[n], a[idx]];
      return a;
    });
  }

  async function programar() {
    if (!form.copy_text && form.formato !== "story") {
      setError("Escribí el copy de la publicación");
      return;
    }
    if (!form.fechaHora) {
      setError("Seleccioná fecha y hora");
      return;
    }
    if (isCarrusel && carruselUrls.length < 2) {
      setError("Seleccioná al menos 2 imágenes para el carrusel");
      return;
    }
    const dt = new Date(form.fechaHora);
    if (isNaN(dt.getTime())) {
      setError("Fecha y hora inválida");
      return;
    }
    if (dt <= new Date()) {
      setError("La fecha debe ser en el futuro");
      return;
    }
    setScheduling(true);
    setError("");
    try {
      await post(ENDPOINTS.CALENDARIO_PROGRAMAR, {
        red_social: form.red_social,
        copy_text: form.copy_text,
        fecha_hora: dt.toISOString(),
        formato: form.formato,
        imagen_url: isCarrusel ? null : form.imagen_url || null,
        imagenes_urls: isCarrusel ? carruselUrls : null,
      });
      setMsg("Publicación programada correctamente");
      setShowModal(false);
      setForm({
        red_social: cuentas[0]?.red_social || "instagram",
        copy_text: "",
        fechaHora: "",
        formato: "post",
        imagen_url: "",
      });
      setCarruselUrls([]);
      cargar();
    } catch (e) {
      setError(e.response?.data?.message || "Error al programar");
    } finally {
      setScheduling(false);
    }
  }

  async function cancelarPub(id) {
    try {
      await patch(ENDPOINTS.SOCIAL_CANCELAR(id));
      setAllPubs((prev) => prev.map((p) => (p.id === id ? { ...p, estado: "cancelado" } : p)));
    } catch {}
  }

  async function handleEliminarImagen(img) {
    if (!window.confirm("¿Eliminar esta imagen de la biblioteca?")) return;
    try {
      await del(ENDPOINTS.IMAGENES_BIBLIOTECA_ELIMINAR(img.id));
      setImagenes((prev) => prev.filter((i) => i.id !== img.id));
      if (form.imagen_url === img.imagen_url) setForm((f) => ({ ...f, imagen_url: "" }));
      setCarruselUrls((prev) => prev.filter((u) => u !== img.imagen_url));
    } catch {
      alert("No se pudo eliminar la imagen");
    }
  }

  const dias = new Date(anio, mes, 0).getDate();
  const primerDia = new Date(anio, mes - 1, 1).getDay();
  const celdas = Array.from({ length: 42 }, (_, i) => {
    const d = i - primerDia + 1;
    return d > 0 && d <= dias ? d : null;
  });
  const hoy = new Date();
  const esHoy = (d) =>
    d === hoy.getDate() && mes === hoy.getMonth() + 1 && anio === hoy.getFullYear();

  function pubsDelDia(d) {
    if (!d) return [];
    return allPubs
      .filter((p) => {
        // Solo publicaciones con fecha programada explícita o estado programado/publicado con fecha
        const fechaStr = p.programado_para || (p.estado === "publicado" ? p.publicado_at : null);
        if (!fechaStr) return false;
        const f = new Date(fechaStr);
        if (isNaN(f.getTime())) return false;
        return f.getDate() === d && f.getMonth() + 1 === mes && f.getFullYear() === anio;
      })
      .sort((a, b) =>
        (a.programado_para || a.publicado_at || "").localeCompare(
          b.programado_para || b.publicado_at || ""
        )
      );
  }

  function itemsDelDia(d) {
    const items = [];
    for (const e of eventos) {
      const f = new Date(e.fecha_programada);
      if (f.getDate() === d && f.getMonth() + 1 === mes)
        items.push({ label: e.titulo, color: formatoColors[e.formato] || colors[e.red_social] });
    }
    for (const p of pubsDelDia(d)) {
      items.push({
        label: (p.copy_publicado || "").slice(0, 20),
        color: formatoColors[p.formato] || colors[p.red_social],
      });
    }
    return items;
  }

  function handleDayClick(d) {
    if (!d) return;
    const items = pubsDelDia(d);
    if (items.length > 0) setSelectedDay(d);
  }

  const dayPubs = selectedDay ? pubsDelDia(selectedDay) : [];

  return (
    <Layout title="Calendario Editorial">
      {msg && (
        <div className="msg-success" style={{ marginBottom: 16, borderRadius: 12 }}>
          <span style={{ flex: 1 }}>{msg}</span>
          <button className="msg-dismiss" onClick={() => setMsg("")}>
            ×
          </button>
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
        <button style={btn} onClick={() => setShowModal(true)}>
          + Programar Publicación
        </button>
      </div>

      <div style={card}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 16,
          }}
        >
          <button
            style={btnNav}
            onClick={() => {
              mes === 1 ? (setMes(12), setAnio(anio - 1)) : setMes(mes - 1);
            }}
          >
            ←
          </button>
          <h3
            style={{
              fontSize: 16,
              fontWeight: 700,
              color: "var(--text)",
              textTransform: "capitalize",
            }}
          >
            {new Date(anio, mes - 1).toLocaleString("es-AR", { month: "long", year: "numeric" })}
          </h3>
          <button
            style={btnNav}
            onClick={() => {
              mes === 12 ? (setMes(1), setAnio(anio + 1)) : setMes(mes + 1);
            }}
          >
            →
          </button>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 2 }}>
          {["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"].map((d) => (
            <div
              key={d}
              style={{
                textAlign: "center",
                fontSize: 10,
                color: "var(--text-muted)",
                padding: 6,
                textTransform: "uppercase",
                fontWeight: 600,
              }}
            >
              {d}
            </div>
          ))}
          {celdas.map((d, i) => {
            const items = d && d > 0 ? itemsDelDia(d) : [];
            const tienePubs = d && d > 0 ? pubsDelDia(d).length > 0 : false;
            const isSelected = d && d > 0 && selectedDay === d;
            return (
              <div
                key={i}
                onClick={() => handleDayClick(d)}
                style={{
                  minHeight: 72,
                  border: isSelected
                    ? "2px solid var(--primary)"
                    : tienePubs
                      ? "1.5px solid var(--primary)"
                      : "1px solid var(--border-subtle)",
                  borderRadius: 6,
                  padding: 4,
                  background: d ? "var(--surface)" : "var(--surface-2)",
                  cursor: tienePubs ? "pointer" : "default",
                }}
              >
                {d && (
                  <div
                    style={{
                      fontSize: 12,
                      color: esHoy(d) ? "var(--primary)" : "var(--text-secondary)",
                      fontWeight: esHoy(d) ? 700 : 400,
                      marginBottom: 2,
                    }}
                  >
                    {d}
                    {esHoy(d) && (
                      <span style={{ fontSize: 9, color: "var(--text-muted)", marginLeft: 2 }}>
                        hoy
                      </span>
                    )}
                  </div>
                )}
                {items.slice(0, 3).map((item, j) => (
                  <div
                    key={j}
                    style={{
                      background: item.color || "var(--text-muted)",
                      color: "#fff",
                      fontSize: 9,
                      padding: "2px 4px",
                      borderRadius: 3,
                      marginBottom: 1,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {item.label}
                  </div>
                ))}
                {items.length > 3 && (
                  <div style={{ fontSize: 9, color: "var(--text-muted)" }}>
                    +{items.length - 3} más
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Day detail panel */}
      {selectedDay && (
        <>
          <div
            onClick={() => setSelectedDay(null)}
            style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)", zIndex: 200 }}
          />
          <div
            style={{
              position: "fixed",
              top: 0,
              right: 0,
              width: 420,
              height: "100vh",
              background: "var(--surface)",
              borderLeft: "1px solid var(--border)",
              zIndex: 201,
              overflowY: "auto",
              padding: 24,
              boxShadow: "-4px 0 20px rgba(0,0,0,.1)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 20,
              }}
            >
              <h2 style={{ fontSize: 18, fontWeight: 700, color: "var(--text)" }}>
                {selectedDay} de{" "}
                {new Date(anio, mes - 1).toLocaleString("es-AR", { month: "long" })}
              </h2>
              <button
                onClick={() => setSelectedDay(null)}
                style={{
                  background: "none",
                  border: "none",
                  fontSize: 20,
                  cursor: "pointer",
                  color: "var(--text-muted)",
                }}
              >
                ×
              </button>
            </div>

            {dayPubs.length === 0 ? (
              <EmptyState
                icon="����"
                title="Sin publicaciones"
                description="No hay publicaciones para este día"
              />
            ) : (
              dayPubs.map((p) => (
                <div
                  key={p.id}
                  style={{
                    background: "var(--surface-2)",
                    border: "1px solid var(--border)",
                    borderRadius: 12,
                    padding: 16,
                    marginBottom: 12,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: 10,
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontSize: 18 }}>{redIcon[p.red_social] || "🌐"}</span>
                      <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text)" }}>
                        {p.red_social}
                      </span>
                      <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                        {formatHora(p.programado_para || p.publicado_at)}
                      </span>
                    </div>
                    <span style={estadoBadge(p.estado)}>{p.estado}</span>
                  </div>

                  {p.imagen_url && (
                    <div style={{ marginBottom: 10, borderRadius: 8, overflow: "hidden" }}>
                      <img
                        src={p.imagen_url}
                        alt=""
                        style={{ width: "100%", height: 160, objectFit: "cover", display: "block" }}
                        onError={(e) => {
                          e.target.style.display = "none";
                        }}
                      />
                    </div>
                  )}

                  <p
                    style={{
                      fontSize: 13,
                      color: "var(--text)",
                      lineHeight: 1.6,
                      whiteSpace: "pre-wrap",
                      marginBottom: 10,
                    }}
                  >
                    {p.copy_publicado || "—"}
                  </p>

                  {p.estado === "programado" && (
                    <button style={btnDanger} onClick={() => cancelarPub(p.id)}>
                      Cancelar publicación
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}

      {/* Modal de programación */}
      {showModal && (
        <>
          <div
            onClick={() => setShowModal(false)}
            style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 200 }}
          />
          <div
            style={{
              position: "fixed",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 14,
              padding: 24,
              width: "min(900px, 95vw)",
              maxHeight: "90vh",
              overflow: "unset",
              zIndex: 201,
              boxShadow: "0 20px 60px rgba(0,0,0,0.2)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 20,
              }}
            >
              <h2 style={{ fontSize: 18, fontWeight: 700, color: "var(--text)" }}>
                Programar Publicación
              </h2>
              <button
                onClick={() => setShowModal(false)}
                style={{
                  background: "none",
                  border: "none",
                  fontSize: 20,
                  cursor: "pointer",
                  color: "var(--text-muted)",
                }}
              >
                ×
              </button>
            </div>

            {error && (
              <div className="msg-error" style={{ marginBottom: 12, borderRadius: 8 }}>
                <span>{error}</span>
              </div>
            )}

            <div style={{ marginBottom: 12 }}>
              <label
                style={{
                  fontSize: 12,
                  color: "var(--text-muted)",
                  display: "block",
                  marginBottom: 4,
                }}
              >
                Fecha y hora de publicación
              </label>
              <input
                type="datetime-local"
                style={inputStyle}
                value={form.fechaHora}
                min={new Date().toISOString().slice(0, 16)}
                onChange={(e) => setForm({ ...form, fechaHora: e.target.value })}
              />
            </div>

            <div
              style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}
            >
              <div>
                <label
                  style={{
                    fontSize: 12,
                    color: "var(--text-muted)",
                    display: "block",
                    marginBottom: 4,
                  }}
                >
                  Red Social
                </label>
                <select
                  style={selectEl}
                  value={form.red_social}
                  onChange={(e) => setForm({ ...form, red_social: e.target.value })}
                >
                  {cuentas.length > 0 ? (
                    cuentas.map((c) => (
                      <option key={c.red_social} value={c.red_social}>
                        {c.red_social} — {c.nombre_cuenta}
                      </option>
                    ))
                  ) : (
                    <>
                      <option>instagram</option>
                      <option>facebook</option>
                    </>
                  )}
                </select>
              </div>
              <div>
                <label
                  style={{
                    fontSize: 12,
                    color: "var(--text-muted)",
                    display: "block",
                    marginBottom: 4,
                  }}
                >
                  Formato
                </label>
                <select
                  style={selectEl}
                  value={form.formato}
                  onChange={(e) => {
                    const f = e.target.value;
                    setForm({
                      ...form,
                      formato: f,
                      copy_text: f === "story" ? "" : form.copy_text,
                    });
                  }}
                >
                  <option>post</option>
                  <option>story</option>
                  <option>reel</option>
                  <option>carrusel</option>
                </select>
              </div>
            </div>

            {form.formato !== "story" && (
              <div style={{ marginBottom: 12 }}>
                <label
                  style={{
                    fontSize: 12,
                    color: "var(--text-muted)",
                    display: "block",
                    marginBottom: 4,
                  }}
                >
                  Copy
                </label>
                <textarea
                  style={{ ...inputStyle, minHeight: 80, resize: "vertical" }}
                  value={form.copy_text}
                  onChange={(e) => setForm({ ...form, copy_text: e.target.value })}
                  placeholder="Escribí el texto de la publicación..."
                />
              </div>
            )}

            {/* Imagen selector */}
            <div style={{ marginBottom: 16 }}>
              <label
                style={{
                  fontSize: 12,
                  color: "var(--text-muted)",
                  display: "block",
                  marginBottom: 4,
                }}
              >
                {isCarrusel
                  ? `Imágenes del carrusel (${carruselUrls.length}/10 — mínimo 2)`
                  : "Imagen (opcional)"}
              </label>
              {isCarrusel && carruselUrls.length > 0 && (
                <div
                  style={{
                    display: "flex",
                    gap: 6,
                    overflowX: "auto",
                    marginBottom: 8,
                    paddingBottom: 4,
                  }}
                >
                  {carruselUrls.map((url, idx) => (
                    <div key={idx} style={{ position: "relative", flexShrink: 0 }}>
                      <img
                        src={url}
                        alt=""
                        style={{
                          width: 64,
                          height: 64,
                          objectFit: "cover",
                          borderRadius: 6,
                          border: "2px solid var(--primary)",
                          display: "block",
                        }}
                        onError={(e) => {
                          e.target.style.display = "none";
                        }}
                      />
                      <span
                        style={{
                          position: "absolute",
                          top: 2,
                          left: 2,
                          background: "var(--primary)",
                          color: "#fff",
                          fontSize: 9,
                          fontWeight: 700,
                          width: 16,
                          height: 16,
                          borderRadius: "50%",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        {idx + 1}
                      </span>
                      <button
                        onClick={() => setCarruselUrls((prev) => prev.filter((_, i) => i !== idx))}
                        style={{
                          position: "absolute",
                          top: 2,
                          right: 2,
                          background: "var(--danger)",
                          color: "#fff",
                          border: "none",
                          borderRadius: "50%",
                          width: 16,
                          height: 16,
                          fontSize: 10,
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          lineHeight: 1,
                        }}
                      >
                        ×
                      </button>
                      <div
                        style={{ display: "flex", justifyContent: "center", gap: 2, marginTop: 2 }}
                      >
                        {idx > 0 && (
                          <button
                            onClick={() => moveCarruselImg(idx, -1)}
                            style={{
                              background: "var(--surface-2)",
                              border: "1px solid var(--border)",
                              borderRadius: 4,
                              fontSize: 10,
                              cursor: "pointer",
                              padding: "0 4px",
                              color: "var(--text-muted)",
                            }}
                          >
                            ←
                          </button>
                        )}
                        {idx < carruselUrls.length - 1 && (
                          <button
                            onClick={() => moveCarruselImg(idx, 1)}
                            style={{
                              background: "var(--surface-2)",
                              border: "1px solid var(--border)",
                              borderRadius: 4,
                              fontSize: 10,
                              cursor: "pointer",
                              padding: "0 4px",
                              color: "var(--text-muted)",
                            }}
                          >
                            →
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {!isCarrusel && form.imagen_url && (
                <div style={{ marginBottom: 8, display: "flex", gap: 8, alignItems: "center" }}>
                  <img
                    src={form.imagen_url}
                    alt=""
                    style={{ height: 48, borderRadius: 6, objectFit: "cover" }}
                    onError={(e) => {
                      e.target.style.display = "none";
                    }}
                  />
                  <button style={btnSmall} onClick={() => setForm({ ...form, imagen_url: "" })}>
                    Quitar
                  </button>
                </div>
              )}
              {imagenes.length > 0 ? (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(5, 1fr)",
                    gap: "8px",
                    maxHeight: "300px",
                    overflowY: "scroll",
                    overflowX: "hidden",
                    paddingRight: 4,
                    flexShrink: 0,
                  }}
                >
                  {imagenes.map((img) => {
                    const isSel = isCarrusel
                      ? carruselUrls.includes(img.imagen_url)
                      : form.imagen_url === img.imagen_url;
                    const isHovered = hoveredImgId === img.id;
                    return (
                      <div
                        key={img.id}
                        onMouseEnter={() => setHoveredImgId(img.id)}
                        onMouseLeave={() => setHoveredImgId(null)}
                        onClick={() =>
                          isCarrusel
                            ? toggleCarruselImg(img.imagen_url)
                            : setForm({ ...form, imagen_url: img.imagen_url })
                        }
                        style={{
                          width: 160,
                          height: 160,
                          borderRadius: 6,
                          overflow: "hidden",
                          cursor: "pointer",
                          position: "relative",
                          flexShrink: 0,
                          border: isSel ? "2px solid #FF6B00" : "1px solid var(--border)",
                          opacity: isCarrusel && carruselUrls.length >= 10 && !isSel ? 0.4 : 1,
                        }}
                      >
                        <img
                          src={img.imagen_url}
                          alt=""
                          style={{
                            width: 160,
                            height: 160,
                            objectFit: "cover",
                            display: "block",
                            flexShrink: 0,
                          }}
                          onError={(e) => {
                            e.target.style.display = "none";
                          }}
                        />
                        {isCarrusel && isSel && (
                          <span
                            style={{
                              position: "absolute",
                              top: 3,
                              left: 3,
                              background: "#FF6B00",
                              color: "#fff",
                              fontSize: 9,
                              fontWeight: 700,
                              width: 16,
                              height: 16,
                              borderRadius: "50%",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                            }}
                          >
                            {carruselUrls.indexOf(img.imagen_url) + 1}
                          </span>
                        )}
                        {isHovered && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEliminarImagen(img);
                            }}
                            title="Eliminar imagen"
                            style={{
                              position: "absolute",
                              top: 3,
                              right: 3,
                              background: "rgba(220,38,38,0.88)",
                              color: "#fff",
                              border: "none",
                              borderRadius: 4,
                              width: 18,
                              height: 18,
                              fontSize: 10,
                              cursor: "pointer",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              lineHeight: 1,
                            }}
                          >
                            🗑
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  Sin imágenes en biblioteca
                </p>
              )}
            </div>

            <button style={{ ...btn, width: "100%" }} onClick={programar} disabled={scheduling}>
              {scheduling ? "Programando..." : "Programar Publicación"}
            </button>
          </div>
        </>
      )}
    </Layout>
  );
}
