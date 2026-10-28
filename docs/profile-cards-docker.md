# Exportación de fichas en Docker

La generación de fichas utiliza el servicio Docker `profile-cards`, que prepara
HTML, PDF y PNG con Python 3.12, Chromium y PyMuPDF, separado del entorno de
análisis. La única salida del proyecto sigue siendo `outputs/t12_profile_cards/`.
Preparar o comprobar la imagen no reemplaza las fichas existentes ni autoriza
su divulgación.

## Construir y ejecutar

Requisitos: Docker Desktop con contenedores Linux y los dos archivos de entrada
documentados en [la guía de fichas](profile-cards.md). Desde la raíz:

```powershell
docker compose --profile profile-cards build profile-cards
docker compose --profile profile-cards run --rm --pull never profile-cards
```

La construcción necesita conectividad para descargar paquetes públicos; la
ejecución de exportación no tiene red. La imagen puede ocupar varios cientos
de MB. No instala Python, fuentes ni navegadores en el anfitrión.

**Destino existente:** si `outputs/t12_profile_cards/` ya existe, la exportación
se rechaza antes de modificarlo. No se borra, mezcla ni sobrescribe. Un reemplazo
de ese conjunto necesita una decisión explícita; no hace falta reemplazarlo para
ejecutar las pruebas de la imagen.

## Entorno y fuentes

- `Dockerfile.profile-cards` usa la misma base Python 3.12.10 fijada por digest
  que el análisis, pero una imagen y un entorno virtual independientes.
- Chromium, Fontconfig y Liberation proceden del repositorio Debian firmado
  congelado por `DEBIAN_SNAPSHOT`. PyMuPDF utiliza la versión fijada en
  `requirements-profile-cards.txt`; no se añaden paquetes a `requirements.txt`.
- En Linux, Arial se resuelve a **Liberation Sans** y Georgia a **Liberation
  Serif**, mediante `docker/profile-cards-fonts.conf`. No se copian fuentes de
  Windows. La construcción comprueba ambas resoluciones.
- Las versiones de paquetes están en
  `/usr/local/share/profile-cards-packages.txt`, dentro de la imagen. El
  `report.json` generado conserva hashes de entradas, artefactos y navegador,
  versiones PyMuPDF/MuPDF y comprobaciones de geometría.

No se promete igualdad binaria con los PDF de Chrome en Windows: cambian motor,
fuentes y metadatos. La aceptación exige mantener cifras, texto, cinco páginas
individuales carta, cuaderno de cinco páginas, PNG de 2550 × 3300 a 300 dpi,
fuentes de al menos 8 pt y texto dentro de página. También exige revisión visual.

## Límites del contenedor

El exportador se ejecuta como UID/GID 1000, con raíz de solo lectura, sin red,
sin capacidades Linux y con `no-new-privileges`. Solo el directorio `outputs/`
permite persistir resultados; los dos directorios de entrada se superponen como
montajes de solo lectura. No se monta `data/` ni el perfil personal del navegador.
El código y las pruebas también son de solo lectura.

Chromium dispone de `/tmp` temporal de 1 GiB y memoria compartida privada de
256 MiB. No se comparte el IPC del anfitrión. Los temporales desaparecen con el
contenedor y las pruebas no necesitan crear otra carpeta permanente de fichas.

`docker/profile-cards-seccomp.json` conserva una política de denegación por
defecto. Permite namespaces y `chroot` para el sandbox de Chromium, sin conceder
capacidades del anfitrión; `clone3` devuelve `ENOSYS` para permitir el fallback
de libc. La procedencia y los cambios respecto de la política upstream están
en `docker/NOTICE`, con la licencia correspondiente. Esto no cambia la licencia
del trabajo analítico del equipo.

No se utiliza `--no-sandbox`, modo privilegiado, `SYS_ADMIN` ni seccomp sin
restricciones. Si el kernel, AppArmor o el motor no permiten iniciar el sandbox,
la exportación debe fallar: no se desactiva esa protección para hacerla pasar.
La documentación upstream sobre namespaces está en
[Playwright Docker](https://playwright.dev/docs/docker#crawling-and-scraping).

## Comprobar sin reemplazar las fichas

En el anfitrión, las comprobaciones de configuración usan el cliente de Compose:

```powershell
python -B -m unittest discover -s tests -p test_docker_profile_cards.py -v
```

Las pruebas de renderizado utilizan entradas sintéticas y directorios temporales
del contenedor, no la carpeta canónica existente:

```powershell
docker compose --profile profile-cards run --rm --pull never profile-cards python -B -m unittest discover -s tests -p test_generate_profile_cards.py -v
docker compose --profile profile-cards run --rm --pull never profile-cards python -B -m unittest discover -s tests -p test_docker_profile_cards.py -v
```

Las regresiones incorporadas tras la verificación independiente utilizan las
entradas reales montadas en solo lectura y exportan únicamente en temporales.
Comprueban integridad, rechazo de destinos existentes y el estado del sandbox
interno de Chromium:

```powershell
docker compose --profile profile-cards run --rm --pull never profile-cards python -B -m unittest discover -s tests -p test_profile_cards_independent_runtime.py -v
```

`T12_BROWSER=/usr/bin/chromium` se configura solo en este servicio. La suite
general del análisis continúa en su propio entorno:

```powershell
docker compose run --rm --pull never analysis python -B -m unittest discover -s tests -v
```

Las comprobaciones estáticas no demuestran que Chromium arranque. Un resultado
de construcción o ejecución pendiente debe registrarse como pendiente, no como
reproducción aprobada. Este exportador tampoco sustituye ejecutar desde los datos
originales el proceso completo de T14 ni la revisión conjunta de divulgación.

## Evidencia de la comprobación local

Se construyó la imagen en Docker Desktop, Linux/amd64, con Python 3.12.10,
Chromium 156.0.8078.47 (`156.0.8078.47-1~deb12u1`), Fontconfig 2.14.1-4,
Liberation 2.1.5-1 y PyMuPDF 1.28.0. No se afirma validación en ARM ni igualdad
binaria con Windows.

- Las nueve pruebas del generador pasaron dentro del exportador, incluida la
  exportación PDF/PNG real con entradas sintéticas.
- Las dos pruebas de límites del exportador pasaron dentro de ese servicio;
  las dos comprobaciones de Compose se ejecutan en el anfitrión y se omiten
  explícitamente donde no está instalado el cliente Docker.
- Antes de incorporar las dos regresiones independientes, la suite de `analysis`
  ejecutó 76 pruebas: 70 aprobadas y seis omitidas por sus condiciones explícitas,
  sin fallos. Las dos pruebas de entorno que
  fallaban con Python 3.14 en el anfitrión pasaron en el contenedor de análisis.
- Una exportación con las entradas reales, en `/tmp` del contenedor, produjo
  los cinco perfiles con tamaños aproximados, fuente mínima de 8.1 pt y cuaderno
  de cinco páginas. Repetir sobre el mismo destino fue rechazado sin cambios.
- La carpeta canónica conservó sus 19 archivos sin cambios de contenido. No se
  sustituyeron las fichas de Windows ni se creó otra salida permanente.
- La verificación independiente confirmó UID/GID 1000, capacidades efectivas y
  de límite vacías, raíz y entradas de solo lectura, ausencia de red y política
  seccomp cargada. La página `chrome://sandbox/`, consultada con
  `--allow-chrome-scheme-url`, mostró sandbox de namespaces, namespaces de PID y
  red y Seccomp-BPF con TSYNC activos. Se incorporaron las dos sondas como
  regresiones para el servicio, sin repetir la suite completa del análisis.

Estas comprobaciones no cierran T14 desde las fuentes originales, la revisión
de divulgación ni la entrega. La imagen y su caché de construcción permanecen
locales; no se publicó ninguna imagen.
