# Guía para agentes

## Arquitectura

- Mantener un monolito modular bajo `backend/app/modules`.
- PostgreSQL es la base canónica y Alembic es la única vía para cambiar su esquema.
- `territories` e `institutions` contienen datos canónicos.
- `sources` describe procedencia; `evidence` conserva afirmaciones y su contenido original.
- Toda institución confirmada debe tener evidencia enlazada.
- Las automatizaciones de IA solo pueden proponer datos en fuentes/evidencias; nunca escribir en tablas canónicas.
- `organizational_units` y `organizational_events` conservan la estructura y sus cambios
  históricos; no se sobrescriben nombres, dependencias ni vigencias sin registrar el evento.
- Toda unidad canónica requiere fundamento legal y enlace diferido a evidencia y fuente.
- Los cargos vinculados a unidades deben pertenecer a la misma institución y su adscripción
  histórica se conserva en `position_unit_assignments`.

## Calidad

Antes de entregar cambios ejecutar `make lint`, `make typecheck` y `make test`.
Agregar una migración, pruebas unitarias, de arquitectura e integración cuando corresponda.

