import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";
import SkeletonLoader from "../components/ui/SkeletonLoader";
import EmptyState from "../components/ui/EmptyState";
import Badge from "../components/ui/Badge";

const card = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 12,
  padding: 20,
  marginBottom: 16,
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
const select = { ...inputStyle, appearance: "auto" };
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
const btnSuccess = { ...btn, background: "var(--success)" };
const btnDanger = { ...btn, background: "var(--danger)" };
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
const btnAutopilot = { ...btn, background: "var(--purple)" };

const FORMAT_SIZE = {
  post: "1024x1024",
  carrusel: "1024x1024",
  reel: "1024x1792",
  story: "1024x1792",
};

function PreviewPost({ c, formato }) {
  const isVertical = formato === "story" || formato === "reel";
  const copyText = c[`copy_${c.variante_seleccionada || "a"}`] || c.copy_a || "";
  return (
    <div
      style={{
        border: "1px solid var(--border)",
        borderRadius: 12,
        overflow: "hidden",
        maxWidth: isVertical ? 270 : 320,
      }}
    >
      {c.imagen_url && (
        <img
          src={c.imagen_url}
          alt=""
          style={{
            width: "100%",
            aspectRatio: isVertical ? "9/16" : "1/1",
            objectFit: "cover",
            display: "block",
          }}
          onError={(e) => {
            e.target.style.display = "none";
          }}
        />
      )}
      <div style={{ padding: "10px 12px" }}>
        <p style={{ fontSize: 12, color: "var(--text)", lineHeight: 1.5, whiteSpace: "pre-wrap" }}>
          {copyText.length > 150 ? copyText.slice(0, 150) + "..." : copyText}
        </p>
      </div>
    </div>
  );
}

const estadoBadge = (e) => {
  const map = {
    aprobado: { bg: "var(--success-bg)", c: "var(--success-text)" },
    publicado: { bg: "var(--blue-bg)", c: "var(--blue-text)" },
    pendiente_aprobacion: { bg: "var(--warning-bg)", c: "var(--warning-text)" },
    rechazado: { bg: "var(--danger-bg)", c: "var(--danger-text)" },
    borrador: { bg: "var(--surface-2)", c: "var(--text-secondary)" },
  };
  const s = map[e] || map.borrador;
  return {
    background: s.bg,
    color: s.c,
    padding: "2px 8px",
    borderRadius: 6,
    fontSize: 11,
    fontWeight: 600,
  };
};

export default function Contenido() {
  const { get, post } = useApi();
  const { user } = useAuth();
  const [form, setForm] = useState({
    red_social: "instagram",
    formato: "post",
    objetivo: "",
    tono: "profesional",
    tema: "",
    num_slides: 5,
  });
  const [resultado, setResultado] = useState(null);
  const [lista, setLista] = useState([]);
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(true);
  const [rechazoMotivo, setRechazoMotivo] = useState("");
  const [error, setError] = useState("");
  const [pubMsg, setPubMsg] = useState("");
  const [actionId, setActionId] = useState(null);
  const [scheduleDate, setScheduleDate] = useState("");
  const [filtro, setFiltro] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [savingKey, setSavingKey] = useState(false);
  const [carruselSlides, setCarruselSlides] = useState(null);

  const isSuperadmin = user?.rol === "superadmin";
  const canAutopilot = usage?.autopilot_enabled || isSuperadmin;
  const isCarrusel = form.formato === "carrusel";

  useEffect(() => {
    loadData();
    get(ENDPOINTS.CONTENIDO_USAGE)
      .then((r) => setUsage(r.data))
      .catch(() => {});
  }, []);

  function loadData() {
    setListLoading(true);
    const url = filtro ? `${ENDPOINTS.CONTENIDO}?estado=${filtro}` : ENDPOINTS.CONTENIDO;
    get(url)
      .then((r) => setLista(r.data.data || []))
      .catch(() => {})
      .finally(() => setListLoading(false));
  }

  useEffect(() => {
    loadData();
  }, [filtro]);

  async function generar(modo = "copilot") {
    if (!form.tema) return;
    setLoading(true);
    setError("");
    setCarruselSlides(null);
    try {
      const { data } = await post(ENDPOINTS.CONTENIDO_GENERAR, { ...form, modo });
      setResultado(data);
      get(ENDPOINTS.CONTENIDO_USAGE)
        .then((r) => setUsage(r.data))
        .catch(() => {});
    } catch (e) {
      setError(e.response?.data?.message || "Error generando contenido");
    } finally {
      setLoading(false);
    }
  }

  async function aprobar(variante) {
    if (!resultado?.id) return;
    await post(ENDPOINTS.CONTENIDO_APROBAR(resultado.id), { variante });
    setResultado((prev) => ({ ...prev, estado: "aprobado", variante_seleccionada: variante }));
    loadData();
  }

  async function publicarDirecto(variante) {
    if (!resultado?.id) return;
    setActionId("pub_directo");
    try {
      await post(ENDPOINTS.CONTENIDO_PUBLICAR_DIRECTO(resultado.id), { variante });
      setPubMsg("Generado y publicado correctamente");
      setResultado(null);
      loadData();
    } catch (e) {
      setError(e.response?.data?.message || "Error al publicar");
    } finally {
      setActionId(null);
    }
  }

  async function rechazar() {
    if (!resultado?.id || !rechazoMotivo) return;
    try {
      const { data } = await post(ENDPOINTS.CONTENIDO_RECHAZAR(resultado.id), {
        comentario: rechazoMotivo,
      });
      setResultado(data);
      setRechazoMotivo("");
    } catch {}
  }

  async function publicarAhora(c) {
    setActionId(c.id + "_pub");
    setPubMsg("");
    const copyText = c[`copy_${c.variante_seleccionada || "a"}`] || c.copy_a || "";
    try {
      await post(ENDPOINTS.SOCIAL_PUBLICAR, {
        red_social: c.red_social,
        copy_text: copyText,
        contenido_id: c.id,
      });
      setPubMsg("Publicado correctamente");
      loadData();
    } catch (e) {
      setPubMsg(e.response?.data?.message || "Error al publicar");
    } finally {
      setActionId(null);
    }
  }

  async function programar(c) {
    if (!scheduleDate) {
      setPubMsg("Seleccioná fecha y hora");
      return;
    }
    setActionId(c.id + "_sched");
    const copyText = c[`copy_${c.variante_seleccionada || "a"}`] || c.copy_a || "";
    try {
      await post(ENDPOINTS.SOCIAL_PROGRAMAR, {
        red_social: c.red_social,
        copy_text: copyText,
        contenido_id: c.id,
        programado_para: new Date(scheduleDate).toISOString(),
      });
      setPubMsg("Programado correctamente");
      setScheduleDate("");
    } catch (e) {
      setPubMsg(e.response?.data?.message || "Error");
    } finally {
      setActionId(null);
    }
  }

  async function generarImagen(c) {
    setActionId(c.id + "_img");
    const tamano = FORMAT_SIZE[c.formato] || "1024x1024";
    try {
      await post(ENDPOINTS.IMAGENES_PARA_CONTENIDO(c.id), { tamano, estilo: "vivid" });
      setPubMsg("Imagen generada para el contenido");
      loadData();
    } catch (e) {
      setPubMsg(e.response?.data?.message || "Error al generar imagen");
    } finally {
      setActionId(null);
    }
  }

  async function generarImagenParaCopy() {
    if (!resultado?.id) return;
    setActionId("gen_img");
    try {
      const tamano = FORMAT_SIZE[resultado.formato] || "1024x1024";
      await post(ENDPOINTS.IMAGENES_PARA_CONTENIDO(resultado.id), { tamano, estilo: "vivid" });
      setPubMsg("Imagen generada para el contenido");
      loadData();
      get(ENDPOINTS.CONTENIDO).then((r) => {
        const updated = (r.data.data || []).find((c) => c.id === resultado.id);
        if (updated) setResultado((prev) => ({ ...prev, imagen_url: updated.imagen_url }));
      });
    } catch (e) {
      setPubMsg(e.response?.data?.message || "Error al generar imagen");
    } finally {
      setActionId(null);
    }
  }

  async function generarCarrusel() {
    if (!resultado?.id) return;
    setActionId("gen_carrusel");
    try {
      const { data } = await post(ENDPOINTS.IMAGENES_CARRUSEL(resultado.id), {
        num_slides: form.num_slides,
        estilo: "vivid",
      });
      setCarruselSlides(data.slides || []);
      setPubMsg(`Carrusel generado: ${data.num_slides} slides`);
    } catch (e) {
      setPubMsg(e.response?.data?.message || "Error generando carrusel");
    } finally {
      setActionId(null);
    }
  }

  async function guardarApiKey() {
    if (!apiKey) return;
    setSavingKey(true);
    try {
      await post(ENDPOINTS.CONTENIDO_API_KEY, { api_key: apiKey });
      setApiKey("");
      get(ENDPOINTS.CONTENIDO_USAGE)
        .then((r) => setUsage(r.data))
        .catch(() => {});
      setPubMsg("API key guardada");
    } catch (e) {
      setError(e.response?.data?.message || "Error");
    } finally {
      setSavingKey(false);
    }
  }

  const setField = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <Layout title="Generar Contenido">
      {/* Usage bar */}
      {usage && usage.limite && (
        <div
          style={{
            ...card,
            padding: 14,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 16,
          }}
        >
          <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            Posts este mes:{" "}
            <strong style={{ color: "var(--text)" }}>
              {usage.posts_mes}/{usage.limite}
            </strong>
          </span>
          <div
            style={{
              width: 120,
              height: 6,
              background: "var(--surface-2)",
              borderRadius: 3,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${Math.min(100, (usage.posts_mes / usage.limite) * 100)}%`,
                background: usage.posts_mes >= usage.limite ? "var(--danger)" : "var(--primary)",
                borderRadius: 3,
              }}
            />
          </div>
        </div>
      )}

      {/* Configuración */}
      <div style={card}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16, color: "var(--text)" }}>
          Configuración
        </h3>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: isCarrusel ? "1fr 1fr 1fr 1fr" : "1fr 1fr 1fr",
            gap: 12,
            marginBottom: 12,
          }}
        >
          <div>
            <label className="field-label-sm">Red Social</label>
            <select style={select} value={form.red_social} onChange={setField("red_social")}>
              <option>instagram</option>
              <option>facebook</option>
              <option>linkedin</option>
              <option>tiktok</option>
              <option>twitter</option>
            </select>
          </div>
          <div>
            <label className="field-label-sm">Formato</label>
            <select style={select} value={form.formato} onChange={setField("formato")}>
              <option>post</option>
              <option>reel</option>
              <option>story</option>
              <option>carrusel</option>
            </select>
          </div>
          <div>
            <label className="field-label-sm">Tono</label>
            <select style={select} value={form.tono} onChange={setField("tono")}>
              <option>profesional</option>
              <option>cercano</option>
              <option>inspirador</option>
              <option>humoristico</option>
            </select>
          </div>
          {isCarrusel && (
            <div>
              <label className="field-label-sm">Slides</label>
              <select
                style={select}
                value={form.num_slides}
                onChange={(e) => setForm({ ...form, num_slides: parseInt(e.target.value) })}
              >
                {[2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                  <option key={n} value={n}>
                    {n} slides
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
          <div>
            <label className="field-label-sm">Objetivo</label>
            <input
              style={inputStyle}
              value={form.objetivo}
              onChange={setField("objetivo")}
              placeholder="Ej: aumentar awareness"
            />
          </div>
          <div>
            <label className="field-label-sm">Tema *</label>
            <input
              style={inputStyle}
              value={form.tema}
              onChange={setField("tema")}
              placeholder="Ej: lanzamiento producto"
            />
          </div>
        </div>
        <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 12 }}>
          Tamaño de imagen: <strong>{FORMAT_SIZE[form.formato] || "1024x1024"}</strong> (
          {form.formato === "story" || form.formato === "reel" ? "vertical" : "cuadrado"})
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button style={btn} onClick={() => generar("copilot")} disabled={loading}>
            {loading ? (
              <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span className="spinner" />
                Generando...
              </span>
            ) : (
              "Generar 3 Variantes"
            )}
          </button>
          {canAutopilot && (
            <button style={btnAutopilot} onClick={() => generar("autopilot")} disabled={loading}>
              Generar y aprobar (Autopilot)
            </button>
          )}
        </div>
        {error && (
          <div className="msg-error" style={{ marginTop: 10, borderRadius: 8 }}>
            {error}
          </div>
        )}
      </div>

      {/* 3 Variantes (pre-aprobación) */}
      {resultado && resultado.estado !== "aprobado" && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr",
              gap: 12,
              marginBottom: 16,
            }}
          >
            {["a", "b", "c"].map((v) => (
              <div
                key={v}
                style={{ ...card, borderColor: "var(--primary)", borderWidth: 2, marginBottom: 0 }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: 10,
                  }}
                >
                  <span style={{ fontSize: 13, fontWeight: 700, color: "var(--primary)" }}>
                    Variante {v.toUpperCase()}
                  </span>
                </div>
                <p
                  style={{
                    fontSize: 13,
                    color: "var(--text-secondary)",
                    lineHeight: 1.6,
                    whiteSpace: "pre-wrap",
                    marginBottom: 8,
                  }}
                >
                  {resultado[`copy_${v}`] || "—"}
                </p>
                {resultado[`hashtags_${v}`] && (
                  <p style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>
                    {resultado[`hashtags_${v}`]}
                  </p>
                )}
                {resultado[`cta_${v}`] && (
                  <p style={{ fontSize: 12, color: "var(--purple-text)", fontWeight: 600 }}>
                    CTA: {resultado[`cta_${v}`]}
                  </p>
                )}
                <div style={{ display: "flex", gap: 6, marginTop: 10, flexWrap: "wrap" }}>
                  <button
                    style={{
                      ...btnSmall,
                      borderColor: "var(--success)",
                      color: "var(--success-text)",
                    }}
                    onClick={() => aprobar(v)}
                  >
                    Aprobar
                  </button>
                  {canAutopilot && (
                    <button
                      style={{
                        ...btnSmall,
                        borderColor: "var(--purple)",
                        color: "var(--purple-text)",
                      }}
                      onClick={() => publicarDirecto(v)}
                      disabled={actionId === "pub_directo"}
                    >
                      Publicar ya
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div style={card}>
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <input
                style={{ ...inputStyle, flex: 1 }}
                placeholder="Motivo del rechazo..."
                value={rechazoMotivo}
                onChange={(e) => setRechazoMotivo(e.target.value)}
              />
              <button style={btnDanger} onClick={rechazar}>
                Rechazar y regenerar
              </button>
            </div>
          </div>
        </>
      )}

      {/* Post-aprobación: generar imagen + preview */}
      {resultado && resultado.estado === "aprobado" && (
        <div style={card}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12, color: "var(--text)" }}>
            Variante aprobada
          </h3>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: resultado.imagen_url ? "auto 1fr" : "1fr",
              gap: 20,
            }}
          >
            {resultado.imagen_url && <PreviewPost c={resultado} formato={resultado.formato} />}
            <div>
              <p
                style={{
                  fontSize: 14,
                  color: "var(--text)",
                  lineHeight: 1.6,
                  whiteSpace: "pre-wrap",
                  marginBottom: 12,
                }}
              >
                {resultado[`copy_${resultado.variante_seleccionada || "a"}`] || resultado.copy_a}
              </p>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {!resultado.imagen_url && !isCarrusel && (
                  <button
                    style={{ ...btnSmall, borderColor: "#EC4899", color: "#EC4899" }}
                    onClick={generarImagenParaCopy}
                    disabled={actionId === "gen_img"}
                  >
                    {actionId === "gen_img"
                      ? "Generando imagen..."
                      : "Generar imagen para este copy"}
                  </button>
                )}
                {!resultado.imagen_url && isCarrusel && (
                  <button
                    style={{ ...btnSmall, borderColor: "#EC4899", color: "#EC4899" }}
                    onClick={generarCarrusel}
                    disabled={actionId === "gen_carrusel"}
                  >
                    {actionId === "gen_carrusel"
                      ? "Generando carrusel..."
                      : `Generar carrusel (${form.num_slides} slides)`}
                  </button>
                )}
                <button
                  style={{
                    ...btnSmall,
                    borderColor: "var(--success)",
                    color: "var(--success-text)",
                  }}
                  onClick={() => publicarAhora(resultado)}
                >
                  Publicar ahora
                </button>
                <button
                  style={btnSmall}
                  onClick={() => {
                    setResultado(null);
                    loadData();
                  }}
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
          {carruselSlides && carruselSlides.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <h4 style={{ fontSize: 13, fontWeight: 700, marginBottom: 8, color: "var(--text)" }}>
                Slides del carrusel
              </h4>
              <div style={{ display: "flex", gap: 12, overflowX: "auto", paddingBottom: 8 }}>
                {carruselSlides.map((s) => (
                  <div
                    key={s.id}
                    style={{
                      minWidth: 180,
                      border: "1px solid var(--border)",
                      borderRadius: 10,
                      overflow: "hidden",
                      flexShrink: 0,
                    }}
                  >
                    {s.imagen_url && (
                      <img
                        src={s.imagen_url}
                        alt=""
                        style={{ width: "100%", height: 180, objectFit: "cover" }}
                        onError={(e) => {
                          e.target.style.display = "none";
                        }}
                      />
                    )}
                    <div style={{ padding: "8px 10px" }}>
                      <div style={{ fontSize: 10, color: "var(--text-muted)", marginBottom: 2 }}>
                        Slide {s.orden}
                      </div>
                      <p style={{ fontSize: 12, color: "var(--text)" }}>{s.copy_slide}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Message */}
      {pubMsg && (
        <div
          className={pubMsg.includes("Error") ? "msg-error" : "msg-success"}
          style={{ marginBottom: 16, borderRadius: 12 }}
        >
          <span style={{ flex: 1 }}>{pubMsg}</span>
          <button className="msg-dismiss" onClick={() => setPubMsg("")}>
            ×
          </button>
        </div>
      )}

      {/* Lista de contenido */}
      <div style={card}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 12,
          }}
        >
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "var(--text)" }}>
            Contenido ({lista.length})
          </h3>
          <select
            style={{ ...select, width: "auto", padding: "6px 10px", fontSize: 12 }}
            value={filtro}
            onChange={(e) => setFiltro(e.target.value)}
          >
            <option value="">Todos</option>
            <option value="pendiente_aprobacion">Pendientes</option>
            <option value="aprobado">Aprobados</option>
            <option value="publicado">Publicados</option>
            <option value="rechazado">Rechazados</option>
          </select>
        </div>

        {listLoading ? (
          <SkeletonLoader type="list" count={4} />
        ) : lista.length === 0 ? (
          <EmptyState
            icon="✎"
            title="No hay contenido"
            description={
              filtro ? "No hay resultados con ese filtro" : "Generá tu primer contenido arriba"
            }
          />
        ) : (
          lista.map((c) => (
            <div
              key={c.id}
              style={{ padding: "12px 0", borderBottom: "1px solid var(--border-subtle)" }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 4,
                }}
              >
                <span style={{ fontSize: 13, color: "var(--text)", fontWeight: 500 }}>
                  {c.tema || c.red_social} — {c.formato}
                </span>
                <span style={estadoBadge(c.estado)}>{c.estado.replace("_", " ")}</span>
              </div>
              <p
                style={{
                  fontSize: 12,
                  color: "var(--text-muted)",
                  marginBottom: 6,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  maxWidth: 500,
                }}
              >
                {c[`copy_${c.variante_seleccionada || "a"}`] || c.copy_a || ""}
              </p>
              {c.imagen_url && (
                <div style={{ display: "flex", gap: 10, marginBottom: 6 }}>
                  <img
                    src={c.imagen_url}
                    alt=""
                    style={{
                      height: 56,
                      width: c.formato === "story" || c.formato === "reel" ? 32 : 56,
                      borderRadius: 6,
                      objectFit: "cover",
                    }}
                    onError={(e) => {
                      e.target.style.display = "none";
                    }}
                  />
                  <p
                    style={{
                      fontSize: 12,
                      color: "var(--text-muted)",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                      maxWidth: 400,
                      alignSelf: "center",
                    }}
                  >
                    {c[`copy_${c.variante_seleccionada || "a"}`] || c.copy_a || ""}
                  </p>
                </div>
              )}
              {c.estado === "aprobado" && (
                <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap" }}>
                  <button
                    style={{
                      ...btnSmall,
                      borderColor: "var(--success)",
                      color: "var(--success-text)",
                    }}
                    onClick={() => publicarAhora(c)}
                    disabled={actionId === c.id + "_pub"}
                  >
                    {actionId === c.id + "_pub" ? "..." : "Publicar ahora"}
                  </button>
                  <input
                    type="datetime-local"
                    style={{ ...inputStyle, width: "auto", padding: "4px 8px", fontSize: 11 }}
                    value={scheduleDate}
                    onChange={(e) => setScheduleDate(e.target.value)}
                  />
                  <button
                    style={{ ...btnSmall, borderColor: "var(--blue)", color: "var(--blue-text)" }}
                    onClick={() => programar(c)}
                    disabled={actionId === c.id + "_sched"}
                  >
                    {actionId === c.id + "_sched" ? "..." : "Programar"}
                  </button>
                  {!c.imagen_url && (
                    <button
                      style={{ ...btnSmall, borderColor: "#EC4899", color: "#EC4899" }}
                      onClick={() => generarImagen(c)}
                      disabled={actionId === c.id + "_img"}
                    >
                      {actionId === c.id + "_img" ? "Generando..." : "Generar imagen"}
                    </button>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* API key propia */}
      {usage?.plan === "Premium" && (
        <div style={card}>
          <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: "var(--text)" }}>
            API Key propia de Anthropic
          </h3>
          <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 10 }}>
            {usage.has_custom_key
              ? "Ya tenés una API key configurada."
              : "Conectá tu propia key para usar tu cuota de Claude directamente."}
          </p>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              style={{ ...inputStyle, flex: 1 }}
              type="password"
              placeholder="sk-ant-..."
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <button style={btnSmall} onClick={guardarApiKey} disabled={savingKey}>
              {savingKey ? "..." : "Guardar"}
            </button>
          </div>
        </div>
      )}
    </Layout>
  );
}
