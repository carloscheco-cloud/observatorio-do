# PE-01 — Núcleo institucional del Poder Ejecutivo

## Estado

Implementado en `feature/poder-ejecutivo`. Pendiente de ejecución de la suite completa y migración sobre PostgreSQL antes de considerarse cerrado.

## Cambios

- Clasificación del poder del Estado.
- Taxonomía controlada de instituciones del Ejecutivo.
- Estado operativo y nivel de cobertura.
- Siglas, slug, web oficial, funciones, creación y última revisión.
- Relaciones históricas entre instituciones con evidencia y períodos de vigencia.
- Migración Alembic reversible `0012`.
- Compatibilidad con payloads institucionales heredados.
- Pruebas de validación de esquemas.

## Validaciones obligatorias

```bash
make lint
make typecheck
make test
make db-up
make migrate
make test-integration
cd backend && python -m alembic downgrade 0011 && python -m alembic upgrade 0012
```

No fusionar hasta que todas las validaciones anteriores resulten correctas.
