# Inventario de archivos originales y documentación de CCPC

T03 obtuvo las fuentes estándar de elecciones federales de **2009, 2012,
2015, 2018, 2021 y 2024**, además del manual de la plataforma. Los originales
se conservan sin modificar ni extraer en `data/raw/`, excluido de Git.

## Procedencia y cobertura

Página oficial de las fuentes: [INE — Conteos Censales de Participación Ciudadana](https://portal.ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/).

[`data/sources.json`](../data/sources.json) registra la URL exacta de cada descarga,
su fecha y hora UTC, año electoral, nombre de archivo local, tamaño en bytes,
SHA-256, cobertura declarada, observación sobre la versión del publicador y lista
de miembros del ZIP. No se indicó una versión de publicación en la página de
origen ni en los seis textos de descripción de campos inspeccionados. Las fechas
de las URL no son números de versión de los datos. El manual es una guía de la
plataforma, no un sustituto del diccionario de datos.

| Elección o recurso | Bytes de la descarga completada | Miembros CSV | Archivo de descripción de campos dentro del ZIP |
| --- | ---: | ---: | --- |
| 2009 | 40,203,573 | 32 | `DatosAbiertos_DECEyEC_ConteosCensales2009/01_descripcioncampos_conteoscensales2009.txt` |
| 2012 | 39,515,896 | 32 | `DatosAbiertos_DECEyEC_ConteosCensales2012/01_descripcioncampos_conteoscensales2012.txt` |
| 2015 | 42,594,136 | 32 | `DatosAbiertos_DECEyEC_ConteosCensales2015/01_descripcioncampos_conteoscensales2015.txt` |
| 2018 | 43,389,665 | 32 | `DatosAbiertos_DECEyEC_ConteosCensales2018/01_descripcioncampos_conteoscensales2018.txt` |
| 2021 | 44,357,326 | 32 | `DatosAbiertos_DECEyEC_ConteosCensales2021/01_descripcioncampos_conteoscensales2021.txt` |
| 2024 | 82,419,841 | 32 | `DatosAbiertos_DECEyEC_ConteosCensales2024/01_descripcioncampos_conteoscensales2024.txt` |
| [Manual de la plataforma, 2009–2024](https://portal.ine.mx/wp-content/uploads/2025/06/Manual-Conteos-Censales-2009-2024.pdf) | 2,624,288 | — | PDF; no es un diccionario |

Total de las siete descargas completas: **295,104,725 bytes**. Los archivos `.part`
son temporales de descargas incompletas, no fuentes originales ni entregables;
pueden eliminarse una vez verificado el archivo completo correspondiente.
Los seis ZIP contienen **192 archivos CSV con nombres de entidades federativas y
seis descripciones TXT**. Esto verifica la disponibilidad de archivos, no la
cobertura completa de la población ni la igualdad de claves territoriales entre años.

Los registros de descarga de los seis ZIP abarcan **2026-10-20 01:50–02:04 UTC**, que corresponde
al **19 de octubre de 2026, 19:50–20:04 en Ciudad de México (UTC−06:00)**.
El manual se descargó nuevamente desde la misma URL oficial el **21 de octubre de
2026 a las 19:01 UTC** tras eliminar la copia local dañada. Sus **2,624,288 bytes**
y SHA-256 coinciden con el registro original; se renderizaron sus **38 páginas**
sin errores ni reparaciones y se extrajo texto de todas ellas.
Conserva las fechas UTC reales; no las sustituyas por la fecha de planificación del equipo.

## Documentación inspeccionada

Las seis descripciones de campos TXT se leyeron como UTF-8, al igual que el primer
encabezado CSV de cada ZIP. No se leyeron filas de registros CSV para este
inventario. El encabezado común inspeccionado es:

```text
AELEC,FELECCION,EDOCVE,EDONOM,MPIOCVE,MPIONOM,SECCION,TIPOSEC,DEF,DEL,SEXO,EDAD,LN,SV,NV,NS
```

Las descripciones documentan claves geográficas, fecha de elección, tipo de sección,
sexo, edad y los conteos `LN`, `SV`, `NV`, `NS`. Indican que la fuente son los
cuadernillos de la lista nominal utilizados en casillas, sin incluir casillas
especiales ni el voto de personas mexicanas residentes en el extranjero. Estas
definiciones orientadas a conteos respaldan una fuente agregada candidata; no
constituyen una auditoría completa de privacidad ni de la unidad de cada fila.
No se debe publicar ni reconstruir la participación individual.

No falta ningún diccionario en los inventarios de los seis ZIP. No se verificó
un diccionario metodológico completo adicional a estas descripciones de campos;
las necesidades de documentación adicional deben registrarse durante T04.

## Advertencias para T04, no conclusiones analíticas

- **La geografía cambia:** las descripciones de 2009–2021 hacen referencia a los
  distritos DERFE 2021; la de 2024, a DERFE 2023. La visualización web anuncia
  cartografía de mayo de 2023, que no debe asumirse válida para todas las tablas
  originales descargadas.
- **Las categorías de sexo cambian:** las descripciones anteriores enumeran `0`/`1`;
  2024 añade `2` para personas no binarias. No fuerces las categorías a un modelo binario.
- **No especificado no significa abstención:** `NS` es participación no especificada
  con motivos documentados de disponibilidad de cuadernillos o páginas. Define los
  denominadores y las exclusiones en T04 antes de calcular tasas.
- **La escolaridad no aparece en los encabezados inspeccionados.** Tampoco aparecen
  las dimensiones de referencia indígena y afrodescendencia de la plataforma.
  No inventes estos campos ni supongas cruces no disponibles; revisa las tablas reales en T04.
- **Los nombres de archivo varían:** el sufijo de Tamaulipas es `_tamps.csv` en
  2009–2021 y `_tam.csv` en 2024. Utiliza el inventario, no una regla fija de sufijos.

Esta base no incluye datos de la elección judicial de 2025 ni suplementos de voto
anticipado o de personas en prisión preventiva. Esas fuentes requieren una
evaluación separada de cobertura y solapamientos antes de incorporarse.

## Volver a comprobar sin descargar

```powershell
docker compose run --rm analysis python scripts/download_ccpc.py --inspect
```

El código de salida 0 confirma que todos los originales esperados coinciden con
los tamaños y hashes registrados y que las listas de miembros de los ZIP coinciden.
El comando muestra los diccionarios y los primeros encabezados sin extraer archivos.
Las comprobaciones CRC se ejecutaron durante la descarga; los hashes comprueban la
integridad local, no una autenticidad firmada por el publicador. La limpieza, los
denominadores, la supresión, la cobertura geográfica completa y la comparabilidad
longitudinal siguen siendo tareas de **T04/T06**, no resultados de este inventario.
