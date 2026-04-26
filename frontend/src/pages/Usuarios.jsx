import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { ENDPOINTS } from "../constants/endpoints";
import EmptyState from "../components/ui/EmptyState";

const card = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 14,
  padding: 20,
  marginBottom: 16,
};
const input = {
  width: "100%",
  padding: "10px 12px",
  border: "1.5px solid var(--border)",
  borderRadius: 9,
  fontSize: 14,
  outline: "none",
  boxSizing: "border-box",
  marginBottom: 12,
  background: "var(--surface)",
  color: "var(--text)",
};
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
const th = {
  textAlign: "left",
  fontSize: 10,
  color: "var(--text-muted)",
  textTransform: "uppercase",
  padding: "8px 12px",
  borderBottom: "1px solid var(--border)",
  fontWeight: 600,
};
const td = {
  padding: "10px 12px",
  fontSize: 13,
  borderBottom: "1px solid var(--border-subtle)",
  color: "var(--text-secondary)",
};

export default function Usuarios() {
  const { user } = useAuth();
  const { get, post } = useApi();
  const [usuarios, setUsuarios] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ email: "", password: "", nombre: "", rol: "subusuario" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const clienteId = user?.cliente_id;

  useEffect(() => {
    if (!clienteId) return;
    get(ENDPOINTS.USUARIOS, { cliente_id: clienteId })
      .then(({ data }) => setUsuarios(data))
      .catch(() => {});
  }, [clienteId]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.email || !form.password || !form.nombre) {
      setError("Completá todos los campos");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const { data } = await post(ENDPOINTS.USUARIOS, { ...form, cliente_id: clienteId });
      setUsuarios((prev) => [...prev, data]);
      setShowForm(false);
      setForm({ email: "", password: "", nombre: "", rol: "subusuario" });
    } catch (err) {
      setError(err.response?.data?.message || "Error al crear usuario");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Layout title="Usuarios">
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
        <button style={btn} onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancelar" : "+ Nuevo usuario"}
        </button>
      </div>

      {showForm && (
        <form style={card} onSubmit={handleSubmit}>
          {error && (
            <div className="msg-error" style={{ marginBottom: 12, borderRadius: 8 }}>
              <span style={{ flex: 1 }}>{error}</span>
              <button type="button" className="msg-dismiss" onClick={() => setError("")}>
                ×
              </button>
            </div>
          )}
          <input
            style={input}
            placeholder="Nombre"
            value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })}
          />
          <input
            style={input}
            placeholder="Email"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <input
            style={input}
            placeholder="Contraseña"
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          <select
            style={{ ...input, appearance: "auto" }}
            value={form.rol}
            onChange={(e) => setForm({ ...form, rol: e.target.value })}
          >
            <option value="admin">admin</option>
            <option value="subusuario">subusuario</option>
          </select>
          <button style={btn} type="submit" disabled={saving}>
            {saving ? "Guardando..." : "Crear usuario"}
          </button>
        </form>
      )}

      <div style={card}>
        {usuarios.length === 0 ? (
          <EmptyState
            icon="👤"
            title="Sin usuarios"
            description="Agregá usuarios para colaborar en la plataforma"
          />
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={th}>Nombre</th>
                  <th style={th}>Email</th>
                  <th style={th}>Rol</th>
                  <th style={th}>Estado</th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((u) => (
                  <tr key={u.id}>
                    <td style={{ ...td, fontWeight: 500, color: "var(--text)" }}>{u.nombre}</td>
                    <td style={td}>{u.email}</td>
                    <td style={td}>
                      <span
                        style={{
                          background: "var(--purple-bg)",
                          color: "var(--purple-text)",
                          padding: "2px 8px",
                          borderRadius: 6,
                          fontSize: 11,
                          fontWeight: 600,
                        }}
                      >
                        {u.rol}
                      </span>
                    </td>
                    <td style={td}>
                      <span
                        style={{
                          background: u.activo ? "var(--success-bg)" : "var(--danger-bg)",
                          color: u.activo ? "var(--success-text)" : "var(--danger-text)",
                          padding: "2px 8px",
                          borderRadius: 6,
                          fontSize: 11,
                          fontWeight: 600,
                        }}
                      >
                        {u.activo ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
