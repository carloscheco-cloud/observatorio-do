# PE-04: cargos y autoridades del Poder Ejecutivo

PE-04 separa tres conceptos: una `Person` es una identidad pública; una `Position` es un cargo
abstracto adscrito a una institución PE-02; y un `Appointment` es el período histórico durante
el cual una persona ejerce ese cargo. Ser ministro nunca se almacena como atributo permanente
de la persona.

## Alcance y fuentes

La carga inicial contiene Presidencia, Vicepresidencia y los titulares de los 23 ministerios de
PE-02. Usa exclusivamente Constitución, decretos, páginas de Presidencia y portales oficiales.
El manifiesto comparte las fuentes cuando un decreto contiene varias designaciones y conserva
evidencia individual para persona, cargo y nombramiento. La consulta se registró el 3 de agosto
de 2026. No se usaron prensa, Wikipedia, redes sociales ni biografías privadas.

Presidencia y Vicepresidencia usan `constitutional_election`; 20 ministerios usan
`presidential_decree` y tres usan conservadoramente `legal_designation` porque la fuente
oficial acredita juramentación, pero no se localizó el acto jurídico individual. La capacidad
inicial es `substantive`. El modelo también admite
`acting`, `temporary` y `delegated`, sin afirmar que existan en este inventario. Los estados son
`announced`, `pending_start`, `active`, `ended`, `revoked` y `disputed`; `pending` permanece
por compatibilidad con datos anteriores.

## Tiempo e historia

La ocupación actual se deriva del estado y del intervalo `start_date`/`end_date`. Una fecha
final nunca se infiere solo porque aparezca una designación posterior: primero se registra la
fuente que acredita cese, derogación, renuncia, destitución, sustitución o término
constitucional. Los períodos terminados no se eliminan. Una fecha inicial desconocida requiere
una nota explícita y no puede publicarse como cero. Los períodos con fin anterior al inicio son
inválidos. Dos titulares sustantivos solapados de un cargo unipersonal son incompatibles; un
encargado puede coexistir únicamente cuando la evidencia lo justifique.

Para el mandato presidencial se distingue elección, proclamación, juramentación e inicio
constitucional. El período cargado comienza el 16 de agosto de 2024 por inicio constitucional y
juramentación, no por la fecha de una noticia. En los decretos con efectos diferidos se utiliza la
fecha efectiva o la toma de posesión sustentada, documentada en `start_date_basis`.

## Auditoría final al 3 de agosto de 2026

Todos los registros tienen `capacity=substantive`, `status=active` y certeza `alta`, salvo que
la certeza del acto se indique como `parcial`. “Directorio” significa el directorio oficial de
Presidencia consultado el 3 de agosto de 2026. La fuente de vigencia nunca se modela como el
acto original. El locator identifica el artículo del decreto o el párrafo individual de la
juramentación.

| Persona | Cargo / institución | Mecanismo | Inicio y fundamento | Acto (fecha; locator) | Vigencia 2026 | Certeza / observación |
|---|---|---|---|---|---|---|
| Luis Rodolfo Abinader Corona | Presidente / Presidencia | `constitutional_election` | 2024-08-16; inicio constitucional | Mandato 2024-2028 | Juramentación presidencial | Alta; elección, proclamación y comienzo no se confunden |
| Raquel Peña Rodríguez | Vicepresidenta / Vicepresidencia | `constitutional_election` | 2024-08-16; inicio constitucional | Mandato 2024-2028 | Juramentación presidencial | Alta |
| Porfirio Andrés Bautista García | Ministro administrativo / MAPRE | `presidential_decree` | 2024-07-17; decreto sin efecto diferido | 390-24 (2024-07-17; art. 4) | Directorio | Alta; corregido desde 2024-08-16 |
| Sigmund Freund Mena | Ministro / Administración Pública | `presidential_decree` | 2024-07-17; decreto sin efecto diferido | 390-24 (2024-07-17; art. 1) | Directorio | Alta; corregido desde 2024-08-16 |
| Francisco Oliverio Espaillat Bencosme | Ministro / Agricultura | `presidential_decree` | 2026-01-06; fecha del decreto | 2-26 (2026-01-06; art. 1) | Directorio | Alta |
| Roberto Ángel Salcedo Sanz | Ministro / Cultura | `presidential_decree` | 2025-01-31; fecha del decreto | 48-25 (2025-01-31; art. 6) | Directorio | Alta; corregido desde 2025-02-03 |
| Carlos Antonio Fernández Onofre | Ministro / Defensa | `presidential_decree` | 2024-08-16; vigencia del decreto | 445-24 (2024-08-15; art. 1) | Directorio | Alta |
| Kelvin Antonio Cruz Cáceres | Ministro / Deportes y Recreación | `legal_designation` | 2024-08-16; juramentación | No localizado | Directorio | Parcial para el acto; vigencia alta |
| Luis Miguel De Camps García-Mella | Ministro / Educación | `presidential_decree` | 2025-02-26; efecto expreso | 48-25 (2025-01-31; arts. 1-2) | Directorio | Alta |
| Rafael Evaristo Santos Badía | Ministro / MESCyT | `presidential_decree` | 2026-02-09; fecha del decreto | 84-26 (2026-02-09; art. 1) | Actividad oficial 2026 | Alta; período anterior fuera de alcance |
| Joel Adrián Santos Echavarría | Ministro / Energía y Minas | `legal_designation` | 2024-08-16; juramentación | No localizado para este cargo | Directorio | Parcial; 481-22 era para Presidencia, no Energía |
| Magín Díaz | Ministro / Hacienda y Economía | `presidential_decree` | 2025-07-15; fecha del decreto | 386-25 (2025-07-15; art. 1) | Directorio | Alta |
| Eduardo Sanz Lovatón | Ministro / Industria, Comercio y Mipymes | `presidential_decree` | 2026-01-06; fecha del decreto | 3-26 (2026-01-06; art. 3) | Directorio | Alta |
| Faride Virginia Raful Soriano | Ministra / Interior y Policía | `presidential_decree` | 2024-08-16; efecto expreso | 420-24 (2024-07-30; arts. 1 y 3) | Directorio | Alta |
| Antoliano Peralta Romero | Ministro / Justicia | `presidential_decree` | 2026-01-05; fecha del decreto | 1-26 (2026-01-05; art. 1) | Directorio | Alta |
| Carlos José Valdez Matos | Ministro / Juventud | `presidential_decree` | 2024-07-17; fecha del decreto | 390-24 (2024-07-17; art. 11) | Directorio | Alta |
| Gloria Roely Reyes Gómez | Ministra / Mujer | `presidential_decree` | 2026-01-06; fecha del decreto | 2-26 (2026-01-06; art. 3) | Directorio | Alta |
| José Ignacio Paliza | Ministro / Presidencia | `legal_designation` | 2024-08-16; juramentación | No localizado | Directorio | Parcial para el acto; vigencia alta |
| Víctor Orlando Bisonó Haza | Ministro / Vivienda y Edificaciones | `presidential_decree` | 2026-01-15; efecto expreso | 3-26 (2026-01-06; art. 1) | Directorio | Alta; corregido desde 2026-01-06 |
| Armando Paíno Henríquez Dájer | Ministro / Medio Ambiente | `presidential_decree` | 2024-08-16; efecto expreso | 434-24 (2024-08-02; arts. 1 y 3) | Directorio | Alta |
| Rafael Eduardo Estrella Virella | Ministro / Obras Públicas | `presidential_decree` | 2025-02-26; efecto expreso | 48-25 (2025-01-31; arts. 3-4) | Directorio | Alta |
| Roberto Álvarez | Ministro / Relaciones Exteriores | `presidential_decree` | 2020-08-16; fecha del decreto | 324-20 (2020-08-16; art. 5) | Directorio | Alta |
| Víctor Elías Atallah Lajam | Ministro / Salud Pública | `presidential_decree` | 2024-01-17; fecha del decreto | 36-24 (2024-01-17; art. 1) | Directorio | Alta |
| Eddy de Jesús Olivares Ortega | Ministro / Trabajo | `presidential_decree` | 2025-01-31; fecha del decreto | 48-25 (2025-01-31; art. 5) | Directorio | Alta; corregido desde 2025-02-03 |
| David Collado Morales | Ministro / Turismo | `presidential_decree` | 2020-08-16; fecha del decreto | 324-20 (2020-08-16; art. 16) | Actividad oficial de julio de 2026 | Alta; nombramiento y vigencia separados |

No hay `start_date` nulas en esta carga. Para Kelvin Cruz, Joel Santos y José Ignacio Paliza,
el 16 de agosto de 2024 representa la juramentación oficial observada, no la fecha inferida de
un decreto. En esos tres registros `legal_act`, `decree_number`, `decree_date`, URL y locator
del acto quedan nulos; `notes` documenta que el acto individual no fue localizado.

## Identidad y privacidad

La clave conservadora normaliza espacios, mayúsculas y tildes del nombre oficial. Los títulos
profesionales, militares o académicos no forman parte del nombre canónico. La coincidencia
aproximada nunca fusiona personas; una duda debe quedar `skipped` para revisión. PE-04 no
guarda cédula, dirección, teléfono, correo personal, afiliación partidaria, fecha de nacimiento,
familia, patrimonio, sanciones ni datos de nómina.

## Operación

La carga es atómica e idempotente:

```console
python -m app.modules.executive_authorities --dry-run
python -m app.modules.executive_authorities
python -m app.modules.executive_authorities rollback --dry-run
python -m app.modules.executive_authorities rollback
```

`executive_authority_load_records` identifica únicamente registros creados por esta versión.
El rollback los elimina en orden referencial y no toca PE-02 ni PE-03. Antes de bajar la
migración `0014` debe ejecutarse el rollback real; el downgrade rechaza una base que aún tenga
propiedad PE-04.

## Actualización futura

Para detectar un cambio se contrasta periódicamente el directorio oficial con los decretos y
portales institucionales. Una autoridad nueva crea otro nombramiento; no sobrescribe el
anterior. El período previo solo se cierra cuando una fuente oficial sustenta su término. Las
vacantes, encargos, anuncios futuros y controversias se expresan con estado/capacidad y
evidencia, nunca inventando un titular o una fecha. La carga actual no pretende reconstruir
todos los períodos históricos anteriores a las autoridades vigentes.
