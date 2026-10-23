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

- Las exclusiones de 2024 contienen 36 grupos con LN total de 105; 31 grupos
  tienen LN menor que cinco. En 28, el resultado conocido es homogéneo: SV o NV
  es cero. Estos valores son hallazgos, **no umbrales oficiales de supresión**.
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
