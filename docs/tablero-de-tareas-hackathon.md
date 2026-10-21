# Cronograma y Tablero de Tareas - Reto 1: Perfiles Ciudadanos

Plan de trabajo para el Hackathon "Hackea la participación: Datos que construyen democracia".

## Fechas y prioridades

- **Fecha de referencia del equipo:** 19 de octubre de 2026.
- **Cierre oficial indicado en la convocatoria:** 31 de octubre de 2026 a las 23:59 horas.
- **Meta interna de envío:** 30 de octubre. El 31 queda como margen de contingencia.
- **Registro:** la convocatoria fija su cierre el 15 de octubre.
- **Alcance obligatorio:** documento técnico, fichas de 4 a 6 perfiles, presentación ejecutiva, código o repositorio correspondiente y ambas cartas firmadas.
- **Alcance opcional:** interfaz web interactiva y despliegue.

La rúbrica asigna 35 puntos al apego al reto, 30 a claridad y solidez, 20 a originalidad y 15 a viabilidad institucional.

## Uso del tablero

Estados permitidos: **Pendiente**, **En curso**, **Bloqueada** y **Completada**. Sustituir "Por asignar" por el nombre de una persona responsable antes de iniciar cada tarea. Marcar una tarea como completada solo cuando exista la evidencia descrita.

Las dependencias condicionan el cierre: se pueden preparar plantillas, índice y borradores en paralelo, pero no cerrar narrativas ni cifras antes de validar el análisis. Las fechas son metas de planificación, no resultados ya alcanzados.

### 1. Requisitos, datos y preparación · 19–20 de octubre

| ID | Tarea y criterio de cierre | Depende de | Responsable | Estado |
| :--- | :--- | :--- | :--- | :--- |
| T01 | Verificar constancia de registro y requisitos: equipo paritario de 2 a 4 integrantes, edad de 18 a 35 años al cierre, nacionalidad y residencia en México, credencial vigente, restricciones de participación y representante con cuenta bancaria mexicana a su nombre. Registrar pendientes; si falta el registro, consultar a la organización sin asumir admisión. | — | Por asignar | Completada |
| T02 | Descargar los formatos oficiales de ambas cartas y coordinar las firmas de todas las personas integrantes. **Cierre previsto: 22 de octubre**, con documentos completos y legibles. Guardarlos fuera del repositorio público. | T01 | Por asignar | Pendiente |
| T03 | Descargar los datos agregados CCPC y su documentación. Registrar URL, fecha de descarga, elección, cobertura y versión si existe; conservar una copia original sin modificar. Cierre: inventario de fuentes y diccionarios disponibles, con ausencias documentadas. | — | Por asignar | Completada |
| T04 | Definir qué representa cada fila y auditar variables, claves geográficas, denominadores, faltantes, supresiones y comparabilidad temporal. Cierre: matriz de variables y unidad de análisis justificadas; escolaridad solo si está disponible y su incorporación es válida. No reconstruir cruces inexistentes ni historiales individuales a partir de agregados. | T03 | Por asignar | Pendiente |
| T05 | Preparar el entorno local con Python, Pandas y Scikit-learn, registrar versiones e iniciar instrucciones de ejecución y el índice del documento técnico. Cierre: entorno verificable y estructura de trabajo local. No requiere publicar ni desplegar. | — | Por asignar | Pendiente |

### 2. Limpieza y segmentación · 21–23 de octubre

| ID | Tarea y criterio de cierre | Depende de | Responsable | Estado |
| :--- | :--- | :--- | :--- | :--- |
| T06 | Implementar limpieza reproducible sin sobrescribir originales. Validar claves, duplicados, rangos, denominadores y consistencia de totales; distinguir cero, faltante y dato suprimido. Cierre: tabla analítica y reporte de exclusiones, transformaciones y comprobaciones. | T04, T05 | Por asignar | Pendiente |
| T07 | Comparar soluciones de segmentación candidatas para 4, 5 y 6 perfiles. Justificar variables, escalado, ponderaciones y método; fijar semillas cuando corresponda. Evaluar separación, estabilidad ante cambios razonables, tamaños e interpretabilidad. Cierre: comparación documentada, no solo ejecución del algoritmo. | T06 | Por asignar | Pendiente |
| T08 | Seleccionar la solución y exportar resultados agregados con identificadores y métricas trazables. Cierre: 4 a 6 perfiles diferenciados y limitaciones explícitas. Si no hay una solución defendible, revisar variables o método y registrar el bloqueo; no inventar diferencias para cumplir el número. | T07 | Por asignar | Pendiente |

### 3. Interpretación y entregables · 24–27 de octubre

| ID | Tarea y criterio de cierre | Depende de | Responsable | Estado |
| :--- | :--- | :--- | :--- | :--- |
| T09 | Nombrar y describir cada perfil con tamaño, composición, patrón de participación y evidencia numérica. Cierre: 4 a 6 descripciones no estigmatizantes; distinguir observaciones de hipótesis sociológicas y evitar inferencias individuales o causales no sustentadas. | T08 | Por asignar | Pendiente |
| T10 | Formular estrategias institucionales diferenciadas por perfil. Cierre: cada estrategia vincula evidencia, barrera hipotética, acción, canal, requerimientos razonables e indicador de evaluación; no presentar impactos hipotéticos como demostrados. | T09 | Por asignar | Pendiente |
| T11 | Completar el documento técnico iniciado en T05: fuentes, unidad de análisis, limpieza, metodología y validación, perfiles, estrategias, supuestos, limitaciones y referencias. Cierre: borrador PDF de **8 a 12 cuartillas, Arial/Calibri 11 e interlineado 1.5**. | T06, T08, T09, T10 | Por asignar | Pendiente |
| T12 | Diseñar y exportar las Fichas de Perfil con resumen narrativo e iconográfico de cada segmento, indicadores y fuentes. Cierre: archivos **PDF/PNG de alta resolución**, legibles al tamaño de entrega y con cifras coincidentes con el análisis. La convocatoria no fija dimensiones ni DPI; documentar la exportación elegida. | T09, T10 | Por asignar | Pendiente |
| T13 | Elaborar la presentación ejecutiva. Cierre: **máximo 10 diapositivas** que expliquen problema, datos, método, perfiles, estrategias, utilidad institucional y limitaciones, con cifras consistentes con el documento y las fichas. | T08, T09, T10 | Por asignar | Pendiente |

**Decisión de alcance:** evaluar una web únicamente después de contar con los borradores de T11–T13 y sin comprometer T14–T17. Si no hay capacidad, entregar las fichas estáticas; son el producto visual obligatorio del Reto 1.

### 4. Verificación e integración · 28–29 de octubre

| ID | Tarea y criterio de cierre | Depende de | Responsable | Estado |
| :--- | :--- | :--- | :--- | :--- |
| T14 | Ejecutar el análisis desde los datos originales en un entorno limpio siguiendo las instrucciones. Cierre: dependencias y pasos documentados, comprobaciones aprobadas y resultados reproducibles; explicar cualquier variación numérica esperable. Revisar que código, salidas y material compartido no incluyan datos personales ni credenciales. | T08, T11, T12, T13 | Por asignar | Pendiente |
| T15 | Revisar todos los materiales contra la lista de entrega y la rúbrica; corregir inconsistencias. Cierre: documento y presentación finales, fichas legibles, cartas completas y código accesible mediante archivos o enlace verificable, según la modalidad elegida. | T02, T11, T12, T13, T14 | Por asignar | Pendiente |
| T16 | Empaquetar y abrir de nuevo el `.zip`, identificado con el nombre del equipo y el eje temático. Cierre: archivo íntegro, PDFs/PNG legibles, inventario completo y permisos de lectura comprobados si se usan enlaces; sin archivos temporales ni secretos. | T15 | Por asignar | Pendiente |

### 5. Envío y contingencia · 30–31 de octubre

| ID | Tarea y criterio de cierre | Depende de | Responsable | Estado |
| :--- | :--- | :--- | :--- | :--- |
| T17 | **Enviar el 30 de octubre** el paquete final a **grecia.castro@ine.mx** y **cirse.rodriguez@ine.mx**, exclusivamente por correo electrónico según la convocatoria. Cierre: conservar copia del correo enviado y del paquete exacto; comprobar avisos de rechazo o rebote y guardar acuse si se recibe. Un correo enviado no demuestra por sí solo recepción. | T01, T16 | Por asignar | Pendiente |
| T18 | Reservar el **31 de octubre** para resolver incidencias de entrega antes de las **23:59 horas**. Si hay un problema, contactar a la organización y seguir sus indicaciones; no suponer prórroga ni recepción. Cierre: registrar el resultado y cualquier incertidumbre pendiente. | T17 | Por asignar | Pendiente |

## Lista de control del paquete final

La omisión de entregables mínimos obligatorios es causa de descalificación. Verificar el contenido real del paquete, no solo el estado del tablero.

- [ ] Documento técnico PDF de 8 a 12 cuartillas, Arial/Calibri 11, interlineado 1.5, con metodología, 4 a 6 perfiles y estrategias diferenciadas.
- [ ] Fichas de todos los perfiles en PDF/PNG de alta resolución, con resumen narrativo e iconográfico.
- [ ] Presentación ejecutiva de máximo 10 diapositivas.
- [ ] Código o enlace al repositorio correspondiente, con acceso comprobado e instrucciones de reproducción.
- [ ] Carta de cesión de derechos firmada por todas las personas integrantes.
- [ ] Carta declaratoria de decir verdad firmada por todas las personas integrantes.
- [ ] Solo datos agregados y disociados en el análisis; sin datos personales ni credenciales en el código, salidas o repositorio público. Las cartas administrativas se conservan en el paquete de envío, no en el repositorio público.
- [ ] Cifras, nombres de perfiles y fuentes consistentes entre análisis, documento, fichas y presentación.
- [ ] `.zip` identificado con nombre del equipo y eje temático, abierto y verificado después del empaquetado.
- [ ] Envío a ambos correos dentro del plazo, con copia conservada y revisión de incidencias.

## Fuentes de los requisitos

- [Convocatoria](Convocatoria_Hackaton-1.pdf): bases primera y quinta (participación y registro), cuarta (Reto 1), sexta (entregables), séptima (envío) y octava (evaluación).
- [Rúbrica de evaluación](<Rúbrica de evaluación_Hackaton .pdf>): distribución de puntos y niveles de desempeño.
