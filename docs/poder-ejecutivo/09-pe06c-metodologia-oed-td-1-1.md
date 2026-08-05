# PE-06C: metodología OED-TD-1.1

## Motivo, alcance y versionado

OED-TD-1.1 conserva los 100 puntos y las ocho dimensiones de OED-TD-1.0, pero añade escalas discretas para las cinco dimensiones que PE-06B dejó pendientes. OED-TD-1.0 queda histórica e inmutable; 1.1 la sucede sin recalcular PE-05 ni PE-06B. Una futura modificación de condiciones, puntos o lenguaje público exige una nueva versión, nunca editar una publicada.

Los pesos son: identidad institucional 10; marco legal 15; estructura y organigrama 15; autoridades actuales 15; actos de designación 20; contacto institucional y OAI 10; buscabilidad 10; estabilidad de enlaces y metadatos 5. Total: 100. Las reglas 1.0 de identidad, autoridades y designaciones se conservan; esta versión formaliza las cinco dimensiones restantes.

## Principios de cálculo

Solo puntúan observaciones con evidencia enlazada. Cada componente guarda versión, `rule_code`, puntos, máximo, observación, evidencia, razón de cálculo y explicación pública. Los valores intermedios libres se rechazan. `pending_evaluation` no significa cero y queda fuera del máximo evaluado. `not_applicable` se excluye del denominador. Un cero exige la condición explícita de la regla y alcance de revisión documentado. Un error temporal nunca prueba ausencia ni enlace roto. No se concede el máximo por defecto y toda limitación reduce el nivel conforme a la escala.

El puntaje bruto suma reglas representativas. El máximo evaluado suma pesos aplicables y evaluados; el normalizado es `bruto / máximo evaluado × 100`. La cobertura es el máximo evaluado sobre 100. Madurez: menos de 60, parcial; 60 a menos de 90, provisional; desde 90, completa. Ningún resultado produce `rank` ni posición comparativa.

## Catálogo completo de reglas nuevas

| dimensión | regla | condición verificable | puntos | explicación pública |
|---|---|---|---:|---|
| legal_framework | TD11-LEGAL_FRAMEWORK-15 | Sección oficial atribuida; norma principal identificable; documentos accesibles; número, fecha y enlaces oficiales; cobertura suficiente | 15 | Marco legal oficial completo y verificable. |
| legal_framework | TD11-LEGAL_FRAMEWORK-12 | Sección y normas principales accesibles; una carencia menor de metadatos, actualización o cobertura | 12 | Marco legal sustancial con una limitación menor. |
| legal_framework | TD11-LEGAL_FRAMEWORK-09 | Marco oficial parcial, lista sin todos los documentos o metadatos/enlaces incompletos | 9 | Marco legal oficial disponible parcialmente. |
| legal_framework | TD11-LEGAL_FRAMEWORK-06 | Referencias oficiales dispersas y solo parte verificable | 6 | Referencias legales oficiales limitadas. |
| legal_framework | TD11-LEGAL_FRAMEWORK-03 | Base legal mencionada sin documento oficial verificable | 3 | Base legal mencionada, sin documento verificable. |
| legal_framework | TD11-LEGAL_FRAMEWORK-00 | Revisión completa documentada sin marco oficial localizable | 0 | No se localizó marco legal oficial en el alcance revisado. |
| organizational_structure | TD11-ORGANIZATIONAL_STRUCTURE-15 | Organigrama institucional oficial, inequívoco, fechado/versionado, legible, suficiente y descargable o navegable | 15 | Organigrama institucional completo y verificable. |
| organizational_structure | TD11-ORGANIZATIONAL_STRUCTURE-12 | Organigrama institucional oficial completo y legible, sin fecha o versión verificable | 12 | Organigrama completo sin fecha o versión verificable. |
| organizational_structure | TD11-ORGANIZATIONAL_STRUCTURE-09 | Estructura sustancial u organigrama parcial/interactivo con limitaciones | 9 | Estructura oficial sustancial con limitaciones. |
| organizational_structure | TD11-ORGANIZATIONAL_STRUCTURE-06 | Estructura textual oficial sin organigrama institucional completo | 6 | Estructura textual oficial disponible. |
| organizational_structure | TD11-ORGANIZATIONAL_STRUCTURE-03 | Estructura limitada o solo organigrama de unidad interna | 3 | Solo se verificó estructura limitada o de una unidad. |
| organizational_structure | TD11-ORGANIZATIONAL_STRUCTURE-00 | Búsqueda completa sin estructura institucional oficial localizable | 0 | No se localizó estructura oficial en el alcance revisado. |
| official_contact_information | TD11-OFFICIAL_CONTACT_INFORMATION-10 | Dirección, teléfono, correo/canal general; OAI y teléfono/correo OAI; SAIP o equivalente, todos oficiales | 10 | Contacto institucional y OAI completos. |
| official_contact_information | TD11-OFFICIAL_CONTACT_INFORMATION-08 | Contacto institucional completo; OAI identificada con canal suficiente | 8 | Contacto completo y canal OAI suficiente. |
| official_contact_information | TD11-OFFICIAL_CONTACT_INFORMATION-06 | Contacto institucional suficiente; OAI parcialmente documentada | 6 | Contacto suficiente y OAI parcial. |
| official_contact_information | TD11-OFFICIAL_CONTACT_INFORMATION-04 | Contacto institucional parcial; OAI no localizada o incompleta | 4 | Contacto institucional parcial. |
| official_contact_information | TD11-OFFICIAL_CONTACT_INFORMATION-02 | Un único canal institucional básico verificable | 2 | Solo se verificó un canal institucional básico. |
| official_contact_information | TD11-OFFICIAL_CONTACT_INFORMATION-00 | Revisión completa sin contacto oficial verificable | 0 | No se localizó contacto oficial en el alcance revisado. |
| document_searchability | TD11-DOCUMENT_SEARCHABILITY-10 | Check confirma HTML/PDF con texto seleccionable, título/metadatos mínimos y localización clara | 10 | Contenido buscable e identificable. |
| document_searchability | TD11-DOCUMENT_SEARCHABILITY-08 | Texto seleccionable; metadatos o navegación incompletos | 8 | Contenido buscable con limitaciones menores. |
| document_searchability | TD11-DOCUMENT_SEARCHABILITY-06 | Contenido parcialmente buscable o extracción limitada | 6 | Contenido parcialmente buscable. |
| document_searchability | TD11-DOCUMENT_SEARCHABILITY-04 | Documento legible pero no buscable o escaneado | 4 | Documento legible, sin búsqueda de texto. |
| document_searchability | TD11-DOCUMENT_SEARCHABILITY-02 | Recurso accesible con dificultades técnicas graves de interpretación | 2 | Consulta técnicamente muy limitada. |
| document_searchability | TD11-DOCUMENT_SEARCHABILITY-00 | Recurso oficial disponible pero técnicamente inutilizable | 0 | Recurso disponible, pero inutilizable para consulta. |
| stable_links | TD11-STABLE_LINKS-05 | URL directa o redirección oficial estable, 2xx, tipo correcto e identificación básica | 5 | Recurso oficial estable y correctamente identificado. |
| stable_links | TD11-STABLE_LINKS-04 | Disponible con redirección o carencia menor de metadatos | 4 | Recurso disponible con una limitación menor. |
| stable_links | TD11-STABLE_LINKS-03 | Disponible con URL poco estable, navegación indirecta o metadatos pobres | 3 | Recurso disponible mediante acceso poco estable. |
| stable_links | TD11-STABLE_LINKS-02 | Restringido, intermitente o `technical_error` no concluyente | 2 | Acceso no concluyente por limitación técnica. |
| stable_links | TD11-STABLE_LINKS-01 | `not_found_provisional` con alternativa o evidencia histórica | 1 | Enlace provisionalmente no localizado; existe referencia complementaria. |
| stable_links | TD11-STABLE_LINKS-00 | `broken_link_confirmed` conforme a PE-06A | 0 | Enlace roto confirmado mediante comprobaciones suficientes. |

## Evidencia y distinciones

Marco legal exige atribución institucional y evidencia de la norma principal, catálogo, archivos y metadatos correspondientes al nivel. Varias páginas pueden formar una misma cobertura, pero la razón debe enumerar su aporte. Una simple mención activa 3, nunca 15.

En estructura, un organigrama institucional representa la institución completa; el de OAI representa solo esa unidad. Un directorio lista contactos, un menú organiza navegación y una estructura textual describe dependencias: ninguno se presenta como organigrama completo. La legibilidad, fecha/versión, atribución y cobertura se verifican por separado.

Contacto evalúa canales institucionales, no personas. No se guardan ni puntúan datos personales. La OAI puede acreditarse por su canal funcional; SAIP o equivalente es un subcriterio, pero esta fase no crea solicitudes SAIP.

Buscabilidad usa exclusivamente `SearchabilityCheck` y observaciones verificadas. No usa OCR ni infiere resultados por extensión. Estabilidad usa el historial de `ResourceCheck`: un `technical_error` puntual permanece no concluyente; cero requiere `broken_link_confirmed`.

## Múltiples recursos, contradicciones y correcciones

Los recursos no se suman. Se selecciona explícitamente una observación representativa vigente y la razón identifica por qué; las demás quedan como evidencia complementaria. No se permite escoger silenciosamente el mejor resultado. Si un recurso bueno y otro roto cubren el mismo objeto, se documentan vigencia, URL, alcance y discrepancia antes de seleccionar. Si cubren objetos distintos, la escala refleja cobertura y limitaciones. Un organigrama institucional prevalece para cobertura institucional; uno OAI solo complementa. Contacto general completo con OAI parcial activa como máximo 6. Resultados contradictorios bloquean el cálculo hasta incluir reconciliación explícita.

Una corrección crea una evaluación histórica nueva y conserva observaciones, evidencias, regla aplicada y evaluación anterior. El lenguaje público describe disponibilidad observable, nunca acusa incumplimiento, fraude o corrupción, y no expone payloads crudos, notas internas ni identificadores sensibles.
