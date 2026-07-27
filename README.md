# Observatorio del Estado Dominicano

API e infraestructura de datos independiente para registrar instituciones públicas con
trazabilidad documental. Los bloques 1 a 4 implementan un monolito modular con FastAPI,
SQLAlchemy, PostgreSQL y Alembic, incluyendo personas, cargos, fundamentos legales y
designaciones históricas, además de unidades, jerarquías y eventos organizativos.

## Inicio rápido

```bash
cp .env.example .env
docker compose up --build
```

La API estará en `http://localhost:8000`, su documentación en `/docs`, y dispone de
`/health` y `/health/db`.

## Desarrollo local

Requiere Python 3.12 y PostgreSQL 16:

```bash
make install
make db-up
make migrate
make seed
make run
```

Validación:

```bash
make check
make test-integration
```

## Integridad y procedencia

- `territories` e `institutions` son datos canónicos.
- `sources` conserva la procedencia y `evidence` la afirmación observable.
- `institution_evidence` hace trazable cada institución hasta su evidencia.
- PostgreSQL impide confirmar una institución sin evidencia y retirar su último respaldo.
- PostgreSQL y el servicio rechazan escrituras canónicas cuando `app.actor_type = 'ai'`.
- Cada cargo referencia un fundamento legal respaldado por evidencia.
- Las designaciones confirmadas requieren persona, cargo, institución, evidencia y fuente.
- Los cargos de ocupante único no admiten designaciones confirmadas solapadas.
- `organizational_units` conserva unidades con vigencia, múltiples raíces legales y
  relaciones padre-hijo protegidas contra ciclos.
- Una unidad canónica requiere fundamento legal y un vínculo diferido a evidencia y fuente.
- `organizational_events` registra cambios sin sobrescribir la historia, y
  `position_unit_assignments` conserva la adscripción histórica de los cargos.
- El organigrama actual o histórico se consulta en
  `/api/v1/institutions/{id}/organizational-chart?as_of=YYYY-MM-DD`; ancestros,
  descendientes, ruta, cargos y responsables se consultan desde `/organizational-units`.

## Empleo público y nóminas

El Bloque 5 incorpora relaciones laborales históricas, períodos mensuales versionados,
entradas y componentes de remuneración, comparación entre períodos, métricas y señales
observables. Los principales recursos están bajo `/api/v1/employment-relationships`,
`/api/v1/payroll-periods` y `/api/v1/payroll-findings`.

Las referencias sensibles se conservan únicamente como HMAC-SHA256 usando
`PAYROLL_REFERENCE_SALT`; nunca se exponen `raw_payload` ni identificadores sensibles en
respuestas públicas. La procedencia, evidencia, fila, payload original, procesamiento,
versión, actor y estado de validación se conservan en capas diferenciadas. Los actores IA
solo pueden proponer fuentes, evidencias o señales analíticas.

La cabeza Alembic actual es `0009`. Las semillas de los bloques 4 a 9 son idempotentes y
todos sus datos organizativos y salariales están marcados como ficticios y controlados.

## Presupuesto público y ejecución financiera

El Bloque 6 incorpora ciclos y versiones, clasificadores, fuentes de financiamiento,
programas, apropiaciones, modificaciones, ejecución, ingresos, transferencias y
hallazgos observables. Cada cifra canónica conserva procedencia, evidencia, período,
payload original no público, versión, actor y checksum; los actores IA no escriben estas
tablas.

La API expone `/api/v1/budget-cycles`, `/budget-classifiers`, `/budget-programs`,
`/budget-appropriations`, `/budget-modifications`, `/budget-execution-records`,
`/budget-revenues`, `/interinstitutional-transfers` y `/budget-findings`, además de
métricas, historial, evolución y comparación. La ingesta ofrece vista previa y dry-run
con checksum, mapeo, errores por fila, límite de tamaño y protección contra fórmulas CSV.

## Compras públicas y ejecución contractual

El Bloque 7 modela procesos, lotes, ítems, proveedores, ofertas, evaluaciones,
adjudicaciones, contratos, modificaciones, órdenes, entregas, pagos, garantías,
impugnaciones, versiones y señales exclusivamente observables. La API está bajo
`/api/v1/procurement-processes`, `/suppliers`, `/procurement-bids`,
`/procurement-awards`, `/procurement-contracts`, `/contract-amendments`,
`/contract-payments` y `/procurement-findings`, con métricas institucionales,
concentración por proveedor e historial.

Todo registro canónico exige fuente y evidencia coherentes. Los identificadores sensibles
se admiten solo como hashes SHA-256, el payload original queda excluido de respuestas
públicas y PostgreSQL impide incompatibilidades, importes negativos, pagos excesivos,
sobrescritura silenciosa y escrituras canónicas por actores IA. La ingesta futura dispone
de adaptadores y vista previa CSV con dry-run, checksum, límites y protección contra fórmulas.

## Deuda pública, obligaciones y riesgos fiscales

El Bloque 8 incorpora acreedores, instrumentos, condiciones, desembolsos, servicio,
pagos, saldos versionados, emisiones, garantías, obligaciones, transferencias, subsidios
institucionales, compromisos plurianuales, reestructuraciones y riesgos exclusivamente
observables. Montos y tasas usan `Numeric`/`Decimal`; toda escritura canónica exige
procedencia y evidencia y rechaza actores IA.

La API expone `/api/v1/creditors`, `/debt-instruments`, `/debt-disbursements`,
`/debt-payments`, `/public-guarantees`, `/public-obligations`, `/financial-transfers`,
`/public-subsidies`, `/multi-year-commitments` y `/fiscal-risk-findings`, además de
exposición, historial, métricas, servicio y comparaciones institucionales.

## Patrimonio y activos públicos

El Bloque 9 incorpora categorías históricas, bienes públicos, ubicaciones, extensiones
para inmuebles, vehículos, equipos, infraestructura e intangibles, además de custodia,
transferencias, eventos, mantenimiento, valoraciones, seguros, gravámenes, inventarios,
disposiciones, versiones y señales observables. Los importes usan `Numeric`/`Decimal`.

La API expone `/api/v1/asset-categories`, `/public-assets`, `/asset-locations`,
`/asset-assignments`, `/asset-transfers`, `/asset-maintenance-records`,
`/asset-valuations`, `/physical-inventories`, `/asset-disposals` y `/asset-findings`,
además de historial y métricas institucionales. La ingesta controlada ofrece vista previa,
dry-run, checksum, errores por fila, límites de tamaño y protección CSV.

Los actores IA no escriben datos patrimoniales canónicos. Placas, VIN, chasis, títulos,
seriales y pólizas se conservan únicamente mediante hash o enmascaramiento; ubicaciones
restringidas no exponen dirección pública y `raw_payload` queda fuera de los esquemas de
respuesta. Las semillas del bloque son ficticias, controladas e idempotentes.

## Motor transversal de señales y revisión

El Bloque 10 incorpora `risk_engine`, que versiona taxonomías, reglas y umbrales;
registra ejecuciones reproducibles; unifica señales; conserva evidencia contradictoria;
deduplica recurrencias; y audita revisiones, supresiones, publicaciones y puntuaciones.
**Una señal o puntuación no equivale a una acusación ni permite concluir fraude,
corrupción, ilegalidad, culpabilidad o intención.**

Los módulos canónicos no dependen del motor y ninguna regla escribe en sus tablas. Las
reglas propuestas por IA quedan desactivadas hasta aprobación humana. Una alerta
confirmada o pública exige evidencia y la publicación exige revisión humana. La falta de
datos se expresa separadamente del riesgo sustantivo.

La API ofrece `/api/v1/risk-taxonomy`, `/risk-rules`, `/risk-findings`, evidencia,
historial y vistas por entidad. Las escrituras viven bajo `/api/v1/internal/risk-*`,
usan los encabezados conceptuales `X-Actor-Type` y `X-Actor-Id`, y están preparadas para
autorización futura. Las respuestas públicas excluyen notas internas, payloads originales
y referencias sensibles, y tienen paginación limitada.

La migración `0010` crea el esquema, índices y guardas PostgreSQL. Las semillas de
taxonomía, reglas, umbrales, ejecución, alertas, revisión, supresión y puntuación son
ficticias, controladas e idempotentes.

```bash
python -m app.modules.risk_engine run
python -m app.modules.risk_engine run --domain procurement
python -m app.modules.risk_engine run --institution-id UUID
python -m app.modules.risk_engine run --rule-id UUID
python -m app.modules.risk_engine dry-run --domain payroll
python -m app.modules.risk_engine backfill --period-start 2025-01-01 --period-end 2025-12-31
python -m app.modules.risk_engine summary
```

Para crear una regla, cree una nueva versión mediante el servicio interno, declare campos,
entidades, ventana, umbrales y plantillas simples, e implemente `RuleEvaluator`. El
evaluador solo devuelve `RuleResult` con `FindingCandidate`; persistencia, deduplicación,
auditoría y puntuación pertenecen al núcleo transversal. La explicación identifica
observación, regla, umbral, comparación, diferencia, período, evidencia y límites.

El motor funcional registra once adaptadores SQLAlchemy: nómina, empleo, presupuesto,
compras, deuda, patrimonio, instituciones, organización, designaciones, trazabilidad y
cruces de dominio. Cada ejecución consulta datos canónicos en lotes, genera candidatos
con evidencia estructurada, aísla errores por adaptador, aplica supresiones, agrupa por
regla, persiste o incrementa recurrencias mediante huella estable y recalcula puntuaciones.
`dry-run` ejecuta las mismas consultas y devuelve el mismo resumen sin persistir
hallazgos, enlaces, grupos ni puntuaciones.
