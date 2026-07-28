# Despliegue operativo

Construcción y arranque de la API:

```bash
docker build -f backend/Dockerfile -t observatorio-api:latest .
docker run --rm -p 8000:8000 --env-file /ruta/segura/backend.env observatorio-api:latest
```

La imagen arranca exclusivamente Uvicorn; no ejecuta migraciones, semillas ni scheduler.
Antes de sustituir réplicas, ejecute una sola tarea de migración. El comando usa un
advisory lock PostgreSQL:

```bash
docker run --rm --env-file /ruta/segura/backend.env observatorio-api:latest \
  python -m app.db.migrate upgrade head
```

El rollback disponible revierte una revisión y debe validarse contra un respaldo:

```bash
docker run --rm --env-file /ruta/segura/backend.env observatorio-api:latest \
  python -m app.db.migrate downgrade -1
```

## Variables

Backend de producción: `APP_ENV=production`, `DATABASE_URL`, `CORS_ORIGINS`,
`TRUSTED_HOSTS`, `ARTIFACT_STORAGE_BACKEND=s3`, `S3_ENDPOINT_URL`, `S3_REGION`,
`S3_BUCKET`, `S3_ACCESS_KEY_ID` y `S3_SECRET_ACCESS_KEY`. `DATABASE_URL` admite
`postgres://`, `postgresql://` y `postgresql+psycopg://`; se normaliza al driver psycopg.
La URI directa o del pooler de Supabase conserva parámetros TLS como `sslmode=require`.
Los límites del pooler se respetan ajustando `DATABASE_POOL_SIZE`,
`DATABASE_MAX_OVERFLOW` y `DATABASE_POOL_TIMEOUT_SECONDS`.

Mantenga `INGESTION_SCHEDULER_ENABLED=false`; workers y scheduler son procesos separados.
No ejecute `app.db.seed` en producción.

Frontend en Vercel: `NEXT_PUBLIC_API_URL` (URL completa terminada en `/api/v1/public`),
`NEXT_PUBLIC_SITE_URL` y `NEXT_PUBLIC_ROBOTS_INDEX`. El build falla claramente si falta
la primera. Vercel no requiere secretos del backend.

`/health` no abre una conexión a datos. `/health/db` ejecuta `SELECT 1` en PostgreSQL.
