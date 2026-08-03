# PE-02: inventario oficial inicial del Poder Ejecutivo

Consulta realizada el 3 de agosto de 2026. El manifiesto versionado contiene 25 registros:
Presidencia, Vicepresidencia y los 23 ministerios que el Clasificador de Organismos del
Estado Dominicano (COEDOM) identifica inequívocamente como ministerios vigentes.

## Fuentes y criterio de inclusión

- La Constitución publicada por la Presidencia sustenta Presidencia y Vicepresidencia
  (artículos 122, 125 y 128).
- El [listado A-Z de COEDOM](https://map.gob.do/COEDOM/Home/SearchAZ?page=1&searchString=M),
  publicado por el Ministerio de Administración Pública, sustenta nombre, sigla, tipología
  y sector de cada ministerio.
Cada afirmación genera evidencia independiente, con URL, localizador, extracto, hash de
contenido, tipo de fuente y fecha de consulta. Cada evidencia ministerial conserva como
localizador la URL estable del detalle individual del organismo en COEDOM; la fuente común
continúa siendo el directorio oficial y no se multiplica artificialmente por ministerio.
Los sitios web institucionales son atributos informativos contrastados, no fuentes de la
carga. Se omiten fechas de creación porque no se
investigó una base legal inequívoca por cada entidad. Las reseñas funcionales se limitan a
la condición constitucional o al sector publicado por COEDOM.

## Registros y exclusiones

Se incluyen Presidencia de la República, Vicepresidencia de la República, Ministerio
Administrativo de la Presidencia, Ministerio de la Presidencia, y los ministerios de
Administración Pública, Agricultura, Cultura, Defensa, Deportes y Recreación, Educación,
Educación Superior Ciencia y Tecnología, Energía y Minas, Hacienda y Economía, Industria
Comercio y Mipymes, Interior y Policía, Justicia, Juventud, Mujer, Vivienda Hábitat y
Edificaciones, Medio Ambiente y Recursos Naturales, Obras Públicas y Comunicaciones,
Relaciones Exteriores, Salud Pública y Asistencia Social, Trabajo y Turismo.

Se excluyen Ministerio Público (órgano constitucional autónomo, no ministerio ejecutivo),
Ministerio de Economía, Planificación y Desarrollo y Ministerio de Hacienda como registros
separados (COEDOM publica Ministerio de Hacienda y Economía), y todos los gabinetes, consejos,
comisiones y organismos adscritos. Tampoco se cargan relaciones: aunque el organigrama
oficial muestra la estructura general, el esquema exige una fecha inicial de vigencia y no
se encontró una fecha común inequívoca. Esto evita convertir la fecha de consulta en una
fecha jurídica inventada.

## Ejecución, dry-run y rollback

Desde la raíz, con `DATABASE_URL` apuntando a PostgreSQL:

```console
python -m app.modules.executive_inventory --dry-run
python -m app.modules.executive_inventory
```

El comando emite `created`, `updated`, `unchanged`, `skipped` y `errors`. El modo dry-run
ejecuta todas las validaciones y escrituras y revierte la transacción. La carga real usa
una sola transacción; cualquier error revierte territorio, fuentes, evidencias, enlaces e
instituciones. Nunca cambia campos canónicos existentes: coincidencias exactas con su
evidencia quedan `unchanged`, divergencias quedan `skipped`, y una coincidencia canónica a
la que solo le falta la evidencia exacta del manifiesto recibe un enlace adicional y se
reporta `updated`. La evidencia previa nunca se sustituye ni elimina.

## Limitaciones pendientes

Quedan pendientes la investigación legal individual de fechas de creación/vigencia, las
relaciones jerárquicas con períodos sustentados, y una evaluación separada de gabinetes o
consejos principales. El manifiesto no incluye autoridades y no cubre presupuesto,
nómina, compras ni interfaz pública.
