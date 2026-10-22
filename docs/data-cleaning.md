# T06: limpieza reproducible de CCPC 2009–2024

El comando offline valida las seis elecciones y produce una tabla **entidad ×
sexo × tramo de edad por elección**, siguiendo las reglas de [T04](data-audit.md).
No mezcla años ni construye historiales individuales. La primera segmentación
sigue definida para 2024; limpiar la serie histórica no cambia esa decisión.
No modifica los ZIP ni el manifiesto. Los resultados son de uso interno: la
política de difusión de grupos pequeños sigue pendiente.

## Ejecutar desde PowerShell

Con Docker Desktop iniciado y la imagen local de T05 disponible:

```powershell
docker compose run --rm --pull never analysis python scripts/clean_ccpc.py --all-years
```

El comando lee `data/sources.json`, verifica los seis ZIP y procesa sus **192 CSV**
por bloques, sin extraerlos. Termina con código **0** y un resumen JSON si todas
las comprobaciones pasan. Publica un paquete completo en `data/processed/ccpc_all/`:

- `2009/`, `2012/`, `2015/`, `2018/`, `2021/`, `2024/`: cada carpeta contiene su
  `table.csv` y `report.json`, con validaciones, exclusiones, transformaciones y
  reconciliación de totales independientes.
- `summary.json`: inventario de años, rutas relativas, conteos y totales por año,
  hash del manifiesto y límites de comparación. No suma poblaciones entre elecciones.

Si falla una elección, **no se publica ninguna carpeta anual parcial** del nuevo
paquete. Los resultados anteriores se conservan. El ZIP de cada año y el
manifiesto se comprueban antes y después del procesamiento; al finalizar el lote
se vuelven a comprobar los seis ZIP y el manifiesto.

Para procesar solo una elección, sin necesitar las fuentes de las otras cinco:

```powershell
docker compose run --rm --pull never analysis python scripts/clean_ccpc.py --year 2012
```

Genera `data/processed/ccpc_2012/`. **Sin `--year` ni `--all-years`, se mantiene el
comportamiento anterior: solo 2024**, con salida en `data/processed/ccpc_2024/`.

Si la carpeta ya existe, el comando falla sin reemplazarla. Para repetir el análisis
y conservar la ejecución anterior:

```powershell
docker compose run --rm --pull never analysis python scripts/clean_ccpc.py --all-years --run-name ccpc_all_repeat
```

Compara los hashes `table_sha256` de los reportes de cada año. Con los mismos
originales, código y entorno, las tablas y reportes deben coincidir byte por byte,
incluso usando otro tamaño de bloque. El reporte identifica el hash del comando:
si cambia el código, incluso sus comentarios, ese metadato cambia deliberadamente.
Los resultados están excluidos de Git y persisten al
eliminar los contenedores. No los publiques automáticamente.

### Opciones

| Opción | Uso |
| --- | --- |
| `--help` | Describe el comando sin procesar datos. |
| `--chunk-size 150000` | Filas por bloque; entero positivo. No cambia las reglas ni los resultados. |
| `--year AÑO` | Procesa 2009, 2012, 2015, 2018, 2021 o 2024; predeterminado 2024. No se puede combinar con `--all-years` ni seleccionar años distintos repitiendo `--year`. |
| `--all-years` | Procesa las seis elecciones, con salidas separadas por año y publicación conjunta. |
| `--run-name NOMBRE` | Carpeta nueva dentro de `data/processed/`; predeterminada `ccpc_AÑO` o `ccpc_all`. Solo letras ASCII, números, guion y guion bajo. |
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
| Procedencia | Una entrada por elección seleccionada; tamaño, SHA-256 e inventario ZIP exactos; hashes de ZIP y manifiesto antes y después. El modo anual no lee filas de otras elecciones. |
| Cobertura de archivos | Por año: 32 CSV no vacíos, una entidad por CSV, sin entidades repetidas; conjunto de entidades 1–32. No equivale a cobertura poblacional exhaustiva. |
| Esquema | Los 16 campos de T04, en el orden documentado; UTF-8 con BOM opcional. No se omiten filas vacías ni se convierten tokens como `NA` automáticamente. |
| Clave | `(AELEC, EDOCVE, SECCION, SEXO, EDAD)` normalizada; comparación exacta de tuplas, dentro y entre bloques. La exclusividad de entidad entre CSV impide claves compartidas entre archivos. Un duplicado detiene la ejecución. |
| Identificadores | Enteros normalizados; `EDOCVE` se exporta con dos dígitos, `SEXO` como código categórico. Municipio 1–570, sección positiva, DEF 1–41 en 2009–2021 y 1–40 en 2024; DEL 1–45. No se homologan catálogos externos. |
| Geografía | Por elección, consistencia de nombres y de `(entidad, sección) → municipio, tipo, DEF, DEL`. Tipos U, M y R. No se exige que una sección tenga los mismos atributos en años distintos. |
| Conteos | `LN` positivo; `SV`, `NV`, `NS` enteros no negativos; `LN = SV + NV + NS`. Se aceptan representaciones enteras con espacios externos, no fracciones ni negativos. |
| Faltantes y supresión | Blancos distritales → faltante, nunca cero; conteos blancos → error. Tokens desconocidos → error por posible supresión no documentada, nunca imputación o reconstrucción. `NS` no se interpreta como supresión. |
| Edad y sexo | Edad mínima 18; tramos 18–24, 25–34, 35–44, 45–59, 60+. Sexo 0/1 en 2009–2021 y 0/1/2 en 2024. No se inventa sexo 2 en años anteriores ni se rellena su ausencia con ceros. Las edades mayores de 110 se conservan y aportan conteos separados para sensibilidad. |
| Agregación | Solo combinaciones observadas. Se suman conteos antes de calcular tasas; no se promedian porcentajes de filas. Se conserva población con participación desconocida. |
| Tasas | Participación `100×SV/(SV+NV)`, abstención `100×NV/(SV+NV)`, no especificación `100×NS/LN`, cobertura conocida `100×(SV+NV)/LN`. Denominador conocido cero → tasas de participación/abstención vacías, no cero. |
| Fechas | Se exige `AELEC` igual al año seleccionado; se conservan los literales de `FELECCION`, sin una regla global de interpretación. |
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

## Ampliación multianual · 22 de octubre de 2026

Se añadieron `--year` y `--all-years` después de observar pruebas RED por ausencia
de ambas opciones. La suite completa ampliada en Docker terminó con **29 pruebas:
28 aprobadas y 1 omisión esperada** de la prueba opcional de persistencia desde el
anfitrión. Incluye selección de los seis años, dominios históricos, fechas literales,
separación anual, reproducibilidad, rechazo de sobrescritura y ausencia de resultados
parciales si falla el último año. También conserva las pruebas originales de 2024.
La primera ejecución focalizada excedió 180 segundos; sus casos terminaron aprobados
en la suite completa posterior, con un límite de tiempo mayor.
La verificación independiente detectó que repetir `--year` con años distintos
ignoraba el primero. Se añadió una regresión RED y se corrigió el analizador para
rechazar ese caso con código 2 antes de escribir archivos. Después aprobaron
**3 pruebas focalizadas**: el rechazo de años contradictorios, la compatibilidad
del modo 2024 y las opciones, y el lote multianual reproducible. No se repitió la
suite completa ni el barrido real tras esta corrección exclusiva de argumentos;
los reportes conservan el hash de la versión que produjo los datos.
La revalidación independiente de esa corrección aprobó 14 ejecuciones acotadas
del comando público: rechazo sin escrituras, modos anual y multianual y
compatibilidad con la versión anterior de 2024. No quedaron bloqueos de la
verificación independiente; los casos no afectados conservaron su dictamen inicial.

La ejecución real de `--all-years` terminó correctamente y validó **54.872.712
filas en 192 CSV**, con **1.956 grupos analíticos** y cero exclusiones:

| Elección | Filas fuente | Grupos analíticos |
| --- | ---: | ---: |
| 2009 | 8.706.843 | 320 |
| 2012 | 8.604.456 | 320 |
| 2015 | 9.106.059 | 320 |
| 2018 | 9.251.122 | 320 |
| 2021 | 9.430.502 | 320 |
| 2024 | 9.773.730 | 356 |

Los cuatro totales de cada año coincidieron con T04 y con su tabla analítica;
todas las comprobaciones de los seis reportes resultaron aprobadas. La tabla
2024 del lote coincide **byte por byte** con la tabla previa de 2024. El reporte
identifica la nueva versión del comando mediante su hash, por lo que no se exige
que ese metadato coincida con el de una versión anterior del código.
El paquete completo y su resumen se conservan en `data/processed/ccpc_all/`.
El procesamiento superó los 15 minutos del primer límite de espera: se retomó
la conexión al mismo contenedor activo y terminó sin reiniciar ni duplicar la ejecución.

La serie limpia no demuestra comparabilidad automática: distinguir 2009/2015/2021
de 2012/2018/2024 y considerar los cambios de cartografía, cobertura y categorías
documentados en T04. No se ha realizado una segmentación histórica ni una
homologación territorial entre elecciones.

La reproducción integrada del análisis final y de los entregables sigue siendo
T14; la selección de 4–6 perfiles y la evaluación de estabilidad corresponden a T07.
