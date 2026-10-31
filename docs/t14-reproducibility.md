# T14 · Reproducción integral y revisión de materiales

**2026-10-29 · Estado: completada, con una prueba de persistencia no ejecutada y documentada.**
El análisis se ejecutó desde los originales en contenedores nuevos y sin red,
sin sobrescribir resultados existentes. Esta constancia no autoriza divulgación
ni sustituye la integración final de T15.

## Resultado

| Comprobación | Evidencia observada |
| --- | --- |
| Originales y resultados existentes | 159 archivos protegidos, 309.382.190 bytes; SHA-256 sin cambios antes y después de reproducir |
| Limpieza de seis elecciones | 54.872.712 filas, 192 CSV de origen, 1.956 grupos; cero exclusiones y conciliaciones aprobadas |
| Segmentación | Seis candidatos de 2024; 36 candidatos históricos, seis referencias y 18 pares |
| Perfiles seleccionados | Cinco perfiles; 320 asignaciones centrales y 5.754 históricas |
| Cruce por tipo de sección | 15 filas y conciliación exacta de conteos |
| Resumen reducido | Cinco perfiles, 30 referencias, 36 métricas y seis pares; `publication_authorized: false` |
| Reproducibilidad numérica | 51 comparaciones de CSV idénticas byte a byte; sin tolerancia numérica utilizada |
| Pruebas | 77 pruebas distintas aprobadas entre los entornos complementarios; una prueba de persistencia no ejecutada |
| Comparación adicional | 117 controles de agregados/artefactos y 34 controles de PDF/PNG aprobados |

La reproducción no modificó código, originales ni resultados previos.

## Entorno e aislamiento

- Referencia de código: `b2122f74d77681c64efd49a6e6e1fdcb6762d8d8`.
- Host Windows; Docker Server 29.9.2 y Compose v5.6.1, contexto local
  `desktop-linux`, imágenes Linux/amd64 ya disponibles. No se reconstruyeron
  imágenes ni se instalaron o descargaron dependencias.
- Análisis: Python 3.12.10, Pandas 3.0.6, Scikit-learn 1.9.1 y NumPy 2.5.4;
  `check_environment.py` y `pip check` finalizaron correctamente.
- Imagen de análisis: `sha256:61e1e39d37f62116110e5f352aa7e1c9b0d360e2798b6e89b93b3a0d9f6cd1c8`.
- Imagen de exportación: `sha256:40d166183bbe39d1361261eea423123a68e5be70e78456b1fb3a65341f4590c1`;
  PyMuPDF 1.28.0 y navegador de la imagen.

Las dependencias y la construcción de las imágenes están documentadas en
[entorno local](local-setup.md) y [exportación Docker](profile-cards-docker.md).
Esta ejecución verifica una instancia nueva de esas imágenes existentes, no
una reconstrucción de imágenes desde cero.

Se inspeccionaron los montajes efectivos: código, originales y raíz del
contenedor de solo lectura, `network_mode: none` y escrituras exclusivamente
en carpetas temporales externas al repositorio. Las carpetas de datos procesados
y salidas comenzaron vacías. En el exportador también se sustituyeron los dos
montajes anidados de entrada por los resultados recién reproducidos, de solo
lectura; no se reutilizaron los perfiles existentes para generar las fichas.

## Pasos ejecutados

En los comandos siguientes, `P` representa la carpeta temporal de procesados y
`O` la de salidas, ambas externas y vacías al inicio. Los originales se leyeron
desde `data/raw/` conforme al manifiesto; `--inspect` no realiza descargas.

La envoltura de análisis usada para cada fila fue:

```text
docker --context desktop-linux compose run --rm --pull never --no-deps -v "P:/workspace/data/processed" -v "O:/workspace/outputs" analysis python -B <argumentos>
```

| Argumentos, en orden de ejecución | Salida | Segundos |
| --- | --- | ---: |
| `scripts/check_environment.py` | 0 | 6,832 |
| `-m pip check` | 0 | 2,464 |
| `scripts/download_ccpc.py --inspect` | 0 | 5,204 |
| `-m unittest discover -s tests -v` | 0 | 694,409 |
| `scripts/clean_ccpc.py --all-years` | 0 | 1.262,780 |
| `scripts/compare_segments.py` | 0 | 14,029 |
| `scripts/compare_history.py` | 0 | 61,133 |
| `scripts/export_profiles.py --run-name t08_profiles_final` | 0 | 10,622 |
| `scripts/prepare_disclosure_summary.py` | 0 | 5,333 |
| `scripts/cross_profile_section_types.py` | 0 | 213,516 |

El nombre `t08_profiles_final` es explícito: el cruce y el resumen reducido
dependen de esa ruta. La reproducción de T09 consiste en cotejar el texto
redactado con los resultados; no existe un generador de esa narrativa.

La exportación T12 terminó con salida 0 en 11,967 segundos:

```text
docker --context desktop-linux compose --profile profile-cards run --rm --pull never --no-deps -v "O:/workspace/outputs" -v "O/t08_profiles_final:/workspace/outputs/t08_profiles_final:ro" -v "O/profile_section_types_2024:/workspace/outputs/profile_section_types_2024:ro" profile-cards
```

Con esos mismos montajes se ejecutaron en el exportador las suites
`test_generate_profile_cards.py`, `test_docker_profile_cards.py` y
`test_profile_cards_independent_runtime.py`, mediante
`python -B -m unittest discover -s tests -p <archivo> -v`.
Resultados: 9 aprobadas; 2 aprobadas y 2 omitidas de host; 2 aprobadas,
respectivamente. Las dos pruebas de configuración de host se comprobaron
aparte, limitando Docker a `compose --profile profile-cards config --format json`.

### Omisiones e incidencia de ejecución

La suite general aprobó 70 pruebas y omitió ocho por disponibilidad de host o
exportador. Las ejecuciones complementarias cubrieron siete de esas ocho.
El total de 77 corresponde a pruebas distintas, no a la suma de reejecuciones.

Quedó sin ejecutar
`test_docker_persistence.DockerPersistenceTests.test_persistence_and_original_integrity_in_isolated_workspace`:
activa el servicio `download` con red y no se ejecutó bajo esta verificación
local sin red. No se atribuye aprobación a esa prueba. La comprobación directa
de montajes, generación persistida en carpetas temporales y hashes sin cambios
es evidencia separada, no una ejecución de esa prueba.

El primer intento falló antes de crear contenedores porque se indicó
`compose run --no-build`, opción inexistente en esta versión. Se corrigió a
`run --pull never --no-deps`, sin `--build`, y se verificaron nuevamente las
imágenes locales. Los 14 comandos de la ejecución reanudada terminaron con
salida 0. El fallo inicial no se presenta como una prueba aprobada.

## Diferencias respecto de las salidas existentes

De 98 comparaciones de artefactos, 55 fueron idénticas byte a byte, incluidas
las 51 comparaciones de CSV. Las demás diferencias inspeccionadas corresponden a:

- Huellas del código productor y propagación de hashes de informes anteriores.
- 25 textos explicativos distintos traducidos del inglés al español.
- Terminaciones de línea CRLF/LF en HTML y README de T12.
- Fuentes/plataforma, huella del navegador y metadatos/fechas de PDF.

No se observó deriva numérica. No se promete igualdad binaria de los PDF/PNG
entre plataformas. Los cinco PDF individuales y el cuaderno de cinco páginas
mantuvieron texto normalizado y cifras iguales: tamaño carta, texto dentro de
página, mínimo 8,1 puntos; cinco PNG de 2550 × 3300 y 300 dpi. La inspección de
las cinco vistas previas no detectó recortes o superposiciones visibles.
El redondeo de cifras publicadas puede impedir sumas exactas, pero no explica
una variación del análisis: en esta reproducción no hubo tal variación.

## Privacidad y coherencia de materiales actuales

Se inventariaron 189 archivos sin modificaciones durante la inspección:
161 textos examinados, 14 PDF, diez PNG y doce HTML; estas categorías se
superponen. El alcance incluye código/configuración versionados, materiales
actuales seleccionados y salidas agregadas, no todo el historial ni archivos
ignorados o remotos.

- Sin positivos adicionales en los patrones examinados de credenciales,
  claves privadas, CURP/RFC, identificadores bancarios y teléfonos. Dos
  coincidencias de correo son destinatarios institucionales públicos.
- Informe de ocho páginas y presentación de diez diapositivas renderizables.
  Sin adjuntos, formularios, JavaScript ni acciones adicionales de página en
  los elementos inspeccionados. Los enlaces del informe son de navegación;
  su `OpenAction` establece una vista inicial, no ejecuta código.
- Diez PNG con CRC válidos, dimensiones y resolución esperadas, sin bloques
  textuales/EXIF; doce HTML sin referencias remotas detectadas.
- Coherencia aprobada de los 30 porcentajes centrales de T09, otros 30 de
  composición/NS, tabla de T11 y cifras principales de T13 con los resultados
  reproducidos. Los manifiestos T12 original y reproducido conciliaron sus
  17 hashes de artefactos y entradas.

| Versión inspeccionada | SHA-256 |
| --- | --- |
| `docs/documento-tecnico.pdf` | `92dde8e2eb526fcde4470926d229c2ca5633322c7bd914ba2aa1a3b338dab140` |
| `docs/presentacion-reto1-ine.pdf`, metadatos corregidos | `a5f40452ddac91e515c253548838cca52614ec6de29375bf474bfc40a8d8aede` |
| Copia externa de la presentación anterior | `86f6381caf6daf23f9e8c063911202a32fc640f6e80e8755a93c003ae1005237` |

No se hizo OCR, reconocimiento exhaustivo de nombres ni análisis forense de
objetos PDF eliminados. Convocatoria y rúbrica se inventariaron, pero no se
auditaron sus metadatos. Los controles acotados no certifican anonimato.

## Evidencia local y siguiente paso

Los registros se conservaron fuera del repositorio en el archivo local
`t14-verification-evidence-20261029.zip` del directorio temporal de OpenCode.
Incluye 130 archivos: resúmenes de ejecución/comparación/privacidad,
`presentation_sanitization.json`, inventarios, registros, vistas previas y
sondas. El archivo se abrió nuevamente y se comprobaron CRC y SHA-256 de
cada miembro. SHA-256 del archivo:
`5f18c70ad42636770c9cdb245260450dc4c2742fbca2ed5581039a7f951b7abb`.

La copia del PDF original se conserva por separado como
`t14-presentation-original-86f6381caf6d.pdf` en ese mismo directorio externo.
Las salidas regeneradas y carpetas de trabajo temporales se eliminaron después
de conservar la evidencia. Ni el archivo de evidencia ni el PDF original con
autor forman parte del paquete de entrega; su ubicación temporal no garantiza
conservación permanente.

T14 se cierra con la omisión de prueba explícita indicada anteriormente, sin
atribuir aprobación a esa prueba. T15 conserva la decisión sobre archivos y
canales definitivos, derechos y cartas. Se mantiene
`publication_authorized: false`; esta constancia no modifica esa decisión.
Si se vuelve a exportar o modificar un PDF, se debe comprobar la nueva versión
y actualizar su hash antes de entregar.
