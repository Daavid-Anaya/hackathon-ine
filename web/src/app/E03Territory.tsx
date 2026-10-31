import { useState } from 'react';
import './E03Territory.css';

const BARRIER = { TRAVEL: 'travel', WAITING: 'waiting', INFORMATION: 'information' } as const;
type BarrierId = (typeof BARRIER)[keyof typeof BARRIER];

interface TerritorialMeasure {
  id: BarrierId;
  barrier: string;
  title: string;
  action: string;
  resources: string;
  channels: string;
  validation: string;
}

interface DemoCommunity {
  id: string;
  label: string;
  name: string;
  context: string;
  barriers: readonly BarrierId[];
}

const measures: readonly TerritorialMeasure[] = [
  {
    id: BARRIER.TRAVEL, barrier: 'Traslado y dispersión', title: 'Evaluar cercanía territorial',
    action: 'Inspeccionar los accesos y estudiar la factibilidad de una casilla extraordinaria. El escenario no decide su instalación.',
    resources: 'Recorridos de campo, revisión de rutas y coordinación distrital.',
    channels: 'Asambleas comunitarias, módulos itinerantes y cartelería de acceso abierto.',
    validation: 'Dictamen técnico de la Junta Distrital y acuerdo del Consejo Distrital, dentro del calendario aplicable. No se emiten desde este demostrador.',
  },
  {
    id: BARRIER.WAITING, barrier: 'Espera con acompañantes', title: 'Preparar una espera segura y sombreada',
    action: 'Estudiar áreas de espera exteriores con sombra para personas que acuden con acompañantes. No implica ofrecer un servicio de cuidado de menores.',
    resources: 'Mobiliario, sombra, señalización y revisión de la circulación.',
    channels: 'Información comunitaria abierta y señalización en el recinto del escenario.',
    validation: 'Revisión logística y de seguridad del espacio por responsables institucionales antes de un piloto, sin obstruir accesos.',
  },
  {
    id: BARRIER.INFORMATION, barrier: 'Información oral o bilingüe', title: 'Adaptar los canales de información',
    action: 'Explorar información oral y materiales bilingües cuando un diagnóstico territorial lo justifique.',
    resources: 'Personal bilingüe o interpretación, revisión lingüística y materiales claros.',
    channels: 'Radio comunitaria, asambleas y perifoneo de difusión general.',
    validation: 'Contraste comunitario de pertinencia y revisión institucional de contenidos. El perfil analítico no permite deducir la lengua de una comunidad.',
  },
];

const communities: readonly DemoCommunity[] = [
  { id: 'community-1', label: 'Ejemplo A · Dispersión', name: 'Comunidad ficticia A',
    context: 'El caso representa viviendas dispersas y posibles dificultades de traslado al punto de atención.', barriers: [BARRIER.TRAVEL] },
  { id: 'community-2', label: 'Ejemplo B · Espera', name: 'Comunidad ficticia B',
    context: 'El caso representa un recinto compartido donde algunas personas llegan con acompañantes y necesitan condiciones de espera adecuadas.', barriers: [BARRIER.WAITING] },
  { id: 'community-3', label: 'Ejemplo C · Información', name: 'Comunidad ficticia C',
    context: 'El caso plantea explorar formatos orales o bilingües, cuya pertinencia tendría que contrastarse localmente.', barriers: [BARRIER.INFORMATION] },
];

export function E03Territory() {
  const [communityId, setCommunityId] = useState(communities[0].id);
  const [selected, setSelected] = useState<BarrierId[]>([...communities[0].barriers]);
  const community = communities.find(item => item.id === communityId) ?? communities[0];
  const options = measures.filter(item => selected.includes(item.id));

  function chooseCommunity(value: string) {
    const next = communities.find(item => item.id === value);
    if (!next) return;
    setCommunityId(next.id);
    setSelected([...next.barriers]);
  }

  function toggleBarrier(id: BarrierId) {
    setSelected(previous => previous.includes(id) ? previous.filter(value => value !== id) : [...previous, id]);
  }

  return <div className="e03-territory">
    <p className="eyebrow">02 / La experiencia</p>
    <span className="status-chip">Ejemplo sintético</span>
    <h2 id="experience-title">Explorador territorial</h2>
    <p>Explora un caso comunitario, combina barreras hipotéticas y conoce qué medidas podrían estudiarse, con qué recursos y bajo qué condiciones.</p>
    <p className="small" id="e03-case-help">Los casos son inventados. No describen comunidades reales ni se deducen del perfil P03. No se utilizan ubicaciones ni datos personales.</p>
    <div className="e03-selector">
      <label htmlFor="e03-community">Comunidad ficticia</label>
      <select id="e03-community" name="demo-community" value={community.id} aria-describedby="e03-case-help" onChange={event => chooseCommunity(event.target.value)}>
        {communities.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}
      </select>
    </div>
    <section className="e03-context" aria-labelledby="e03-community-title">
      <p className="eyebrow">El contexto del ejemplo</p><h3 id="e03-community-title">{community.name}</h3><p>{community.context}</p>
    </section>
    <fieldset className="e03-barriers" aria-describedby="e03-barriers-help">
      <legend>Barreras del escenario</legend>
      <p className="small" id="e03-barriers-help">Puedes combinar o desmarcar las hipótesis. Al cambiar de comunidad se recupera la selección inicial de ese ejemplo.</p>
      {measures.map(item => <label key={item.id}>
        <input type="checkbox" name="e03-barrier" value={item.id} checked={selected.includes(item.id)} onChange={() => toggleBarrier(item.id)} />
        <span>{item.barrier}</span>
      </label>)}
    </fieldset>
    <section aria-labelledby="e03-options-title">
      <h3 id="e03-options-title">Opciones a estudiar</h3>
      <p className="e03-summary" role="status" aria-label="Resumen de medidas" aria-live="polite" aria-atomic="true">{options.length} {options.length === 1 ? 'opción' : 'opciones'} para estudiar.</p>
      {options.length === 0 ? <div className="e03-empty"><h4>Sin barreras seleccionadas</h4><p>Esto no demuestra que no existan barreras. Hace falta un diagnóstico territorial independiente.</p></div>
        : options.map(item => <article className="e03-measure" key={item.id} aria-labelledby={`e03-measure-${item.id}`}>
          <p className="eyebrow">{item.barrier}</p><h4 id={`e03-measure-${item.id}`}>{item.title}</h4><p>{item.action}</p>
          <dl><dt>Recursos necesarios</dt><dd>{item.resources}</dd><dt>Canales de acceso voluntario</dt><dd>{item.channels}</dd><dt>Condiciones y validación</dt><dd>{item.validation}</dd></dl>
        </article>)}
    </section>
    <p className="e03-warning">Ninguna selección aprueba la instalación de casillas ni sustituye un dictamen técnico.</p>
    <p className="small e03-disclaimer">Este recorrido no clasifica personas, calcula PACE ni predice participación electoral. No consulta SIJE ni otras fuentes operativas. Las selecciones se descartan al salir de E03 o recargar la página.</p>
  </div>;
}
