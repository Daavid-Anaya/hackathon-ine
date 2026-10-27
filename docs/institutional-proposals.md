# T10 — Propuestas y estrategias institucionales de fomento a la participación

**Documento técnico de propuestas institucionales. Formulación para el Reto 1 del Hackathon INE.**
Se articulan cinco estrategias institucionales diferenciadas correspondientes a los perfiles analíticos P01–P05 derivados de los Conteos Censales de Participación Ciudadana (CCPC 2024), complementadas con medidas transversales de información y accesibilidad institucional.

---

## 1. Alcance y marco metodológico

Para dar cabal cumplimiento a la convocatoria y la rúbrica de evaluación del Reto 1 (*"Estrategias diferenciadas de fomento a la participación para cada perfil"*), este documento formula intervenciones operativas e institucionales diferenciadas según las características estructurales, demográficas y territoriales observadas en cada grupo.

### Principios de formulación institucional:
1. **Atribuciones constitucionales y régimen normativo:** Las propuestas se circunscriben a los ámbitos de competencia del INE (organización electoral, logística de casillas, Registro Federal de Electores, capacitación cívica y divulgación neutral). Para garantizar la viabilidad institucional, cada estrategia explicita su anclaje en la Ley General de Instituciones y Procedimientos Electorales (LGIPE) y el Reglamento de Elecciones, distinguiendo las facultades operativas vigentes de aquellas que requieren la aprobación de Acuerdos específicos del Consejo General o dictámenes de los Consejos Distritales.
2. **Distinción estricta entre modelo, caracterización e hipótesis externas:** La segmentación se ajustó exclusivamente sobre la tasa de participación conocida (`participation_pct`) de los grupos agregados. Edad, sexo y entidad identifican y caracterizan las unidades de observación, mientras que el tipo de sección (U/M/R) se incorporó con posterioridad como descriptor; ninguna de estas dimensiones formó parte de la métrica de distancia del clustering. Asimismo, los datos censales de CCPC **no contienen variables de ocupación, turnos laborales, trabajo de cuidados no remunerado, pertenencia étnica o lingüística, discapacidad ni tiempos de espera en casilla**. En consecuencia, las barreras señaladas **no son hallazgos del clustering**, sino hipótesis operativas externas que requieren contraste empírico propio. Etiquetarlas como hipótesis es una salvaguarda de formulación, no una garantía de inmunidad ante la falacia ecológica; por ello, se prohíbe asumir que las condiciones de una hipótesis aplican de manera homogénea a todas las personas integrantes de un perfil.
3. **Indicadores de servicio, no promesas de votación:** Los indicadores de evaluación miden cobertura, puntualidad, accesibilidad y eficiencia operativa del servicio institucional. No se prometen incrementos hipotéticos en tasas de voto, ya que el ejercicio del sufragio es un derecho libre y secreto no determinable por un modelo de agrupamiento.
4. **Condición de propuesta en la medición operativa:** Los sistemas institucionales citados (SIIRFE, SIJE, SICE, UTSI) representan fuentes propuestas sujetas a dictamen técnico de factibilidad; su mención no certifica que dispongan inmediatamente de los campos requeridos ni exime de fijar universo, ventana temporal y regla de denominador cero («No aplica»).
5. **Privacidad, protección de datos y prohibición de contacto proactivo:** En estricto apego a la Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados (LGPDPPSO) y a la reserva confidencial del Padrón Electoral, **queda prohibido el contacto proactivo individualizado (*push*) mediante SMS, mensajería dirigida, llamadas telefónicas o georreferenciación de personas**. Las intervenciones no profilean ni discriminan individualmente a la ciudadanía; operan exclusivamente a través de canales institucionales abiertos y de acceso voluntario (*pull*), optimizando la infraestructura y logística en demarcaciones territoriales agregadas sin recabar ni tratar datos personales de contacto a partir de los perfiles.

---

## 2. Evidencia disponible y límites analíticos

| Referencia | Evidencia documental | Qué permite sustentar | Qué NO permite concluir |
| :--- | :--- | :--- | :--- |
| **E1** | [T09: Interpretación de perfiles](profile-interpretation.md) | Composición agregada de LN por edad, sexo, entidades de presencia y tipo de sección (U/M/R) en 2024. | Motivos individuales de abstención, apatía, preferencias políticas o desinterés ciudadano. |
| **E2** | [T07/T08: Contexto histórico](historical-robustness.md) | Comportamiento y estabilidad relativa de estratos entre elecciones (2009–2024). | Trayectorias individuales o cohortes longitudinales de seguimiento de votantes. |
| **E3** | [Revisión de divulgación](disclosure-review.md) | Requisitos de protección de datos agregados y disociados para uso público y reproducible. | Publicación de microdatos individuales o reclasificación nominal de casillas. |
| **E4** | [Auditoría de variables T04](data-audit.md) | Disponibilidad exclusiva de agregados demográficos (edad, sexo, LN) y estatus de sufragio (SV, NV, NS). | Medición censal de turnos fabriles, ocupación laboral, cuidados, discapacidad o tiempos de traslado. |

---

## 3. Estrategias institucionales diferenciadas (E01 a E05)

### E01 — Flexibilidad operativa en credencialización y justificación cívico-laboral (Perfil P01)

| Dimensión | Detalle de la formulación |
| :--- | :--- |
| **Perfil meta** | **P01 — Menor participación observada** (`CCPC-2024-K5-P01`). |
| **Evidencia observada** | Representa el **13.5% de la LN elegible** con **40.3% de participación conocida** (la más baja de la solución). Concentración en adultos jóvenes: **60.0% en 25–34 años** y **36.0% en 18–24 años** (96% sub-35). Marcada composición masculina en la LN (**92.1% hombres**). Mayoritariamente urbano (**66.2%**), con presencia en 25 entidades federativas. |
| **Barrera hipotética** | *(Hipótesis operativa externa no observada en los CCPC; sujeta a contraste empírico propio)*. Alta movilidad por inserción laboral o estudiantil; desactualización de domicilio en la Credencial para Votar; posibles restricciones de horario por jornadas laborales de fin de semana en sectores fabriles o de servicios que dificultarían acudir a los Módulos de Atención Ciudadana (MAC) o a la casilla. |
| **Acción institucional diferenciada** | **Programa de Flexibilidad Operativa en MAC y Justificación Cívico-Laboral:**<br>1. Extensión de horarios de atención vespertina (hasta las 20:00 hrs) y apertura sabatina/dominical en MAC ubicados en corredores de alta actividad fabril, comercial y universitaria.<br>2. Habilitación de esquema exprés de reimpresión de credencial por robo o extravío sin cita previa en los últimos 60 días antes de la jornada electoral.<br>3. Convenios institucionales entre el INE, secretarías del trabajo locales y cámaras patronales (e.g., CCE, CONCAMIN) para emitir cartas de justificación y acuerdos de permiso remunerado para votar en centros de trabajo con turno dominical. |
| **Canales idóneos** | Módulos móviles de credencialización del RFE instalados en áreas comunes de parques industriales y campus universitarios; cartelería física informativa en centros de trabajo y transporte público metropolitano; avisos de difusión general en el portal institucional del INE y mesas de concertación laboral (canales abiertos de acceso voluntario, sin contacto individualizado ni rastreo). |
| **Requerimientos razonables** | Convenio marco con cámaras industriales y comerciales; reasignación presupuestal para compensación de horas extraordinarias del personal de los MAC seleccionados; campañas focalizadas de trámite de credencial en períodos preelectorales. |
| **Fundamento normativo e instrumento requerido** | **Fundamento:** LGIPE arts. 126 y 138–144 (atribuciones de la DERFE para expedición de credenciales y ubicación de módulos); art. 44, num. 1, inc. k (atribución de la Presidencia del Consejo General para suscribir convenios); Ley Federal del Trabajo art. 132, fracc. IX (obligación patronal de conceder tiempo para votar).<br>**Instrumento de instrumentación:** Acuerdo del Consejo General que apruebe el Plan Integral y Calendario de Actualización del Padrón Electoral (horarios y esquemas sin cita de reimpresión), junto con el convenio marco institucional suscrito con cámaras patronales. |
| **Indicador de evaluación** | $$\text{Tasa de Cobertura en Horario Extendido (TCHE)} = 100 \times \frac{\text{Trámites realizados en MAC seleccionados en sábado, domingo o turno vespertino}}{\text{Total de trámites de credencialización en los MAC seleccionados}}$$ **Especificación de propuesta operativa:**<br>• *Universo:* Módulos de Atención Ciudadana (fijos y móviles) en los distritos urbanos prioritarios.<br>• *Ventana temporal:* Campaña Anual Intensa y período extraordinario de credencialización (septiembre a febrero previo a la elección).<br>• *Denominador cero:* Si no se registran trámites totales en los módulos evaluados en el período, registrar «No aplica» (N/A), no cero.<br>• *Fuente institucional propuesta:* SIIRFE (la disponibilidad del desglose horario por módulo queda sujeta a dictamen técnico de la DERFE). |

---

### E02 — Información ejecutiva móvil y certidumbre logística en tiempo real (Perfil P02)

| Dimensión | Detalle de la formulación |
| :--- | :--- |
| **Perfil meta** | **P02 — Participación observada intermedia-baja** (`CCPC-2024-K5-P02`). |
| **Evidencia observada** | Representa el **21.5% de la LN elegible** con **50.1% de participación conocida**. Estructura etaria equilibrada en rangos productivos: **36.5% en 25–34 años**, **33.3% en 35–44 años** y **27.0% en 18–24 años**. Mayoría masculina (**60.8% hombres**). Presente en 30 entidades federativas y predominantemente urbano (**69.4%**). |
| **Barrera hipotética** | *(Hipótesis operativa externa no observada en los CCPC; sujeta a contraste empírico propio)*. Tensión de tiempo por coexistencia de responsabilidades laborales y familiares; posible incertidumbre sobre el tiempo de espera y las filas en la casilla; necesidad de información sintética e imparcial sobre candidaturas locales. |
| **Acción institucional diferenciada** | **Herramienta Digital "Tu Tiempo y Tu Casilla":**<br>1. Optimización móvil de alta velocidad para la consulta de ubicación de casilla con indicador estimado de afluencia o recomendación de franjas horarias de menor fila.<br>2. Fichas de síntesis ejecutiva, estandarizadas y neutras, de plataformas registradas por candidatura en el sistema "Candidatas y Candidatos, Conóceles", diseñadas para lectura ágil en pantallas móviles.<br>3. Difusión de rutas de transporte público y alternativas de movilidad hacia los centros de votación urbanos. |
| **Canales idóneos** | Asistente virtual institucional automatizado (Chatbot Inés en WhatsApp sin consumo de datos excesivo); cartelería con código QR de acceso directo instalada en parabuses y estaciones de transporte masivo; micrositio móvil ligero. |
| **Requerimientos razonables** | Pruebas de carga y redundancia en servidores del INE para soportar picos de concurrencia el día de la jornada electoral; diseño UX/UI accesible enfocado en bajo consumo de datos; personal de soporte técnico y actualización continua de bases de datos. |
| **Fundamento normativo e instrumento requerido** | **Fundamento:** LGIPE art. 62 (atribuciones de la UTSI para desarrollo de sistemas y telecomunicaciones); art. 32 (acceso a la información pública electoral); Reglamento de Elecciones art. 23 bis (operación obligatoria del Sistema "Candidatas y Candidatos, Conóceles").<br>**Instrumento de instrumentación:** Lineamientos técnicos y operativos aprobados conjuntamente por la Comisión de Organización Electoral y la Comisión de Tecnologías de la Información. |
| **Indicador de evaluación** | $$\text{Disponibilidad y Rendimiento de Consulta (DRC)} = 100 \times \frac{\text{Consultas a ubicación y candidaturas resueltas con tiempo } \le 2.0\text{ s}}{\text{Total de consultas entrantes a la plataforma}}$$ **Especificación de propuesta operativa:**<br>• *Universo:* Solicitudes HTTP recibidas en los servidores públicos de consulta electoral del INE.<br>• *Ventana temporal:* Día de la jornada electoral (de 07:00 a 19:00 hrs).<br>• *Denominador cero:* Si no se reciben solicitudes en la ventana, registrar «No aplica» (N/A).<br>• *Fuente institucional propuesta:* Registros de telemetría y logs de balanceadores de la UTSI (sujeto a capacidades de instrumentación y retención de logs). |

---

### E03 — Facilitación territorial y corresponsabilidad comunitaria (Perfil P03)

| Dimensión | Detalle de la formulación |
| :--- | :--- |
| **Perfil meta** | **P03 — Participación observada intermedia** (`CCPC-2024-K5-P03`). |
| **Evidencia observada** | Representa el **23.5% de la LN elegible** con **59.5% de participación conocida**. Composición etaria amplia (adultez media predominante): **28.4% en 45–59 años**, **25.0% en 35–44 años**, **22.1% en 25–34 años**. Mayoría femenina (**60.6% mujeres**). Presente en 31 entidades. Destaca por una **alta presencia rural (18.7%)** (superada solo por P01 con 19.3%) y la mayor brecha bruta rural vs. urbana entre los cinco perfiles (**62.3% rural frente a 58.9% urbana**, amplitud de 3.4 pp). |
| **Barrera hipotética** | *(Hipótesis operativa externa no observada en los CCPC; sujeta a contraste empírico propio)*. Dispersión geográfica y costos de traslado en secciones rurales y mixtas; posibles cargas de cuidado doméstico no remunerado que compiten con el tiempo de desplazamiento; necesidad de información en formatos orales o lenguas originarias. |
| **Acción institucional diferenciada** | **Plan de Cercanía Territorial y Apoyo Comunitario:**<br>1. Instalación prioritaria de casillas extraordinarias y especiales en localidades rurales o mixtas con aislamiento geográfico superior a 45 minutos de camino respecto de la cabecera seccional.<br>2. Habilitación de áreas de espera seguras y sombreadas en el exterior de las casillas comunitarias para facilitar la estancia de personas acompañadas por menores o dependientes durante el ejercicio del voto.<br>3. Distribución de materiales cívicos e informativos sobre la ubicación y horario de casillas mediante formatos bilingües (lenguas originarias donde aplique) y perifoneo comunitario en coordinación con autoridades tradicionales. |
| **Canales idóneos** | Asambleas ejidales y comunitarias; módulos de credencialización itinerantes del RFE; radiodifusoras comunitarias e indigenistas (INPI); cartelería en tiendas rurales comunitarias (Diconsa/Liconsa). |
| **Requerimientos razonables** | Coordinación logística con Consejos Distritales para la aprobación e inspección anticipada de rutas de acceso a casillas extraordinarias; material de señalización resistente a la intemperie; personal bilingüe o intérpretes en zonas con población indígena. |
| **Fundamento normativo e instrumento requerido** | **Fundamento:** LGIPE art. 256, nums. 1 y 2 (facultad expresa de los Consejos Distritales para acordar la instalación de casillas extraordinarias cuando las condiciones geográficas, de infraestructura o socioculturales dificulten el acceso); art. 258 (publicación formal de listas de ubicación).<br>**Instrumento de instrumentación:** Dictamen técnico de factibilidad emitido por la Junta Distrital Ejecutiva respectiva y Acuerdo de aprobación del Consejo Distrital correspondiente dentro del calendario electoral. |
| **Indicador de evaluación** | $$\text{Puntualidad en Apertura de Casillas Extraordinarias (PACE)} = 100 \times \frac{\text{Casillas extraordinarias con reporte de instalación antes de las 08:30 hrs}}{\text{Total de casillas extraordinarias aprobadas por el Consejo Distrital}}$$ **Especificación de propuesta operativa:**<br>• *Universo:* Secciones rurales y mixtas con casillas extraordinarias aprobadas por los Consejos Distritales.<br>• *Ventana temporal:* Primer corte del reporte de instalación (08:30 hrs del día de la elección).<br>• *Denominador cero:* Si el Consejo Distrital no aprobó casillas extraordinarias en la demarcación (denominador = 0), registrar «No aplica» (N/A). Si se aprobaron casillas pero ninguna reportó apertura a tiempo o no se instalaron, el indicador arroja 0.0%, no «No aplica».<br>• *Fuente institucional propuesta:* SIJE (módulo de instalación; sujeta a cobertura de comunicación telefónica/móvil de los CAE). |

---

### E04 — Agilización de flujo en casillas densas y fortalecimiento del funcionariado (Perfil P04)

| Dimensión | Detalle de la formulación |
| :--- | :--- |
| **Perfil meta** | **P04 — Participación observada intermedia-alta** (`CCPC-2024-K5-P04`). |
| **Evidencia observada** | **Es el perfil más grande de la Lista Nominal (25.4% de la LN)**, con una participación destacada de **67.3%**. Concentrado en edades maduras: **42.7% en 45–59 años** y **28.6% en 60 años o más** (71.2% de 45 años o más). Predominio de mujeres (**68.0% mujeres**). Presencia en 31 entidades y fuertemente urbano (**69.7%**). |
| **Barrera hipotética** | *(Hipótesis operativa externa no observada en los CCPC; sujeta a contraste empírico propio)*. Posible saturación física y cuellos de botella en secciones urbanas con Listas Nominales muy grandes; tiempos prolongados de espera de pie; eventual declinación o deserción de la ciudadanía insaculada para integrar Mesas Directivas de Casilla (FMDC) ante la complejidad de las actas y las largas jornadas de escrutinio. |
| **Acción institucional diferenciada** | **Optimización del Flujo Electoral y Respaldo Integral al FMDC:**<br>1. Optimización del circuito de votación y disposición espacial de canceles electorales en inmuebles urbanos con múltiples casillas contiguas, garantizando el aprovechamiento simultáneo de los módulos de votación reglamentarios y la operación continua del cancel portátil de accesibilidad sin obstruir el tránsito hacia las urnas.<br>2. Rediseño ergonómico de la estación de votación urbana con señalización diferenciada para la entrega de credencial, canceles y depósito en urnas, evitando aglomeraciones.<br>3. Paquete integral de apoyo al funcionariado de casilla (FMDC): capacitación modular presencial y digital, dotación adecuada de mobiliario, iluminación, refrigerio y acompañamiento continuo de Capacitadores Asistentes Electorales (CAE) durante el escrutinio. |
| **Canales idóneos** | Talleres de capacitación ciudadana en centros vecinales; comunicación directa de los CAE con funcionarias/os insaculados; módulos distritales de atención fija; medios masivos locales de comunicación. |
| **Requerimientos razonables** | Guía técnica de distribución de espacios aprobada por la Dirección Ejecutiva de Organización Electoral (DEOE) para sedes con alta concentración de casillas contiguas; presupuesto para dotación alimentaria y kits ergonómicos del FMDC; calendarización flexible de simulacros electorales. |
| **Fundamento normativo e instrumento requerido** | **Fundamento:** LGIPE arts. 81–87 (integración y atribuciones de las Mesas Directivas de Casilla); art. 253, nums. 1 y 2 (regla de instalación de casillas básicas y contiguas por cada 750 electores); Reglamento de Elecciones Anexo 4.1 (diseño técnico de canceles modulares).<br>**Instrumento de instrumentación:** Guía Técnica de Distribución de Espacios y Adendas al Manual de la y el Funcionario de Casilla aprobadas por la DEOE y la DECEYEC. |
| **Indicador de evaluación** | $$\text{Tasa de Aceptación y Permanencia de FMDC (TAP)} = 100 \times \frac{\text{Personas ciudadanas capacitadas que integraron efectivamente la casilla}}{\text{Total de cargos requeridos de propietarios y suplentes en la demarcación}}$$ **Especificación de propuesta operativa:**<br>• *Universo:* Secciones urbanas consolidadas con concentración de casillas contiguas.<br>• *Ventana temporal:* Conclusión de la segunda etapa de capacitación electoral (mayo a jornada electoral).<br>• *Denominador cero:* Si no se aprueban casillas en la demarcación, registrar «No aplica» (N/A), no cero.<br>• *Fuente institucional propuesta:* SICE (sujeto a los tiempos de captura de sustituciones en las Juntas Distritales). |

---

### E05 — Protocolo de accesibilidad universal y trato preferencial (Perfil P05)

| Dimensión | Detalle de la formulación |
| :--- | :--- |
| **Perfil meta** | **P05 — Mayor participación observada** (`CCPC-2024-K5-P05`). |
| **Evidencia observada** | Representa el **16.1% de la LN elegible** y ostenta la **mayor participación observada: 76.3%**. Mayoritariamente integrado por personas adultas mayores: **61.0% de 60 años o más** y **37.2% en 45–59 años** (98.1% de 45 años o más). Fuerte predominio femenino (**67.9% mujeres**). Mayoritariamente urbano (**73.4%**), presente en 17 entidades federativas. |
| **Barrera hipotética** | *(Hipótesis operativa externa no observada en los CCPC; sujeta a contraste empírico propio)*. Barreras arquitectónicas en locales sede (escalones, rampas deterioradas, falta de pasamanos); fatiga por esperas de pie bajo condiciones climáticas adversas; requerimiento de elementos auxiliares de visión (lupas) o plantillas en sistema Braille para sufragio autónomo. |
| **Acción institucional diferenciada** | **Protocolo de Accesibilidad Universal y Atención Preferencial en Casilla:**<br>1. Criterio vinculante de accesibilidad: obligación de instalar el 100% de las casillas en plantas bajas, con acceso a nivel de piso libre de desniveles pronunciados o con rampas funcionales comprobadas.<br>2. Garantía y disponibilidad visible de aditamentos de accesibilidad: mamparas especiales para personas con movilidad reducida o en silla de ruedas, lupas de aumento para lectura de boletas y plantillas en sistema Braille.<br>3. Aplicación estricta y supervisada del derecho a fila preferencial sin espera para personas adultas mayores, habilitando sillas de descanso techadas en el perímetro inmediato de la mesa de votación. |
| **Canales idóneos** | Verificación física y documental de inmuebles por parte de las Juntas Distritales Ejecutivas (Cédula de Inspección); colaboración informativa en centros de día, clubes de personas mayores (INAPAM), salas de espera de unidades de medicina familiar (IMSS, ISSSTE) y plazas cívicas. |
| **Requerimientos razonables** | Auditoría física de locales antes de la aprobación del Consejo Distrital; compra centralizada y distribución oportuna de kits de accesibilidad (lupas, plantillas, mamparas adaptadas); instrucción específica en el manual de los CAE para supervisar la aplicación de la fila preferencial. |
| **Fundamento normativo e instrumento requerido** | **Fundamento:** LGIPE art. 255, num. 1, inc. a (requisito de libre y fácil acceso físico para toda la ciudadanía); Reglamento de Elecciones Anexo 4.1 (dotación obligatoria de mampara especial, lupa de aumento y plantilla Braille); Protocolo para la Inclusión de Personas con Discapacidad del INE.<br>**Instrumento de instrumentación:** Cédula de Verificación de Inmuebles de aplicación vinculante por las Juntas Distritales Ejecutivas y Acuerdos de aprobación de sedes por los Consejos Distritales. |
| **Indicador de evaluación** | $$\text{Cumplimiento de Estándares de Accesibilidad Física (CEAF)} = 100 \times \frac{\text{Casillas verificadas en planta baja con acceso libre de desniveles o con rampa}}{\text{Total de casillas instaladas en el distrito}}$$ **Especificación de propuesta operativa:**<br>• *Universo:* Total de casillas aprobadas e instaladas en la demarcación distrital.<br>• *Ventana temporal:* Recorridos distritales de examinación (febrero–abril) y validación en la apertura de casillas el día de la jornada.<br>• *Denominador cero:* Si no se instalan casillas en la demarcación, registrar «No aplica» (N/A), no cero.<br>• *Fuente institucional propuesta:* Cédula de Verificación de Inmuebles y reporte del SIJE (sujeto a la homologación de criterios técnicos por la DEOE). |

---

## 4. Medidas institucionales transversales (G01 a G03)

Para garantizar que las estrategias diferenciadas no comprometan los principios de neutralidad institucional ni generen exclusión involuntaria, se mantienen como salvaguardas permanentes las tres medidas generales de servicio público:

1. **G01 — Información oficial verificable y actualizada:** Directorio factual público sobre requisitos, fechas límite de credencialización y ubicación de casillas, sometido a revisión de vigencia documental.
   $$\text{Vigencia Documental} = 100 \times \frac{\text{Entradas revisadas en el período}}{\text{Total de entradas publicadas}}$$
2. **G02 — Contenidos equivalentes en formatos accesibles:** Todo material impreso o digital debe disponer de alternativa seleccionable, legible por lectores de pantalla y versión en texto claro.
   $$\text{Cobertura de Revisión de Accesibilidad} = 100 \times \frac{\text{Materiales que aprueban la lista de verificación}}{\text{Total de materiales evaluados}}$$
3. **G03 — Orientación oportuna y corrección de dudas:** Canal institucional centralizado para resolver inquietudes técnicas y corregir inconsistencias reportadas por la ciudadanía sobre servicios y trámites.
   $$\text{Respuesta Oportuna} = 100 \times \frac{\text{Consultas respondidas dentro del plazo establecido}}{\text{Total de consultas válidas recibidas}}$$

---

## 5. Matriz resumen de articulación operativa

| Perfil | Estrategia | Eje central | Ámbito territorial prioritario | Métrica de servicio |
| :--- | :--- | :--- | :--- | :--- |
| **P01** (Menor part. / 40.3%) | **E01** | Flexibilidad de trámites y justificación laboral | Corredores urbanos e industriales (sub-35 años) | Tasa de trámites en horarios extendidos (TCHE) |
| **P02** (Intermedia-baja / 50.1%) | **E02** | Certeza de tiempos y fichas móviles de candidaturas | Áreas urbanas y metropolitanas (25–44 años) | Rendimiento y disponibilidad de consultas (DRC) |
| **P03** (Intermedia / 59.5%) | **E03** | Casillas extraordinarias y facilitación de cuidados | Secciones rurales y mixtas (mujeres y familias) | Puntualidad en apertura de casillas rurales (PACE) |
| **P04** (Intermedia-alta / 67.3%) | **E04** | Agilización de casillas densas y apoyo a FMDC | Zonas urbanas consolidadas (adultez 45+) | Permanencia y capacitación de FMDC (TAP) |
| **P05** (Mayor part. / 76.3%) | **E05** | Accesibilidad universal y fila prioritaria garantizada | Plantas bajas urbanas y centros comunitarios (60+) | Cumplimiento de accesibilidad física (CEAF) |

---

## 6. Estado de integración y comprobaciones de cierre

| Criterio de cierre del Reto 1 | Estado | Evidencia y justificación |
| :--- | :--- | :--- |
| **Estrategias diferenciadas por perfil** | **Cumplido** | Cinco estrategias (E01 a E05) vinculadas uno a uno con P01 a P05. |
| **Estructura metodológica de 6 campos** | **Cumplido** | Cada propuesta detalla evidencia, barrera hipotética, acción, canal, recursos e indicador verificable. |
| **Prevención de falacia ecológica e individual** | **En prevención activa / Límite metodológico reconocido** | Las barreras se formulan explícitamente como hipótesis operativas externas (no son hallazgos del clustering ni están medidas en los CCPC). Se prohíbe la imputación de necesidades individuales a partir de estratos agregados. |
| **Protección de datos y no perfilamiento individual** | **Salvaguarda de diseño incorporada / Pendiente de auditoría de tratamiento operativo** | Se excluye el contacto proactivo (*push*) y el perfilamiento individual. No obstante, el tratamiento de metadatos técnicos (direcciones IP, parámetros de búsqueda en formularios o logs de servidor) en las herramientas de consulta (*pull*) permanece sujeto a la emisión de Avisos de Privacidad y protocolos de seguridad conforme a la LGPDPPSO. |
| **Atribuciones y viabilidad institucional** | **Fundamentación referencial propuesta / Pendiente de cotejo con texto oficial** | Se identifican artículos e instrumentos normativos referenciales (LGIPE, Reglamento de Elecciones, LFT), pero su cotejo literal y vigencia puntual permanecen como propuesta técnica referencial hasta su validación documental con los textos oficiales del DOF. |
| **Indicadores operativos de calidad de servicio** | **Formulados a nivel de propuesta técnica** | Cuentan con fórmula matemática, universo, ventana temporal y regla de denominador cero («No aplica»). Su instrumentación real queda sujeta al dictamen técnico de disponibilidad de campos en los sistemas fuente propuestos (SIIRFE, SIJE, SICE, UTSI). |

Este documento concluye la **formulación técnica y metodológica de la tarea T10** para su integración en la **Sección 7 del Informe Técnico (T11)** y en las **Fichas de Perfil (T12)**. Dicho cierre documental no constituye ni sustituye la validación jurídica formal de los artículos citados, la aprobación presupuestal u operativa de los órganos ejecutivos del INE, ni la autorización de divulgación externa de materiales, las cuales permanecen sujetas a los dictámenes institucionales y a la revisión de divulgación correspondiente (T14–T15).
