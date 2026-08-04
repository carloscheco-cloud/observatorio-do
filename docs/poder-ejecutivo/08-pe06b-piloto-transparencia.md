# PE-06B: piloto controlado de transparencia documental

Consulta: 4 de agosto de 2026. Metodología conservada: OED-TD-1.0. PE-06B crea una
evaluación histórica separada y no modifica PE-05. No produce ranking, no envía solicitudes
SAIP y no usa prensa, redes sociales, Wikipedia u OCR.

## Alcance y fuentes oficiales

| Institución | Portal inequívoco | Marco legal | Estructura | Contacto/OAI |
|---|---|---|---|---|
| Ministerio de Administración Pública | `map.gob.do` | Mapa oficial con leyes, decretos y resoluciones; no se revisó cada descarga | Sección oficial respondió, pero no mostró una versión institucional descargable | Dirección, teléfono, OAI, correo `transparencia@map.gob.do` y canal SAIP localizados |
| Ministerio de Hacienda y Economía | `hacienda.gob.do` | Catálogo con normas, números, fechas y descargas | Resolución 226-2025 y documentos de estructura con fecha | Av. México 45, 809-687-5131, `info@hacienda.gov.do`; OAI localizada |
| Ministerio de Educación | `minerd.gob.do` | Marco legal con Ley 66-97 | El mapa enlaza organigrama interactivo; fecha/versión no confirmadas | Portal general y OAI localizados; correo OAI vigente no confirmado |
| Ministerio de Salud Pública y Asistencia Social | `msp.gob.do` | Resolución DIGEIG 002-2021 descargable; no equivale al inventario legal completo | Organigrama OAI, Resolución 168 de 17-12-2020; no es el organigrama institucional completo | Portal de servicios: Av. Héctor Homero Hernández, 809-541-3121, `info@mispas.gob.do`; contacto OAI no confirmado allí |
| Ministerio de Medio Ambiente y Recursos Naturales | `ambiente.gob.do` | Sección con leyes, decretos, reglamentos, resoluciones y normas | Manual 2024, PDF textual de 463 páginas con estructura y organigramas | RAI, correos, teléfono/extensiones, dirección y formulario oficial localizados |

Las URL exactas, extractos, fecha de consulta y resultados técnicos están en
`pe06b_manifest.json`. Compartir dominio no se trató como atribución: cada página muestra la
identidad del ministerio correspondiente.

## Dimensiones, resultados y cobertura

Se observaron `legal_framework`, `organizational_structure`,
`official_contact_information`, `document_searchability` y `stable_links`. Sus pesos posibles
suman 55, pero OED-TD-1.0 no define escalas que conviertan esos estados documentales en
puntos. Las cinco quedan `pending_evaluation`, sin componente y sin cero. La evaluación
histórica PE-06B hereda con trazabilidad los tres componentes PE-05 (45%); por tanto, la
cobertura real es 45% y la madurez es `partial`. Toda evaluación conserva `rank = NULL` y
`comparison_position = NULL`.

OED-TD-1.0 no define una subescala para penalizar esas limitaciones. Por ello PE-06B no
inventa reducciones: una dimensión verificada usa su peso existente y toda limitación queda
en la observación textual. Una dimensión pendiente se excluiría de la cobertura y no recibiría
cero. “No localizado” no significa inexistente.

## Checks técnicos y buscabilidad

Se realizó una comprobación HTTP por cada uno de 15 recursos puntuables candidatos. Los 15
registrados respondieron 200. Se conservaron estado, MIME, tiempo, longitud y URL comprobada.
No se inventó una segunda tentativa. Una comprobación separada del índice general de
transparencia de MISPAS produjo un bucle de redirección: se conserva como recurso adicional y
`ResourceCheck(technical_error)`, con HTTP 301 observado, fuera de
`broken_link_confirmed` y fuera de puntuación.

Los HTML fueron inspeccionados como texto. Los tres PDF registrados —resolución DIGEIG de
MISPAS, organigrama OAI de MISPAS y manual 2024 de Medio Ambiente— produjeron extracción
textual y por eso se clasifican como buscables. No se hizo OCR. Título, fecha y número de norma
solo se guardan cuando fueron observados. Una respuesta 200 es evidencia puntual de acceso,
no garantía de permanencia futura.

## Historia, propiedad y rollback

PE-06B posee sus 16 fuentes, evidencias y recursos nuevos, 16 `ResourceCheck`, 15
`SearchabilityCheck`, 25 observaciones, 5 evaluaciones y 15 componentes acumulados. Esos
componentes son copias trazables de los tres componentes PE-05 por institución; sus
observaciones, evidencias y recursos originales siguen siendo exclusivamente PE-05. No crea tareas
manuales porque ninguna acción humana concreta adicional fue necesaria para ejecutar el
piloto; tampoco duplica tareas PE-05. El rollback elimina solo registros propiedad de
`PE-06B-2026-08-04` y preserva PE-05 y la infraestructura PE-06A.

## Comparación PE-05 y PE-06B

PE-05 cubre 25 instituciones con tres dimensiones y 45% de cobertura, usando evidencia
PE-02/PE-04 sin nuevas comprobaciones técnicas. PE-06B evalúa documentalmente cinco
dimensiones adicionales en cinco ministerios, pero mantiene 45% puntuado porque esas
dimensiones quedan pendientes de una escala explícita. Son cortes históricos distintos; no
deben mezclarse ni ordenarse.

## Auditoría de las 25 dimensiones nuevas

En todos los casos el requisito es la dimensión indicada, el estado es
`partially_verified`, la puntuación es `pending_evaluation` y la regla OED-TD-1.0 aplicada es:
“peso definido, escala de transformación no definida; no crear componente ni asignar cero”.

| Institución | Dimensión | Máximo | Evidencia/observación | Limitación y razón exacta |
|---|---|---:|---|---|
| MAP | legal_framework | 15 | Mapa legal oficial | No se comprobó cada archivo; sin escala OED-TD-1.0 |
| MAP | organizational_structure | 15 | Sección Estructura Orgánica | Sin versión descargable comprobada; pendiente |
| MAP | official_contact_information | 10 | Portal MAP/OAI | Datos localizados, pero sin escala de completitud |
| MAP | document_searchability | 10 | HTML con texto | Texto observado, sin escala de puntos |
| MAP | stable_links | 5 | HTTP 200 único | Una tentativa no demuestra estabilidad |
| Hacienda | legal_framework | 15 | Catálogo legal oficial | Catálogo no revisado exhaustivamente; sin escala |
| Hacienda | organizational_structure | 15 | Resolución 226-2025/estructura | Evidencia sólida, pero OED-TD-1.0 no define puntuación |
| Hacienda | official_contact_information | 10 | Portal institucional/OAI | Contactos observados, sin escala de completitud |
| Hacienda | document_searchability | 10 | HTML con texto y metadatos | Sin regla de conversión a puntos |
| Hacienda | stable_links | 5 | HTTP 200 único | No prueba estabilidad temporal |
| MINERD | legal_framework | 15 | Marco legal/Ley 66-97 | Catálogo no exhaustivo; sin escala |
| MINERD | organizational_structure | 15 | Mapa con organigrama interactivo | Fecha/versión no confirmadas; pendiente |
| MINERD | official_contact_information | 10 | Portal y mapa OAI | Correo OAI vigente no confirmado; pendiente |
| MINERD | document_searchability | 10 | HTML con texto | Sin regla de conversión a puntos |
| MINERD | stable_links | 5 | HTTP 200 único | No prueba estabilidad temporal |
| MISPAS | legal_framework | 15 | Resolución DIGEIG 002-2021 | No es inventario institucional completo; pendiente |
| MISPAS | organizational_structure | 15 | Organigrama OAI/Resolución 168 | No es organigrama institucional completo; pendiente |
| MISPAS | official_contact_information | 10 | Portal de servicios | Contacto individual OAI/SAIP no confirmado; pendiente |
| MISPAS | document_searchability | 10 | PDF con extracción textual | Sin regla de conversión a puntos |
| MISPAS | stable_links | 5 | HTTP 200 y check adicional con bucle | `technical_error`; sin enlace roto ni estabilidad probada |
| Medio Ambiente | legal_framework | 15 | Marco legal oficial | Evidencia localizada, pero catálogo no exhaustivo y sin escala |
| Medio Ambiente | organizational_structure | 15 | Manual 2024 textual | Evidencia sólida, pero sin regla OED-TD-1.0 de máximo |
| Medio Ambiente | official_contact_information | 10 | Página RAI/OAI | Evidencia completa observada, pero sin escala de puntuación |
| Medio Ambiente | document_searchability | 10 | PDF textual sin OCR | Buscabilidad verificada, sin regla de puntos |
| Medio Ambiente | stable_links | 5 | HTTP 200 único | No prueba estabilidad temporal |

## Limitaciones, lenguaje público y tareas pendientes

La revisión es documental, acotada y no exhaustiva. No demuestra cumplimiento legal,
calidad administrativa, inexistencia documental ni estabilidad futura. El lenguaje público
permitido es: “localizado”, “no localizado en las fuentes revisadas”, “respondió en la fecha de
consulta”, “texto extraído” y “limitación observada”. No se permiten acusaciones, conclusiones
de corrupción, payloads crudos, notas internas ni identificadores sensibles.

No hay tareas manuales nuevas ni solicitudes SAIP. Queda pendiente una futura fase autorizada
para comprobar versiones de organigramas y contactos OAI no confirmados, sin presumir su
ausencia.

## Derecho de corrección

Cada institución puede aportar una URL oficial, versión documental o aclaración verificable.
La corrección se incorporará como nueva evidencia y nueva evaluación histórica; no se
sobrescriben PE-05 ni PE-06B.
