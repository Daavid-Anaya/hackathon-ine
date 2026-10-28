# T12 — Fichas de perfil y exportación reproducible

Las cinco fichas son **borradores internos**. Integran descripción T09, gráficos
de composición de LN y propuestas T10 sin convertir hipótesis en atributos
individuales. La generación no autoriza compartirlas ni entregarlas al concurso:
la revisión conjunta de divulgación de T14–T15 sigue pendiente.

## Generar PDF y PNG

La exportación local utiliza Chrome, Chromium o Edge instalado y PyMuPDF 1.28.0.
No modifica las dependencias ni la imagen del análisis. En un entorno Python
separado, instala `requirements-profile-cards.txt`; no se necesita Pandas para
este comando. No descarga un navegador ni instala fuentes automáticamente.

```powershell
python -m pip install -r requirements-profile-cards.txt
python -B scripts/generate_profile_cards.py --browser "C:\Program Files\Google\Chrome\Application\chrome.exe" --output outputs/t12_profile_cards
```

Instalar dependencias requiere conectividad; generar las fichas utiliza únicamente
archivos locales, un perfil de navegador temporal separado del perfil personal y
HTML sin recursos externos. El comando bloquea resolución de nombres en ese
proceso, pero no constituye un aislamiento de red equivalente al contenedor.
No se desactiva el sandbox del navegador. En Linux/macOS, utiliza el mismo comando
con `--browser` apuntando al ejecutable local; esos entornos requieren sus propias
pruebas de renderizado. No se afirma equivalencia binaria entre sistemas.

Entradas predeterminadas:

- `outputs/t08_profiles_final/profiles.csv`: cinco perfiles K=5 de 2024.
- `outputs/profile_section_types_2024/cross.csv`: cruce U/M/R de los mismos perfiles.

La única salida canónica de las fichas es `outputs/t12_profile_cards/`, también
predeterminada en el generador. `--profiles` y `--cross` permiten seleccionar otras
ubicaciones de los mismos productos de entrada. El comando exige un destino
inexistente cuyo padre exista: si la carpeta canónica ya existe, se detiene sin
sobrescribirla. Cualquier reemplazo posterior debe ser explícito. También rechaza
entradas incompletas o inconsistentes y opciones desconocidas. No modifica las
entradas ni recalcula la segmentación.

## Formato y comprobaciones

### Paleta lila elegida para las fichas

Por decisión del proyecto se utiliza la paleta del [Manual de Identidad del INE
del 9 de septiembre de 2026, sección 2.3, páginas 11–12](https://repositoriodocumental.ine.mx/xmlui/bitstream/handle/123456789/190007/JGE2ex202609-09-ap-1-1-a.pdf).
Es una referencia histórica elegida para este diseño, Esta adaptación no implica aval institucional ni autoriza utilizar logotipos oficiales.

| Aplicación | Color | HEX |
| --- | --- | --- |
| Pleca, indicadores y barras | Lila institucional | `#674092` |
| Encabezados de sección | Lila oscuro | `#49276F` |
| Texto y etiquetas | Azul | `#383B7E` |
| Fondo de estrategia y barras | Lila claro | `#D1BDEF` |
| Separador del encabezado | Lila | `#9680B4` |
| Separadores secundarios | Gris | `#A6A8AA` |
| Página impresa | Blanco | `#FFFFFF` |

Los textos usan tonos oscuros; los lilas claros no se usan como texto sobre
blanco. La regresión comprueba contraste de al menos 4.5:1 en los pares de texto
y 3:1 en las barras. El contenido numérico, la tipografía y la geometría no cambian.
El comando de generación anterior aplica esta paleta en la salida canónica.

### Tamaños aproximados y porcentajes

Las fichas y el cuaderno muestran tamaños de LN aproximados en millones, con una
decimal y redondeo `ROUND_HALF_UP`, junto con los porcentajes originales. Los
porcentajes se calculan con los conteos validados de entrada, no con los tamaños
aproximados. Los tamaños y porcentajes redondeados pueden no sumar los totales.
Se conservan los conteos originales para la validación interna; no se modifican
las entradas ni se recalculan los modelos.

Este criterio se aplica a los PDF, PNG y el cuaderno de la salida canónica,
que mantienen su condición de borrador pendiente de revisión conjunta.

### Productos

| Producto | Especificación elegida |
| --- | --- |
| Cinco PDF individuales | Carta vertical, 612 × 792 pt (215.9 × 279.4 mm), una página por perfil, márgenes de 12 mm |
| Cinco PNG individuales | 2550 × 3300 px, 300 dpi; rasterizados desde el mismo PDF |
| Cuaderno PDF | Las mismas cinco páginas, ordenadas P01–P05 |
| HTML individual y cuaderno | Texto seleccionable, SVG con etiquetas y equivalente narrativo; sin fuentes o recursos remotos |
| `report.json` | Hashes SHA-256 de entradas y artefactos, versiones PyMuPDF/MuPDF, hash del navegador, tamaño, número de páginas y fuente mínima |

La convocatoria no prescribe tamaño ni DPI: carta y 300 dpi son decisiones de
exportación del proyecto. Los PDF conservan texto y gráficos vectoriales. Las
PNG contienen la página completa, no una captura de una ventana de navegador.
`--html-only` genera un borrador sin motor PDF y **no completa T12**:

```powershell
docker compose run --rm --pull never analysis python -B scripts/generate_profile_cards.py --html-only --output outputs/t12_profile_cards
```

Se validan identidades, conteos LN/SV/NV/NS, tasas, composiciones y reconciliación
del cruce antes de generar. Todos los porcentajes descriptivos salen de las
entradas validadas, sin cifras narrativas fijas en el código. El proceso rechaza
PDF de más de una página, texto fuera de página o fuentes menores de 8 pt.
Esas pruebas geométricas **no sustituyen** revisar visualmente las cinco páginas
al tamaño final. La legibilidad de etiquetas y el contraste deben comprobarse en
los productos exportados, no inferirse del CSS.

La reproducción busca equivalencia de contenido y geometría con las mismas
entradas, motor, navegador y fuentes. Los PDF pueden contener diferencias de
serialización entre ejecuciones; no se promete identidad binaria de los PDF.
`report.json` permite identificar exactamente el conjunto inspeccionado.

## Pruebas y límites de cierre

```powershell
python -B -m unittest discover -s tests -p test_generate_profile_cards.py -v
$env:T12_BROWSER = "C:\Program Files\Google\Chrome\Application\chrome.exe"
python -B -m unittest discover -s tests -p test_generate_profile_cards.py -v
```

Sin `T12_BROWSER`, la prueba de exportación real se omite explícitamente; el resto
utiliza entradas sintéticas. Con esa variable se verifican PDF y PNG reales.
La suite habitual del repositorio sigue siendo
`docker compose run --rm analysis python -m unittest discover -s tests -v`.

Las fuentes SIIRFE, SIJE, SICE y UTSI son propuestas sujetas a factibilidad. Las
fichas conservan la regla de denominador cero, las rampas funcionales de E05, la
distinción entre observaciones e hipótesis y el acceso voluntario sin contacto
individualizado por perfil. La formulación completa y los universos de medición
están en [T10](institutional-proposals.md); los límites de inferencia y divulgación,
en [T09](profile-interpretation.md) y la [revisión de divulgación](disclosure-review.md).

Todos los archivos generados permanecen bajo `outputs/`, ignorado por Git. No
incluyas fichas, conteos reales ni capturas de los perfiles en commits o PR sin
la revisión de divulgación correspondiente.

## Evidencia local de esta implementación

La revisión cromática lila se exportó en `outputs/t12_profile_cards_lila/` y se
inspeccionaron visualmente sus cinco PNG. Las ocho pruebas T12 pasan, incluida
la regresión de paleta/contraste y la exportación real. La comparación con la
versión anterior confirma texto PDF, cifras, geometría y salidas de la CLI sin
cambios; únicamente se modificó la presentación cromática. Los archivos anteriores
se conservan intactos. El nuevo conjunto mantiene cinco PDF individuales y un
cuaderno de cinco páginas, PNG a 300 dpi y fuente mínima de 8.1 pt.

Se generó `outputs/t12_profile_cards_final/` con cinco PDF de una página, cinco
PNG de 2550 × 3300 px a 300 dpi y el cuaderno PDF de cinco páginas. Se revisaron
visualmente las cinco PNG: sin recortes o superposiciones visibles. La fuente
mínima extraída de cada PDF es 8.1 pt y el texto está dentro de la página.
Los hashes concretos de ese conjunto interno se conservan en su `report.json`.

Las cinco pruebas T12 originales pasaron con Chrome y PyMuPDF 1.28.0 en el
anfitrión y en una copia aislada durante la verificación independiente. También
se incorporaron los sondeos independientes de entradas límite y separación de
dependencias como regresiones. La ejecución completa previa de 68 pruebas tuvo
62 aprobadas, dos fallidas por exigir el entorno documentado
(Python 3.12 y entorno virtual, frente al Python 3.14 anfitrión) y cuatro omitidas
relacionadas con Docker. Esos requisitos ya existían en la base y no se relajaron.
Docker Desktop no estaba disponible: la reproducción en el contenedor y la
revisión final de divulgación **no se consideran realizadas**.
