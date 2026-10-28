# hackathon-ine

Hackathon del INE, Reto 1: perfiles de participación ciudadana a partir de datos
agregados y disociados de CCPC. El entorno utiliza Python, Pandas y Scikit-learn.

## Iniciar con Docker (Windows PowerShell)

Inicia Docker Desktop con contenedores Linux y ejecuta desde la raíz del repositorio:

```powershell
docker compose build analysis
docker compose run --rm analysis
```

Ejecuta cada comando solo cuando el anterior termine correctamente. El comando
predeterminado comprueba Python, Pandas y Scikit-learn con datos sintéticos y
después finaliza. Es un entorno de procesamiento por lotes, no un servidor web;
no necesita puertos ni servicios en ejecución permanente. Docker proporciona su
propio entorno de Python 3.12; el uso habitual no requiere Python en el equipo anfitrión.

## Datos y comprobaciones

```powershell
docker compose run --rm analysis python -m unittest discover -s tests -v
docker compose run --rm analysis python scripts/download_ccpc.py --inspect
```

El análisis habitual no tiene acceso a la red y consulta el código y los datos
originales mediante montajes de solo lectura. Los archivos generados se conservan
en `data/processed/` y `outputs/` del equipo anfitrión. `--inspect` requiere las
fuentes descargadas: verifica sus hashes y muestra las descripciones de campos
y el primer encabezado CSV de cada ZIP, no las filas de registros.

Solo cuando sea necesario descargar las fuentes, ejecuta de forma explícita:

```powershell
docker compose --profile download run --rm download
```

Este servicio independiente habilita la red y la escritura en `data/` del equipo
anfitrión, incluido el manifiesto de procedencia. Descarga aproximadamente 295 MB
del portal oficial del INE; reutiliza las descargas existentes verificadas sin
acceder a la red. Ambos scripts admiten `--help`. Consulta los [detalles de
configuración](docs/local-setup.md) para conocer los permisos, el uso interactivo
y la reconstrucción de la imagen.

Los ZIP/PDF originales y el entorno de ejecución quedan fuera de Git. La procedencia
de los archivos se registra en el [manifiesto de fuentes](data/sources.json), generado
por el descargador. La [limpieza reproducible de T06](docs/data-cleaning.md) valida
las seis elecciones y genera tablas y reportes separados por año sin modificar originales:

```powershell
docker compose run --rm --pull never analysis python scripts/clean_ccpc.py --all-years
```

La salida nueva se guarda en `data/processed/ccpc_all/`, con carpetas por año y un
`summary.json`; si ya existe, utiliza otro `--run-name`, sin sobrescribirla.
`--year 2012` procesa solo ese año; sin seleccionar un modo se conserva el valor
predeterminado anterior de 2024. Los resultados son internos hasta revisar
la política de difusión de grupos pequeños.

La [comparación de segmentación de T07](docs/segmentation-comparison.md) evalúa
K-means y Ward para 4, 5 y 6 segmentos sobre los grupos agregados de **2024**:

```powershell
docker compose run --rm --pull never analysis python -B scripts/compare_segments.py
```

Genera `report.json` y `comparison.csv` en `outputs/t07_comparison/`, sin
sobrescribir ejecuciones anteriores (`--run-name` permite otra carpeta). Incluye
semillas, sensibilidad a variables, ponderaciones, elegibilidad y edades extremas,
tamaños, composición y estabilidad al retirar entidades. No mezcla elecciones
ni exporta asignaciones finales: esa selección se realiza con el comando T08.
Todavía no se han implementado una interfaz ni un despliegue.

La [extensión histórica de T07](docs/historical-robustness.md) compara las seis
elecciones por separado y usa referencias fijas dentro de las series
2012/2018/2024 y 2009/2015/2021, sin sumar poblaciones entre elecciones:

```powershell
docker compose run --rm --pull never analysis python -B scripts/compare_history.py
```

La nueva salida es `outputs/t07_history/`. Conserva el comando de 2024 y sus
resultados anteriores; la referencia histórica no representa trayectorias de personas.

La [selección y exportación T08](docs/profile-selection.md) utiliza cinco perfiles
centrales de 2024 y conserva el contexto de las seis elecciones, incluidos los
candidatos anuales y las referencias históricas de 4, 5 y 6 bandas:

```powershell
docker compose run --rm --pull never analysis python -B scripts/export_profiles.py
```

Genera nueve archivos en `outputs/t08_profiles/`: perfiles, asignaciones centrales
e históricas, métricas, exclusiones y evidencia con hashes. `--run-name` permite
otra ejecución sin sobrescribir. Las salidas son internas y requieren revisión
de divulgación antes de publicarse; no son historiales de personas. Los nombres
y descripciones se trabajan en el [borrador interno T09](docs/profile-interpretation.md)
y las [propuestas generales T10](docs/institutional-proposals.md) cubren información,
accesibilidad y calidad del servicio, sin dirigir acciones por perfil. Son un
borrador interno pendiente de revisión y cierre, no intervenciones evaluadas.
Las narrativas con composición demográfica
se conservan localmente en `outputs/t09_profiles_narrative/README.md`, fuera de
Git; la rama no las transporta ni autoriza su difusión.

Para preparar una **vista reducida pendiente de revisión**, sin modificar T08 ni
autorizar publicación:

```powershell
docker compose run --rm --pull never analysis python -B scripts/prepare_disclosure_summary.py
```

La [revisión de divulgación](docs/disclosure-review.md) documenta los campos y
precisión de `outputs/t08_disclosure_summary/`. No contiene asignaciones ni
conteos exactos, no sustituye la evidencia interna y no debe compartirse
automáticamente: la revisión final de materiales y canales corresponde a T14–T15.

## Documentos del proyecto

- [Configuración y ejecución local](docs/local-setup.md)
- [Índice inicial del documento técnico (T05 → T11)](docs/technical-report-outline.md)
- [Inventario de fuentes CCPC, documentación y limitaciones](docs/data-sources.md)
- [Auditoría de variables y unidad de análisis de T04](docs/data-audit.md)
- [Limpieza, validaciones y tabla analítica de T06](docs/data-cleaning.md)
- [Comparación de segmentación y limitaciones de T07](docs/segmentation-comparison.md)
- [Robustez histórica y referencias por serie electoral](docs/historical-robustness.md)
- [Selección de perfiles y exportaciones trazables T08](docs/profile-selection.md)
- [Diagnóstico urbano–mixto–rural de 2024, método y límites](docs/section-type-diagnostic.md)
- [Cruce de perfiles fijos P01–P05 con tipo de sección](docs/profile-section-cross.md)
- [Interpretación T09, trazabilidad y revisión del borrador interno](docs/profile-interpretation.md)
- [Propuestas institucionales generales T10 y pendientes de cierre](docs/institutional-proposals.md)
- [Fichas internas T12: contenido, formato y validaciones](docs/profile-cards.md)
- [Generación de fichas PDF/PNG en Docker](docs/profile-cards-docker.md)
- [Revisión de divulgación y borrador de resúmenes](docs/disclosure-review.md)
- [Tablero de tareas del hackathon](docs/tablero-de-tareas-hackathon.md)
