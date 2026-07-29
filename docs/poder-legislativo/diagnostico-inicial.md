# Poder Legislativo — diagnóstico inicial

Fecha de inicio: 2026-07-29  
Rama: `feature/poder-legislativo`

## Diagnóstico breve

El repositorio ya implementa un monolito modular con FastAPI, SQLAlchemy, PostgreSQL y Alembic. Existen dominios reutilizables para instituciones, territorios, personas, cargos, fuentes, evidencia, fundamento legal, nómina, presupuesto, compras, patrimonio, riesgo e ingesta.

El módulo legislativo debe reutilizar:

- `institutions`: Congreso Nacional, Senado y Cámara de Diputados.
- `territories`: provincias, Distrito Nacional y circunscripciones cuando se modelen como divisiones electorales verificadas.
- `persons`: identidad pública de legisladores.
- `sources` y `evidence`: procedencia de toda afirmación.
- `legal_bases`: Constitución, reglamentos y leyes orgánicas.
- módulos transversales de nómina, presupuesto y compras mediante `institution_id`.
- plataforma de ingesta para fuentes del Senado, Cámara de Diputados y portales de transparencia.

## Decisiones del primer bloque

1. Crear un dominio independiente `app.modules.legislative`.
2. No duplicar personas, instituciones, territorios, presupuesto, nómina ni compras.
3. Modelar el escaño separado del legislador para conservar sustituciones e historia.
4. Modelar partido y bloque por separado, porque no son equivalentes.
5. Registrar disponibilidad de iniciativas, asistencia, votaciones y declaraciones como estado explícito.
6. Exigir `source_id` y `evidence_id` en cada registro canónico legislativo.
7. Mantener períodos de vigencia para cámaras, escaños, bloques y mandatos.

## Núcleo agregado

- `legislative_chambers`
- `legislative_terms`
- `legislative_parties`
- `legislative_blocs`
- `legislative_seats`
- `legislative_mandates`

## Próximo bloque

Crear la migración Alembic reversible, registrar los modelos en el contexto de metadatos, añadir servicios y esquemas Pydantic, y exponer endpoints de lectura para cámaras, legisladores y mandatos actuales.
