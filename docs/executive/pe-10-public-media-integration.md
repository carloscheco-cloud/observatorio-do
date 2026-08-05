# PE-10 — Integración visual pública

## Objetivo

Conectar los activos visuales trazables de PE-09 con las fichas públicas de instituciones y autoridades del Poder Ejecutivo, sin inventar imágenes y sin ocultar su procedencia.

## Alcance implementado

- consumo de los endpoints públicos de media assets;
- imagen principal en fichas institucionales;
- retrato principal en fichas de autoridades;
- galería documentada cuando existen varios activos aprobados;
- atribución visible con fuente, leyenda y nota de licencia;
- texto alternativo obligatorio suministrado por el registro aprobado;
- fallback visual determinista cuando no existe una imagen aprobada;
- compatibilidad con activos HTTPS de fuentes oficiales o almacenamiento gestionado;
- diseño adaptable a escritorio y dispositivos móviles.

## Orden editorial

### Instituciones

1. banner oficial;
2. edificio institucional;
3. logo institucional;
4. fallback aprobado.

### Autoridades

1. retrato oficial;
2. fallback aprobado.

Dentro de cada tipo se prioriza el activo marcado como principal. Si no hay uno principal, se utiliza el primer activo aprobado entregado por la API.

## Principios de publicación

- El frontend solo consume activos expuestos por la API pública de PE-09.
- La ausencia de una imagen aprobada no se interpreta como ausencia de una imagen oficial.
- El fallback no simula fotografías, retratos ni logos.
- Cada activo conserva atribución visible y enlace a su fuente cuando está disponible.
- No se exponen campos editoriales internos, checksum ni decisiones privadas de aprobación.

## Seguridad

La política CSP permite imágenes HTTPS porque los activos pueden residir en portales oficiales o almacenamiento gestionado. La lista efectiva de imágenes publicables continúa controlada por el estado `approved` en el backend.

## Fuera de alcance

- interfaz administrativa para carga y aprobación;
- descarga o copia automática de imágenes remotas;
- reconocimiento facial;
- generación de retratos sintéticos;
- edición de logos oficiales;
- carga masiva de activos reales.

## Validación esperada

- tipos TypeScript y cliente API;
- selección editorial por tipo y activo principal;
- fallback sin imágenes inventadas;
- atribución y texto alternativo;
- build de Next.js y pruebas del frontend;
- prueba manual en Preview antes del merge.
