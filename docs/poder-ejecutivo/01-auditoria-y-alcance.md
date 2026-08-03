# Poder Ejecutivo — Auditoría inicial y alcance de implementación

Fecha de inicio: 2026-07-29  
Rama de trabajo: `feature/poder-ejecutivo`  
Objetivo: alcanzar aproximadamente 80% funcional antes del 2026-10-01.

## 1. Diagnóstico del repositorio

El repositorio ya implementa una plataforma transversal y modular sobre FastAPI, SQLAlchemy, PostgreSQL y Alembic. El módulo Poder Ejecutivo debe construirse como una especialización del dominio institucional existente, sin duplicar modelos de nómina, presupuesto, compras, patrimonio, autoridades, evidencia ni alertas.

### Componentes existentes reutilizables

- `app.modules.institutions`: registro canónico de instituciones y evidencia asociada.
- `app.modules.organizational_units`: unidades y organigramas históricos.
- `app.modules.persons`, `positions`, `appointments`: autoridades, cargos y períodos.
- `app.modules.legal_basis`: fundamentos legales.
- `app.modules.employment_relationships`, `payroll_periods`, `payroll_entries`: empleo y nómina.
- `app.modules.budget`: presupuesto y ejecución.
- `app.modules.procurement_processes`, `suppliers`: compras y proveedores.
- `app.modules.public_assets`, `asset_categories`: patrimonio público.
- `app.modules.territories`: provincias, municipios y demás territorios.
- `app.modules.risk_engine`: señales observables con revisión humana.
- `app.modules.ingestion`: catálogo de fuentes, artefactos, staging, linaje y carga autorizada.
- `app.modules.public_api`: superficie pública estable.
- `frontend/`: producto ciudadano en Next.js/TypeScript.

## 2. Brechas encontradas para Poder Ejecutivo

El modelo base de `institutions` actualmente contiene nombre, tipo libre (`kind`), territorio, estado y evidencia. Para representar correctamente el Poder Ejecutivo faltan, como mínimo:

1. Clasificación canónica del poder del Estado.
2. Tipología institucional controlada y extensible.
3. Siglas y nombre corto.
4. Estado operativo institucional separado del estado de validación del registro.
5. Relación jerárquica directa entre instituciones.
6. Fechas de creación, inicio y término institucional cuando apliquen.
7. Alcance nacional o territorial.
8. Identificador público estable (`slug`).
9. Estado de cobertura y fecha de revisión.
10. Consultas públicas específicas para el árbol del Poder Ejecutivo.

Las relaciones detalladas internas deben seguir usando `organizational_units`; la nueva relación entre instituciones representará adscripción o dependencia institucional de alto nivel.

## 3. Decisiones de arquitectura

- No crear una tabla paralela `executive_institutions`.
- Extender `institutions` con atributos transversales útiles para todos los poderes.
- Incorporar una clasificación `state_branch`, comenzando por `executive`, sin cargar datos de Legislativo o Judicial en esta rama.
- Reemplazar progresivamente el texto libre de `kind` por una taxonomía controlada, manteniendo compatibilidad durante la migración.
- Modelar la jerarquía institucional con una tabla histórica de relaciones, no con un único `parent_id` que sobrescriba el pasado.
- Toda carga real deberá pasar por fuentes, evidencia, staging, validación y servicio canónico existente.
- Los datos ficticios o demostrativos deberán llevar marcación explícita.

## 4. Primer bloque concreto de implementación

### Bloque PE-01 — Núcleo institucional del Poder Ejecutivo

Entregables técnicos:

1. Migración Alembic reversible para ampliar el modelo institucional.
2. Enumeraciones controladas para poder del Estado, tipo institucional, alcance y estado operativo.
3. Tabla histórica de relaciones jerárquicas entre instituciones.
4. Campos públicos: siglas, slug, fecha de creación, sitio oficial, cobertura y última revisión.
5. Validaciones para impedir ciclos jerárquicos y relaciones incompatibles.
6. Esquemas Pydantic de lectura y escritura compatibles con la API existente.
7. Servicios de consulta del árbol ejecutivo actual o a una fecha determinada.
8. Pruebas unitarias e integración para migración, validaciones y consultas.

### Criterios de aceptación

- Una institución puede clasificarse inequívocamente como perteneciente al Poder Ejecutivo.
- Presidencia, ministerios, organismos adscritos, autónomas, superintendencias, empresas públicas y gobernaciones pueden representarse sin texto ambiguo.
- Las relaciones institucionales conservan vigencia histórica.
- No se admiten ciclos.
- Cada registro confirmado conserva trazabilidad documental.
- Las rutas existentes continúan funcionando.
- La migración puede revertirse sin dejar objetos huérfanos.
- `make check` y las pruebas de integración deben aprobar antes de continuar a PE-02.

## 5. Secuencia inmediata posterior

- PE-01: núcleo institucional y jerarquía.
- PE-02: inventario oficial priorizado y catálogo de fuentes.
- PE-03: carga controlada de Presidencia, Vicepresidencia y ministerios.
- PE-04: API pública del árbol ejecutivo y fichas institucionales.
- PE-05: interfaz Next.js de navegación y filtros.

No se iniciará PE-02 mientras PE-01 tenga migraciones, pruebas o compatibilidad rotas.
