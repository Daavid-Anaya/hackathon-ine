# T08 — Cinco perfiles de 2024 con contexto de seis elecciones

Se selecciona **K-means con cinco segmentos de participación de 2024**, sin
escalado y con igual peso por grupo agregado elegible. La entrega conserva los
resultados históricos de **2009, 2012, 2015, 2018, 2021 y 2024**, sin sumar sus
poblaciones ni imponer un número óptimo universal de conglomerados. Las salidas
son **internas**, no una publicación autorizada de grupos pequeños.

Existe una [vista reducida separada para revisión de divulgación](disclosure-review.md).
No modifica este paquete ni autoriza su publicación; los archivos completos
siguen siendo evidencia interna.

## Ejecución

Con los seis paquetes T06 y la comparación histórica T07 disponibles:

```powershell
docker compose run --rm --pull never analysis python -B scripts/export_profiles.py
```

La salida se crea en `outputs/t08_profiles/`. Para otra ejecución, utilice
`--run-name t08_repeat`; nunca se sobrescribe una carpeta existente. `--input`
selecciona la carpeta de seis paquetes dentro de `data/processed`; `--history`
selecciona el `report.json` histórico dentro de `outputs`. `--root` admite una
raíz aislada para pruebas. Consulte `--help`.

No se descargan datos ni se reconstruye la imagen. Si faltan los insumos, siga
primero las instrucciones de [T06](data-cleaning.md) y [T07 histórica](historical-robustness.md).
El entorno debe coincidir con las versiones registradas en T07.

## Por qué cinco perfiles centrales

La selección es una decisión documentada, no una regla automática que escoge la
máxima silueta. En la [comparación de 2024](segmentation-comparison.md#comparación-registrada--22-de-octubre-de-2026):

| K-means | Silueta | ARI mínimo entre semillas | ARI mínimo al excluir entidades |
| --- | ---: | ---: | ---: |
| 4 segmentos | 0.536 | 0.877 | 0.748 |
| **5 segmentos** | **0.564** | **1.000** | **0.960** |
| 6 segmentos | 0.568 | 0.891 | 0.882 |

Cinco mejora la separación frente a cuatro y tiene la mayor estabilidad mínima
observada. Seis gana aproximadamente 0.004 de silueta, pero reduce la estabilidad
mínima y el tamaño del segmento menor. No se ha demostrado una utilidad
institucional adicional que justifique esa partición más fina.

Se usa `participation_pct = 100 * SV / (SV + NV)`, semilla 0, veinte
inicializaciones y los parámetros del motor T07. Cada grupo de entidad × sexo ×
banda de edad tiene el mismo peso: el objetivo es distinguir niveles entre
grupos, no minimizar un error ponderado por población. La ponderación por LN
queda como sensibilidad, no como una alternativa equivalente. LN sí pondera las
composiciones y las tasas de perfil calculadas a partir de conteos.

La edad, el sexo y la entidad describen la composición, pero no entran en las
distancias. Añadir no especificados cambiaría el significado hacia participación
y completitud del registro. No se infieren motivos, preferencias, causas ni
tipos individuales de ciudadanía.

## Identificadores y archivos

Los perfiles centrales usan `CCPC-2024-K5-P01` a `CCPC-2024-K5-P05`, ordenados por
centroide creciente. Los identificadores son interpretables **dentro del modelo
y la evidencia del paquete**: no son identidades longitudinales ni garantizan
las mismas pertenencias con otros datos o parámetros. El centroide es la media
de tasas de grupos; no debe confundirse con la tasa del perfil basada en conteos.

| Archivo | Contenido |
| --- | --- |
| `report.json` | Decisión, parámetros, evidencia de selección, perfiles, entorno, procedencia, elegibilidad anual, limitaciones y hashes de los otros ocho archivos |
| `profiles.csv` | Cinco perfiles de 2024: centroide, conteos LN/SV/NV/NS, grupos, entidades, tasas, rangos y composición por sexo/edad |
| `assignments.csv` | Correspondencia de cada grupo elegible de 2024 con su perfil, claves, conteos y tasa |
| `historical_assignments.csv` | Asignaciones de los grupos elegibles de las seis elecciones a las referencias fijas de 4, 5 y 6 bandas |
| `fixed_reference.csv` | Tamaño, conteos, tasas y composición anual de cada banda fija; mantiene bandas vacías |
| `annual_comparison.csv` | Los 36 candidatos anuales y sus siete sensibilidades por candidato, sin selección anual universal |
| `pairwise.csv` | Las 18 comparaciones dentro de cada serie: cambios, correlación, ARI y concordancia de bandas |
| `exclusions.csv` | Claves, conteos y motivos de exclusión por año; sin asignación ni tasa de grupos no elegibles |
| `t07_evidence.json` | Copia byte a byte del informe histórico T07, incluidos estabilidad, sensibilidades y movimientos de claves agregadas |

Las composiciones en los CSV son objetos JSON en `sex_ln_share_pct` y
`age_ln_share_pct`. Los porcentajes usan LN elegible **de cada elección**, nunca
una población sumada entre años. Una banda vacía tiene conteos cero y tasas
vacías en CSV (`null` en JSON), no participación cero. Los datos históricos no
incorporan categorías de sexo inexistentes como observaciones sintéticas.

### Referencias históricas, no perfiles finales anuales

| Serie | Referencia fija | Ejemplo de identificador |
| --- | ---: | --- |
| 2012 / 2018 / 2024 | 2024 | `CCPC-REF-2024-K5-R01` |
| 2009 / 2015 / 2021 | 2021 | `CCPC-REF-2021-K5-R01` |

Se conservan **los tres valores de k**, no solo cinco. Cada referencia se ajusta
una vez, mantiene sus centroides y asigna por proximidad; los empates eligen la
banda inferior. Los identificadores `REF` son diagnósticos de esa serie y k,
distintos de los perfiles centrales `P`. No se equiparan bandas entre series ni
etiquetas arbitrarias de ajustes anuales. En 2024 se comprueba que la referencia
k=5 reproduce la partición seleccionada.

## Trazabilidad y límites

Antes de exportar, el comando valida los seis paquetes T06 y coteja sus hashes,
conteos, metadatos y elegibilidad con T07. Reajusta los **36 modelos base**,
comprueba métricas y composiciones, reconstruye **seis referencias fijas** y
contrasta **18 comparaciones temporales**. No repite los barridos de semillas,
exclusión de entidades ni sensibilidades: conserva explícitamente esa evidencia
T07. No autentica una firma externa ni sustituye la reproducción completa T14.

Los hashes originales de los procesos T07 se conservan junto con los del código
actual T08/T07. No se exige igualdad entre el hash del productor histórico y el
actual: una traducción de mensajes puede cambiarlo sin alterar los cálculos;
la compatibilidad se comprueba mediante parámetros, entorno, datos y resultados.
Se verifican otra vez los hashes de entradas y evidencia antes de publicar el
paquete completo por renombrado, sin modificar los insumos ni salidas previas.

La elegibilidad conserva las reglas T07: denominador conocido ≥30 y cobertura
conocida ≥80%. Los grupos excluidos siguen contabilizados. Los cambios de
cobertura, composición y geografía limitan las comparaciones. Las referencias
son retrospectivas, no validación predictiva; el orden relativo histórico puede
persistir sin que persistan las pertenencias. No representan movimientos de
personas ni cohortes. La revisión de divulgación permanece pendiente antes de
usar asignaciones o cifras detalladas en materiales públicos.

## Evidencia de ejecución

La primera prueba focalizada falló porque no existía `export_profiles.py` (RED).
Tras la implementación aprobaron las seis pruebas de la nueva CLI (117.193 s).
La ejecución real generó cinco perfiles, **320 asignaciones centrales**, **5.754
asignaciones históricas** y conservó 36 candidatos, seis referencias y 18 pares.
Las salidas están en `outputs/t08_profiles/`, fuera de Git.

La suite completa del código final ejecutó **51 pruebas: 50 aprobadas y una
omitida**, sin fallos ni errores (515.902 s). La omitida es la comprobación opcional
de persistencia Docker desde el anfitrión; su motivo fue `Prueba opcional de
persistencia desde el equipo anfitrión; requiere la imagen local construida`.
No se cambiaron dependencias ni los comandos existentes T06/T07.

Dos ejecuciones del código final, `t08_profiles_final` y `t08_profiles_repeat`,
generaron los nueve archivos idénticos byte a byte. La primera carpeta es la
evidencia final de T08; la ejecución inicial `t08_profiles` se conserva sin
sobrescritura y registra el hash de la versión anterior a la última validación
del esquema de estabilidad. Para reproducir el paquete final en otra carpeta:

```powershell
docker compose run --rm --pull never analysis python -B scripts/export_profiles.py --run-name t08_nueva_ejecucion
```

### Resumen numérico seleccionado de 2024

| Perfil | Grupos | Proporción de LN elegible | Participación basada en conteos | Rango de tasas de los grupos |
| --- | ---: | ---: | ---: | ---: |
| `CCPC-2024-K5-P01` | 52 | 13.49% | 40.34% | 32.10–44.92% |
| `CCPC-2024-K5-P02` | 70 | 21.51% | 50.15% | 45.21–54.48% |
| `CCPC-2024-K5-P03` | 76 | 23.50% | 59.55% | 54.84–63.15% |
| `CCPC-2024-K5-P04` | 78 | 25.43% | 67.34% | 63.46–71.30% |
| `CCPC-2024-K5-P05` | 44 | 16.07% | 76.35% | 71.62–80.92% |

Las cinco filas abarcan los 320 grupos elegibles y LN=98.330.243. Los 36 grupos
excluidos de 2024, con LN=105, se conservan en la contabilidad y en
`exclusions.csv`, no se asignan ni se interpretan como participación cero.
Las otras elecciones mantienen su propia población y contabilidad en el informe.
Los nombres y narrativas corresponden a T09; las estrategias institucionales a T10.
