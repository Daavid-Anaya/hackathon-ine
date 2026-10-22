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
la política de difusión de grupos pequeños. Todavía no se han implementado la
segmentación, una interfaz ni un despliegue.

## Documentos del proyecto

- [Configuración y ejecución local](docs/local-setup.md)
- [Índice inicial del documento técnico (T05 → T11)](docs/technical-report-outline.md)
- [Inventario de fuentes CCPC, documentación y limitaciones](docs/data-sources.md)
- [Auditoría de variables y unidad de análisis de T04](docs/data-audit.md)
- [Limpieza, validaciones y tabla analítica de T06](docs/data-cleaning.md)
- [Tablero de tareas del hackathon](docs/tablero-de-tareas-hackathon.md)
