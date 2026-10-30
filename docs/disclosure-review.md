# Revisión de divulgación — borrador separado de T08

Se prepara una **vista reducida, pendiente de revisión final**, sin modificar la
evidencia interna ni autorizar una publicación. Sirve de base numérica para
T09–T13; no sustituye la revisión conjunta de los documentos, fichas y presentación
en T14–T15. T08 conserva su cierre y sus archivos originales.

## Generar el borrador

```powershell
docker compose run --rm --pull never analysis python -B scripts/prepare_disclosure_summary.py
```

Requiere el paquete interno `outputs/t08_profiles_final/`. Genera una carpeta
nueva `outputs/t08_disclosure_summary/`, ignorada por Git. `--input` permite otro
paquete T08 dentro de `outputs`; `--run-name` permite otro destino nuevo dentro
de `outputs`, sin sobrescribir. `--root` admite pruebas aisladas. Consulte `--help`.
No descarga fuentes, reajusta modelos, modifica T08 ni habilita publicación.

## Resultado de la revisión preliminar

La revisión se efectuó sobre el commit T08 `24ce422` y sus nueve archivos finales.
Un diagnóstico local de solo lectura confirmó los siguientes riesgos:

- Las exclusiones de 2024 contienen 36 grupos. Se observaron celdas de tamaño
  reducido y casos con resultados conocidos homogéneos. Estos hallazgos motivan
  revisar la divulgación y no constituyen umbrales oficiales de supresión.
- Aunque se eliminen tasas o `exclusions.csv`, las diferencias entre los totales
  de dos escenarios de `t07_evidence.json` permiten recuperar el vector de conteos
  de un grupo excluido. No se reproducen su clave ni sus conteos en esta guía.
- Los conteos exactos y las composiciones de alta precisión permiten reconstruir
  marginales. Esto no demuestra que sus tablas conjuntas o personas sean
  identificables; tampoco basta para certificar anonimato.
- En el índice Git inspeccionado, `data/` y `outputs/` solo contienen como archivos
  rastreados `data/README.md` y `data/sources.json`; las salidas están ignoradas.
  No se auditó todo el historial ni las publicaciones remotas.

Por ello no se copia ningún informe interno completo ni se conserva el conjunto
de consultas alternativas en el borrador externo.

## Contrato de la vista reducida

| Archivo | Filas | Campos conservados |
| --- | ---: | --- |
| `profiles.csv` | 5 | Identificador central, año, participación y proporción de LN elegible |
| `historical_reference.csv` | 30 | Serie, referencia, año, identificador de banda k=5, participación y proporción de LN elegible |
| `annual_metrics.csv` | 36 | Año, método, k y silueta de los candidatos base; sin sensibilidades |
| `historical_comparison.csv` | 6 | Serie, referencia, par de años, cambio medio, correlación de rangos, concordancia de bandas y ARI anual de K-means, para k=5 |
| `manifest.json` | — | Estado, precisión, hashes de procedencia y de los otros cinco archivos, limitaciones y hash del exportador |
| `README.md` | — | Uso, significado, fuente y advertencia de revisión pendiente |

Los porcentajes y cambios en puntos porcentuales usan **un decimal**; los
coeficientes y siluetas, **dos**, con `ROUND_HALF_UP`. No se ajustan las sumas
redondeadas a 100%. La precisión es una decisión de presentación para este
borrador, **no una garantía de confidencialidad ni un criterio aprobado por el INE**.
Las tasas indefinidas se conservan vacías, no como ceros.

La participación es `100 * SV / (SV + NV)`; NS no es abstención. La proporción de
LN usa la población elegible de cada elección. El cambio medio entre años tiene
igual peso por clave agregada común, no es un cambio nacional ponderado por
población. La concordancia de bandas es un porcentaje de grupos, no de personas.

Las referencias son fijas dentro de cada serie: 2024 para 2012/2018/2024 y 2021
para 2009/2015/2021. Mostrar solo k=5 reduce las tabulaciones superpuestas y no
selecciona cinco conglomerados óptimos para cada año. Los 36 candidatos base
conservan los tres valores de k para comparar separación sin exportar membresías.
No se equiparan identificadores entre series ni se interpretan como trayectorias
individuales. Los perfiles centrales siguen limitados a los grupos elegibles de
2024, no caracterizan a los grupos excluidos.

### Campos que no cruzan al borrador

No se exportan LN/SV/NV/NS exactos, claves de entidad/sexo/edad, asignaciones,
exclusiones, tamaños exactos en grupos o entidades, extremos de participación,
centroides, composiciones demográficas ni escenarios de sensibilidad. No se
copian textos libres o columnas desconocidas de la entrada. Los identificadores,
años, métodos y pares se validan contra dominios explícitos; los indicadores
deben ser finitos y estar dentro de rango.

Se verifican el contrato, selección, series, procedencia y los hashes de los ocho
artefactos T08, y se comprueban nuevamente antes de finalizar la carpeta local
completa por renombrado. Esto es integridad local, no una firma del
INE ni una repetición de la validación de modelos. Los hashes no son una medida
de protección estadística. Se conservan los originales internos sin sobrescribir.

## Alcance y decisiones pendientes

El manifiesto siempre declara `status: draft_pending_review` y
`publication_authorized: false`; el comando no ofrece una opción para aprobarlo.
Una lista explícita de campos evita copiar los detalles detectados, pero el
redondeo no demuestra que no pueda reconstruirse información con otras fuentes.
La plataforma oficial ya publica los originales: esta vista evita amplificar
detalle innecesario, no convierte los datos públicos en secretos.

Antes de difundir deben resolverse:

1. Los destinatarios y canales concretos, y la lista exacta de archivos de cada entrega.
2. Las condiciones de uso, atribución y cesión de derechos aplicables. La
   [convocatoria](convocatoria-hackaton.pdf), páginas 3–4, requiere datos agregados,
   sin datos personales, y los entregables del Reto 1, no expresamente los nueve
   archivos internos. Su página 6 contempla cesión por diez años y difusión con
   fines institucionales o educativos; no se presume una licencia pública a partir
   de esta revisión técnica. Debe comprobarse también la carta aplicable.
3. La combinación con tablas, narrativas, composiciones y anexos de T09–T13,
   publicaciones anteriores y fuentes auxiliares; ninguna descripción nueva se
   aprueba automáticamente por usar este paquete.
4. La decisión responsable sobre la versión final en T14–T15. No existe una
   aprobación institucional ni una certificación de anonimato por generar el borrador.

Las cartas administrativas, firmas, credenciales y datos bancarios del equipo
permanecen fuera del repositorio público y se manejan por el canal oficial que
corresponda; no forman parte de esta vista analítica.

## Comprobaciones

```powershell
docker compose run --rm --pull never analysis python -B -m unittest discover -s tests -p test_disclosure_summary.py -v
docker compose run --rm --pull never analysis python -B -m unittest discover -s tests -v
```

Se observó RED al no existir el comando y GREEN con las cinco pruebas focalizadas
(91.008 s). Cubren columnas permitidas, precisión, seis elecciones, referencias
separadas, estado no autorizado, hashes, rechazo de entradas incompatibles,
ausencia de filtración de textos adicionales, repetibilidad y no sobrescritura.
La suite completa ejecutó **56 pruebas: 55 aprobadas y una omitida**, sin fallos
ni errores (614.557 s). La omitida es la comprobación opcional de persistencia
Docker desde el anfitrión; su motivo fue `Prueba opcional de persistencia desde
el equipo anfitrión; requiere la imagen local construida`.

Las ejecuciones reales `outputs/t08_disclosure_summary/` y
`outputs/t08_disclosure_repeat/` generaron los seis archivos idénticos byte a byte,
con cinco perfiles, seis elecciones, 30 bandas-año de referencia, 36 candidatos
base y seis comparaciones k=5. Ambas conservaron el estado de borrador y la
publicación no autorizada.

La verificación independiente de los controles de divulgación no encontró
bloqueos: confirmó el contrato de campos, cantidades y series, la precisión,
el estado no autorizado, la integridad y los rechazos sin cambios de entrada ni
salidas parciales. En una copia temporal aislada ejecutó las cinco pruebas
focalizadas (91.655 s) y comprobaciones adicionales de columnas y textos
inyectados, rangos, redondeo, dominios, integridad y compatibilidad de las seis
CLI existentes. Esto verifica el funcionamiento del borrador, no su anonimato
ni una aprobación para difundirlo.

## Constancia de revisión preliminar de materiales — 2026-10-28

**Resultado: sin hallazgos en los controles descritos; divulgación final
pendiente.** Esta constancia identifica versiones y comprobaciones concretas.
No certifica anonimato, no constituye aprobación institucional y no autoriza
automáticamente el envío al concurso ni la publicación en GitHub.

### Alcance y versiones

Los canales declarados por el equipo son la entrega por correo al INE y un
repositorio público de GitHub. La posible web no está desplegada y la
presentación todavía no está elaborada. Esta revisión preliminar cubre los
materiales existentes, no esos productos futuros ni todo el historial público.

| Material comprobado | Versión local |
| --- | --- |
| Informe candidato de ocho páginas | `docs/documento-tecnico (2).pdf` |
| Cinco fichas PDF, cinco PNG y cuaderno PDF de cinco páginas | `outputs/t12_profile_cards/`, perfiles P01–P05 |
| Procedencia de las fichas | `outputs/t12_profile_cards/report.json`, con hashes de entradas y artefactos |

Identificadores SHA-256 comprobados:

- Informe candidato: `047606b495ac124e8a47d17c95413c491cb24057d176b3d78286f23cf05c50db`.
- `report.json` de las fichas: `661ed886f1a2ad19d46372b2a6014c5b30c8cfe1951463bc639b87748ad152d3`.

Los 19 archivos de la carpeta de fichas permanecieron sin cambios durante la
inspección. El informe candidato aún no sustituye al PDF anterior versionado;
no debe confundirse la comprobación del candidato con la de esa versión anterior.

### Controles completados

- **Contenido revisado:** tamaños de LN aproximados y porcentajes conservados;
  omisión de nombres de integrantes en el informe candidato; advertencias sobre
  agregación, inferencia individual e hipótesis no evaluadas. Se generalizaron
  los desgloses accesorios de grupos pequeños y el total retirado en la prueba
  de edades extremas, conservando sus conclusiones metodológicas.
- **Metadatos de fichas y cuaderno:** los seis PDF tienen el campo de autor vacío,
  sin XMP, adjuntos, anotaciones ni formularios. No se observaron acciones de
  apertura, entradas JavaScript del catálogo ni acciones adicionales de página
  en las claves inspeccionadas.
- **PNG:** las cinco imágenes conservan 2550 × 3300 píxeles y 300 dpi. No
  contienen bloques `tEXt`, `zTXt`, `iTXt` ni `eXIf`; sus comprobaciones CRC son
  válidas.
- **Integridad y coherencia:** los hashes de artefactos coinciden con el
  manifiesto y los hashes de entrada corresponden a los archivos de perfiles y
  cruce utilizados. Los tamaños aproximados, pesos de LN, participación y NS
  coinciden para los cinco perfiles entre las fichas, el informe candidato y
  las entradas validadas. Este cotejo no sustituye recalcular los modelos.

Estos resultados se limitan a los archivos y elementos inspeccionados. No son
una garantía universal de ausencia de contenido oculto ni de inferencias al
combinar otras fuentes. Los datos originales del INE siguen siendo públicos.

### Pendientes para el cierre conjunto

1. Elaborar la presentación y revisar su coherencia con el informe, las fichas
   y cualquier anexo; cerrar la lista exacta de archivos y enlaces de la entrega.
2. Completar T14 desde los datos originales en un entorno limpio. Las pruebas
   del análisis y la exportación comprobada en Docker no sustituyen ese recorrido.
3. Resolver las condiciones de publicación y cesión aplicables. Se leyó el
   formato de carta, que declara obra original e inédita y cesión patrimonial por
   diez años; no se confirmó con el INE su interpretación respecto del repositorio
   público. La aceptación de términos por el equipo no constituye por sí sola
   esa aclaración, ni esta observación demuestra un incumplimiento.
4. Completar y firmar las cartas al concluir el trabajo, según lo indicado por
   el equipo, y mantener las versiones cumplimentadas fuera del repositorio público.
5. Sustituir el PDF anterior por la versión final cuando el equipo lo decida;
   actualizar la referencia y volver a comprobar cualquier archivo cuyo contenido
   cambie. Las correcciones actuales no eliminan versiones previas del historial.
6. Registrar la decisión responsable sobre la versión y los canales definitivos
    en T15. La revisión preliminar no cambia `publication_authorized: false` ni
    aprueba automáticamente materiales nuevos, una web futura o usos distintos.

## Integración T15

**Estado: revisión técnica e integración completadas, con observación de derechos
sin resolver; este cierre no autoriza divulgación ni envío.**
Esta sección actualiza el estado de trabajo sin modificar la constancia histórica
del 28 de octubre. La presentación ya existe y T14 está completada con la prueba
no ejecutada documentada en [su constancia](t14-reproducibility.md).

### Selección del equipo

El equipo indicó: «En un ZIP vamos a entregar lo siguiente: Documento tecnico,
Fichas de perfil, presentación ejecutiva, enlace del repositorio carta de cesión
de derechos, carta de declaración de decir la verdad».

| Componente seleccionado | Material local o referencia | Estado |
| --- | --- | --- |
| Documento técnico | `docs/documento-tecnico.pdf` | Misma versión de ocho páginas revisada en T14 |
| Fichas de los cinco perfiles | `outputs/t12_profile_cards/ficha_P01` a `ficha_P05`, en PDF y PNG | Integridad comprobada contra el manifiesto revisado; PDF de una página y PNG de 2550 × 3300 a 300 dpi según la revisión previa |
| Presentación ejecutiva | `docs/presentacion-reto1-ine.pdf` | Misma versión de diez diapositivas revisada en T14; archivo local sin seguimiento en Git |
| Enlace al repositorio | `https://github.com/Daavid-Anaya/hackathon-ine` | Acceso público sin autenticación comprobado a la página, un archivo de código y guía de ejecución de `main`; ver alcance más abajo |
| Carta de cesión de derechos | Documento administrativo privado | El equipo confirmó que está completo y firmado por todas las personas integrantes; sin inspección independiente |
| Carta declaratoria de decir verdad | Documento administrativo privado | El equipo confirmó que está completo y firmado por todas las personas integrantes; sin inspección independiente |

Las cartas se mantienen fuera del repositorio público. El enlace sustituye la
inclusión del código fuente como archivos en el ZIP. No se seleccionaron datos
originales, salidas analíticas detalladas, HTML intermedios, copias anteriores
ni archivos temporales de verificación. No se creó todavía el ZIP: su montaje,
comprobación de cartas adjuntas e integridad corresponden a T16.

### Comprobación local de versiones

Se recalcularon los SHA-256 y coincidieron con las versiones ya revisadas:

| Archivo | Bytes | SHA-256 |
| --- | ---: | --- |
| `docs/documento-tecnico.pdf` | 95.474 | `92dde8e2eb526fcde4470926d229c2ca5633322c7bd914ba2aa1a3b338dab140` |
| `docs/presentacion-reto1-ine.pdf` | 4.998.699 | `a5f40452ddac91e515c253548838cca52614ec6de29375bf474bfc40a8d8aede` |
| `outputs/t12_profile_cards/report.json` | 2.982 | `661ed886f1a2ad19d46372b2a6014c5b30c8cfe1951463bc639b87748ad152d3` |

Los **17 artefactos** enumerados en `report.json` coinciden con sus hashes;
también coinciden las **dos entradas**, `profiles.csv` y `cross.csv`. La igualdad
binaria permite conservar la evidencia previa de legibilidad, geometría,
coherencia y controles acotados de metadatos para esas mismas versiones. No se
repitieron los modelos, la inspección visual ni el análisis de metadatos; no se
atribuye una nueva certificación de anonimato ni se da por aprobada la prueba
omitida en T14.

### Acceso público al repositorio

Con autorización expresa del equipo, se comprobaron mediante consultas web
públicas, sin iniciar sesión ni usar credenciales:

| Recurso | Resultado |
| --- | --- |
| [Repositorio](https://github.com/Daavid-Anaya/hackathon-ine) | Página legible, identificada como pública, con README y listado de código de `main` |
| [Archivo de código](https://raw.githubusercontent.com/Daavid-Anaya/hackathon-ine/refs/heads/main/scripts/check_environment.py) | Contenido accesible de `scripts/check_environment.py` |
| [Guía de ejecución](https://raw.githubusercontent.com/Daavid-Anaya/hackathon-ine/refs/heads/main/docs/local-setup.md) | Instrucciones Docker y de reproducción accesibles |

Esto acredita lectura pública en el momento de la comprobación, no una clonación,
descarga completa ni ejecución desde una copia remota.

### Cotejo final y cierre técnico

Se completó el cotejo de los entregables seleccionados y la rúbrica, sin nuevos
bloqueos técnicos concretos en el alcance inspeccionado:

| Criterio oficial | Evidencia |
| --- | --- |
| Apego a la temática — 35 puntos | Informe pp. 1–5: CCPC, método y cinco perfiles; pp. 5–7: estrategias. Presentación, diapositivas 1–8; fichas P01–P05 |
| Claridad y solidez — 30 puntos | Informe pp. 2–3 y 7–8: denominadores, comparación, límites y referencias. Presentación, diapositivas 4–6 y 10; reproducción T14 |
| Originalidad y creatividad — 20 puntos | Informe pp. 5–7 y presentación, diapositivas 7–9: propuestas E01–E05, canales e indicadores; síntesis visual en fichas |
| Viabilidad institucional — 15 puntos | Informe pp. 5–7: requerimientos y medidas de servicio; presentación, diapositivas 7–10: validación, pilotaje, evaluación y salvaguardas |

Los pesos corresponden a la rúbrica, pp. 1–3. El potencial de aplicación adicional
que menciona la convocatoria se contempla cualitativamente, sin inventar una
quinta ponderación ni asignar una calificación. Las nueve métricas de comparación,
las cinco tasas de participación y los cinco pesos de LN cotejados entre informe
y presentación coinciden; la ficha P01 también concilia con el informe. Para las
demás fichas se conserva la evidencia previa mediante los hashes verificados,
sin atribuir una nueva inspección visual completa ni nuevas mediciones de fuente
o interlineado. No se observaron impactos causales o de participación presentados
como demostrados en los contenidos inspeccionados.

Por instrucción del equipo —«Sino hay más que checa deja cerrada la T15»— se cierra
**T15 como revisión técnica e integración**. Se conserva la presentación sin
cambios. La compatibilidad de los recursos de Canva con la cesión y la condición
de obra inédita frente al repositorio público siguen sin confirmación; el cierre
no certifica cumplimiento jurídico ni aprobación institucional. Los avisos de
borrador interno y `internal_only: true` no se modifican y se mantiene
`publication_authorized: false`.

Las cartas están completas y firmadas según el equipo, sin inspección independiente.
No se repitió T14 ni su prueba de persistencia omitida. T16 queda pendiente para
montar y abrir el ZIP, comprobar las cartas efectivamente adjuntas, versiones y
enlaces; T17 corresponde al envío. No se creó el ZIP ni se enviaron materiales.
