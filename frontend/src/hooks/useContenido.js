/**
 * Hook que centraliza el estado y las acciones del módulo de Contenido.
 * @returns {{ state: Object, actions: Object }}
 */
import { useState, useEffect } from "react";
import { useApi } from "./useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";

const FORMAT_SIZE = {
  post: "1024x1024",
  carrusel: "1024x1024",
  reel: "1024x1792",
  story: "1024x1792",
};

export function useContenido() {
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
  const [carruselSlides, setCarruselSlides] = useState(null);

  const isSuperadmin = user?.rol === "superadmin";
  const canAutopilot = usage?.autopilot_enabled || isSuperadmin;
  const isCarrusel = form.formato === "carrusel";

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
    get(ENDPOINTS.CONTENIDO_USAGE)
      .then((r) => setUsage(r.data))
      .catch(() => {});
  }, []);
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
    try {
      await post(ENDPOINTS.IMAGENES_PARA_CONTENIDO(c.id), {
        tamano: FORMAT_SIZE[c.formato] || "1024x1024",
        estilo: "vivid",
      });
      setPubMsg("Imagen generada");
      loadData();
    } catch (e) {
      setPubMsg(e.response?.data?.message || "Error");
    } finally {
      setActionId(null);
    }
  }

  async function generarImagenParaCopy() {
    if (!resultado?.id) return;
    setActionId("gen_img");
    try {
      await post(ENDPOINTS.IMAGENES_PARA_CONTENIDO(resultado.id), {
        tamano: FORMAT_SIZE[resultado.formato] || "1024x1024",
        estilo: "vivid",
      });
      setPubMsg("Imagen generada");
      loadData();
      get(ENDPOINTS.CONTENIDO).then((r) => {
        const updated = (r.data.data || []).find((c) => c.id === resultado.id);
        if (updated) setResultado((prev) => ({ ...prev, imagen_url: updated.imagen_url }));
      });
    } catch (e) {
      setPubMsg(e.response?.data?.message || "Error");
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
      setPubMsg(`Carrusel: ${data.num_slides} slides`);
    } catch (e) {
      setPubMsg(e.response?.data?.message || "Error");
    } finally {
      setActionId(null);
    }
  }

  const setField = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return {
    state: {
      form,
      resultado,
      lista,
      usage,
      loading,
      listLoading,
      error,
      pubMsg,
      actionId,
      scheduleDate,
      filtro,
      rechazoMotivo,
      carruselSlides,
      isSuperadmin,
      canAutopilot,
      isCarrusel,
      FORMAT_SIZE,
    },
    actions: {
      setForm,
      setResultado,
      setError,
      setPubMsg,
      setFiltro,
      setScheduleDate,
      setRechazoMotivo,
      setField,
      generar,
      aprobar,
      publicarDirecto,
      rechazar,
      publicarAhora,
      programar,
      generarImagen,
      generarImagenParaCopy,
      generarCarrusel,
    },
  };
}
