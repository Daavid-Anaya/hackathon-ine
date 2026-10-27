# Diagnóstico urbano–mixto–rural de 2024

**Evidencia interna, pendiente de revisión de divulgación. No autoriza publicación
ni envío externo.** El diagnóstico encuentra diferencias descriptivas entre tipos
de sección y examina su composición, sin modificar los cinco perfiles T08 ni
atribuir efectos causales. No es una segmentación municipal ni una estrategia de
comunicación dirigida a grupos demográficos.

## Ejecución reproducible

Desde la raíz del proyecto, con la imagen local ya disponible:

```powershell
docker compose run --rm --pull never analysis python -B scripts/diagnose_section_types.py
```

Requiere el ZIP original de 2024 y `data/processed/ccpc_all/2024/{table.csv,report.json}`.
La fuente debe coincidir en tamaño y SHA-256 con la registrada en T06. El comando
reconcilia cada combinación de entidad, sexo y edad al colapsar el nuevo desglose.
No descarga datos, no ajusta modelos y no escribe sobre T06, T08 o T09.

Genera una carpeta **nueva**, `outputs/section_types_2024/`, excluida de Git:

| Archivo | Contenido |
| --- | --- |
| `summary.csv` | Conteos agregados por tipo, tasas brutas, NS, proporción de LN, soporte común y tasas estandarizadas. |
| `report.json` | Procedencia, hashes, reconciliación, composiciones marginales internas, soporte común, comparaciones y limitaciones. |
| `README.md` | Límites de interpretación y carácter interno. |

Si la carpeta existe, el comando falla sin sobrescribirla. Para repetir, elegir
otro nombre, por ejemplo `--run-name section_types_2024_repeat`.
`--chunk-size 200000` controla las filas por bloque, no una muestra ni un filtro.
`--root RUTA` permite trabajar con datos sintéticos aislados; `--help` describe las
opciones. Las tablas detalladas y composiciones del informe no deben trasladarse
automáticamente a fichas, presentación o repositorios públicos.

## Qué se compara y por qué

1. **Reconstrucción de la dimensión territorial:** sumar LN/SV/NV/NS por entidad ×
   tipo de sección × sexo × banda de edad desde las fuentes originales. Mantener
   U, M y R separados; no tratar M como un punto medio numérico.
2. **Tasas brutas:** calcular `100 × ΣSV/(ΣSV+ΣNV)` después de sumar conteos.
   Acompañarlas con `100 × ΣNS/ΣLN`: desconocer participación no es abstención.
3. **Soporte común:** conservar para la comparación estandarizada únicamente las
   combinaciones entidad–sexo–edad presentes en los tres tipos con D>=30 y
   cobertura conocida>=80%, donde D=SV+NV. Son heurísticas exploratorias, no reglas
   oficiales de divulgación. No completar combinaciones ausentes con ceros.
4. **Estandarización:** aplicar a U, M y R los mismos pesos de composición. Para
   cada estrato común h, `w_h = (D_Uh+D_Mh+D_Rh)/Σ_h(D_Uh+D_Mh+D_Rh)` y
   `tasa_estandarizada_t = Σ_h w_h × tasa_th`. Así se compara cada tipo con una
   estructura de referencia común de entidad, sexo y edad.

Se informa también la tasa bruta dentro del soporte común. Esto distingue el
cambio de población comparada del cambio de pesos; no debe atribuirse toda
diferencia entre la tasa bruta original y la estandarizada a la composición.

## Resultados observados

Se procesaron **9.773.730 filas de 2024** y se reconciliaron los conteos con T06.
La comparación conjunta cuenta con **319 estratos comunes**. Las cifras siguientes
se muestran con dos decimales; la evidencia local conserva la precisión de cálculo.

| Indicador (%) | Urbana | Mixta | Rural |
| --- | ---: | ---: | ---: |
| Proporción de LN total | 69.45 | 13.04 | 17.51 |
| Participación bruta entre registros conocidos | 59.88 | 57.94 | 60.11 |
| Participación no especificada: NS/LN | 6.20 | 6.45 | 7.36 |
| Denominador conocido conservado en soporte común | 99.63 | 99.83 | 99.83 |
| Participación bruta en soporte común | 59.93 | 57.96 | 60.13 |
| Participación estandarizada en soporte común | 59.51 | 58.56 | 60.08 |

**Lectura descriptiva:**

- La tasa rural no resulta inferior a la urbana en estos resúmenes de participación
  conocida. Eso no permite afirmar que todas las secciones rurales participen más.
- La diferencia urbana–mixta pasa de aproximadamente **1.97 pp** en el soporte
  común a **0.95 pp** con pesos comunes: la comparación es sensible a la composición.
- La dirección no es uniforme: en 203 de los 319 estratos la tasa urbana supera
  a la mixta, y en 116 ocurre lo contrario. La rural supera a la urbana en 193,
  frente a 126 con la relación contraria. Son conteos de estratos, no de personas
  ni porcentajes ponderados por población.
- La no especificación es mayor en el agregado rural. Los resultados no permiten
  conocer la participación de los registros NS ni suponer que sea igual a la de
  los registros conocidos.

## Alcance y siguiente decisión

Este resultado demuestra que `TIPOSEC` aporta una dimensión descriptiva que la
tabla T06 original no conservaba, no que deba entrar automáticamente en las
distancias del modelo. Este diagnóstico general no describe por sí solo la
distribución de P01–P05 por tipo; el [cruce complementario de perfiles fijos](profile-section-cross.md)
desarrolla esa comparación separadamente, conservando los resultados originales.

No se evaluaron diferencias municipales ni comparabilidad histórica urbano-rural.
La estandarización no controla variables ausentes y no identifica causas. Los
grupos sin elegibilidad o soporte común, incluida la categoría no binaria sin
representación suficiente para esa comparación, no quedan caracterizados por
las tasas estandarizadas. La revisión de divulgación sigue pendiente.

## Comprobaciones realizadas

- RED observado antes de implementar; después aprobaron cuatro pruebas sintéticas
  por CLI: separación U/M/R y composición común, repetibilidad y rechazo de
  sobrescritura, rechazo de fuente alterada y tasas desconocidas sin imputación.
- Suite completa en Docker: **60 pruebas, 59 aprobadas y una omitida**, la prueba
  opcional de persistencia desde el anfitrión. No se declara esa prueba ejecutada.
- Ejecución real con salida 0; hashes T08 y del borrador T09 idénticos antes y
  después. Los hashes de los artefactos generados coinciden con el nuevo informe.
- No se modificaron los helpers compartidos ni los comandos existentes; no
  corresponde un diferencial de comportamiento de un parser o helper modificado.

Fuentes metodológicas: [auditoría de variables y denominadores](data-audit.md),
[entorno local](local-setup.md) y [selección T08 conservada](profile-selection.md).
