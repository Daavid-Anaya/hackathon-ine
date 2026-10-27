# Cruce de P01–P05 con tipo de sección — 2024

**Cruce descriptivo interno; no autoriza publicación ni envío externo.** Se
conservan las asignaciones de los cinco perfiles T08 y se describe su desglose
urbano, mixto y rural. No se reajusta el clustering ni se decide reemplazarlo.

## Ejecución reproducible

```powershell
docker compose run --rm --pull never analysis python -B scripts/cross_profile_section_types.py
```

Requiere el ZIP original de 2024, el paquete T06 en
`data/processed/ccpc_all/2024/` y el paquete interno T08 en
`outputs/t08_profiles_final/`. Las asignaciones T08 deben corresponder a esa misma
tabla T06 y contener exactamente sus claves elegibles base, sin duplicados ni
cambios en los conteos. Se verifican los ocho artefactos registrados en T08.

El comando crea **una carpeta nueva**, `outputs/profile_section_types_2024/`,
excluida de Git. Si existe, se rechaza la ejecución sin sobrescribirla.
`--run-name profile_section_types_2024_repeat` permite repetir con otro nombre;
`--chunk-size 200000` controla la lectura por bloques, no una muestra;
`--root RUTA` sirve para datos sintéticos aislados y `--help` muestra las opciones.

| Archivo interno | Contenido |
| --- | --- |
| `cross.csv` | Una fila por combinación observada de perfil y tipo: conteos, participación, NS, proporción de LN dentro del perfil y comparación con soporte común. |
| `report.json` | Linaje T06/T08, reconciliaciones, amplitudes descriptivas y soporte común por perfil, con hashes y límites. |
| `README.md` | Límites de interpretación y ausencia de autorización para compartir. |

Las cifras detalladas permanecen en esos archivos internos. No se exportan las
microceldas originales, claves geográficas detalladas ni nuevas asignaciones.

## Qué se hace y por qué

1. **Reconstruir el tipo de sección:** reutilizar la agregación del
   [diagnóstico U/M/R](section-type-diagnostic.md) para sumar LN/SV/NV/NS por
   entidad × tipo × sexo × banda de edad. Así se recupera la dimensión no
   conservada en la tabla T06 inicial, sin inventarla a partir de sus totales.
2. **Heredar el perfil fijo:** unir por entidad × sexo × edad con
   `assignments.csv` de T08. Todos los subgrupos U/M/R de esa clave conservan
   su perfil padre. No se reclasifican según la tasa del subgrupo.
3. **Reconciliar:** al colapsar los tipos, deben coincidir todos los grupos T06;
   los subgrupos asignados deben sumar exactamente LN/SV/NV/NS de cada perfil
   T08. Los grupos sin asignación quedan contabilizados aparte, no en un sexto perfil.
4. **Separar tamaño y participación:** `within_profile_ln_share_pct` divide la LN
   de cada tipo por la LN del perfil. No es participación ni proporción del perfil
   dentro de U, M o R. La participación suma SV y NV antes de calcular su cociente;
   NS no se convierte en abstención.
5. **Comparar composición dentro de cada perfil:** reutilizar los criterios de
   soporte U/M/R común y los pesos agrupados por entidad–sexo–edad del diagnóstico
   anterior, pero calcularlos separadamente en P01, P02, P03, P04 y P05. No se
   imputan ausencias ni tasas indefinidas.

Cada perfil tiene su propia referencia de estandarización. Por eso las tasas
estandarizadas permiten comparar **U/M/R dentro de ese perfil**, no afirmar que
todos los perfiles fueron llevados a una única estructura demográfica común.
Se muestran también tasas brutas del soporte común y cuánto denominador conocido
se conserva; no atribuir toda variación a los pesos si además cambió el soporte.

## Qué permite concluir el cruce observado

La ejecución de 2024 produjo las **15 combinaciones P01–P05 × U/M/R**, después de
leer 9.773.730 filas. Las tasas brutas mantienen el orden creciente P01–P05 en
cada tipo de sección, aunque hay diferencias U/M/R dentro de los perfiles.

- P01 y P03 presentan las mayores amplitudes brutas entre tipos de esta solución.
  La estandarización reduce la amplitud de P03, sin eliminarla.
- P04 también muestra una reducción al usar composición común. Esto no demuestra
  qué parte tiene una causa territorial ni controla factores no observados.
- P02 es el único perfil que pierde una pequeña parte del denominador conocido
  al restringirse a soporte común; hay que distinguir selección de soporte y
  reponderación antes de interpretar su cambio.
- El orden de las medias brutas no valida externamente cinco grupos naturales,
  ni acredita homogeneidad interna de todos sus estratos. Tampoco demuestra que
  una tasa del subgrupo fuera del rango del padre sea un error: cambió la unidad.

La evidencia no impone automáticamente sustituir el modelo, pero sí permite
describir el contexto U/M/R que oculta su unidad agregada. La decisión de comparar
otro clustering queda pendiente; no se establece un umbral arbitrario de amplitud
para tomarla. No se estudiaron municipios ni efectos causales.

## Verificación y preservación

- RED observado antes de implementar. Tres pruebas por CLI aprobaron después:
  herencia de perfiles y reconciliación, rechazo de asignaciones incompatibles,
  duplicadas o incompletas incluso con hashes actualizados, y repetibilidad sin
  sobrescritura.
- Suite completa: **63 pruebas, 62 aprobadas y una omitida**, la comprobación
  opcional de persistencia desde el anfitrión; no se declara ejecutada.
- Ejecución real con salida 0 y `models_refitted: false`. Trece archivos protegidos
  de T08, T09 y el diagnóstico U/M/R anterior conservaron sus hashes antes y después.
- No se modificaron los helpers compartidos ni los comandos previos. La salida
  nueva no concede aprobación de divulgación ni cierra la brecha de T10.

Referencias: [perfiles T08 conservados](profile-selection.md),
[guía de caracterización T09](profile-interpretation.md) y
[auditoría de variables y denominadores](data-audit.md).
