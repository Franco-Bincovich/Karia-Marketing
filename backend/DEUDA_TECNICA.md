# Deuda Técnica — NEXO Backend

## Pendiente para próxima iteración

### automatizaciones_repository.py (no creado)
Las queries directas en automatizaciones_service.py (líneas 61, 66, 82-89, 130-137, 148-155, 162-168) necesitan un repositorio propio.
Bloqueante: requiere reestructurar el módulo completo.
Prioridad: Media.

### Refresh tokens (no implementado)
La sesión muere cuando expira el JWT sin posibilidad de renovación.
Impacto: UX degradada — el usuario tiene que volver a loguearse.
Prioridad: Alta para producción.

### Alembic (no implementado)
Las migraciones se corren manualmente. Sin rollback automático.
Bloqueante: requiere migrar las 35 migraciones existentes.
Prioridad: Media.

### Sentry (no implementado)
El catch-all en error_handler.py no trackea errores a servicio externo.
Impacto: sin visibilidad de errores en producción.
Prioridad: Alta para producción.

### Calendario.jsx (no dividido)
896L — 500 de estilos inline. Requiere migrar estilos a shared.js primero.
Prioridad: Media.

### Python 3.9 → 3.10+ upgrade (bloqueante para CVEs)
cryptography 44.0.1 tiene 2 CVEs (fix: 46.x, requiere Python 3.10+).
Pillow 11.3.0 tiene 2 CVEs (fix: 12.x, requiere Python 3.10+).
filelock 3.19.1 tiene 2 CVEs (fix: 3.20+, requiere Python 3.10+).
pypdf 4.1.0 tiene 21 CVEs (fix: 6.x, major bump).
Acción: migrar a Python 3.10+ resuelve 26 de 42 CVEs de un golpe.
Prioridad: Alta para producción.

### Migración completa a httpOnly cookies
El frontend sigue usando localStorage para tokens. Las cookies httpOnly están configuradas en el backend pero el frontend necesita:
- Eliminar localStorage.setItem/getItem de AuthContext.jsx
- Agregar withCredentials: true al axios instance
- Testear login/logout/refresh completo
Prioridad: Alta para producción.

### Inline styles → shared.js (parcial)
23 archivos frontend definen estilos duplicados. shared.js existe pero la migración de cada archivo es mecánica. Variaciones menores (borderRadius 12 vs 14) requieren auditoría visual.
Prioridad: Baja (cosmético, no afecta funcionalidad).
