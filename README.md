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

La cabeza Alembic actual es `0005`. Las semillas de los bloques 4 y 5 son idempotentes y
todos sus datos organizativos y salariales están marcados como ficticios y controlados.
