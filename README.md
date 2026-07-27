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

La cabeza Alembic actual es `0004`. Las semillas del bloque 4 son idempotentes y todos sus
datos organizativos están marcados expresamente como ficticios y controlados.
