# PE-08: interfaz pública del Poder Ejecutivo

## Propósito y alcance

Este módulo permite consultar la estructura y documentación pública localizada del Poder Ejecutivo. No constituye una evaluación de honestidad, legalidad, corrupción o desempeño gubernamental. El MVP cubre el resumen, directorio de 25 instituciones, fichas, autoridades y cambios persistidos expuestos por PE-07.

## Arquitectura y rutas

Se amplía el frontend existente en `frontend/`: Next.js 15, App Router, Server Components y CSS propio. No se creó una aplicación paralela. Las rutas son `/poder-ejecutivo`, `/poder-ejecutivo/instituciones/[slug]`, `/poder-ejecutivo/autoridades`, su detalle opcional `[id]`, y `/poder-ejecutivo/cambios`. Los formularios usan parámetros de URL, son utilizables sin JavaScript y conservan paginación del servidor.

## Conexión API y variables

`lib/executive-api.ts` consume exclusivamente `GET /api/v1/executive`. `NEXT_PUBLIC_API_BASE_URL` contiene solo el origen público (por ejemplo, `https://api.oedominicano.org`); no admite secretos. El cliente aplica timeout de ocho segundos, caché de 60 segundos y errores explícitos para red, 404, 422, respuesta vacía, configuración ausente e indisponibilidad. No genera datos sustitutos. `NEXT_PUBLIC_API_URL` permanece para las rutas públicas anteriores y `NEXT_PUBLIC_SITE_URL` alimenta metadata y sitemap.

## Estados, privacidad y accesibilidad

Hay skeleton de carga, error con reintento, 404 neutral y estados vacíos que distinguen ausencia de cero o inexistencia. Los tipos contienen solo el contrato público PE-07; las vistas seleccionan campos explícitos y no presentan payloads, hashes, rutas, notas privadas, detalles de cálculo ni datos personales. Formularios etiquetados, foco visible, jerarquía de títulos, tablas con desplazamiento, enlaces identificables y barras con roles ARIA permiten navegación por teclado y lectores de pantalla. La cuadrícula y los filtros responden a 360 px, 390 px, tableta y escritorio.

## Transparencia documental

La puntuación mide disponibilidad y calidad documental observada; no conducta. La cobertura expresa la proporción metodológica evaluada y la madurez `complete` solo indica dimensiones evaluadas. Dimensiones pendientes muestran “Pendiente de evaluación”, no cero. Se visualizan las ocho dimensiones que entregue PE-07 mediante barras accesibles, explicación pública, `rule_code`, evidencia y limitaciones. Se conserva la versión `OED-TD-1.0` u `OED-TD-1.1` recibida. La comparación ordinal está desactivada y no se muestra lenguaje de clasificación.

## Dashboard vivo

`docs/status/oed-implementation-status.json` es la fuente única de fecha, bloque, alcance, estados y limitaciones. `/status` la importa directamente. Se usan estados verificables (`public_mvp`) y no porcentajes arbitrarios.

## Despliegue, pruebas y límites

Vercel debe configurar las tres variables públicas y permitir el origen de PE-07 en CORS. Las verificaciones son `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` y, desde la raíz, las validaciones Python indicadas por el repositorio. Las pruebas unitarias mockean `fetch` sin internet. La información depende de fuentes incorporadas por fases anteriores; una ausencia solo significa que no fue localizada en ese alcance. El MVP exige navegación y lectura correcta de resumen, directorio, ficha, autoridades, cambios, transparencia, estados y privacidad en móvil y escritorio.

## Validación E2E conectada

El 5 de agosto de 2026 se ejecutó una validación local reproducible y sin internet. Se inició un contenedor `postgres:16-alpine` exclusivo, con almacenamiento `tmpfs`, base efímera y enlace limitado a la interfaz de loopback. La base se migró secuencialmente de 0001 a 0018 mediante `python -m app.db.migrate upgrade 0018`. Después se ejecutaron, en orden, los loaders de inventario PE-02, dependencias PE-03, autoridades PE-04, transparencia PE-05, validación de manifiesto PE-06A, PE-06B y PE-06D. No se usaron bases de desarrollo o producción.

FastAPI se inició en `<API_LOCAL_URL>` con `DATABASE_URL` apuntando exclusivamente a esa base, `TRUSTED_HOSTS` limitado a loopback y `CORS_ORIGINS=<FRONTEND_LOCAL_URL>`. Next.js se inició en `<FRONTEND_LOCAL_URL>` con `NEXT_PUBLIC_API_BASE_URL=<API_LOCAL_URL>`. Los valores concretos fueron variables temporales de proceso y no se persistieron. `/health`, `/api/v1/executive/summary`, `/institutions` y el preflight `OPTIONS` respondieron 200; el preflight devolvió exclusivamente el origen del frontend.

El resumen observado fue: 25 instituciones activas, 23 ministerios, Presidencia y Vicepresidencia presentes, 25 autoridades actuales, 2 relaciones vigentes, 25 instituciones evaluadas, 5 evaluaciones completas, 20 parciales y comparación ordinal desactivada. El Ministerio de Agricultura validó el caso parcial con cobertura 45 %, madurez `partial`, tres dimensiones evaluadas y cinco marcadas “Pendiente de evaluación”, sin presentar ausencia como cero.

Las fichas completas observadas fueron MAP 76/100, Ministerio de Hacienda y Economía 91/100, MINERD 83/100, MISPAS 68/100 y Medio Ambiente 91/100. Todas mostraron cobertura 100 %, madurez `complete`, ocho dimensiones, metodología OED-TD-1.1, explicaciones, reglas, evidencia y limitaciones. No aparecieron clasificación ordinal ni los campos técnicos desactivados. En MISPAS, “Estabilidad de enlaces” mostró 4/5 y una limitación neutral. El audit persistido PE-06D confirmó que el recurso principal respondió 200 y que un índice complementario tuvo un bucle de redirección registrado como `technical_error`; no fue `broken_link_confirmed` y no justificó cero. La interfaz conserva únicamente la explicación pública y no expone la razón interna de cálculo.

Se verificaron autoridad con acto localizado (MAP) y sin acto localizado (MIDEREC), incluyendo nombre, cargo, fecha y lenguaje neutral. Las relaciones `incoming`, `outgoing` y `all` devolvieron exclusivamente filas persistidas; una dirección sin resultados permaneció vacía. La Presidencia mostró su norma persistida. Cambios devolvió 64 eventos de nombramiento, metodología, evaluación y relación, sin convertir eventos técnicos en noticias políticas.

Playwright reutiliza la infraestructura existente. `tests/e2e/executive-real.spec.ts` queda desactivado por defecto y solo corre con `PE08_REAL_E2E=true`, `PLAYWRIGHT_EXTERNAL_SERVERS=true` y `PLAYWRIGHT_BASE_URL` dirigido al frontend controlado. Sus 14 escenarios cubren resumen, directorio, filtro, parcial, las cinco completas, MISPAS, autoridades, detalle, estado 404, cambios, foco, ausencia de desbordamiento en 360×800, 390×844, 768×1024 y 1440×900, consola, respuestas y capturas. El resultado conectado fue 14/14 aprobado, sin errores de consola, hidratación, CORS o solicitudes fallidas en rutas válidas. El 404 fue intencional.

Las evidencias locales son `frontend/test-results/pe08-real-desktop.png`, `pe08-real-mobile.png`, `pe08-real-partial.png` y `pe08-real-complete.png`. `frontend/test-results/` está ignorado globalmente y `git ls-files frontend/test-results` no devuelve archivos; las capturas previas del estado de error tampoco están rastreadas.

Con la validación conectada aprobada, la fuente única puede conservar `mvp_status=public_mvp` y PE-08 como validado. La declaración depende de repetir este procedimiento en cada cambio del contrato o de la interfaz. Persisten como límites la dependencia de fuentes oficiales incorporadas, la ausencia de una relación entrante dentro del directorio de 25 para el ejemplo disponible y que la explicación pública de MISPAS resume neutralmente el error técnico sin publicar detalles internos.
