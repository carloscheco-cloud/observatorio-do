# PE-09 — Enriquecimiento Visual y Media Assets

## Auditoría de partida

El repositorio usa un monolito modular FastAPI/SQLAlchemy/Alembic, PostgreSQL 16 y un frontend Next.js 15. Las instituciones viven en `institutions`, las personas en `persons`, las autoridades se representan mediante designaciones y PE-07 expone lectura pública bajo `/api/v1/executive`.

La plataforma de ingesta ya dispone de `ArtifactStorage` para archivos crudos y evidencia de ETL. Ese almacenamiento no debe convertirse en el catálogo editorial público: conserva artefactos de procesamiento, puede contener material no publicable y responde a un ciclo de vida distinto. PE-09 crea un dominio independiente y deja abierta una implementación S3-compatible para copias gestionadas o caché.

No se encontró una tabla previa equivalente a `media_assets` ni contratos públicos para edificios, logos o retratos.

## Esquema definitivo mínimo

La migración `0019` crea `media_assets` con propietario institucional o personal, tipo, procedencia, URL pública, estrategia de almacenamiento, verificación, aprobación, condición de principal, texto alternativo, pie, licencia, dimensiones, checksum, auditoría y relación de sustitución.

Tipos permitidos:

- `institution_building`
- `authority_portrait`
- `institution_logo`
- `official_banner`
- `fallback`

Estados editoriales:

- `pending`
- `approved`
- `rejected`
- `archived`

Estrategias de almacenamiento:

- `remote_official`: la URL pública es la URL oficial validada.
- `managed`: copia aprobada en almacenamiento propio S3-compatible.
- `cached`: copia técnica renovable, conservando la URL oficial de origen.
- `generated_fallback`: recurso gráfico propio, sin representar edificio, persona o logo reales.

La base impide asociar simultáneamente un activo a institución y persona, exige propietario salvo fallback, exige procedencia salvo fallback generado, restringe dimensiones inválidas y evita más de un activo principal aprobado por entidad y tipo.

## API pública de solo lectura

- `GET /api/v1/executive/institutions/{slug}/media`
- `GET /api/v1/executive/authorities/{person_id}/media`
- `GET /api/v1/executive/media/{asset_id}`

Solo se exponen activos `approved`. No se publican `storage_key`, checksum, identidad del revisor, motivo de rechazo ni notas operativas. Una colección vacía devuelve `fallback_required=true`; no inventa una imagen.

## Política editorial

1. Priorizar Presidencia, ministerios, portales institucionales, archivos oficiales y cuentas institucionales verificadas.
2. No usar perfiles personales o redes no institucionales como fuente automática.
3. Registrar URL de origen, nombre de fuente, fecha de verificación, entidad, tipo y nota de licencia cuando esté disponible.
4. Validar que el contenido corresponda a la entidad o persona y que no esté desactualizado antes de aprobar.
5. No publicar cambios de identidad institucional o retratos sin revisión humana.
6. Archivar o sustituir sin borrar el historial; `supersedes_asset_id` conserva la cadena editorial.
7. Usar `alt_text` descriptivo y neutral. El pie no debe introducir interpretación política.

## Estrategia de almacenamiento

La fase inicial admite URL remota oficial, porque reduce copias y conserva trazabilidad directa. Para producción estable se recomienda un bucket S3-compatible privado de escritura y público mediante CDN o proxy, con claves no predecibles, MIME validado, límites de tamaño, checksum SHA-256, stripping de metadata sensible y variantes responsivas.

La aplicación debe resolver en este orden:

1. activo principal aprobado gestionado o cacheado;
2. activo principal aprobado remoto oficial;
3. otro activo aprobado del tipo solicitado;
4. fallback propio accesible.

La caché nunca sustituye `source_url`; solo completa `public_url` y `storage_key`.

## Próximos pasos de implementación

1. Añadir servicio interno autenticado para alta, revisión, aprobación, rechazo, archivado y sustitución.
2. Añadir comando de carga CSV/JSON con dry-run, validación de URLs, MIME, dimensiones y duplicados.
3. Incorporar pruebas PostgreSQL de upgrade/downgrade, restricciones e índices parciales.
4. Añadir pruebas API para aprobación, ocultamiento de campos internos, 404 y fallback.
5. Integrar contratos de medios en tarjetas y fichas de PE-10 mediante `next/image` y allowlist/proxy controlado.
6. Crear fallback institucional y fallback de autoridad como activos propios, sin siluetas que sugieran identidad real.
7. Ejecutar piloto con una institución y una autoridad antes de cargar las 25 entidades.
