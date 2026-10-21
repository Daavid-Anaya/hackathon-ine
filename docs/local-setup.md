# Reproducir el entorno local de CCPC

Docker proporciona el entorno de Python, Pandas y Scikit-learn. Utiliza Windows
PowerShell desde la raíz del repositorio. Es un entorno de análisis por lotes,
no una aplicación web: la comprobación predeterminada termina y el contenedor sale.
No requiere instalar Python en el equipo anfitrión, cambiar la política de
ejecución de PowerShell ni realizar un despliegue.

## Iniciar y comprobar con Docker

Instala Docker Desktop con el complemento Compose e inicia el motor Linux
(normalmente mediante WSL 2 en Windows). Completa los requisitos del primer
inicio de Docker Desktop antes de continuar. `docker info` debe conectarse
correctamente. Este flujo utiliza un motor Docker local, no un contexto remoto.

Ejecuta cada comando solo cuando el anterior termine correctamente:

```powershell
docker version
docker compose version
docker compose config --quiet
docker compose build analysis
docker compose run --rm analysis
docker compose run --rm analysis python -m unittest discover -s tests -v
```

La primera construcción descarga la imagen base de Python y los paquetes fijados;
puede requerir varios minutos y espacio adicional en disco. Las construcciones
posteriores reutilizan las capas en caché. No utilices `docker compose up` para
mantener activo el entorno: no hay ningún servidor que iniciar.

La imagen utiliza Python **3.12.10** sobre Debian Bookworm, con la imagen base
fijada mediante su digest, e instala las dependencias de `requirements.txt` en
`/opt/venv`, sin cambiar sus versiones ni hashes y admitiendo únicamente paquetes
binarios wheel. `requirements.in` declara las dependencias directas. Si no existe
un wheel compatible, la construcción falla en lugar de cambiar las versiones.
La imagen se ejecuta con el usuario `analyst` (UID/GID 1000), sin privilegios de root.

La comprobación básica termina con código 0 y muestra un JSON con las versiones
instaladas y `"smoke_test": "ok"`, después de verificar operaciones de Pandas y
escalado de Scikit-learn con datos sintéticos. Las pruebas utilizan descargas
simuladas y archivos sintéticos temporales; no descargan ni analizan registros
electorales. Las pruebas específicas de Docker también comprueban el usuario de
ejecución y los límites de lectura y escritura; se omiten fuera del contenedor.

Una prueba de regresión adicional desde el equipo anfitrión comprueba la
persistencia entre contenedores eliminados y que los originales sintéticos no
cambien al rechazar escrituras. Esta comprobación avanzada y opcional requiere
la imagen construida y un lanzador de Python 3, pero solo utiliza la biblioteca
estándar: no necesita un entorno virtual local ni paquetes de análisis. Trabaja
en un directorio temporal aislado del sistema y nunca lee las fuentes reales.
El análisis habitual no requiere Python en el equipo anfitrión. Para ejecutar
esta prueba de forma explícita desde PowerShell:

```powershell
$env:RUN_DOCKER_HOST_PROBES = '1'
try {
    py -3 -B -m unittest discover -s tests -p test_docker_persistence.py -v
} finally {
    Remove-Item Env:RUN_DOCKER_HOST_PROBES -ErrorAction SilentlyContinue
}
```

Esta prueba exclusiva del equipo anfitrión se omite en la ejecución habitual
de pruebas y dentro de los contenedores.

### Trabajar de forma interactiva o ejecutar scripts

```powershell
docker compose run --rm analysis python
docker compose run --rm analysis sh
docker compose run --rm analysis python scripts/check_environment.py
```

Los scripts y las pruebas se montan directamente desde el equipo anfitrión en
modo de solo lectura; sus cambios estarán disponibles en el siguiente contenedor
sin reconstruir la imagen. Después de cambiar dependencias o el Dockerfile,
reconstruye con `docker compose build analysis`. No instales paquetes de forma
interactiva dentro de un contenedor temporal. Eliminar un contenedor con `--rm`
no elimina los datos ni los resultados del equipo anfitrión.

### Almacenamiento y permisos

Compose crea `data/processed/` y `outputs/` en el equipo anfitrión si no existen.
Estos dos montajes conservan los archivos generados después de finalizar los
contenedores; los originales y el código son de solo lectura. Solo se exponen
las rutas montadas de forma explícita, no el repositorio completo, las
credenciales, el socket de Docker ni el entorno del equipo anfitrión.

En Linux o WSL, comprueba que esos dos directorios existan en el equipo anfitrión
y permitan escritura al UID/GID 1000 antes de ejecutar el contenedor. Si tu usuario
tiene otros identificadores, puedes especificarlos para esa ejecución desde una
terminal Linux: `docker compose run --rm --user "$(id -u):$(id -g)" analysis`.
No ejecutes el análisis como root ni concedas escritura general sobre los originales
para eludir los permisos. Esta sintaxis no corresponde a PowerShell.

El acceso a datos montados desde Windows puede ser más lento que desde el sistema
de archivos Linux de WSL. Mover el repositorio es opcional y no forma parte de esta transición.

## Descargar o verificar las fuentes

Inspecciona las fuentes ya descargadas sin conexión y sin permisos de escritura:

```powershell
docker compose run --rm analysis python scripts/download_ccpc.py --inspect
```

Si faltan fuentes, ejecuta explícitamente el servicio de descarga:

```powershell
docker compose --profile download run --rm download
```

Solo este servicio habilita la red y la escritura en `data/` del equipo anfitrión,
porque el descargador debe guardar los originales y reemplazar `sources.json`
de forma atómica mediante un archivo temporal en el mismo directorio. No lo
ejecutes simultáneamente con el análisis ni con otra descarga. No publica puertos
ni se ejecuta automáticamente junto al análisis. En Linux, su usuario también
necesita permisos de escritura sobre `data/` y `data/raw/` del equipo anfitrión.

Se descargan los seis ZIP estándar de elecciones y el manual de la plataforma.
Cada ZIP nuevo pasa una comprobación CRC; se verifica la firma del PDF y se genera
un registro SHA-256 por archivo completado. El descargador no extrae, transforma
ni sobrescribe los originales existentes. Estos deben coincidir con el hash del
manifiesto; un original sin registro o modificado detiene el comando para su
inspección manual. Los hashes identifican los bytes descargados; la página de
origen no proporcionó una suma de comprobación firmada por el publicador que
permitiera establecer una autenticidad independiente.

`--inspect` requiere los siete archivos y el manifiesto. Comprueba tamaños,
hashes y listas de miembros de los ZIP, y lee una cantidad limitada de
documentación TXT y el primer encabezado CSV de cada ZIP. No es una auditoría
de filas ni una certificación de privacidad.

Ejecuta un solo descargador a la vez. Un intento que falla normalmente elimina
su propio archivo temporal. Una terminación forzada puede dejar un `.part`;
el siguiente intento utiliza un archivo parcial independiente y no considera
ese resto como una fuente. Se conserva localmente un archivo
`DatosAbiertos_DECEyEC_ConteosCensales2024.zip.part` del primer intento que agotó
el tiempo disponible; Git lo ignora y no forma parte del inventario. El hash del
ZIP de 2024 completado se verificó de manera independiente. Si un proceso se
detiene entre guardar un original y registrar su procedencia, la siguiente
ejecución rechaza ese archivo sin registro; consérvalo y reconcilia su procedencia
en lugar de eliminarlo o inventar una fecha de descarga.

## Conexiones lentas

Permite suficiente tiempo para las transferencias de red. No desactives TLS ni
la validación de hashes, no cambies las versiones de las dependencias y no
ejecutes varios instaladores de forma simultánea.

## Límites del entorno de trabajo

| Ruta | Propósito | Git |
| --- | --- | --- |
| `/opt/venv` | Python y dependencias exclusivos del contenedor; no es un montaje del equipo anfitrión | Solo en la imagen |
| `data/raw/` | Originales de solo lectura durante el análisis | Excluido |
| `data/sources.json` | Procedencia de solo lectura durante el análisis | Incluido |
| `data/processed/` | Tablas extraídas o limpias, con escritura y persistencia | Excluido |
| `outputs/` | Resultados generados, con escritura y persistencia | Excluido |
| `scripts/`, `tests/` | Montajes directos del código en modo de solo lectura | Incluido |
| `docs/` | Documentación; no se monta | Incluido |

El servicio independiente de descarga es la excepción explícita que permite
escribir datos. La lista de archivos permitidos de `.dockerignore` excluye del
contexto de construcción los originales, los entornos del equipo anfitrión, los
metadatos de Git, los resultados y otros archivos ajenos al entorno. No publiques
la imagen local ni subas datos como parte del desarrollo habitual.

No publiques datos personales, credenciales ni cartas administrativas firmadas.
T04 debe validar la unidad de observación y la agregación permitida antes de
iniciar la limpieza o la segmentación.

Los cambios de dependencias son tareas deliberadas de mantenimiento, no pasos
de ejecución habitual. Edita `requirements.in` y regenera `requirements.txt`
con sus hashes mediante uv en un contenedor de construcción desechable con
Python 3.12, separado del servicio de análisis de solo lectura. Reconstruye y
prueba la imagen después de cambiar dependencias. Conserva el archivo de
dependencias fijadas en Git; no lo regeneres solo para reproducir el entorno.
Actualizar la etiqueta o el digest de la imagen base también requiere una
decisión de mantenimiento seguida de las mismas comprobaciones.

Referencia: [documentación de uv sobre fijación de dependencias y sincronización](https://docs.astral.sh/uv/pip/compile/).
