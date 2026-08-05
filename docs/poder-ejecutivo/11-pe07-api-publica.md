# PE-07: API pública del Poder Ejecutivo

## Propósito y alcance

PE-07 ofrece una superficie ciudadana, trazable y exclusivamente de lectura sobre los datos
persistidos por PE-01 a PE-06D. No investiga, infiere ni crea instituciones, relaciones,
autoridades, normas o evaluaciones. La ausencia de un valor significa **no disponible** y nunca
cero o inexistencia.

El prefijo es `/api/v1/executive`. El router forma parte del monolito modular existente en
`backend/app/modules/public_api`; usa la sesión SQLAlchemy común y esquemas Pydantic públicos
separados del ORM. No hay endpoints POST, PUT, PATCH ni DELETE.

## Endpoints

| Método y ruta | Uso |
| --- | --- |
| `GET /summary` | Conteos, cobertura, metodologías y última actualización. |
| `GET /institutions` | Listado filtrable y paginado. |
| `GET /institutions/{slug}` | Ficha institucional pública. |
| `GET /institutions/{slug}/authority` | Autoridad actual confirmada. |
| `GET /institutions/{slug}/relationships` | Relaciones persistidas. |
| `GET /institutions/{slug}/legal-basis` | Bases jurídicas persistidas. |
| `GET /institutions/{slug}/transparency` | Evaluación más reciente e historial. |
| `GET /authorities` | Autoridades y nombramientos públicos. |
| `GET /authorities/{person_or_appointment_id}` | Trayectoria institucional pública. |
| `GET /changes` | Eventos históricos demostrables. |

Todos los ejemplos deben anteponer `/api/v1/executive`, por ejemplo:

```http
GET /api/v1/executive/institutions?page=1&page_size=20&institution_type=ministry
```

## Parámetros, paginación y orden

`institutions` acepta `search`, `institution_type`, `parent_slug`,
`has_current_authority`, `has_transparency_assessment`, `maturity_status`, `sort_by` y
`sort_order`. Los órdenes permitidos son `official_name`, `institution_type`, `updated_at`,
`transparency_score` y `transparency_coverage`; nunca se interpola un nombre de columna recibido.

`authorities` acepta `search`, `institution_slug`, `position_type`, `active_only`, `sort_by` y
`sort_order`. `changes` acepta `date_from`, `date_to`, `change_type` e `institution_slug`.
Relaciones acepta `direction=incoming|outgoing|all`.

Las colecciones usan una envoltura estable:

```json
{"items": [], "page": 1, "page_size": 20, "total": 0, "pages": 0}
```

`page` comienza en 1. `page_size` admite de 1 a 100 y vale 20 por defecto. UUID, fechas y horas
se serializan como cadenas ISO 8601; los decimales se serializan consistentemente mediante los
esquemas Pydantic.

## Respuestas y trazabilidad

La ficha enlaza evidencia con su fuente oficial, localizador y fecha de observación. La autoridad
distingue `act_located=false` de la inexistencia de un acto. La base legal publica únicamente
normas ya estructuradas. Las relaciones proceden exclusivamente de filas persistidas; no se crean
ciclos ni dependencias inferidas.

La evaluación más reciente se determina por fecha e identificador, nunca por una fila histórica
arbitraria. Una institución fuera de PE-06D puede presentar la evaluación parcial de PE-05 y sus
dimensiones pendientes. Los componentes muestran explicación y razón públicas; no exponen la
razón interna de cálculo.

## Semántica de puntuación y cobertura

El **score mide disponibilidad y calidad documental** según la metodología indicada. No mide
corrupción, honestidad, legalidad ni desempeño político. `complete` significa cobertura
metodológica completa; no significa ausencia de deficiencias. La cobertura expresa qué proporción
del marco metodológico pudo evaluarse. Los datos dependen de las fuentes oficiales localizadas.

El ranking está desactivado: `ranking_enabled=false`, `rank=null` y
`comparison_position=null`. PE-07 no recalcula evaluaciones ni habilita comparaciones ordinales.

## Errores

- `404`: institución o autoridad no localizada, con mensaje neutral en español.
- `422`: parámetros, enum, orden o límites de paginación inválidos.
- `400`: rango de fechas invertido.
- `500`: FastAPI no incluye detalles de implementación en respuestas de producción.

Los errores de validación tienen código, mensaje público, campos inválidos, identificador de
solicitud y fecha. Los stack traces no forman parte del contrato.

## Seguridad, CORS y privacidad

CORS conserva la configuración central `CORS_ORIGINS`; se especifica como lista separada por
comas. En producción no admite `*`, localhost ni orígenes implícitos. `TRUSTED_HOSTS` controla los
hosts válidos. Las variables se documentan en `.env.example` y no contienen secretos.

La lista pública de campos excluye payloads crudos, hashes, metadatos, notas privadas, rutas,
secretos, datos de identidad sensibles y detalles internos. Para personas solo se publica nombre,
cargo, institución, períodos y evidencia institucional persistida por PE-04.

Las rutas reciben rate limit, ETag, caché breve, `X-Request-ID` y cabeceras defensivas. Las
consultas de listados cargan autoridades, evaluaciones, padres y conteos en lotes; los detalles
resuelven evidencia y fuentes mediante joins para evitar N+1. No fue necesaria una migración ni un
índice adicional.

## Limitaciones y preparación para PE-08

`changes` solo devuelve nombramientos, terminaciones, relaciones, evaluaciones y publicaciones de
metodología que tienen fecha persistida. No inventa eventos de institución o estado cuando el
modelo no conserva un evento demostrable. Algunas bases jurídicas no están asociadas directamente
a la institución y solo aparecen cuando una posición o requisito documental conserva ese vínculo.

PE-08 podrá consumir estos contratos estables para visualizaciones, estados vacíos y navegación
ciudadana. Debe conservar los avisos de score/cobertura, ranking desactivado, paginación y estados
“no disponible”, sin acceder a esquemas internos.

## Integración con PostgreSQL 16

Las pruebas integrales requieren PostgreSQL 16 real. El fixture común crea una base template,
ejecuta Alembic hasta la revisión esperada `0018` y clona una base independiente para cada prueba.
Al terminar fuerza el cierre de conexiones, elimina cada clon y finalmente elimina el template.
PE-07 usa este mismo fixture; no mantiene infraestructura paralela ni una sustitución SQLite.

La variable preferida es `POSTGRES_TEST_ADMIN_URL`. Debe apuntar a una base administrativa
existente y usar `postgresql+psycopg`. El usuario necesita `CREATEDB` o privilegio de superusuario,
además de poder consultar `pg_stat_activity`, terminar conexiones de las bases efímeras y ejecutar
`DROP DATABASE`. Ejemplo sin credenciales reales:

```dotenv
POSTGRES_TEST_ADMIN_URL=postgresql+psycopg://usuario:password@localhost:5433/postgres
```

Si la contraseña contiene `@`, `:`, `/`, `%` u otros caracteres reservados, debe codificarse como
parte de una URL. El fixture acepta `DATABASE_URL` como compatibilidad cuando no existe la variable
preferida, y en ese caso usa la base administrativa `postgres` con el mismo host y usuario.

Comandos desde la raíz del repositorio:

```text
python -m pytest backend/tests/integration/test_pe07_public_executive_postgresql.py -v
python -m pytest -m integration
```

En desarrollo local, las integrales se omiten con una razón explícita únicamente cuando no se
configuró ninguna de las dos variables. Una variable configurada pero inválida falla temprano con
un mensaje seguro para driver incorrecto, host no accesible, autenticación fallida, base
administrativa inexistente o falta de `CREATEDB`; nunca imprime la contraseña ni la URL completa.

El job de CI proporciona un service container PostgreSQL 16 con credenciales efímeras y define
`POSTGRES_TEST_ADMIN_URL`. En CI la ausencia de configuración es un error, no un skip, y la suite
integral se ejecuta separadamente para que cualquier omisión sea visible.

Ante un error de autenticación, comprobar sin copiar la URL a logs: que el puerto corresponda a la
instancia esperada, que el usuario exista en esa instancia, que la contraseña sea la vigente y que
los caracteres reservados estén codificados. Un servidor que responde en el puerto configurado
puede pertenecer a otro clúster y rechazar credenciales válidas para el contenedor del proyecto.
