# PE-05: transparencia digital documental

## Propósito y límites

PE-05 mide disponibilidad y calidad documental digital, no honestidad, legalidad, corrupción,
calidad del servicio ni desempeño gubernamental. Una ausencia digital no demuestra
inexistencia jurídica; “no localizado” significa únicamente que el recurso no apareció en el
alcance y fecha declarados. Una página institucional tampoco sustituye un acto jurídico.

La evaluación inicial reutiliza exclusivamente evidencia oficial registrada por PE-02 y PE-04
al 3 de agosto de 2026. No realizó nuevas búsquedas web ni comprobaciones HTTP. Por ello es
una evaluación parcial de las 25 instituciones: identidad/sitio, autoridad vigente y acto de
designación. Marco legal, estructura, contacto/OAI, calidad técnica y permanencia/metadatos
quedan `not_evaluated`; no se convierten en cero ni en `not_applicable`.

## Metodología inmutable OED-TD-1.0

| Dimensión | Peso |
|---|---:|
| Identidad institucional y sitio oficial | 10 |
| Marco legal localizable | 15 |
| Estructura y organigrama | 15 |
| Autoridades actuales | 15 |
| Actos de designación | 20 |
| Información de contacto y OAI | 10 |
| Calidad técnica y buscabilidad | 10 |
| Permanencia de enlaces y metadatos | 5 |

Total: 100. El puntaje bruto es la suma de componentes aplicables evaluados. El máximo
evaluado es la suma de sus pesos. El normalizado es `bruto / máximo evaluado × 100`. Una
dimensión auténticamente `not_applicable` se excluye del numerador y denominador; una no
revisada permanece ausente y reduce la cobertura, sin fingir un resultado. Se conservan bruto,
normalizado, máximo, cobertura, fórmula, componentes, observaciones e incertidumbre.

Para actos de designación: 20 exige acto localizado, descargable, buscable y con metadatos;
16 corresponde a acto localizado con deficiencias o propiedades técnicas aún no completas;
12 a nombramiento oficial verificable cuyo acto individual no fue localizado; 6 a autoridad
identificada sin evidencia suficiente del nombramiento; 0 a autoridad actual no verificable
oficialmente. PE-05 no presume cualidades técnicas no comprobadas.

Las bandas internas del puntaje normalizado son: 90–100, disponibilidad digital avanzada;
75–89.999, alta; 60–74.999, intermedia; 40–59.999, limitada; 0–39.999, muy limitada. No se
publican como clasificación institucional cuando la cobertura es menor de 60%.

La madurez se deriva exclusivamente de la cobertura ponderada: menos de 60% es `partial`,
con clasificación pública fija `evaluación parcial` y sin ranking ni posición comparativa; de
60% a menos de 90% es `provisional`, con banda descriptiva siempre acompañada de cobertura;
desde 90% es `complete`. Los umbrales impiden que pocas dimensiones con buen resultado se
presenten como evaluación integral. La carga inicial tiene `10 + 15 + 20 = 45` puntos de peso
evaluado sobre 100: cobertura 45%, madurez `partial`, clasificación pública `evaluación
parcial`, `rank=NULL` y `comparison_position=NULL`.

## Matriz de cobertura inicial

Todas las instituciones comparten exactamente el mismo alcance. `not_applicable` no se usó.

| Institución | Identidad | Marco legal | Estructura | Autoridades | Designación | Contacto/OAI | Buscabilidad | Enlaces/metadatos |
|---|---|---|---|---|---|---|---|---|
| Presidencia de la República | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Vicepresidencia de la República | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio Administrativo de la Presidencia | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Administración Pública | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Agricultura | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Cultura | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Defensa | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Deportes y Recreación | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Educación | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Educación Superior, Ciencia y Tecnología | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Energía y Minas | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Hacienda y Economía | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Industria, Comercio y Mipymes | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Interior y Policía | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Justicia | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de la Juventud | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de la Mujer | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de la Presidencia | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de la Vivienda, Hábitat y Edificaciones | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Medio Ambiente y Recursos Naturales | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Obras Públicas y Comunicaciones | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Relaciones Exteriores | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Salud Pública y Asistencia Social | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Trabajo | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |
| Ministerio de Turismo | evaluated | pending_evaluation | pending_evaluation | evaluated | evaluated | pending_evaluation | pending_evaluation | pending_evaluation |

## Estados y trazabilidad

Los estados son `verified_digitally`, `verified_offline`, `partially_verified`,
`pending_manual_search`, `requested_via_saip`, `not_located_in_reviewed_sources`,
`broken_link`, `source_unavailable`, `published_not_searchable`, `metadata_incomplete` y
`not_applicable`. No existe `not_published`: solo podrá incorporarse en otra metodología con
un canal oficial y una búsqueda suficientes para sostener esa afirmación.

Cada observación conserva institución, requisito, recurso opcional, fecha, revisor humano,
automatizado o híbrido, alcance, hallazgo, certeza, evidencia y metodología. Las observaciones
son históricas y no se sobrescriben. Los recursos conservan URL y, solo cuando se comprueban,
MIME, descarga, texto, OCR, metadatos, checksum, estado HTTP y última revisión. Un timeout es
`source_unavailable`; `broken_link` requiere 404/410 inequívoco o fallos repetidos. Un PDF sin
texto puede registrarse como `published_not_searchable` sin ejecutar OCR.

Los 72 recursos corresponden a 25 identidades, 25 autoridades vigentes y 22 actos localizados.
Las tres observaciones de actos no localizados no apuntan a un recurso inexistente; por eso 75
observaciones menos esas 3 ausencias producen 72 recursos. MIME, buscabilidad, OCR, HTTP,
checksum y metadatos permanecen `NULL` porque PE-05 no hizo comprobaciones técnicas nuevas.

## Tareas manuales y solicitudes SAIP/OAI

Kelvin Cruz, Joel Santos para Energía y Minas y José Ignacio Paliza tienen una observación
`not_located_in_reviewed_sources` y una tarea `open`, vinculada al nombramiento y con las
fuentes revisadas. No se afirma que sus actos no existan ni que haya incumplimiento. PE-05 no
crea solicitudes SAIP: el total inicial es cero. Una solicitud solo deja `draft` cuando fue
realmente enviada; códigos, plazos y respuestas nunca se inventan.

## Historia, corrección y operación

Una mejora, deterioro o enlace caído crea observación y evaluación nuevas; no elimina el
recurso ni la evaluación anterior. OED-TD-1.0 no se modifica después de publicarse: los cambios
serán OED-TD-1.1 u OED-TD-2.0. Una institución puede aportar el enlace oficial y evidencia,
solicitar corrección y ejercer derecho de réplica; la revisión registra fecha, alcance y una
nueva evaluación reproducible.

Cada componente persiste requisito, dimensión, peso, puntaje otorgado, máximo, estado de
verificación, observación, evidencia, versión y razón de cálculo. El score puede recalcularse
desde esos componentes sin usar `calculation_details` como respaldo único. Una evaluación
histórica conserva su propia clasificación pública, cobertura y fecha. Un cambio de reglas
requiere OED-TD-1.1 o una versión posterior; nunca una edición silenciosa de OED-TD-1.0.

```console
python -m app.modules.digital_transparency --dry-run
python -m app.modules.digital_transparency
python -m app.modules.digital_transparency recalculate
python -m app.modules.digital_transparency audit-report
python -m app.modules.digital_transparency rollback --dry-run
python -m app.modules.digital_transparency rollback
```

El rollback usa `digital_transparency_load_records`, elimina únicamente propiedad PE-05 y
preserva PE-02, PE-03 y PE-04. Después del rollback puede bajarse 0015 a 0014. El downgrade se
niega mientras existan registros de propiedad.

## Lenguaje público

Correcto: “No fue localizado en las fuentes oficiales digitales revisadas al 3 de agosto de
2026.” Incorrecto: “El ministerio ocultó el decreto.”

Correcto: “El recurso devolvió un error en dos comprobaciones realizadas.” Incorrecto: “La
institución eliminó deliberadamente el documento.”

Noticias y debates futuros deben citar metodología, fecha, alcance, evidencia e incertidumbre;
no pueden convertir una brecha documental en acusación política, penal o ética.
