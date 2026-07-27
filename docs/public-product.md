# Producto público

La superficie pública vive bajo `/api/v1/public` y es estrictamente de lectura. Las
rutas canónicas e internas existentes no son consumidas directamente por el frontend.
Las colecciones devuelven datos, paginación, filtros, orden, fecha de generación,
frescura y advertencias. Los errores contienen un identificador y nunca incluyen trazas.

## Extender el producto

- **Endpoint:** añada consulta, esquema y ruta dentro de `app.modules.public_api`.
  Seleccione columnas explícitamente, limite y pagine. Nunca reutilice un esquema interno.
- **Campo público:** documente necesidad, clasificación y fuente; agréguelo a una lista
  permitida y a una prueba. Payloads, hashes, notas y propuestas IA no son publicables.
- **Página:** cree una ruta App Router y use `frontend/lib/api.ts`. Incluya carga, vacío,
  error, metadata, navegación por teclado y diseño responsive.
- **Visualización:** use `components/charts.tsx`; conserve tabla alternativa, unidad,
  período, fuente, calidad y anotaciones.

## Desarrollo y despliegue

Copie `.env.example` y `frontend/.env.example`. Ejecute `make stack`, o `make run` y
`make frontend-dev` por separado. El frontend usa sólo variables `NEXT_PUBLIC_*`.

Vercel debe usar `frontend` como directorio raíz, `npm run build` y definir
`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SITE_URL` y `NEXT_PUBLIC_ROBOTS_INDEX`. Las previews
deben mantener la indexación desactivada.

La caché incorpora ETag, memoria local y un adaptador Redis. Canonicalización,
publicación y cambios de fuente deben invalidar por prefijo al conectarse al bus. El
rate limiting local debe respaldarse con Redis o el proxy en producción.

Sólo se muestran registros con estado público. La ausencia se representa como no
disponible. Las señales son observaciones y no equivalen a acusaciones. No se activa
analítica ni rastreador externo por defecto.
