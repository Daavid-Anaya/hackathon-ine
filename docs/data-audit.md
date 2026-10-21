# T04: unidad de análisis y auditoría de variables CCPC

**Decisión:** trabajar con conteos agregados, no con personas ni historiales.
La unidad analítica inicial será **entidad × sexo × tramo de edad en 2024**.
La auditoría del 21 de octubre de 2026 cubrió los **192 CSV completos** de las
seis elecciones: **54.872.712 filas**. Esta definición prepara T06; todavía no
se ha generado una tabla limpia ni ejecutado una segmentación.

## Qué representa una fila

Cada fila fuente es una celda **elección × entidad × sección × sexo × edad**,
con cuatro conteos: lista nominal (`LN`), con marca de voto (`SV`), sin marca
de voto (`NV`) y participación no especificada (`NS`). No es una persona:
hay celdas con `LN` mayor que uno. Municipio, tipo de sección y distritos son
atributos geográficos de esa celda, no nuevas observaciones independientes.

La clave candidata es `(AELEC, EDOCVE, SECCION, SEXO, EDAD)`. No se encontraron
hashes duplicados de esa clave, conservando los hashes entre bloques de cada
archivo y verificando que los archivos de una elección no compartieran entidad.
Es una comprobación mediante hash, no una demostración de unicidad por comparación
literal. T06 debe validar la clave al construir la tabla y rechazar duplicados,
no sumarlos silenciosamente.

## Matriz de variables

Los 192 archivos comparten estos 16 campos, en este orden. Ninguna columna
adicional de escolaridad, referencia indígena o afrodescendencia está disponible.

| Campo | Significado y dominio observado | Papel y tratamiento definido para T06 |
| --- | --- | --- |
| `AELEC` | Año electoral: 2009, 2012, 2015, 2018, 2021, 2024 | Selección y contexto temporal; no usar como distancia numérica de segmentación. |
| `FELECCION` | Fecha de elección en texto; formato no uniforme | Conservar el literal. No interpretar automáticamente el valor ambiguo de 2024. |
| `EDOCVE` | Entidad, valores 1–32 | Identificador; parte de toda clave territorial. No usar su magnitud para agrupar perfiles. |
| `EDONOM` | Nombre de entidad | Etiqueta; no clave de unión. Sin blancos observados. |
| `MPIOCVE` | Clave municipal local a la entidad, dentro de 1–570 | Usar `(EDOCVE, MPIOCVE)`; el rango no valida un catálogo externo. |
| `MPIONOM` | Nombre municipal | Etiqueta; consistente dentro de la clave municipal de cada elección. |
| `SECCION` | Sección de residencia indicada en la credencial | Usar `(AELEC, EDOCVE, SECCION)`; no asumir continuidad entre años. |
| `TIPOSEC` | `U`: urbana; `M`: mixta; `R`: rural | Contexto categórico. No incorporar a la unidad inicial ni tratar como escala ordinal. |
| `DEF` | Distrito federal; rangos 1–41 hasta 2021, 1–40 en 2024 | Identificador contextual; tiene faltantes y cambia la referencia cartográfica. |
| `DEL` | Distrito local; rango observado 1–45 | Identificador contextual; tiene faltantes. No imputar a partir del nombre municipal. |
| `SEXO` | `0`: hombres; `1`: mujeres; `2`: no binario, solo en 2024 | Dimensión categórica; preservar `2`, sin recodificarlo como hombre, mujer o faltante. |
| `EDAD` | Años cumplidos a la elección; mínimo 18; máximos 117–140 según año | Agrupar en 18–24, 25–34, 35–44, 45–59 y 60 o más; señalar edades extremas. |
| `LN` | Lista nominal en los cuadernillos catalogados; entero positivo | Tamaño/peso de población registrada, no número de filas; denominador de no especificación. |
| `SV` | Registros con marca de voto; entero no negativo | Numerador de participación conocida. Un cero es un conteo válido. |
| `NV` | Registros sin marca de voto; entero no negativo | Complemento conocido de participación. No incluye `NS`. |
| `NS` | Registros con participación no especificada; entero no negativo | Indicador de cobertura; no convertir en abstención ni en cero. |
| Escolaridad — ausente | No existe en los seis esquemas | **Excluir del análisis.** No imputar ni fabricar cruces con fuentes territoriales. |

Guardar identificadores como claves, normalizando sus representaciones de forma
explícita; los códigos numéricos observados no prueban equivalencia con claves de
INEGI u otros catálogos. Para comparar atributos se normalizaron distritos a número
y blancos a faltante, sin modificar los originales. No hubo conflictos de
`(entidad, sección) → municipio, tipo, DEF, DEL` dentro de cada elección, ni de
`entidad → nombre` o `(entidad, municipio) → nombre`.

## Conteos y denominadores comprobados

En todas las filas se cumple **`LN = SV + NV + NS`**. No se observaron conteos
negativos, fraccionarios, blancos ni tokens no numéricos en estos cuatro campos.
Los totales son de los archivos disponibles; no acreditan por sí solos cobertura
completa del electorado.

| Elección | Filas fuente | ΣLN | ΣSV | ΣNV | ΣNS | Filas con `SV + NV = 0` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2009 | 8.706.843 | 77.481.831 | 33.316.974 | 42.298.963 | 1.865.894 | 142.141 |
| 2012 | 8.604.456 | 76.490.962 | 47.383.154 | 28.939.159 | 168.649 | 9.839 |
| 2015 | 9.106.059 | 83.563.462 | 36.926.612 | 41.517.874 | 5.118.976 | 309.186 |
| 2018 | 9.251.122 | 89.123.997 | 51.784.399 | 31.249.856 | 6.089.742 | 363.901 |
| 2021 | 9.430.502 | 93.532.133 | 46.389.189 | 43.099.624 | 4.043.320 | 246.681 |
| 2024 | 9.773.730 | 98.330.348 | 54.899.228 | 37.105.466 | 6.325.654 | 323.984 |

El [manual oficial](../data/raw/Manual-Conteos-Censales-2009-2024.pdf), pp. 17–18,
define las tasas siguientes. **Primero sumar conteos en la unidad elegida**;
no promediar tasas de filas o secciones sin ponderar.

| Indicador | Fórmula porcentual | Interpretación |
| --- | --- | --- |
| Participación conocida | `100 × ΣSV / (ΣSV + ΣNV)` | Entre registros con estatus conocido; no equivale a `SV/LN`. |
| Abstención conocida | `100 × ΣNV / (ΣSV + ΣNV)` | Complemento de la participación conocida. |
| No especificación | `100 × ΣNS / ΣLN` | Fracción sin estatus conocido; acompañará toda tasa de participación. |
| Tamaño de la unidad | `ΣLN` | Peso poblacional; no contar filas como personas. |

Si un denominador agregado es cero, la tasa es **indefinida**, no cero. Las filas
fuente con `SV + NV = 0` conservan `LN` y `NS` al agregar: eliminarlas antes
subestimaría población y no especificación. El criterio de cobertura suficiente
para segmentar se evaluará en T06/T07, sin presentar estas tasas como estimaciones
de la participación de los casos desconocidos.

## Faltantes, ceros, supresión y anomalías

| Elección | Municipios distintos¹ | Secciones distintas¹ | Faltantes distritales: filas | Secciones afectadas |
| --- | ---: | ---: | --- | ---: |
| 2009 | 2.458 | 64.934 | `DEF`: 28.477; `DEL`: 28.477 | 318 |
| 2012 | 2.455 | 65.599 | `DEF`: 15.677; `DEL`: 15.677 | 221 |
| 2015 | 2.458 | 68.362 | Ninguno | 0 |
| 2018 | 2.463 | 68.408 | Ninguno | 0 |
| 2021 | 2.468 | 68.812 | Ninguno | 0 |
| 2024 | 2.477 | 70.751 | `DEL`: 20.912 | 136 |

¹ Claves compuestas con entidad; conteos dentro de cada elección, no territorios
homologados entre años. Los blancos distritales son literalmente un espacio en
2009/2012 y una cadena vacía en 2024; no hubo otros campos blancos observados.

- **Cero:** valor observado válido en `SV`, `NV` y `NS`. No usarlo para rellenar
  distritos ni tasas indefinidas. `LN` tiene mínimo uno en todas las elecciones.
- **No especificado:** `NS` recoge problemas de disponibilidad de cuadernillos,
  páginas o marcas; los diccionarios anteriores también mencionan requerimientos
  jurisdiccionales. Es desconocimiento del estatus, no abstención ni un marcador
  documentado de supresión estadística.
- **Supresión:** no se observaron tokens especiales no numéricos en los conteos.
  Los diccionarios no establecen una convención de supresión; esto **no demuestra**
  ausencia de supresión o exclusiones anteriores a la publicación. No reconstruir
  valores supuestamente ocultos.
- **Edades extremas:** máximos de 130, 132, 117, 137, 139 y 140 años, respectivamente.
  Hay 1.663, 402, 359, 304, 376 y 227 filas con edad mayor de 110. No están
  documentadas como centinelas: señalar y evaluar sensibilidad en T06/T07; no
  eliminarlas ni corregirlas automáticamente. El tramo 60+ no certifica su validez.
- **Privacidad:** existen microceldas `LN=1`. Una fuente agregada no es una garantía
  de anonimato. No publicar esas filas ni inferir el voto de individuos; antes de
  difundir agregados pequeños, revisar riesgo de identificación y reglas de salida.

## Unidad analítica justificada y comparabilidad

Para la primera tabla de perfiles se fija **2024**, una fila por
`(EDOCVE, SEXO, tramo de edad)`, sumando `LN`, `SV`, `NV` y `NS` sobre todas las
secciones de cada combinación realmente observada. Los cinco tramos son los de
etapas de vida del manual, p. 12. Son categorías de análisis, **no** los 4–6 perfiles
que se evaluarán posteriormente en T07. No crear combinaciones sin observaciones
ni rellenar sus conteos con ceros.

Esta unidad conserva cruces que existen en la fuente, permite comparar composición
y participación por grupos y evita segmentar microceldas seccionales o mezclar
elecciones de distinto tipo. Se pierde detalle intraterritorial: los perfiles
describirán grupos agregados, no tipos de personas ni comportamientos individuales.
Los códigos de entidad, sexo y edad identifican/contextualizan la unidad; la
selección final de características, escalado y ponderaciones corresponde a T07.

Se preserva la categoría no binaria: hay **105 filas fuente** de sexo `2` en 2024
(no necesariamente 105 personas). Su escasez requiere revisar tamaños y cobertura
antes de segmentar o divulgar tasas; no fusionarla con categorías binarias ni
inventar ceros de esa categoría en años anteriores. La política de publicación de
grupos pequeños queda pendiente antes de difundir resultados, no de esta auditoría.

| Aspecto temporal | Restricción |
| --- | --- |
| Tipo de elección | El manual, p. 30, separa 2009/2015/2021 de 2012/2018/2024. Usar esas series para contexto, sin atribuir diferencias automáticamente al tiempo. |
| Geografía | Distritos referidos a DERFE 2021 en archivos 2009–2021 y a DERFE 2023 en 2024. Cambian cantidades de municipios y secciones; no hay correspondencia longitudinal validada. |
| Sexo | `0/1` hasta 2021; `0/1/2` en 2024. Ausencia histórica de `2` no significa población cero. |
| Edad | Son cortes transversales de edades a cada elección, no cohortes seguidas ni historiales de votación. |
| Fechas | Literales: `5/7/2009`, `1/7/2012`, `7/6/2015`, `1/7/2018`, `6/6/2021`, `06/02/2024`. El último es ambiguo; seleccionar por `AELEC`, conservar el literal y no aplicar una regla global de parseo. |
| Cobertura | Se excluyen casillas especiales y voto desde el extranjero según los diccionarios. Cambia `NS`; comparar siempre con su proporción y sin asumir cobertura idéntica. |

## Alcance de la comprobación y siguiente paso

Se contrastaron los seis TXT y las 38 páginas del manual con una lectura offline
de todos los CSV, sin extraer ZIP ni modificar originales. El procesamiento usó
Python **3.14.0**, Pandas **2.3.3**, `ZipFile.open` y `read_csv` en bloques de
150.000 filas, UTF-8 con manejo de BOM y errores estrictos, conservando blancos
(`keep_default_na=False`). Todos los archivos fueron compatibles con esa
codificación; no se afirma que todos tengan BOM. Se comprobaron esquemas, dominios,
blancos, enteros, sumas, identidad contable, denominadores, claves candidatas y
dependencias geográficas dentro de cada año. Los seis SHA-256 coincidieron con el
[manifiesto](../data/sources.json) antes y después del procesamiento.

La inspección se ejecutó con código en memoria; **todavía no existe un comando de
auditoría de filas versionado**. La tabla anterior es evidencia del barrido realizado,
no una prueba automatizada de regresión. T06 deberá convertir estas comprobaciones
en validaciones reproducibles de la tabla limpia. El comando `download_ccpc.py
--inspect` solo verifica integridad, diccionarios y primeros encabezados: no reproduce
esta auditoría de filas. No se validaron catálogos territoriales externos, cobertura
poblacional exhaustiva, equivalencia longitudinal ni una garantía de anonimización.

**T04 queda documentada:** matriz, unidad, denominadores, faltantes, supresión no
documentada y límites temporales. **T06 sigue pendiente:** implementar limpieza y
validaciones reproducibles, resolver el tratamiento de anomalías sin perder la
trazabilidad y exportar solo la tabla analítica y su reporte de transformaciones.
Consultar el [inventario de T03](data-sources.md) para las URL y diccionarios exactos.
