import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { ENDPOINTS } from "../constants/endpoints";
import EmptyState from "../components/ui/EmptyState";

const card       = { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, padding: 20 };
const inputStyle = { width: "100%", padding: "10px 12px", border: "1.5px solid var(--border)", borderRadius: 9, fontSize: 14, outline: "none", boxSizing: "border-box", background: "var(--surface)", color: "var(--text)" };
const selectEl   = { ...inputStyle, appearance: "auto" };
const btn        = { padding: "10px 20px", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: "pointer" };
const btnNav     = { ...btn, background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", padding: "8px 14px" };
const btnSmall   = { padding: "6px 14px", border: "1px solid var(--border)", borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: "pointer", background: "var(--surface)", color: "var(--text-secondary)" };
const colors     = { instagram: "#E1306C", facebook: "#1877F2", linkedin: "#0A66C2", tiktok: "#333", twitter: "#1DA1F2" };

export default function Calendario() {
  const { get, post } = useApi();
  const [eventos, setEventos] = useState([]);
  const [pubs, setPubs] = useState([]);
  const [mes, setMes] = useState(new Date().getMonth() + 1);
  const [anio, setAnio] = useState(new Date().getFullYear());
  const [showModal, setShowModal] = useState(false);
  const [cuentas, setCuentas] = useState([]);
  const [imagenes, setImagenes] = useState([]);
  const [form, setForm] = useState({ red_social: "instagram", copy_text: "", fecha: "", hora: "", formato: "post", imagen_url: "" });
  const [carruselUrls, setCarruselUrls] = useState([]);
  const [scheduling, setScheduling] = useState(false);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  useEffect(() => { cargar(); }, [mes, anio]);

  function cargar() {
    get(ENDPOINTS.CALENDARIO, { mes, anio }).then(r => setEventos(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.SOCIAL_PUBLICACIONES).then(r => setPubs((r.data.data || []).filter(p => p.estado === "programado"))).catch(() => {});
  }

  useEffect(() => {
    get(ENDPOINTS.SOCIAL_CUENTAS).then(r => {
      const activas = (r.data.data || []).filter(c => c.activa);
      setCuentas(activas);
      if (activas.length > 0) setForm(f => ({ ...f, red_social: activas[0].red_social }));
    }).catch(() => {});
    get(ENDPOINTS.IMAGENES_BIBLIOTECA).then(r => setImagenes(r.data.data || [])).catch(() => {});
    get(ENDPOINTS.IMAGENES).then(r => setImagenes(prev => [...prev, ...(r.data.data || [])])).catch(() => {});
  }, []);

  const isCarrusel = form.formato === "carrusel";

  function toggleCarruselImg(url) {
    setCarruselUrls(prev => {
      if (prev.includes(url)) return prev.filter(u => u !== url);
      if (prev.length >= 10) return prev;
      return [...prev, url];
    });
  }

  function moveCarruselImg(idx, dir) {
    setCarruselUrls(prev => {
      const arr = [...prev];
      const newIdx = idx + dir;
      if (newIdx < 0 || newIdx >= arr.length) return arr;
      [arr[idx], arr[newIdx]] = [arr[newIdx], arr[idx]];
      return arr;
    });
  }

  function normalizeHora(h) {
    if (!h) return null;
    // Already 24h format like "13:30" or "09:00"
    if (/^\d{1,2}:\d{2}$/.test(h.trim())) return h.trim();
    // 12h format: "1:30 p.m.", "01:30 a.m.", "1:30 PM", etc.
    const match = h.match(/^(\d{1,2}):(\d{2})\s*(a\.?m\.?|p\.?m\.?|AM|PM)$/i);
    if (match) {
      let hrs = parseInt(match[1], 10);
      const mins = match[2];
      const ampm = match[3].replace(/\./g, "").toLowerCase();
      if (ampm === "pm" && hrs < 12) hrs += 12;
      if (ampm === "am" && hrs === 12) hrs = 0;
      return `${String(hrs).padStart(2, "0")}:${mins}`;
    }
    return h.trim();
  }

  async function programar() {
    if (!form.copy_text) { setError("Escribí el copy de la publicación"); return; }
    if (!form.fecha) { setError("Seleccioná la fecha"); return; }
    if (!form.hora) { setError("Seleccioná la hora"); return; }
    if (isCarrusel && carruselUrls.length < 2) { setError("Seleccioná al menos 2 imágenes para el carrusel"); return; }

    const hora24 = normalizeHora(form.hora);
    if (!hora24 || !/^\d{2}:\d{2}$/.test(hora24)) { setError("Formato de hora inválido"); return; }

    const dt = new Date(`${form.fecha}T${hora24}:00`);
    if (isNaN(dt.getTime())) { setError("Fecha u hora inválida"); return; }
    if (dt <= new Date()) { setError("La fecha debe ser en el futuro"); return; }

    setScheduling(true); setError("");
    const fechaHora = dt.toISOString();
    try {
      await post(ENDPOINTS.CALENDARIO_PROGRAMAR, {
        red_social: form.red_social, copy_text: form.copy_text,
        fecha_hora: fechaHora, formato: form.formato,
        imagen_url: isCarrusel ? null : (form.imagen_url || null),
        imagenes_urls: isCarrusel ? carruselUrls : null,
      });
      setMsg("Publicación programada correctamente");
      setShowModal(false);
      setForm({ red_social: cuentas[0]?.red_social || "instagram", copy_text: "", fecha: "", hora: "", formato: "post", imagen_url: "" });
      setCarruselUrls([]);
      cargar();
    } catch (e) { setError(e.response?.data?.message || "Error al programar"); }
    finally { setScheduling(false); }
  }

  const dias = new Date(anio, mes, 0).getDate();
  const primerDia = new Date(anio, mes - 1, 1).getDay();
  const celdas = Array.from({ length: 42 }, (_, i) => { const d = i - primerDia + 1; return d > 0 && d <= dias ? d : null; });
  const hoy = new Date();
  const esHoy = (d) => d === hoy.getDate() && mes === hoy.getMonth() + 1 && anio === hoy.getFullYear();

  function itemsDelDia(d) {
    const items = [];
    for (const e of eventos) {
      const f = new Date(e.fecha_programada);
      if (f.getDate() === d && f.getMonth() + 1 === mes) items.push({ tipo: "evento", label: e.titulo, color: colors[e.red_social] });
    }
    for (const p of pubs) {
      const f = new Date(p.programado_para || p.publicado_at);
      if (f.getDate() === d && f.getMonth() + 1 === mes) items.push({ tipo: "pub", label: (p.copy_publicado || "").slice(0, 20), color: colors[p.red_social] });
    }
    return items;
  }

  return (
    <Layout title="Calendario Editorial">
      {msg && (
        <div className="msg-success" style={{ marginBottom: 16, borderRadius: 12 }}>
          <span style={{ flex: 1 }}>{msg}</span>
          <button className="msg-dismiss" onClick={() => setMsg("")}>×</button>
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
        <button style={btn} onClick={() => setShowModal(true)}>+ Programar Publicación</button>
      </div>

      <div style={card}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <button style={btnNav} onClick={() => { mes === 1 ? (setMes(12), setAnio(anio - 1)) : setMes(mes - 1); }}>←</button>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: "var(--text)", textTransform: "capitalize" }}>
            {new Date(anio, mes - 1).toLocaleString("es-AR", { month: "long", year: "numeric" })}
          </h3>
          <button style={btnNav} onClick={() => { mes === 12 ? (setMes(1), setAnio(anio + 1)) : setMes(mes + 1); }}>→</button>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 2 }}>
          {["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"].map(d => (
            <div key={d} style={{ textAlign: "center", fontSize: 10, color: "var(--text-muted)", padding: 6, textTransform: "uppercase", fontWeight: 600 }}>{d}</div>
          ))}
          {celdas.map((d, i) => {
            const items = d ? itemsDelDia(d) : [];
            return (
              <div key={i} style={{
                minHeight: 72, border: esHoy(d) ? "2px solid var(--primary)" : "1px solid var(--border-subtle)",
                borderRadius: 6, padding: 4, background: d ? "var(--surface)" : "var(--surface-2)",
              }}>
                {d && <div style={{ fontSize: 12, color: esHoy(d) ? "var(--primary)" : "var(--text-secondary)", fontWeight: esHoy(d) ? 700 : 400, marginBottom: 2 }}>{d}</div>}
                {items.slice(0, 3).map((item, j) => (
                  <div key={j} style={{ background: item.color || "var(--text-muted)", color: "#fff", fontSize: 9, padding: "2px 4px", borderRadius: 3, marginBottom: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {item.label}
                  </div>
                ))}
                {items.length > 3 && <div style={{ fontSize: 9, color: "var(--text-muted)" }}>+{items.length - 3} más</div>}
              </div>
            );
          })}
        </div>
      </div>

      {/* Modal de programación */}
      {showModal && (
        <>
          <div onClick={() => setShowModal(false)} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 200 }} />
          <div style={{
            position: "fixed", top: "50%", left: "50%", transform: "translate(-50%, -50%)",
            background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14,
            padding: 24, width: 520, maxHeight: "85vh", overflowY: "auto", zIndex: 201,
            boxShadow: "0 20px 60px rgba(0,0,0,0.2)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <h2 style={{ fontSize: 18, fontWeight: 700, color: "var(--text)" }}>Programar Publicación</h2>
              <button onClick={() => setShowModal(false)} style={{ background: "none", border: "none", fontSize: 20, cursor: "pointer", color: "var(--text-muted)" }}>×</button>
            </div>

            {error && <div className="msg-error" style={{ marginBottom: 12, borderRadius: 8 }}><span>{error}</span></div>}

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
              <div>
                <label style={{ fontSize: 12, color: "var(--text-muted)", display: "block", marginBottom: 4 }}>Fecha</label>
                <input type="date" style={inputStyle} value={form.fecha} onChange={e => setForm({ ...form, fecha: e.target.value })} />
              </div>
              <div>
                <label style={{ fontSize: 12, color: "var(--text-muted)", display: "block", marginBottom: 4 }}>Hora</label>
                <input type="time" style={inputStyle} value={form.hora} onChange={e => setForm({ ...form, hora: e.target.value })} />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
              <div>
                <label style={{ fontSize: 12, color: "var(--text-muted)", display: "block", marginBottom: 4 }}>Red Social</label>
                <select style={selectEl} value={form.red_social} onChange={e => setForm({ ...form, red_social: e.target.value })}>
                  {cuentas.length > 0 ? cuentas.map(c => <option key={c.red_social} value={c.red_social}>{c.red_social} — {c.nombre_cuenta}</option>) : <><option>instagram</option><option>facebook</option></>}
                </select>
              </div>
              <div>
                <label style={{ fontSize: 12, color: "var(--text-muted)", display: "block", marginBottom: 4 }}>Formato</label>
                <select style={selectEl} value={form.formato} onChange={e => setForm({ ...form, formato: e.target.value })}>
                  <option>post</option><option>story</option><option>reel</option><option>carrusel</option>
                </select>
              </div>
            </div>

            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 12, color: "var(--text-muted)", display: "block", marginBottom: 4 }}>Copy</label>
              <textarea style={{ ...inputStyle, minHeight: 80, resize: "vertical" }} value={form.copy_text} onChange={e => setForm({ ...form, copy_text: e.target.value })} placeholder="Escribí el texto de la publicación..." />
            </div>

            {/* Imagen selector */}
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 12, color: "var(--text-muted)", display: "block", marginBottom: 4 }}>
                {isCarrusel ? `Imágenes del carrusel (${carruselUrls.length}/10 — mínimo 2)` : "Imagen (opcional)"}
              </label>

              {/* Carrusel: strip de imágenes seleccionadas con orden */}
              {isCarrusel && carruselUrls.length > 0 && (
                <div style={{ display: "flex", gap: 6, overflowX: "auto", marginBottom: 8, paddingBottom: 4 }}>
                  {carruselUrls.map((url, idx) => (
                    <div key={idx} style={{ position: "relative", flexShrink: 0 }}>
                      <img src={url} alt="" style={{ width: 64, height: 64, objectFit: "cover", borderRadius: 6, border: "2px solid var(--primary)", display: "block" }} onError={e => { e.target.style.display = "none"; }} />
                      <span style={{ position: "absolute", top: 2, left: 2, background: "var(--primary)", color: "#fff", fontSize: 9, fontWeight: 700, width: 16, height: 16, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center" }}>{idx + 1}</span>
                      <button onClick={() => setCarruselUrls(prev => prev.filter((_, i) => i !== idx))} style={{ position: "absolute", top: 2, right: 2, background: "var(--danger)", color: "#fff", border: "none", borderRadius: "50%", width: 16, height: 16, fontSize: 10, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", lineHeight: 1 }}>×</button>
                      <div style={{ display: "flex", justifyContent: "center", gap: 2, marginTop: 2 }}>
                        {idx > 0 && <button onClick={() => moveCarruselImg(idx, -1)} style={{ background: "var(--surface-2)", border: "1px solid var(--border)", borderRadius: 4, fontSize: 10, cursor: "pointer", padding: "0 4px", color: "var(--text-muted)" }}>←</button>}
                        {idx < carruselUrls.length - 1 && <button onClick={() => moveCarruselImg(idx, 1)} style={{ background: "var(--surface-2)", border: "1px solid var(--border)", borderRadius: 4, fontSize: 10, cursor: "pointer", padding: "0 4px", color: "var(--text-muted)" }}>→</button>}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Single image: preview */}
              {!isCarrusel && form.imagen_url && (
                <div style={{ marginBottom: 8, display: "flex", gap: 8, alignItems: "center" }}>
                  <img src={form.imagen_url} alt="" style={{ height: 48, borderRadius: 6, objectFit: "cover" }} onError={e => { e.target.style.display = "none"; }} />
                  <button style={btnSmall} onClick={() => setForm({ ...form, imagen_url: "" })}>Quitar</button>
                </div>
              )}

              {/* Gallery grid */}
              {imagenes.length > 0 ? (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 6, maxHeight: 140, overflowY: "auto" }}>
                  {imagenes.slice(0, 20).map(img => {
                    const isSelected = isCarrusel
                      ? carruselUrls.includes(img.imagen_url)
                      : form.imagen_url === img.imagen_url;
                    return (
                      <div key={img.id} onClick={() => isCarrusel ? toggleCarruselImg(img.imagen_url) : setForm({ ...form, imagen_url: img.imagen_url })} style={{
                        borderRadius: 6, overflow: "hidden", cursor: "pointer", position: "relative",
                        border: isSelected ? "2px solid var(--primary)" : "1px solid var(--border)",
                        opacity: isCarrusel && carruselUrls.length >= 10 && !isSelected ? 0.4 : 1,
                      }}>
                        <img src={img.imagen_url} alt="" style={{ width: "100%", height: 56, objectFit: "cover", display: "block" }} onError={e => { e.target.style.display = "none"; }} />
                        {isCarrusel && isSelected && (
                          <span style={{ position: "absolute", top: 2, right: 2, background: "var(--primary)", color: "#fff", fontSize: 9, fontWeight: 700, width: 16, height: 16, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center" }}>
                            {carruselUrls.indexOf(img.imagen_url) + 1}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Sin imágenes en biblioteca</p>
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
