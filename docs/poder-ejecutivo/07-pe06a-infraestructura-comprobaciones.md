# PE-06A: infraestructura histórica de comprobaciones técnicas

## Propósito y alcance

PE-06 se dividió en dos entregas para separar hechos técnicos reproducibles de la investigación
documental. PE-06A incorpora exclusivamente la infraestructura histórica para comprobaciones de
recursos. PE-06B revisará por lotes las cinco dimensiones pendientes y, solo con evidencia oficial
atribuible, podrá crear observaciones y evaluaciones históricas nuevas.

PE-06A no evalúa instituciones, no modifica puntuaciones, no crea rankings, no envía solicitudes
SAIP y no realiza solicitudes de red. El manifiesto `PE-06A-2026-08-03` está vacío: define el
formato de entrada futuro y contiene cero comprobaciones productivas.

## Hallazgo metodológico: portal de transparencia bajo dominio institucional pero con sujeto documental distinto

La sección `https://presidencia.gob.do/transparencia` identifica su contenido como el portal de
transparencia de la antigua Dirección General de Comunicación (DICOM), para junio de 2014 a
diciembre de 2021. Compartir el dominio de Presidencia no demuestra identidad institucional. Un
encabezado visual tampoco sustituye la atribución documental: debe prevalecer el sujeto que el
propio contenido identifica.

Por ello, el marco legal, la OAI, el organigrama y los demás recursos DICOM no pueden atribuirse ni
puntuar automáticamente a la Presidencia de la República de PE-02. La ambigüedad se conserva solo
como límite metodológico; PE-06A no crea una observación productiva sobre ella.

## `ResourceCheck`

Cada fila registra un intento técnico independiente: recurso, fecha, tipo, clasificación, respuesta
HTTP observada, URL final observada, cantidad de redirecciones, duración, MIME, longitud, error,
número de intento, User-Agent, timeout, herramienta, versión, evidencia opcional y notas. La clave
lógica `(resource_id, checked_at, check_type, attempt_number)` impide duplicados exactos y permite
una secuencia histórica ilimitada.

Las clasificaciones tienen comportamiento cerrado:

- `available`: respuesta final 2xx comprobada.
- `available_with_redirect`: respuesta final 2xx y redirección realmente observada.
- `restricted`: 403; no significa enlace roto.
- `rate_limited`: 429; no significa enlace roto.
- `source_unavailable`: timeout, DNS o respuesta 5xx; representa indisponibilidad temporal.
- `not_found_provisional`: un único 404.
- `broken_link_confirmed`: 410 inequívoco o una segunda comprobación 404/410 del recurso.
- `technical_error`: por ejemplo, certificado inválido o fallo de herramienta.

No se guarda `http_status` si no hubo respuesta HTTP. `final_url` solo se informa cuando fue
observada. Los errores no se convierten en acusaciones de ocultamiento ni incumplimiento.

## `SearchabilityCheck`

Cada fila registra método, resultado, detección de texto, texto seleccionable, metadatos, título,
fecha, número documental, páginas, caracteres extraídos, herramienta, versión, evidencia y notas.
Los métodos admitidos son inspección de HTML, extracción limitada de texto PDF, inspección de
metadatos y revisión manual. Los resultados son `searchable`, `partially_searchable`,
`not_searchable`, `inconclusive` y `technical_error`.

La extensión `.pdf` nunca basta para declarar buscabilidad. `selectable_text=true` requiere una
comprobación con `text_detected=true`, y `searchable` exige texto observado. PE-06A no incluye OCR,
no ejecuta OCR y rechaza herramientas declaradas como OCR.

## Historia, inmutabilidad y trazabilidad

Las dos tablas son append-only. El ORM rechaza actualizaciones y borrados ordinarios; PostgreSQL
también los bloquea. Se conservan fechas y versiones de herramienta para que una comprobación
posterior no sobrescriba una anterior. Las claves foráneas enlazan el recurso y, cuando existe, la
evidencia que respalda el resultado.

`DigitalTransparencyLoadRecord` registra propiedad con la versión PE-06A y los tipos
`resource_check` o `searchability_check`. El rollback elimina solamente filas con esa propiedad.
No elimina recursos, observaciones, componentes, evaluaciones, tareas, instituciones,
nombramientos, fuentes ni evidencias de PE-02/03/04/05. El modo `--dry-run` revierte su propia
transacción.

## Operación segura

Los comandos disponibles son:

```text
python -m app.modules.digital_transparency checks validate
python -m app.modules.digital_transparency checks report
python -m app.modules.digital_transparency checks rollback --dry-run
python -m app.modules.digital_transparency checks rollback
```

`validate` comprueba el manifiesto sin acceder a Internet. `report` cuenta filas persistidas y su
propiedad. Ningún comando ejecuta comprobaciones web.

## Trabajo pendiente para PE-06B

PE-06B deberá investigar las 25 instituciones por lotes, resolver cuidadosamente la atribución de
cada recurso, ejecutar comprobaciones conservadoras con fechas reales y conservar sus resultados.
Solo entonces podrá decidir buscabilidad, crear observaciones respaldadas, calcular cobertura y
generar evaluaciones históricas nuevas. La ambigüedad DICOM/Presidencia, cambios de portales,
bloqueos 403/429, indisponibilidad temporal y PDFs escaneados seguirán requiriendo revisión humana.
