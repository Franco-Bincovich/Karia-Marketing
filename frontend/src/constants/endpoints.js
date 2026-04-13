/**
 * Centraliza todas las URLs de la API.
 * Cambiar BASE_URL aquí afecta toda la app.
 */

export const BASE_URL = "/api";

export const ENDPOINTS = {
  // Auth
  LOGIN: `${BASE_URL}/auth/login`,
  LOGOUT: `${BASE_URL}/auth/logout`,
  ME: `${BASE_URL}/auth/me`,

  // Clientes
  CLIENTES: `${BASE_URL}/clientes`,
  CLIENTE_MARCAS: (clienteId) => `${BASE_URL}/clientes/${clienteId}/marcas`,

  // Usuarios
  USUARIOS: `${BASE_URL}/usuarios`,
  USUARIO_PERMISOS: (usuarioId) => `${BASE_URL}/usuarios/${usuarioId}/permisos`,

  // Feature Flags
  FEATURE_FLAGS: `${BASE_URL}/feature-flags`,
  FEATURE_FLAG: (feature) => `${BASE_URL}/feature-flags/${feature}`,
};
