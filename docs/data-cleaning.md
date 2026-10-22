# T06: limpieza reproducible de CCPC 2024

El comando offline valida los originales y produce una tabla **entidad × sexo ×
tramo de edad**, siguiendo las decisiones de [T04](data-audit.md). No segmenta
perfiles ni modifica los ZIP o el manifiesto. Los resultados son de uso interno:
la política de difusión de grupos pequeños sigue pendiente.

## Ejecutar desde PowerShell

Con Docker Desktop iniciado y la imagen local de T05 disponible:

```powershell
docker compose run --rm --pull never analysis python scripts/clean_ccpc.py
```

El comando lee `data/sources.json`, verifica el ZIP de 2024 y procesa sus 32 CSV
por bloques, sin extraerlos. Termina con código **0** y un resumen JSON si todas
las comprobaciones pasan. Guarda un paquete completo en:

- `data/processed/ccpc_2024/table.csv`: tabla analítica.
- `data/processed/ccpc_2024/report.json`: procedencia, transformaciones, exclusiones,
  anomalías, comprobaciones y reconciliación de totales.

Si la carpeta ya existe, el comando falla sin reemplazarla. Para repetir el análisis
y conservar la ejecución anterior:

```powershell
docker compose run --rm --pull never analysis python scripts/clean_ccpc.py --run-name ccpc_2024_repeat
```

Compara los hashes `table_sha256` de ambos reportes. Con los mismos originales,
código y entorno, los dos archivos deben coincidir byte por byte, incluso usando
otro tamaño de bloque. Los resultados están excluidos de Git y persisten al
eliminar los contenedores. No los publiques automáticamente.

### Opciones

| Opción | Uso |
| --- | --- |
| `--help` | Describe el comando sin procesar datos. |
| `--chunk-size 150000` | Filas por bloque; entero positivo. No cambia las reglas ni los resultados. |
| `--run-name ccpc_2024` | Nombre de una carpeta nueva dentro de `data/processed/`; solo letras ASCII, números, guion y guion bajo. |
| `--root RUTA` | Raíz local alternativa con el mismo esquema `data/sources.json` y `data/raw/`; útil para pruebas aisladas, no descarga fuentes. |

Los errores de argumentos terminan con código **2**; una fuente inválida, un fallo
de validación o una salida existente terminan con **1**, diagnóstico en stderr y
sin resumen de éxito. Una validación fallida no publica tabla ni reporte parcial.
La preparación final utiliza una carpeta temporal propia dentro de
`data/processed/`, en el mismo sistema de archivos, y la elimina al terminar.
Ejecuta un solo proceso por nombre de salida; no ejecutes simultáneamente el
descargador ni edites los originales durante el análisis.

## Reglas implementadas

| Comprobación o transformación | Tratamiento |
| --- | --- |
| Procedencia | Una entrada 2024; tamaño, SHA-256 e inventario ZIP exactos; hashes de ZIP y manifiesto antes y después. No se requieren lecturas de filas de otras elecciones. |
| Cobertura de archivos | 32 CSV no vacíos, una entidad por CSV, sin entidades repetidas; conjunto de entidades 1–32. No equivale a cobertura poblacional exhaustiva. |
| Esquema | Los 16 campos de T04, en el orden documentado; UTF-8 con BOM opcional. No se omiten filas vacías ni se convierten tokens como `NA` automáticamente. |
| Clave | `(AELEC, EDOCVE, SECCION, SEXO, EDAD)` normalizada; comparación exacta de tuplas, dentro y entre bloques. La exclusividad de entidad entre CSV impide claves compartidas entre archivos. Un duplicado detiene la ejecución. |
| Identificadores | Enteros normalizados; `EDOCVE` se exporta con dos dígitos, `SEXO` como código categórico. Municipio 1–570, sección positiva, distritos DEF 1–40 y DEL 1–45; no se homologan catálogos externos. |
| Geografía | Consistencia de nombres de entidad y municipio y de `(entidad, sección) → municipio, tipo, DEF, DEL`. Tipos admitidos: U, M y R. |
| Conteos | `LN` positivo; `SV`, `NV`, `NS` enteros no negativos; `LN = SV + NV + NS`. Se aceptan representaciones enteras con espacios externos, no fracciones ni negativos. |
| Faltantes y supresión | Blancos distritales → faltante, nunca cero; conteos blancos → error. Tokens desconocidos → error por posible supresión no documentada, nunca imputación o reconstrucción. `NS` no se interpreta como supresión. |
| Edad y sexo | Edad mínima 18; tramos 18–24, 25–34, 35–44, 45–59, 60+. Se conserva sexo 2. Las edades mayores de 110 se conservan, se señalan y aportan conteos separados para sensibilidad posterior. |
| Agregación | Solo combinaciones observadas. Se suman conteos antes de calcular tasas; no se promedian porcentajes de filas. Se conserva población con participación desconocida. |
| Tasas | Participación `100×SV/(SV+NV)`, abstención `100×NV/(SV+NV)`, no especificación `100×NS/LN`, cobertura conocida `100×(SV+NV)/LN`. Denominador conocido cero → tasas de participación/abstención vacías, no cero. |
| Fechas | Se selecciona por `AELEC=2024` y se conservan los literales de `FELECCION` en el reporte, sin interpretar `06/02/2024`. |
| Totales y exclusiones | Reconciliación exacta de los cuatro conteos entre fuente y tabla; no se excluyen silenciosamente filas inválidas. Cero exclusiones en una ejecución válida, incluidas edades extremas. |

La tabla incluye claves, conteos, filas fuente contribuyentes, denominador conocido,
tasas porcentuales con ocho decimales y `age_over_110_*`. Estas últimas columnas
permiten evaluar sensibilidad sin publicar microceldas ni eliminar automáticamente
edades extremas. No son variables de segmentación seleccionadas: esa decisión es T07.
El CSV no conserva tipos: al leerlo, declara `EDOCVE` y `SEXO` como cadenas/categorías.

El reporte registra versiones de Python/Pandas, hashes del comando, manifiesto,
ZIP y tabla, filas por archivo, ceros por conteo, faltantes distritales y límites
del análisis. No impone un umbral de cobertura ni una regla de publicación no
acordados. La ausencia de tokens de supresión no demuestra que no hubiera
exclusiones o supresión antes de publicar la fuente.

## Verificación registrada · 22 de octubre de 2026

Se ejecutó el comando completo en el contenedor local existente, sin reconstruir
la imagen, cambiar dependencias ni descargar datos. Python **3.12.10** y Pandas
**3.0.6**. La tabla resultante tiene **356 combinaciones observadas**.

| Evidencia | Resultado |
| --- | ---: |
| Filas fuente validadas | 9.773.730 |
| Entidades / CSV | 32 / 32 |
| ΣLN | 98.330.348 |
| ΣSV | 54.899.228 |
| ΣNV | 37.105.466 |
| ΣNS | 6.325.654 |
| Filas con `SV+NV=0`, conservadas | 323.984 |
| Filas con edad >110, conservadas | 227 |
| Filas con DEL faltante | 20.912 |
| Filas con DEF faltante | 0 |
| Filas excluidas | 0 |

Los totales coinciden con la auditoría de T04 y con la tabla generada; el ZIP y
el manifiesto conservaron sus hashes. Los hashes exactos del paquete se encuentran
en su `report.json`, no constituyen una certificación independiente del publicador.
Se repitió la ejecución completa con `--chunk-size 75000 --run-name ccpc_2024_repeat`:
`table.csv` y `report.json` coincidieron **byte por byte** con la ejecución inicial
de bloques de 150.000 filas. Ambas carpetas se conservan localmente.

Las pruebas sintéticas recorren el comando público con ZIP y manifiesto temporales
fuera del repositorio. Cubren claves duplicadas, dominios, consistencia geográfica,
faltantes, ceros, tokens desconocidos, límites de edad, tasas indefinidas,
preservación de originales, rechazo de salidas existentes y reproducibilidad entre
tamaños de bloque. No descargan datos ni necesitan las fuentes reales:

- RED observado antes de crear el comando: las ocho pruebas nuevas fallaron por
  ausencia de `scripts/clean_ccpc.py`.
- Prueba focalizada en Docker: **8 aprobadas**.
- Suite completa en Docker: **24 pruebas, 23 aprobadas y 1 omitida**, correspondiente
  a la prueba opcional de persistencia desde el anfitrión; no se volvió a ejecutar
  esa prueba opcional en T06. Las comprobaciones de montajes y permisos del contenedor
  sí se ejecutaron y aprobaron.

```powershell
docker compose run --rm --pull never analysis python -B -m unittest discover -s tests -p test_clean_ccpc.py -v
docker compose run --rm --pull never analysis python -B -m unittest discover -s tests -v
```

La reproducción integrada del análisis final y de los entregables sigue siendo
T14; la selección de 4–6 perfiles y la evaluación de estabilidad corresponden a T07.
