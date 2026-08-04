# PE-03: dependencias y adscripciones del Poder Ejecutivo

## Objetivo y alcance

PE-03 incorpora una carga separada, transaccional y versionada de entidades secundarias y
sus vínculos jurídicos. La primera versión privilegia certeza sobre volumen y cubre dos casos
de las instituciones prioritarias: Ministerio de Administración Pública y Ministerio de la
Presidencia. No modifica el frontend ni crea una API pública.

## Auditoría del modelo PE-01/PE-02

El monolito modular conserva instituciones en `institutions`, procedencia en `sources`,
afirmaciones en `evidence`, enlaces de existencia en `institution_evidence` y una evidencia
directa en cada fila de `institution_relationships`. El modelo previo permitía múltiples
relaciones simultáneas, períodos históricos, cierre mediante `valid_to`, cambio de adscripción
mediante una nueva fila y prevención parcial de duplicados. No permitía `valid_from` ausente,
no obligaba a explicar esa ausencia y no prevenía ciclos institucionales. La migración `0013`
resuelve las dos primeras limitaciones y el cargador rechaza ciclos en relaciones estructurales;
la base todavía no tiene un trigger general de ciclos para escrituras ajenas al cargador.

## Taxonomía institucional mínima

| Tipo | Definición y criterio | Diferencia | Ejemplo y fuente |
|---|---|---|---|
| `institute` | Entidad denominada oficialmente instituto, con existencia individual y función estable. | No presume autonomía ni descentralización; esas cualidades requieren texto expreso. | INAP, clasificador COEDOM y portal del MAP. |
| `council` | Órgano colegiado estable creado por norma y con función rectora o coordinadora propia. | No incluye gabinetes ni comisiones temporales. | CONASSAN, Ley 589-16 confirmada por Decreto 693-24. |

No se añadieron tipos redundantes. `decentralized_institution`, `commission`,
`superintendency` y otros tipos existentes permanecen disponibles, pero esta versión no carga
ejemplos sin evidencia primaria suficiente.

## Taxonomía de relaciones

- `attached`: adscripción expresa. Es una vinculación sectorial o de tutela; no equivale por
  sí sola a jerarquía interna. Se usa para CONASSAN → Ministerio de la Presidencia.
- `dependent_on`: dependencia administrativa expresamente publicada. Se añadió porque
  `hierarchical` no expresa la categoría jurídica y `attached` no es sinónimo. Se usa para
  INAP → Ministerio de Administración Pública.

`coordinated` describe articulación funcional y `supervised` vigilancia o supervisión. Ninguna
de ambas implica adscripción. No se cargaron relaciones de presidencia de órganos colegiados,
integración de miembros, sucesión ni coordinación porque participar o presidir un consejo no
prueba subordinación institucional.

## Fuentes, entidades y evidencia

| Entidad | Naturaleza | Relación oficial | Evidencia de entidad | Evidencia de relación |
|---|---|---|---|---|
| Instituto Nacional de Administración Pública (INAP) | Instituto; órgano desconcentrado | `dependent_on` MAP; inicio no atribuido | COEDOM, detalle 36 y organigrama | Portal MAP, sección Dependencias: “es una dependencia” |
| Consejo Nacional para la Soberanía y Seguridad Alimentaria y Nutricional (CONASSAN) | Consejo nacional | `attached` al Ministerio de la Presidencia; inicio no atribuido | Decreto 693-24 como confirmación vigente | Ley 589-16, artículo 12, párrafo |

Fuentes oficiales consultadas el 3 de agosto de 2026:

- `https://map.gob.do/COEDOM/Home/Details/36?Ruta=2`
- `https://map.gob.do/sobre-nosotros/dependencias/`
- `https://presidencia.gob.do/sites/default/files/decree/2024-12/Decreto%20693-24.pdf`
- `https://www.consultoria.gov.do/Consulta/Home/FileManagement?documentId=3379448&managementType=2`

La Ley núm. 589-16 fue promulgada el 5 de julio de 2016 y publicada en la Gaceta Oficial
núm. 10849 el 8 de julio de 2016. Su artículo 12 crea el CONASSAN y su párrafo dispone
literalmente que está adscrito al Ministerio de la Presidencia. La disposición final de entrada
en vigencia exige promulgación, publicación y el transcurso de los plazos del Código Civil.
Como esta versión no verificó el cómputo de esos plazos, no convierte ninguna de esas fechas
en `valid_from`: la relación permanece con fecha inicial no disponible y nota explícita. El
Decreto 693-24 no crea ni modifica la adscripción; solo la menciona como antecedente vigente.

Cada afirmación genera evidencia individual con fuente, extracto, localizador, fecha de
consulta y hash. La evidencia institucional y la evidencia de la relación son registros
separados, incluso cuando proceden del mismo documento.

## Inclusiones y exclusiones

Solo se incluyen entidades vigentes con nombre, naturaleza y vínculo explícitos. Se excluyen:

- INCABIDE: la Ley 60-23 acredita adscripción al antiguo Ministerio de Hacienda; no se
  trasladó al Ministerio de Hacienda y Economía sin verificar la disposición sucesoria exacta
  de la Ley 45-25.
- Fondo Nacional de la Vivienda: el Decreto 191-21 prueba una adscripción histórica, pero la
  reorganización posterior del sector vivienda impide afirmar vigencia actual sin más estudio.
- Consejo de Asesores Especiales sobre turismo náutico y Comisión del Decreto 186-24:
  órganos vinculados a tareas específicas cuya vigencia actual no está acreditada.
- Arte Público Dominicano: programa sin verificación suficiente de vigencia y estructura
  institucional propia.
- Consejo Consultivo para la Transformación Policial y otros gabinetes: se requiere revisar
  norma, permanencia y estructura antes de tratarlos como instituciones canónicas.
- Entidades de Presidencia y Ministerio Administrativo de la Presidencia cuya única señal es
  navegación, organigrama interno o COEDOM sin texto inequívoco del vínculo.
- Órganos constitucionalmente autónomos: no se modelan como subordinados al Ejecutivo.

## Historia, divergencias e idempotencia

`valid_from` solo se llena con fecha jurídica. Cuando se desconoce, permanece `NULL` y `notes`
explica la ausencia. Una nueva adscripción crea otra fila; la anterior se cierra con `valid_to`
y nunca se borra. Los índices parciales impiden duplicados tanto con fecha conocida como sin
ella. El cargador no sobrescribe instituciones confirmadas, evidencias ni relaciones
divergentes: informa `skipped`. Un error fatal revierte fuentes, evidencias, instituciones y
relaciones de toda la ejecución.

## Comandos, dry-run y rollback

PE-02 es prerrequisito porque las instituciones vinculantes deben existir confirmadas:

```console
cd backend
python -m app.modules.executive_inventory
python -m app.modules.executive_dependencies --dry-run
python -m app.modules.executive_dependencies
python -m app.modules.executive_dependencies
python -m app.modules.executive_dependencies rollback --dry-run
python -m app.modules.executive_dependencies rollback
python -m alembic downgrade 0012
```

El dry-run ejecuta la misma operación y revierte la transacción. La primera carga crea dos
instituciones y dos relaciones; la segunda debe informar cuatro elementos `unchanged`.

La migración mantiene un registro de propiedad por cada fuente, evidencia, enlace,
institución y relación realmente creados por PE-03. El rollback elimina primero relaciones y
enlaces propios, luego instituciones propias sin referencias externas, evidencias propias
huérfanas y finalmente fuentes propias sin referencias. Nunca elimina una fila preexistente.
Si encuentra una referencia externa, conserva el dato y su registro de propiedad, informa
`skipped` y el downgrade continúa bloqueado. La operación es atómica, idempotente y admite
`--dry-run`.

Después del rollback real, `python -m alembic downgrade 0012` elimina la tabla de propiedad,
restaura los enums y devuelve `valid_from` a `NOT NULL`. No inventa fechas ni convierte
`INSTITUTE` o `DEPENDENT_ON` a categorías distintas. Intentar el downgrade antes del rollback
falla explícitamente para impedir pérdida o reinterpretación de datos.

## Limitaciones y pendientes

La prevención de ciclos vive en el cargador, no en un trigger PostgreSQL global. La taxonomía
seguirá creciendo solo con casos oficiales. Queda revisar textos consolidados y vigencia para
Presidencia, Ministerio Administrativo de la Presidencia y Ministerio de Hacienda y Economía,
y luego ampliar progresivamente a los demás ministerios. No se atribuyen relaciones ni fechas
con base en dominios, nombres, ubicación, organigramas internos o inferencias de sucesión.
