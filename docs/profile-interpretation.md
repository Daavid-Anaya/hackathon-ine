# T09 — Descripciones trazables de los cinco perfiles

T09 interpreta los cinco perfiles de 2024 seleccionados en [T08](profile-selection.md),
sin ajustar modelos nuevos ni convertir segmentos agregados en tipos de personas.
Las descripciones con composición demográfica se conservan **solo como borrador
local interno**, en `outputs/t09_profiles_narrative/README.md`, excluido de Git.
Este documento registra el método de interpretación, no una aprobación para difundirlas.

El mismo borrador incluye un **contexto histórico separado de 2009–2024**,
como complemento de interpretación de T09. Los perfiles centrales siguen siendo
de 2024; no se redefinen ni se seleccionan nuevos perfiles finales por elección.

## Fuentes y trazabilidad

Cada descripción conserva el identificador `CCPC-2024-K5-P01` a `P05` y cita la
fila correspondiente de `outputs/t08_profiles_final/profiles.csv`. No se usa la
ejecución inicial `outputs/t08_profiles/` ni se altera la evidencia T08.

| Insumo | SHA-256 de la evidencia consultada |
| --- | --- |
| `outputs/t08_profiles_final/profiles.csv` | `9ef1b18f83fca446d5e88bec6fb830010c68ef0025dba36eec65ea725d5f9325` |
| `outputs/t08_profiles_final/report.json` | `8954b9e653763f0452b94d0c977cd501607b39c24d8b05cd97b56d6f1c61db7b` |
| `outputs/t08_profiles_final/assignments.csv`, ampliación descriptiva | `94e06596e424680c1f844b4a5d3509cfdc0141e59f3314e67dac7d8eb8a28e6c` |
| `outputs/profile_section_types_2024/cross.csv`, descriptor TIPOSEC | `f758d27f65da387cadcdd1ad3a1b8ea42213de4f560b89787f46c6ee7f77eee5` |

Las huellas de los ocho artefactos T08, incluido el CSV, se cotejaron con
`artifacts_sha256` del informe. Esto comprueba esas correspondencias locales, no
todos los insumos, la autenticidad del productor ni una reproducción de modelos.
No se repitieron T06–T08.

## Cómo leer las descripciones

| Elemento | Regla de interpretación |
| --- | --- |
| Nombre | Describe un nivel observado de participación relativo a estos cinco segmentos; no una cualidad moral ni un umbral oficial. |
| Tamaño | `ln_share_pct`: proporción de la LN de los grupos elegibles de 2024. No es proporción de votantes ni de la población total de México. |
| Participación | `participation_pct`: `100 × SV / (SV + NV)` sumando los conteos del perfil. No se sustituye por el centroide ni se incluye NS como abstención. |
| Composición | `age_ln_share_pct` y `sex_ln_share_pct`: distribución de la LN del perfil por edad o sexo. No es distribución de quienes votaron ni tasa de participación de esas categorías. |
| Contexto territorial | Distribución de LN por entidad dentro de cada perfil, recalculada desde `assignments.csv` y comparada con el conjunto elegible. No son tasas estatales ni proporciones del perfil dentro de cada entidad; presencia no equivale a concentración. |
| Tipo de sección | U/M/R se incorpora como descriptor desde el cruce de perfiles fijos: composición dentro del perfil, participación, NS y comparación de composición. No modifica distancias ni asignaciones; la estandarización tiene referencia propia por perfil. |
| Calidad y soporte | `unspecified_pct` mide NS/LN; la retención de D=SV+NV en soporte común no implica que toda la LN tenga estatus conocido. Distinguir restricción del soporte y reponderación, especialmente en P02. |
| Precisión | Porcentajes con un decimal, redondeo de mitades hacia arriba. No se ajustan sumas a 100% ni se reconstruyen conteos desde valores redondeados. |
| Explicaciones no demostradas | Señala lo que no puede concluirse de estos datos; no presenta hipótesis concretas como si ya se hubieran formulado o validado. Las posibles explicaciones de T10 deben identificarse como hipótesis por validar. |

Durante la revisión conjunta se acordaron nombres descriptivos de la participación
observada, sin etiquetas demográficas ni atribuciones de actitudes:

| Perfil | Nombre acordado |
| --- | --- |
| P01 | Menor participación observada |
| P02 | Participación observada intermedia-baja |
| P03 | Participación observada intermedia |
| P04 | Participación observada intermedia-alta |
| P05 | Mayor participación observada |

Los cinco bloques individuales ya reúnen sus fuentes, tamaño, participación,
edad, sexo, presencia territorial, composición U/M/R, tasas por tipo, comparación
de composición, NS y límites. Cada uno cita `profiles.csv`, `assignments.csv`,
`cross.csv` y el informe del cruce, con sus campos o papel de procedencia.
Las tablas compartidas se mantienen como soporte comparativo, no como sustituto
de esa narrativa. No se infieren proporciones conjuntas desde marginales ni se
considera distintiva una mayoría urbana sin contrastarla con el conjunto elegible.

El borrador abre ahora con dos tablas comparativas de las mismas dimensiones
para P01–P05 y una síntesis descriptiva al inicio de cada bloque. La primera
tabla compara tamaño, participación conocida, banda de edad más numerosa,
composición por sexo, presencia territorial y NS; la segunda, composición y
amplitudes U/M/R. Las cifras detalladas permanecen fuera de esta guía.
Se explicitan diferencias de los resultados existentes, sin cambiar nombres,
asignaciones o distancias ni presentar la caracterización posterior como un
descubrimiento de tipos individuales o causas.

Edad, sexo, entidad y tipo de sección **no entraron en las distancias del modelo**. La ampliación
descriptiva del 25 de octubre incorpora composición por edad y sexo, comparación
con el conjunto elegible, distribución territorial y tipo de sección por perfil. Las cifras
detalladas permanecen en el borrador interno, no en esta guía ni en el paquete
reducido. No se añaden cruces de edad y sexo, rankings de participación territorial,
escolaridad ni características no observadas. Los grupos excluidos no se
interpretan como participación cero; la categoría no binaria no queda
caracterizada por esta solución elegible.

Las [16 variables disponibles](data-audit.md#matriz-de-variables) no son 16
características de distancia. El proceso comprueba su esquema y consistencia,
pero T06 suma los conteos por entidad × sexo × banda de edad. Municipio, sección,
tipo de sección y distritos se validan en las fuentes, sin conservarlos como
dimensiones en esa tabla. El tipo de sección ya se recuperó de los originales
mediante el [cruce P01–P05 con U/M/R](profile-section-cross.md) y se incorporó al
borrador como descriptor. Municipio y distritos siguen sin analizarse; requerirían
otra agregación, no inferirlos a partir de los perfiles actuales.

## Tratamiento de los puntos de cuidado

| Punto | Tratamiento en T09 | Pendiente antes de compartir |
| --- | --- | --- |
| El paquete reducido no tiene composición | Consultar la fuente interna y mantener esas descripciones en `outputs/`, sin copiar composiciones a esta guía ni modificar el paquete reducido. | Evaluar qué descripciones y precisión pueden incorporarse a cada material externo. |
| Riesgo de estigma o inferencia individual | Usar nombres relativos a la participación observada; describir LN y grupos, no supuestas actitudes de personas. | Revisar también títulos, iconografía y mensajes de las fichas y presentación. |
| Confusión entre correlación y causa | Separar observaciones de hipótesis; no atribuir diferencias a edad, desinterés, acceso u otros motivos sin evidencia. | En T10, proponer validación de las barreras antes de afirmar que una acción las resolverá. |
| Comparaciones históricas indebidas | Mantener las cinco descripciones en 2024 y añadir un apartado histórico separado con las dos referencias T08, sin mezclar series. | No presentar permanencia individual, cohortes ni equivalencia entre series. |
| Reconstrucción con otros materiales | No añadir conteos exactos, claves, asignaciones, extremos ni anexos internos al borrador narrativo. El redondeo no certifica anonimato. | Revisar conjuntamente narrativas, tablas, anexos y fuentes auxiliares, no cada archivo por separado. |
| Pérdida del borrador local | Registrar aquí su ubicación y fuentes. La rama no transporta `outputs/`; el documento debe conservarse en almacenamiento interno controlado. | Acordar custodia y acceso antes de trabajar desde otro equipo; no forzar su incorporación a Git. |

La [revisión de divulgación](disclosure-review.md#alcance-y-decisiones-pendientes)
mantiene pendientes los destinatarios, canales, contenido exacto, condiciones de
uso, atribución y cesión. El envío al concurso también es una forma de compartir;
la frontera no se limita a publicar una web o un repositorio. La revisión de la
versión final en T14–T15 no autoriza compartir borradores detallados antes.

## Contexto histórico incorporado al borrador interno

El apartado histórico se redacta antes del cierre de T09, como complemento
acordado durante la revisión conjunta, no como un requisito originalmente
explícito del tablero. Contiene:

- Distribución de LN elegible en cinco bandas fijas para 2012/2018/2024, con
  referencia 2024, y otra tabla independiente para 2009/2015/2021, con referencia 2021.
- Los seis pares dentro de sus series: cambio medio de participación por clave
  común, correlación de rangos y porcentaje de claves comunes en la misma banda.
- Interpretaciones descriptivas, denominadores y límites de cobertura, composición,
  geografía, inferencia causal y comparación retrospectiva.

Las tablas usan únicamente los campos ya reducidos, sin incorporar composiciones
demográficas históricas, conteos exactos ni asignaciones. Se consultan estos
archivos de `outputs/t08_disclosure_summary/`:

| Insumo | SHA-256 registrado en su manifiesto |
| --- | --- |
| `historical_reference.csv` | `e7ffa4cbfccd1c5896e859e3012e810bb765ec85fcf55ccd583a827cf58e43d0` |
| `historical_comparison.csv` | `7dd7bac77e0caac2d639629a5b443b46aa1f00463cd374931ebd5137b09c73a1` |

El manifiesto conserva `draft_pending_review` y `publication_authorized: false`;
su `source_report_sha256` corresponde al informe final T08 registrado arriba.
T11 integrará la versión revisada para sus destinatarios. Ni añadir esta sección
ni usar el paquete reducido autoriza difusión, cierra automáticamente T09 o inicia T10.

## Comprobación antes de T10

El cierre interno se apoya en estas comprobaciones:

- Existen cinco descripciones y cada identificador aparece una sola vez como perfil.
- Tamaño y participación coinciden con T08 al redondear, y la composición coincide
  con su campo de origen; todos los porcentajes tienen denominador explícito.
- Se conservan nombres descriptivos, sin inferencias individuales, causales o predictivas.
- No se presentan barreras, preferencias o impactos como hechos demostrados.
- Se indica el carácter interno y la revisión de divulgación pendiente.
- Las tablas históricas coinciden con sus fuentes y distinguen porcentajes de LN,
  porcentajes de claves comunes y cambios medios no ponderados por población;
  las referencias permanecen separadas y no representan trayectorias personales.

Cumplir estas comprobaciones permite usar el borrador como insumo interno de
T10, **no cerrar la aprobación de difusión**. T11–T13 integrarán solo la versión
que corresponda a sus destinatarios y revisión.

### Cierre interno de T09

T09 se registra como **Completada** en el [tablero](tablero-de-tareas-hackathon.md)
con las cinco descripciones de 2024 y el contexto histórico separado como evidencia
interna. Por indicación expresa de dejarla sin nombre, el campo Responsable conserva
**Por asignar** para esta tarea; no se modifica la regla general del tablero.

El cierre no autoriza publicación ni envío externo, no cambia el estado pendiente
de revisión de divulgación del material y no inicia T10. El texto completo sigue
excluido de Git en `outputs/t09_profiles_narrative/README.md`; la rama solo conserva
la guía y las referencias, no ese archivo local.

### Revisión interna registrada — 23 de octubre de 2026

- Cotejo automatizado puntual aprobado: cinco identificadores, **30 porcentajes**
  redondeados contra la fuente, tasas recalculadas con SV/NV y proporciones de LN.
- Integridad aprobada: ocho hashes de artefactos y la huella del informe T08;
  **31 enlaces locales** existentes y borrador interno ignorado y no versionado.
- Lectura realizada: cada perfil separa observación, límite e hipótesis; los nombres
  no atribuyen actitudes, causas, valor moral ni comportamiento futuro.
- El primer cotejo temporal falló por la expresión regular que separaba secciones;
  se corrigió el verificador y aprobó, sin cambios en las cifras del borrador.
  `Get-FileHash` no estaba disponible; se usó `certutil` y SHA-256 en Python.
- No aplica RED/GREEN ni suite de modelos: son cambios documentales, no de lógica.
  Esta revisión no constituye una evaluación de anonimato ni aprobación externa.

### Verificación del complemento histórico

- Cotejo aprobado de las **48 cifras** en las tablas: 30 proporciones de LN y
  18 indicadores por pares, contra los resúmenes reducidos y los campos originales
  de T08, con la precisión documentada.
- Se conservaron los **30 porcentajes** de las descripciones centrales y los cinco
  nombres y apartados acordados. No se añadieron perfiles finales de otros años.
- Coincidieron **13 hashes de artefactos**: ocho internos T08 y cinco reducidos,
  además del vínculo del manifiesto reducido con el informe final T08.
- Los **32 enlaces locales** existen; el borrador completo permanece ignorado y
  no versionado. Lectura realizada de series separadas, denominadores y límites.
- No se modificaron las fuentes ni se ejecutaron modelos o suites de análisis;
  corresponde verificación numérica y estructural de documentación pasiva.

## Conservación y siguiente paso

### Ampliación descriptiva comprobada

- Se incorporaron al borrador interno **219 celdas numéricas** cotejadas desde las
  asignaciones: 192 proporciones territoriales, 12 proporciones por sexo y 15
  valores de composición por edad, referencia y diferencia; además, seis conteos
  de presencia territorial. Los porcentajes y diferencias usan un decimal y
  redondeo de mitades hacia arriba, sin ajustar sumas.
- Los cinco bloques narrativos originales y el apartado histórico conservaron
  su contenido, comprobado mediante huellas antes y después de la ampliación.
  No se cambiaron los nombres ni los 30 porcentajes centrales o las 48 cifras
  históricas previamente comprobadas.
- Coincidieron los ocho hashes de artefactos T08 y la huella del informe final.
  Se verificó también el informe T06 de 2024 registrado y el ZIP original de ese
  año; `EDONOM` se usa solo para etiquetar las 32 entidades en el borrador interno.
- No se recalcularon modelos, secciones ni municipios. La comprobación numérica
  y estructural sustituye RED/GREEN y una suite funcional que no corresponde a
  esta ampliación documental. No se declara cumplimiento total del reto ni
  autorización de divulgación; la brecha del alcance general de T10 permanece.

### Integración de TIPOSEC comprobada

Por aprobación expresa, el tipo de sección se integró a la caracterización,
manteniendo el modelo actual. Se cotejaron **90 celdas numéricas** nuevas con
`cross.csv` y su informe, con un decimal y redondeo de mitades hacia arriba.
Se conservaron las tablas anteriores, los cinco bloques narrativos originales
y todo el apartado histórico mediante comparación de huellas de contenido.

Los artefactos de cálculo T08 y de ambos diagnósticos conservaron sus hashes.
El borrador T09 sí se actualizó deliberadamente en esta integración: no debe
confundirse con la garantía de preservación registrada durante el cruce anterior.
No se modificaron scripts ni se repitieron modelos o suites funcionales; son
controles numéricos y estructurales de documentación. No se aprueba divulgación
ni se declara cerrada T10.

### Consolidación de las cinco narrativas — 25 de octubre de 2026

Por autorización expresa se reescribieron los bloques P01–P05 para que cada uno
reúna la caracterización y sus fuentes. A diferencia de las ampliaciones previas,
esta consolidación sí cambia esos bloques; conserva sus nombres, identificadores
y los **30 porcentajes centrales** originales de tamaño, participación y edad.

Se cotejaron además **95 descriptores numéricos** integrados desde T08 y el cruce,
y la referencia urbana del conjunto elegible. Las tablas existentes conservaron
su contenido y el apartado histórico mantuvo su huella. Los ocho artefactos T08,
los dos diagnósticos y sus informes conservaron las correspondencias SHA-256.
Se comprobaron diez enlaces locales y sus fragmentos; el borrador sigue ignorado
y no versionado. Son cambios documentales: no se modificaron scripts, modelos,
asignaciones o condiciones de divulgación ni se repitió una suite funcional.

### Presentación comparativa comprobada

Se añadieron dos tablas de lectura común y cinco síntesis descriptivas para
mostrar qué distingue a cada perfil dentro de la solución existente. Se cotejaron
**55 celdas numéricas** desde T08 y el cruce, con un decimal y redondeo de mitades
hacia arriba. El detalle de cada bloque conservó su huella al excluir únicamente
la nueva síntesis; las tablas anteriores y el contexto histórico no cambiaron.
Los informes y artefactos de cálculo mantuvieron sus hashes y se verificaron
diez enlaces locales y sus fragmentos. No se cambiaron nombres, asignaciones,
scripts o modelos ni se repitió una suite funcional para esta presentación
documental. El borrador sigue interno, ignorado y sin autorización de divulgación.

### Conservación del texto consolidado

El borrador local no es un archivo generado por un comando nuevo: se redactó a
partir de las cinco filas T08 y de los dos resúmenes históricos identificados.
La ampliación utiliza además las asignaciones de 2024 y las etiquetas del ZIP
original, con la trazabilidad indicada en el borrador. Si cambian las fuentes,
sus hashes o los manifiestos, revisar las descripciones y el contexto
antes de reutilizarlos. No hay cambios de código que requieran una suite funcional;
corresponden cotejo numérico, lectura estructural y revisión de lenguaje.
