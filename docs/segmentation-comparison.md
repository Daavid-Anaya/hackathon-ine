# T07 — Comparación reproducible de segmentos agregados de participación

La comparación de 2024 permite discutir cinco o seis estratos de participación,
no afirmar que se descubrieron tipos naturales de ciudadanos. Seis tiene la mayor
silueta base; K-means con cinco conglomerados es más estable en las comprobaciones
de semillas y exclusión de entidades realizadas. **La selección final, las
asignaciones y los nombres de perfiles siguen correspondiendo a T08.**

Ampliación del alcance: la [robustez histórica](historical-robustness.md) añade
ajustes anuales separados y referencias fijas dentro de las series electorales.
Los resultados de 2024 registrados a continuación siguen siendo una base fechada
sin cambios, no una afirmación de validación multianual por sí mismos.

## Reproducir la comparación

Con la imagen local y las salidas de T06 ya disponibles, ejecute desde la raíz del repositorio:

```powershell
docker compose run --rm --pull never analysis python -B scripts/compare_segments.py
docker compose run --rm --pull never analysis python -B scripts/compare_segments.py --run-name t07_repeat
docker compose run --rm --pull never analysis python -B -m unittest discover -s tests -v
```

El primer comando lee `data/processed/ccpc_all/2024/{table.csv,report.json}` y
escribe `outputs/t07_comparison/{report.json,comparison.csv}`. No lee ZIP
originales, accede a la red, modifica T06 ni asigna identificadores de perfiles
finales. Los directorios de salida existentes se rechazan, no se sobrescriben.
Elija un `--run-name` nuevo para repetir.

`--input data/processed/ccpc_2024` admite otro paquete T06 de 2024. `--root`
establece la raíz del proyecto, principalmente para datos de prueba aislados.
`--help` enumera todas las opciones; los parámetros de los modelos están fijados
deliberadamente en el script versionado, no son valores predeterminados ocultos.

Las salidas son internas y están ignoradas por Git. Este documento conserva los
hallazgos de la comparación; el JSON conserva métricas exactas, resúmenes de
conteos, configuración y procedencia.

## Entrada, elegibilidad y salvaguardas

La unidad de análisis fijada en [T04](data-audit.md#unidad-analítica-justificada-y-comparabilidad)
es **2024 × entidad × sexo × banda de edad**. Las elecciones históricas siguen
como contexto; no se agrupan en este ajuste. Cinco bandas de edad no son cinco
perfiles predeterminados.

El SHA-256 de la tabla de entrada de la ejecución del **22 de octubre de 2026** fue
`2e82c59834fd904b03d55d1b5add52beb056554bf4617e600c5a218ffaf76d30`.
El script comprueba la tabla frente a su informe T06, exige las ocho
comprobaciones T06, valida claves/dominios/identidades de conteos y totales, y
verifica que ambos hashes de entrada permanezcan sin cambios durante la
ejecución. Registra los hashes del origen, manifiesto y proceso T06 sin afirmar
que revalida los ZIP originales en T07.

| Contabilidad del escenario base | Grupos | LN aprox. (millones) |
| --- | ---: | ---: |
| Entrada | 356 | 98.3 |
| Elegibles | 320 | 98.3 |
| Fuera del ajuste, aún contabilizados | 36 | Omitida |

Los tamaños de LN se muestran en millones, redondeados a una decimal; entrada
y población elegible coinciden a esta precisión, no en sus conteos exactos.
No deben restarse los valores aproximados para calcular la población excluida.

La elegibilidad es `D = SV + NV >= 30` y `100*D/LN >= 80`. Son **heurísticas
exploratorias**, no límites de confianza, cortes óptimos validados ni reglas de
divulgación. Los 36 grupos no elegibles corresponden a la categoría no binaria
escasa en esta entrada. No se fusionan con categorías binarias ni se tratan como
inexistentes. Por ello el escenario base **no** caracteriza esa categoría; la
alta cobertura poblacional no elimina esta limitación de representación. La
participación no especificada no se recodifica como abstención. No se exportan
asignaciones de grupos de entrada ni tasas individuales de celdas pequeñas.
Sigue siendo necesaria una política de publicación antes de la difusión.

## Variables, escalas, pesos y métodos

| Decisión | Justificación y limitación |
| --- | --- |
| Variable base: `100*SV/(SV+NV)` | Mide directamente la participación entre registros con participación conocida; los denominadores indefinidos no son elegibles, no se imputan. Las tasas se recalculan desde los conteos. |
| Sin cambio de escala base | Una variable porcentual: la estandarización solo reescalaría uniformemente las distancias euclidianas. |
| Igual peso por grupo agregado | Responde qué patrones de participación ocurren entre las unidades analíticas, no qué partición minimiza el error ponderado por población. |
| Edad, sexo y entidad como contexto | Resumen la composición después del ajuste; los identificadores no son distancias continuas. No se introducen variables educativas o socioeconómicas inexistentes. |
| Excluir variables redundantes | La abstención es complementaria de la participación; la cobertura es complementaria del porcentaje no especificado. Ningún par se cuenta dos veces. LN no es una variable de distancia. |
| K-means | Base transparente de distancia euclidiana al cuadrado para estratos de participación; `k=4,5,6`, semilla de referencia 0, `n_init=20`, `max_iter=300`, `tol=1e-4`, algoritmo Lloyd. |
| Agrupamiento jerárquico Ward | Comparador euclidiano determinista sin ponderación que minimiza la varianza en los mismos tres valores de k. Sin sustituto artificial de Ward ponderado. |

Las 20 semillas de K-means son enteros **0–19**, cada una con 20 inicializaciones.
La semilla 0 define la partición de referencia; no se elige retrospectivamente
para favorecer métricas. Las claves de entrada se ordenan y los conjuntos de
hilos numéricos se limitan a un hilo. Entorno registrado: Python 3.12.10, Pandas
3.0.6, NumPy 2.5.4, Scikit-learn 1.9.1.

## Diseño de evaluación

- **Separación:** silueta euclidiana sin ponderar en el espacio de variables de
  cada candidato. Un valor mayor es mejor dentro de esa comparación; no certifica
  conglomerados naturales. El ajuste ponderado por LN sigue teniendo silueta sin
  ponderar. No se deben ordenar los espacios de variables 1D y 2D por sus valores
  de silueta como si las distancias fueran idénticas.
- **Estabilidad:** índice de Rand ajustado (ARI, 1 significa pertenencias
  idénticas salvo permutación de etiquetas) frente a la semilla 0 para las otras
  19 semillas; se reajusta tras retirar cada una de las 32 entidades y se comparan
  pertenencias sobre los grupos retenidos. La estabilidad entre semillas de Ward
  no aplica, no se supone perfecta. Son comprobaciones de sensibilidad
  algorítmica sobre agregados censales, no incertidumbre de encuestas ni
  intervalos de confianza.
- **Tamaños:** conteos de grupos y proporciones de LN de la población elegible,
  no conteos de filas de origen ni una media de porcentajes. La participación del
  perfil es `sum(SV)/sum(D)`.
- **Interpretabilidad:** rangos de participación y tasas basadas en conteos,
  composición de LN por edad/sexo y diversidad de entidades por conglomerado
  base. Sin etiquetas causales.

Cada candidato base tiene además siete sensibilidades evaluadas de una en una:

| Escenario | Cambio frente al escenario base | Grupos elegibles observados |
| --- | --- | ---: |
| `min_d15` | D de al menos 15 | 321 |
| `min_d60` | D de al menos 60 | 320 |
| `coverage70` | Cobertura conocida de al menos 70% | 320 |
| `coverage90` | Cobertura conocida de al menos 90% | 268 |
| `ln_weighted` | Pesos muestrales de K-means = LN, misma variable y elegibilidad | 320 |
| `participation_unspecified` | Participación y `100*NS/LN`, cada una centrada/escalada a varianza unitaria con StandardScaler | 320 |
| `without_age_over_110` | Restar las contribuciones marcadas >110 de los cuatro conteos; recalcular tasas/elegibilidad | 320 |

El escalador de dos variables se ajusta de nuevo a los datos del escenario; la
igualdad de varianza da a los datos no especificados tanta influencia en la
distancia como a la participación, lo que es un cambio sustantivo, no una mejora
automática. Las sensibilidades usan la semilla 0; los recorridos de 20 semillas y
de exclusión de entidades se aplican a los seis candidatos base, no a cada
variante. El ARI usa claves de entrada comunes e informa su número; no debe
ocultar cambios de elegibilidad. Los ajustes no disponibles tienen motivos
explícitos, nunca métricas inventadas.

## Comparación registrada — 22 de octubre de 2026

Los seis candidatos base y todas las sensibilidades aplicables pudieron
evaluarse. Cada comprobación de exclusión de entidades completó 32 reajustes.
Los números siguientes están redondeados; el JSON es la fuente autoritativa.

| Método | k | Silueta | Conglomerado menor: grupos / proporción de LN | ARI entre semillas mín. / mediana | ARI al excluir entidades mín. / mediana |
| --- | ---: | ---: | ---: | ---: | ---: |
| K-means | 4 | 0.536 | 62 / 17.27% | 0.877 / 0.955 | 0.748 / 0.990 |
| Ward | 4 | 0.526 | 49 / 15.53% | N/A | 0.477 / 1.000 |
| K-means | 5 | 0.564 | 44 / 13.49% | 1.000 / 1.000 | 0.960 / 1.000 |
| Ward | 5 | 0.532 | 44 / 15.53% | N/A | 0.509 / 0.930 |
| K-means | 6 | 0.568 | 31 / 8.16% | 0.891 / 1.000 | 0.882 / 1.000 |
| Ward | 6 | 0.555 | 31 / 8.16% | N/A | 0.609 / 0.946 |

**Interpretación:** K-means con seis conglomerados mejora la silueta en solo
aproximadamente 0.004 frente a cinco y crea un segmento mínimo menor. K-means con
cinco conglomerados tiene la mayor estabilidad en el peor caso de semillas y
entidades en este experimento. Ward es más sensible a la exclusión de entidades,
pese a su ajuste determinista. El ARI entre métodos es 0.552, 0.796 y 0.890 para
k=4,5,6, respectivamente: la concordancia mejora con k, pero no demuestra que
seis perfiles sean institucionalmente preferibles.

### Hallazgos de sensibilidad

- Reducir D a 15 introduce un grupo pequeño. Aumentarlo a 60 o reducir la
  cobertura a 70% no cambia la población elegible base. Los tres conservan las
  pertenencias base sobre grupos comunes (ARI=1). Es evidencia limitada, no una
  inmunidad general a las decisiones de elegibilidad.
- Aumentar la cobertura a 90% excluye 52 grupos adicionales. El ARI sobre grupos
  comunes va de 0.893 a 1.000 para K-means y de 0.979 a 0.984 para Ward. Los
  cambios de población representada importan incluso cuando el ARI permanece en 1.
- La ponderación por LN cambia las pertenencias de K-means: ARI **0.787 / 0.892 /
  0.871** para 4/5/6. Los objetivos de igualdad entre grupos y de énfasis
  poblacional no son intercambiables.
- Añadir el porcentaje no especificado estandarizado cambia sustancialmente las
  pertenencias: ARI **0.267 / 0.222 / 0.269** para K-means y **0.303 / 0.180 /
  0.201** para Ward. Esos modelos también agrupan la completitud de los datos,
  por lo que sus segmentos no pueden interpretarse solo como participación.
  Trate NS como diagnóstico del escenario base, no como una barrera de
  comportamiento descubierta ni un rasgo individual demostrado.
- Al retirar las contribuciones de edades mayores de 110 años, las seis particiones
  base permanecen sin cambios (ARI=1), aunque las tasas y los totales cambian
  ligeramente. Esto no valida las edades extremas; acota su influencia en este
  experimento.

### Ejemplo de interpretación, no selección de perfiles finales

K-means con cinco conglomerados ilustra lo que puede explicar el escenario base.
Las filas siguientes se ordenan por participación agregada, **no se nombran ni
exportan como identificadores de perfiles finales**.

| Rango de participación entre grupos | Participación del conglomerado basada en conteos | Grupos | Proporción de LN elegible |
| --- | ---: | ---: | ---: |
| 32.10–44.92% | 40.34% | 52 | 13.49% |
| 45.21–54.48% | 50.15% | 70 | 21.51% |
| 54.84–63.15% | 59.55% | 76 | 23.50% |
| 63.46–71.30% | 67.34% | 78 | 25.43% |
| 71.62–80.92% | 76.35% | 44 | 16.07% |

La composición añade contexto: el conglomerado de mayor participación tiene
aproximadamente 61.00% de su LN en la banda 60+. Es una afirmación sobre su
composición, no que cada persona mayor participa, ni evidencia de que la edad
cause participación. La tabla conservada no permite establecer educación,
motivos, preferencias políticas, historias individuales de voto ni diferencias
intraestatales perdidas por la agregación.

## Verificación y entrega

La prueba focalizada de la CLI falló primero porque el script nuevo no existía
(RED observado) y aprobó tras la implementación y la corrección de datos de
prueba. Las pruebas sintéticas ejercitan todas las comparaciones de k/métodos,
estabilidad, elegibilidad, resúmenes basados en conteos, recálculo en lugar de
tasas almacenadas, rechazo por procedencia, ausencia de modificaciones de
entrada, ausencia de publicación parcial y rechazo de sobrescritura. No
requieren descargas de originales.

La suite completa final de esa etapa completó **37 pruebas: 36 aprobadas y una
omitida**, sin fallos ni errores (242.975 segundos). La prueba omitida era la
comprobación opcional de persistencia Docker desde el anfitrión; su motivo exacto
era `Prueba opcional de persistencia desde el equipo anfitrión; requiere la
imagen local construida`. Las pruebas del entorno del contenedor y las siete
pruebas T07 se ejecutaron correctamente. No se necesitaron cambios de
dependencias, construcciones de imágenes ni operaciones remotas.

Dos ejecuciones reales (`t07_comparison`, `t07_repeat`) produjeron informes y CSV
idénticos byte a byte, confirmado con hashes de objetos Git sin filtrar. Sus JSON
incluyen el hash del script y el entorno exacto; otras versiones de bibliotecas
pueden cambiar pertenencias o resultados de punto flotante, por lo que la
reproducibilidad requiere la imagen fijada.

T08 debe resolver la disyuntiva de cinco frente a seis y el objetivo de
ponderación, reconociendo explícitamente la limitación de cobertura no binaria.
Si los estratos de participación son insuficientes para el uso institucional
previsto, se deben reconsiderar las variables o la unidad con un cambio de
alcance autorizado, en lugar de inventar tipos multidimensionales de ciudadanos.
Las comparaciones históricas se documentan en la extensión separada; las
asignaciones finales, nombres, estrategias y aprobación de publicación siguen
fuera de T07.

Referencias metodológicas: [Guía de agrupamiento de Scikit-learn 1.9.1](https://github.com/scikit-learn/scikit-learn/blob/1.9.1/doc/modules/clustering.rst),
[KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html),
[ARI](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html).
