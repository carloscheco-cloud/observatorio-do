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
- `employment_relationships` conserva vínculos laborales y sus vigencias sin eliminar
  historia; cargo y unidad pertenecen siempre a la institución del vínculo.
- `payroll_periods` y `payroll_entries` son datos canónicos versionados. Una nómina
  confirmada nunca se sobrescribe: toda corrección crea una nueva versión enlazada.
- `payroll_entry_components` desglosa ingresos y descuentos; `payroll_findings` contiene
  únicamente señales observables, nunca conclusiones de fraude o corrupción.
- Ningún identificador sensible se guarda en texto plano. Las referencias se protegen con
  HMAC-SHA256 y `PAYROLL_REFERENCE_SALT`; `raw_payload` no se expone públicamente.
- Solo los servicios autorizados de empleo y nómina escriben sus tablas canónicas. La IA
  puede proponer clasificaciones y hallazgos, pero no realizar escrituras canónicas.

## Calidad

El módulo `budget` conserva ciclos, clasificadores, programas, apropiaciones,
modificaciones, ejecución, ingresos, transferencias, versiones y hallazgos observables.
Un presupuesto confirmado no se sobrescribe; solo el servicio presupuestario autorizado
escribe datos canónicos y los actores IA solo proponen clasificaciones o hallazgos.

Antes de entregar cambios ejecutar `make lint`, `make typecheck` y `make test`.
Agregar una migración, pruebas unitarias, de arquitectura e integración cuando corresponda.

