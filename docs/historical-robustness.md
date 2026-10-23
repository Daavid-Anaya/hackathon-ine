# T07 — Robustez histórica sin agrupar elecciones

Esta extensión mantiene 2024 como análisis central y pregunta si los patrones de
participación se repiten en otras elecciones. Compara modelos anuales de manera
independiente y usa definiciones fijas de participación dentro de cada serie
electoral. No selecciona perfiles finales de T08 ni convierte grupos agregados
en historias individuales.

## Ejecución local

Con los seis paquetes T06 y la imagen local existente disponibles:

```powershell
docker compose run --rm --pull never analysis python -B scripts/compare_history.py
docker compose run --rm --pull never analysis python -B scripts/compare_history.py --run-name t07_history_repeat
```

El directorio de entrada predeterminado es `data/processed/ccpc_all/`, con carpetas
anuales para 2009, 2012, 2015, 2018, 2021 y 2024. `--input` selecciona otro directorio
T06 completo dentro de `data/processed`; `--root` admite otra raíz del proyecto o
de datos de prueba. `--run-name` debe ser un nombre simple de directorio nuevo
dentro de `outputs`. Consulte `--help`.

El paquete de salida contiene:

| Archivo | Propósito |
| --- | --- |
| `report.json` | Todos los candidatos anuales, procedencia, elegibilidad, referencias, composiciones y diagnósticos por pares |
| `annual_comparison.csv` | Seis candidatos base y sus siete sensibilidades por año; Ward ponderado, no admitido, sigue marcado explícitamente como no aplicable |
| `fixed_reference.csv` | Tamaños anuales y tasas basadas en conteos para los rangos de referencia fija, incluidos intervalos vacíos |
| `pairwise.csv` | Cambios de tasas entre claves coincidentes, correlación de rangos, ARI de particiones anuales y concordancia de bandas fijas dentro de cada serie |

No se sobrescribe ningún original, paquete T06 ni resultado previo. Las seis
entradas se validan antes del ajuste; los resultados se publican juntos solo
después de completar la comparación y las comprobaciones de hashes de entrada
antes y después. Los directorios de salida son internos y están ignorados por
Git. El comando existente `compare_segments.py` sigue limitado a 2024.

## Dos preguntas, dos análisis

### Modelos anuales independientes

Cada año reutiliza el [motor de comparación de 2024](segmentation-comparison.md):
escenario base solo con participación, igual peso por grupo agregado elegible,
K-means y Ward para k=4,5,6, veinte semillas fijas de K-means con veinte
inicializaciones cada una, estabilidad al excluir entidades, tamaños/composición
y siete sensibilidades evaluadas de una en una. No se suman conteos anuales entre
elecciones. La silueta y la estabilidad anuales describen la geometría de ese año,
no una clasificación automática de la calidad de las elecciones.

La elegibilidad sigue siendo `SV+NV >= 30` y cobertura conocida de al menos 80%,
con las mismas comprobaciones de umbrales vecinos. Son reglas exploratorias, no
garantías estadísticas ni de publicación. Se registran conteos exactos,
exclusiones y hashes de origen por año. Los códigos históricos de sexo se
restringen a 0/1, mientras que 2024 conserva el código 2; su ausencia en años
anteriores nunca se convierte en una categoría sintética de conteo cero.

### Definiciones fijas dentro de cada serie

| Serie | Año de referencia | Propósito |
| --- | ---: | --- |
| 2012 / 2018 / 2024 | 2024 | Contexto histórico principal del análisis central |
| 2009 / 2015 / 2021 | 2021 | Contexto electoral separado, sin agruparlo con la primera serie |

Para cada k, se ajusta K-means base una sola vez en el año de referencia con la
misma función de creación de modelos, semilla 0 y configuración de la comparación
anual. Se ordenan por participación los centroides realmente ajustados y se
mantienen fijos para los tres años de esa serie. Cada grupo se asigna al centroide
más cercano; los empates eligen el rango inferior. Los puntos medios entre
centroides se registran como límites. Los intervalos exteriores son abiertos.
Los intervalos vacíos permanecen con cero grupos/LN y tasas indefinidas, no con
observaciones inventadas. Los rangos de referencia son diagnósticos, no
identificadores de perfiles finales.

Esto difiere deliberadamente de reajustar y comparar después etiquetas numéricas
de conglomerados, cuyo significado es arbitrario. Ward sigue como comparador
anual: no se inventa un predictor fuera de muestra para él. Las referencias
basadas en el último año son **puntos de comparación retrospectivos**, no prueba
de generalización predictiva.

## Diagnósticos de claves agregadas coincidentes

Para los tres pares de cada serie y cada k, se emparejan las claves elegibles
`(EDOCVE, SEXO, age_band)`. Se informan tanto los conteos de grupos sin pareja
como la LN representada por claves comunes en cada año por separado. Una clave
coincidente no debe interpretarse como las mismas personas ni como una unidad
territorial longitudinal validada.

- Los cambios medios/medianos de participación son diferencias en puntos
  porcentuales sobre claves agregadas comunes, con igual peso por clave, no
  cambios ponderados por población.
- La correlación de Spearman describe la conservación del orden relativo de las
  tasas; es indefinida para tasas constantes, no se le asigna silenciosamente un
  valor perfecto.
- El ARI compara particiones anuales ajustadas de manera independiente sin exigir
  etiquetas numéricas coincidentes. Un ARI alto puede coexistir con un gran cambio
  absoluto de participación.
- La concordancia de bandas fijas y las tablas de movimientos usan las mismas
  definiciones de centroides en ambas fechas. Cuentan claves agregadas, **no
  personas que se mueven entre perfiles**.

Los cambios de NS/cobertura conocida, geografía de origen, composición y grupos
excluidos pueden afectar cada comparación. Conservar claves de entidad/sexo/edad
no valida una correspondencia geográfica longitudinal. Los grupos escasos de la
categoría 2 en 2024 siguen contabilizados, no fusionados con categorías binarias.
No puede presentarse el escenario base como una caracterización de ellos, y la
extensión no resuelve la política de publicación.

## Verificación

Las pruebas sintéticas de la CLI pública cubren seis soluciones anuales
separadas, conservación de centroides de referencia, cambios absolutos pese a
particiones anuales estables, series separadas, intervalos vacíos de referencia,
conteos/composición, ausencia de modificaciones de origen, dominios históricos
de sexo, publicación de todo o nada y repetición determinista sin sobrescritura.

La verificación previa a la traducción exigió conservar stdout/stderr/código de
salida y contenido de resultados del comando de 2024 frente a la base guardada
anterior a la extensión. Se esperaba un cambio en el hash registrado del proceso
porque cambió la implementación compartida; los paquetes anteriores permanecían
intactos. En esa comprobación no se aceptó ninguna otra diferencia de salida.
El comando sigue rechazando entradas históricas; para ellas se usa el nuevo
comando histórico. La traducción autorizada posterior permite además los cambios
de texto humano descritos en la nota de idioma, no cambios numéricos o de protocolo.

Ejecute las suites focalizada y completa con:

```powershell
docker compose run --rm --pull never analysis python -B -m unittest discover -s tests -p test_compare_history.py -v
docker compose run --rm --pull never analysis python -B -m unittest discover -s tests -v
```

## Hallazgos registrados

Dos ejecuciones locales completas del **22 de octubre de 2026** produjeron cada
una **36 candidatos anuales, seis soluciones de referencia fija y 18
comparaciones por pares dentro de las series**. Ningún escenario aplicable
devolvió un ajuste no disponible. Los seis años usan el mismo entorno fijado
Python 3.12.10/Pandas 3.0.6/NumPy 2.5.4/Scikit-learn 1.9.1 que la ejecución de
2024. Los valores exactos se conservan en `outputs/t07_history/`.

### La separación anual no favorece un k universal

| Elección | Grupos elegibles | Silueta de K-means: k=4 | k=5 | k=6 |
| --- | ---: | ---: | ---: | ---: |
| 2012 | 320 | 0.563 | 0.572 | 0.561 |
| 2018 | 320 | 0.556 | 0.552 | 0.542 |
| 2024 | 320 | 0.536 | 0.564 | 0.568 |
| 2009 | 320 | 0.548 | 0.559 | 0.557 |
| 2015 | 318 | 0.554 | 0.561 | 0.562 |
| 2021 | 320 | 0.562 | 0.547 | 0.559 |

El máximo de silueta ocurre con cinco conglomerados en 2012/2009, cuatro en
2018/2021 y seis en 2024/2015. **No son selecciones automáticas de modelos**:
siguen importando los tamaños, la estabilidad y la utilidad sustantiva. En 2015,
k=6 aísla un conglomerado de siete grupos que representan solo aproximadamente
0.99% de la LN elegible, pese a una silueta ligeramente superior a k=5. El
escenario base de 2015 excluye dos de 320 grupos; los pares que incluyen ese año
usan por ello 318 claves elegibles comunes. En 2024, los 36 grupos no binarios
escasos siguen contabilizados fuera del escenario base, como se documentó antes.

### El orden relativo persiste más que las pertenencias exactas

Las tasas usan participación conocida, `SV/(SV+NV)`. Los cambios siguientes son
medias sin ponderar sobre claves agregadas comunes, **no cambios nacionales de
participación ponderados por población**. La concordancia de bandas fijas se
ilustra para k=5, sin seleccionarlo como solución final.

| Par | Claves comunes | Cambio medio (pp) | Correlación de rangos de tasas de Spearman | Misma banda fija k=5 | ARI anual de K-means, k=5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2012 → 2018 | 320 | -0.47 | 0.928 | 66.88% | 0.348 |
| 2012 → 2024 | 320 | -3.55 | 0.907 | 46.56% | 0.307 |
| 2018 → 2024 | 320 | -3.07 | 0.916 | 51.25% | 0.315 |
| 2009 → 2015 | 318 | +3.52 | 0.815 | 61.32% | 0.270 |
| 2009 → 2021 | 320 | +7.35 | 0.673 | 30.94% | 0.086 |
| 2015 → 2021 | 318 | +3.86 | 0.732 | 35.53% | 0.107 |

En la serie principal, el orden relativo es bastante persistente (correlación de
rangos superior a 0.90), pero las particiones anuales exactas y la pertenencia a
bandas fijas persisten mucho menos. Por ello sería engañoso describir los perfiles
de 2024 como tipos históricos de ciudadanos inmutables. La otra serie presenta
menor persistencia relativa y cambios sustanciales de nivel; debe conservarse
como contexto institucional separado.

### Las definiciones fijas revelan cambios de distribución

Con los mismos cinco intervalos de participación ajustados en 2024, el intervalo
inferior contiene 20, 16 y 52 grupos agregados en 2012, 2018 y 2024,
respectivamente. Sus proporciones de LN dentro de cada población anual elegible
son 5.37%, 4.22% y 13.49%. El intervalo superior contiene 55, 52 y 44 grupos
(19.38%, 19.79% y 16.07% de la LN elegible).

Con la referencia separada de cinco intervalos ajustada en 2021, el intervalo
inferior contiene 109, 84 y 45 grupos en 2009, 2015 y 2021 (35.38%, 27.64% y
13.25% de la LN elegible). Son comparaciones distributivas de cortes transversales
agregados, no movimientos individuales ni comparaciones entre intervalos de las
dos series definidos de manera diferente.

La cobertura es una explicación alternativa importante: NS/LN total es
aproximadamente 0.22% en 2012, 6.83% en 2018 y 6.43% en 2024. Condicionar a la
participación conocida no elimina posibles diferencias de cobertura/composición.
Ni los cambios anteriores ni las composiciones demográficas identifican barreras
causales o efectos de intervenciones.

### Evidencia de verificación y entrega a T08

- Suite completa final anterior a la traducción: **45 pruebas, 44 aprobadas y una
  comprobación opcional de persistencia del anfitrión omitida**, sin fallos ni
  errores (415.572 segundos). Se ejecutaron las cinco pruebas de la CLI histórica,
  tres regresiones permanentes de límites independientes y las siete pruebas
  existentes de comparación de 2024. El motivo de omisión fue `Prueba opcional de
  persistencia desde el equipo anfitrión; requiere la imagen local construida`.
- Ambas ejecuciones reales produjeron `report.json`, `annual_comparison.csv`,
  `fixed_reference.csv` y `pairwise.csv` idénticos byte a byte, confirmado con hashes
  de objetos Git sin filtrar. No se necesitaron descargas, cambios de dependencias
  ni reconstrucciones.
- La repetición del comando original de 2024 conservó su informe numérico y CSV;
  la única diferencia JSON fue el hash del código del proceso, exigido por la
  procedencia. No se modificó su directorio de salida original.
- Un verificador independiente inspeccionó árboles inmutables previos a la
  extensión y candidatos en un espacio temporal externo nuevo, y verificó las
  cuatro especificaciones sin bloqueos. Tres formas exitosas de la CLI de 2024,
  la ayuda y los casos negativos conservaron stdout/stderr/códigos de salida;
  coincidieron los campos de informes y bytes de CSV salvo el hash de código
  requerido. Las comprobaciones independientes también verificaron límites
  exactos de elegibilidad, empates, claves disjuntas, intervalos vacíos,
  composición e integridad de comandos rechazados. Las pruebas permanentes
  conservan esos límites sin depender del historial Git ni de commits base fijos.

T08 debe tratar cinco frente a seis como una disyuntiva central de 2024, no imponer
un k a todos los años ni afirmar identidades de perfiles atemporales. Toda
solución elegida debe indicar qué se repite (especialmente el orden relativo de
la serie principal) y qué depende del contexto (niveles, pertenencia, cobertura y
la otra serie electoral). Esta extensión informa esa decisión sin tomarla.