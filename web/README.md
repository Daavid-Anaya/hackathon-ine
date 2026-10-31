# Demostrador institucional · React + Vite + TypeScript

Base navegable de las cinco propuestas institucionales del Reto 1. Incluye Inicio,
catálogo, una página por propuesta, Evaluación y Evidencia. **E01 incluye una
calculadora de cobertura en horario extendido y E02 una consulta móvil guiada**;
E03 incorpora un explorador territorial, E04 un recorrido visual con apoyos al
funcionariado y E05 una lista de verificación de una sede ficticia. Las cinco
demostraciones son ilustrativas; no constituyen servicios oficiales ni validación operativa.

La aplicación se ejecuta en el navegador y requiere JavaScript. Sin JavaScript,
muestra una explicación y un enlace al portal oficial. No requiere backend,
cuentas ni base de datos. No guarda progreso en localStorage, sessionStorage,
cookies o servidores. Las entradas de demostración son temporales.

**Sigue siendo un borrador local, no una publicación autorizada.** No sustituye
el documento técnico, las fichas de perfil, la presentación ni el paquete administrativo de entrega.

## Ejecutar únicamente con Docker

Requisitos: Docker Desktop con contenedores Linux, Docker Compose y un navegador.
**No instales Node ni npm en el anfitrión ni ejecutes los scripts de la web fuera de Docker.**
Desde la raíz del repositorio:

```powershell
docker compose up --build -d --no-deps --wait web
```

Abre **http://127.0.0.1:4321**. El comando inicia únicamente el servicio web;
no ejecuta el análisis ni descarga datos. Para consultar los registros o detenerlo:

```powershell
docker compose logs web
docker compose stop web
```

Después de modificar las fuentes, repite el comando de arranque para reconstruir
la imagen. Es una compilación estática, no un servidor de desarrollo:
no tiene recarga automática ni montajes de las fuentes del anfitrión. Los scripts
de `package.json` son comandos internos de construcción y pruebas del contenedor,
no instrucciones de arranque en el anfitrión. No se utilizan las dependencias
locales existentes que estén ignoradas por Git.

## Límites de los contenedores

La primera construcción descarga las imágenes base fijadas de Node y Nginx sin
privilegios, además de los paquetes npm; puede tardar varios minutos. Las siguientes
construcciones reutilizan la caché de capas de Docker. React, Vite, TypeScript y sus dependencias
permanecen fijados en los archivos de paquetes y de bloqueo; las imágenes base se
fijan mediante su identificador de contenido en `Dockerfile`.

La etapa de Node instala las dependencias con `npm ci`, comprueba los tipos y compila con Vite. La imagen
final contiene únicamente el sitio generado y Nginx: no se copian Node, npm,
fuentes, herramientas del navegador ni datos internos del proyecto a la etapa que
sirve la web. `dist/` se genera durante la construcción, no en el anfitrión.
No se necesitan comandos de Node o npm fuera de Docker.

El servidor utiliza UID/GID 101, un sistema de archivos raíz de solo lectura,
capacidades de Linux eliminadas y un `/tmp` temporal. El puerto 4321 se vincula
únicamente a **127.0.0.1**. No hay montajes del anfitrión y se utiliza una red bridge
dedicada, compartida solo con el servicio opcional de pruebas. La red no es un
cortafuegos de salida. Una red `internal` no publicó el puerto local en el motor
Docker comprobado; la restricción de entrada se mantiene mediante el enlace a loopback.
La ejecución local no implica autorización para publicar.

Los perfiles opcionales `web` y `web-checks` mantienen intacto el flujo predeterminado
de análisis por lotes. No se ha elegido un alojamiento público ni una subruta.
Una vez construida la imagen, la consulta local no requiere internet; los enlaces
a fuentes externas sí lo necesitan.

## Estructura de las fuentes

| Ruta | Propósito |
| --- | --- |
| `index.html` | Entrada Vite, metadatos y alternativa sin JavaScript |
| `src/app/main.tsx` | Montaje de React |
| `src/app/App.tsx` | Navegación, pantallas y estructura compartida |
| `src/app/proposals.ts` | Presentación tipada de E01–E05, vinculada a los datos existentes |
| `src/app/E01Calculator.tsx` | Calculadora TCHE con conteos sintéticos, validación y resultado accesible |
| `src/app/E02Consultation.tsx` | Tres fichas de casillas ficticias y estados de afluencia simulados |
| `src/app/E03Territory.tsx` | Comunidades ficticias, barreras combinables y medidas sujetas a diagnóstico |
| `src/app/E04Flow.tsx` | Esquema seleccionable de etapas, distribución y apoyos al funcionariado |
| `src/app/E05Checklist.tsx` | Condiciones presentes, ausentes o pendientes y acciones de seguimiento |
| `src/data/profiles.js` | Copia de datos seleccionados para el borrador, sin desgloses demográficos |
| `src/app/styles.css` | Paleta de las fichas, diseño adaptable y foco visible |
| `src/app/useScrollReveal.ts` | Apariciones por bloque, una vez por pantalla montada |
| `tests/base.spec.cjs` | Recorridos de la base, teclado, tamaños y movimiento |
| `tests/e01.spec.cjs` | Cálculo, entradas inválidas, denominador cero y descarte del estado de E01 |
| `tests/e02.spec.cjs` | Fichas de ejemplo, estados de afluencia, teclado y descarte del estado de E02 |
| `tests/e03.spec.cjs` | Casos territoriales, combinaciones de barreras y descarte del estado de E03 |
| `tests/e04.spec.cjs` | Etapas, apoyos concretos, navegación por teclado y descarte de la selección |
| `tests/e05.spec.cjs` | Estados de condiciones, seguimiento, límites de certificación y descarte de respuestas |
| `tests/runtime.spec.cjs` | Nginx real, recursos y rechazo de archivos privados |

Las pantallas usan fragmentos (`#/propuestas/E01`, `#/evaluacion`, `#/evidencia`)
para poder recargar y compartir enlaces sin convertir las rutas de archivos privados
en respuestas HTML. Atrás y adelante conservan la navegación. Los bloques son
visibles por defecto; IntersectionObserver activa apariciones suaves. Movimiento
reducido desactiva las animaciones y la ausencia del observador no oculta contenido.

Los archivos Astro y las pruebas del explorador anterior pueden permanecer localmente
como referencia no versionada. No forman parte de las fuentes del demostrador ni se
ejecutan mediante `npm test`. Astro ya no es una dependencia; ese prototipo no es
necesario para construir o comprobar la aplicación.

No hay analítica, fuentes tipográficas remotas, CDN, carga de archivos, contacto
individualizado, ejecución de modelos, filtro histórico ni desgloses demográficos
o geográficos. La URL identifica solamente la pantalla; no contiene entradas de
demostración ni información personal.

## E01 · Calculadora de cobertura

Abre **http://127.0.0.1:4321/#/propuestas/E01**. El ejemplo sintético empieza con
100 trámites totales y 25 en horario extendido: `100 × 25 / 100 = 25.0%`.
Edita ambos conteos para actualizar el resultado, sin enviar datos a un servidor.

- Ambos conteos corresponden a los mismos MAC seleccionados y al mismo período.
- El horario extendido comprende sábado, domingo o turno vespertino; cada trámite
  se cuenta una sola vez y es parte del total.
- Solo se admiten enteros no negativos representables con precisión; no se aceptan
  campos vacíos, decimales, notación científica o un numerador superior al total.
- Con cero trámites totales y cero en horario extendido, muestra **«No aplica»**.
  Con trámites totales positivos y ninguno en horario extendido, muestra **0.0%**.
- Las entradas se restablecen al recargar o salir de la propuesta. No se conservan
  en el navegador, la URL ni una base de datos.

La TCHE mide cobertura de atención, no impacto sobre el voto. No se consulta SIIRFE
ni se presentan estos números como observaciones reales o metas institucionales.

## E02 · Consulta móvil guiada

Abre **http://127.0.0.1:4321/#/propuestas/E02**. Selecciona uno de los tres recintos
inventados: centro comunitario, escuela o biblioteca. Cada ficha presenta una
ubicación de ejemplo, referencia de acceso, horario ilustrativo y condiciones de
accesibilidad del escenario. No permite localizar una casilla real ni determinar
dónde corresponde votar.

El control «Simular afluencia» cambia entre Baja, Moderada, Alta y Sin información.
Este último estado significa ausencia de datos, no baja afluencia. Al seleccionar
otra casilla se carga su estado inicial; al recargar o salir de E02 se restablece
el ejemplo A. No se guarda la selección en el navegador ni en la URL.

No son mediciones en tiempo real, predicciones de espera ni verificación física
de accesibilidad. No hay mapas externos, geolocalización, consultas institucionales,
fichas de candidaturas ni rutas de transporte en esta versión. La interacción
tampoco demuestra el rendimiento real del indicador DRC.

## E03 · Explorador territorial

Abre **http://127.0.0.1:4321/#/propuestas/E03**. Los tres casos comunitarios son
ficticios y parten de una barrera distinta: traslado y dispersión, espera con
acompañantes o información oral/bilingüe. Puedes combinar o desmarcar las barreras
para explorar medidas, recursos, canales abiertos y condiciones de validación.

Sin selección, el explorador no muestra medidas, pero advierte que eso no demuestra
ausencia de necesidades. Cambiar de comunidad restablece sus barreras iniciales;
recargar o salir de E03 recupera el primer ejemplo. No hay mapas, ubicaciones
reales, geolocalización, clasificación individual ni almacenamiento de selección.

Las opciones no son aprobaciones ni un plan operativo listo para ejecutar. Evaluar
una casilla extraordinaria requiere diagnóstico, dictamen técnico y el acuerdo
institucional correspondiente. El recorrido no aplica un umbral automático de
traslado, calcula PACE ni predice cambios en la participación electoral.

## E04 · Recorrido visual y apoyo al funcionariado

Abre **http://127.0.0.1:4321/#/propuestas/E04**. El esquema contiene cuatro etapas
seleccionables: orientación y acceso, mesa de atención, espacio de votación, urnas
y salida. Cada una muestra su propósito, una distribución ilustrativa y los apoyos
propuestos al funcionariado. Los botones funcionan con Tab y Enter o Space; el
estado activo y un anuncio accesible indican qué detalle se está consultando.

Es una síntesis visual, no un plano de inmueble ni un protocolo oficial completo.
No modifica la cantidad de materiales reglamentarios, mide filas, calcula TAP ni
predice tiempos de espera o efectos sobre el voto. Antes de un piloto hacen falta
revisión del inmueble, validación institucional de guías/materiales y recursos.
Recargar o salir de E04 restablece la primera etapa, sin almacenamiento ni datos
personales o conexiones con SICE.

## E05 · Lista de verificación de accesibilidad

Abre **http://127.0.0.1:4321/#/propuestas/E05**. La sede es ficticia. Seis condiciones
se registran como Presente, Ausente o Pendiente de verificar: acceso a nivel o rampa
funcional, mampara adaptada, lupa, plantilla Braille, atención preferencial y sillas
con sombra. Todas empiezan pendientes, sin presumir presencia o ausencia.

El resumen separa respuestas y muestra acciones para barreras declaradas o
verificaciones aún necesarias. Marcar todo presente no certifica accesibilidad ni
aprueba una sede; tampoco se genera una puntuación o el indicador distrital CEAF.
La accesibilidad no es exclusiva de un perfil ni permite inferir discapacidad.
Las respuestas se restablecen al recargar o salir, sin guardar datos personales,
almacenamiento del navegador, entradas en la URL ni consultas a SIJE.

## Datos y procedencia

El módulo de datos **no** está conectado en tiempo real con `outputs/`.
Los porcentajes proceden de
`outputs/t08_disclosure_summary/profiles.csv`:

| Perfil | Participación | Proporción de LN elegible |
| --- | ---: | ---: |
| P01 | 40.3% | 13.5% |
| P02 | 50.1% | 21.5% |
| P03 | 59.5% | 23.5% |
| P04 | 67.3% | 25.4% |
| P05 | 76.3% | 16.1% |

SHA-256 del CSV de origen:
`4ef646e84e4485eb9ee66ee4db428a3e0f05f0463f869bd5cb88c45686512a43`.
Los nombres siguen la [interpretación de perfiles](../docs/profile-interpretation.md);
los resúmenes de propuestas siguen las [propuestas institucionales](../docs/institutional-proposals.md)
y `docs/documento-tecnico.tex`. La interfaz se mantiene en español para coincidir
con estos materiales.

No se copian al sitio conteos exactos de población, composiciones demográficas,
claves geográficas, asignaciones del modelo, exclusiones ni documentos administrativos.
La participación es `100 × SV / (SV + NV)`; NS no es abstención. La proporción de LN
se refiere únicamente a la LN elegible de 2024. Los indicadores
de servicio propuestos son definiciones, no resultados medidos; un denominador
igual a cero significa “No aplica”.

## Comprobaciones

Ejecuta ambos comandos desde la raíz del repositorio y continúa únicamente si la
construcción termina correctamente:

```powershell
docker compose --profile web-checks build web web-checks
docker compose --profile web-checks run --rm web-checks
```

La imagen opcional de pruebas incorpora Chromium y ejecuta la versión fijada de
`playwright-core` dentro de Docker contra el **servicio Nginx real**, después de
que pase su comprobación de salud. No depende de Node ni de un navegador instalado
en el anfitrión. Esta imagen es más grande que la que sirve la web y se construye
solo cuando se solicita. Para detener la web después de las pruebas, se debe
ejecutar explícitamente `docker compose stop web`.

Las comprobaciones internas de los contenedores no demuestran que el navegador
del anfitrión pueda acceder al puerto publicado. Después del arranque en Windows,
ejecuta también:

```powershell
web\tests\check-host.cmd
```

Esta comprobación utiliza solo Docker y el PowerShell incluido en Windows.
Verifica el puerto realmente publicado en la interfaz local y una petición HTTP
desde el anfitrión, sin modificar la política de ejecución.

Las pruebas cubren Inicio, catálogo, E01–E05, Evaluación y Evidencia; recarga,
historial y pantalla no encontrada; navegación por teclado, anchos de 320/768/1440 px,
paleta compartida, apariciones sin repetición al volver a desplazar, movimiento
reducido, ausencia del observador y alternativa sin JavaScript. También comprueban
que no se generen peticiones a recursos externos ni almacenamiento persistente.
Los archivos de pruebas se ejecutan en serie para no iniciar varios navegadores
Chromium simultáneamente dentro de los límites de recursos del contenedor.
Las comprobaciones HTTP rechazan el acceso a fuentes, configuración, salidas
internas, documentos y rutas desconocidas, y comparan el HTML servido con la
compilación de la imagen de pruebas. Los archivos temporales del navegador quedan
en el sistema de archivos temporal del contenedor; no se escriben capturas ni
informes en el árbol de trabajo. Los archivos internos de origen y entrega se
excluyen intencionadamente de ambas imágenes, por lo que las pruebas no calculan
los hashes de esos archivos del anfitrión. Estas comprobaciones no constituyen
una auditoría WCAG completa, una certificación de divulgación ni una verificación
de disponibilidad de los enlaces externos.

## Antes de publicar

No se ha desplegado en un alojamiento público. La publicación requiere autorización
explícita del destino y de la sesión de despliegue, además de revisar la versión
exacta del sitio generado y sus enlaces. La revisión previa del PDF y las fichas
no autoriza este sitio.

Solo **el sitio estático generado** corresponde a un posible despliegue público.
No copies directorios de fuentes, `node_modules/`, la raíz del repositorio,
`outputs/`, datos originales, narrativas internas, cartas firmadas ni PDF sin
publicar. Conserva los avisos de borrador y `publicationAuthorized: false` hasta
que una decisión explícita de publicación y su revisión correspondiente los sustituyan.

El archivo de bloqueo y las entradas de Docker se versionan; `node_modules/`,
`dist/` y `.astro/` del anfitrión permanecen ignorados y fuera de la lista de
archivos permitidos en el contexto de construcción de la web. Los scripts de
análisis, las definiciones de los servicios existentes, las salidas de datos
y los entregables obligatorios permanecen sin cambios.
