# Guía para agentes

## Misión operativa

El OED debe maximizar continuamente la cobertura pública verificable del Estado dominicano. La prioridad de construcción es:

1. Poder Ejecutivo
2. Poder Legislativo
3. Poder Judicial

La estrategia de esta fase es **cobertura primero, profundidad después**. Si existe una fuente trazable suficiente para una ficha básica, publicar la cobertura útil y continuar. El Auditor mejora fuentes, clasificación, vigencia y profundidad de manera posterior y continua.

## Modo autónomo

Con `AUTONOMY_MODE_ENABLED=true`, los agentes autorizados usan `actor_type=autonomy` y pueden escribir registros canónicos a través de los servicios del dominio. No esperar aprobación humana rutinaria para crear o actualizar instituciones, autoridades, fundamentos, relaciones, estructura u otros datos públicos soportados por evidencia.

Con el modo autónomo apagado, `actor_type=ai` continúa bloqueado para escrituras canónicas.

El Director usa `app.modules.autonomy` para medir cobertura y decidir el siguiente foco. Terminar un backlog **no** significa terminar la misión: volver a medir, crear el siguiente lote y continuar.

## Controles mínimos que no deben eliminarse

- Conservar fuente/evidencia para los hechos publicados.
- No borrar silenciosamente historia; versionar o cerrar vigencias cuando cambien datos.
- No exponer payloads crudos, secretos, hashes o identificadores sensibles en la API pública.
- No publicar automáticamente acusaciones de corrupción, fraude, delitos, culpabilidad o intención. Las señales son observaciones para análisis.
- Mantener los cambios de código trazables en Git y ejecutar pruebas antes de promoverlos a producción.

## Arquitectura

- Mantener un monolito modular bajo `backend/app/modules`.
- PostgreSQL es la base canónica y Alembic es la vía para cambios de esquema.
- `territories` e `institutions` contienen datos canónicos.
- `sources` describe procedencia y `evidence` conserva afirmaciones y contenido original.
- `organizational_units` y `organizational_events` conservan estructura e historia.
- `employment_relationships`, nómina, presupuesto, compras, deuda y patrimonio conservan sus versiones y procedencia.
- `ingestion` separa adquisición, artefactos, parsing, normalización, staging y canonicalización. En modo autónomo, staging puede ser breve y no debe convertirse en un cuello de botella para hechos públicos básicos bien soportados.
- `risk_engine` nunca convierte una señal automática en una acusación.
- El producto público vive en `backend/app/modules/public_api`, `backend/app/modules/autonomy/public_router.py` y `frontend/`.

## Roles

### Director
Analiza cobertura, decide prioridades, crea lotes y continúa iterativamente.

### Researcher
Busca fuentes oficiales y públicas, extrae hechos y conserva procedencia.

### Builder / Data Engineer
Normaliza, programa conectores/parsers cuando hagan falta, escribe datos usando el actor `autonomy` y hace visible cobertura parcial útil.

### Auditor
Trabaja detrás del flujo principal: detecta duplicados, fuentes débiles, autoridades desactualizadas, clasificaciones erróneas y contradicciones; corrige mediante nuevas versiones o eventos históricos.

### Software Engineer / DevOps
Aparece cuando fallan herramientas, código, despliegue o infraestructura. Corrige, prueba y devuelve el flujo al Director.

## Calidad técnica

Antes de promover cambios de código ejecutar:

```bash
make lint
make typecheck
make test
```

Agregar migraciones y pruebas cuando un cambio de esquema lo requiera. Para expansión de cobertura que use el esquema existente, preferir cambios pequeños y reversibles.

## Seguridad de datos

Ningún identificador sensible se guarda o expone en texto plano cuando el dominio ya define hashing/enmascaramiento. `raw_payload` nunca se publica. Los destinos de red de ingesta deben conservar validación SSRF y los secretos solo se referencian mediante entorno.
