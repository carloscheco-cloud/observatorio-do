# Observatorio del Estado Dominicano

API e infraestructura de datos independiente para registrar instituciones públicas con
trazabilidad documental. Los bloques 1 y 2 implementan un monolito modular con FastAPI,
SQLAlchemy, PostgreSQL y Alembic.

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
