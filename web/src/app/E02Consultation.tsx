import { useState } from 'react';
import './E02Consultation.css';

const CROWD = { LOW: 'low', MODERATE: 'moderate', HIGH: 'high', UNKNOWN: 'unknown' } as const;
type CrowdState = (typeof CROWD)[keyof typeof CROWD];

interface CrowdPresentation {
  label: string;
  explanation: string;
}

interface DemoStation {
  id: string;
  label: string;
  name: string;
  location: string;
  reference: string;
  accessibility: string;
  crowd: CrowdState;
}

const crowdPresentation: Record<CrowdState, CrowdPresentation> = {
  low: { label: 'Baja', explanation: 'El escenario representa poca afluencia. No permite deducir cuánto duraría una visita.' },
  moderate: { label: 'Moderada', explanation: 'El escenario representa una afluencia intermedia. No describe una fila observada.' },
  high: { label: 'Alta', explanation: 'El escenario representa mucha afluencia. No predice la duración de la espera.' },
  unknown: { label: 'Sin información', explanation: 'No hay datos de afluencia en este escenario. No significa que la afluencia sea baja.' },
};
const crowdChoices = [CROWD.LOW, CROWD.MODERATE, CROWD.HIGH, CROWD.UNKNOWN];
const stations: readonly DemoStation[] = [
  {
    id: 'example-a', label: 'Ejemplo A · Centro comunitario', name: 'Centro comunitario de ejemplo',
    location: 'Sector A de la localidad ficticia.',
    reference: 'Entrada principal frente a la plaza del escenario.',
    accessibility: 'Acceso a nivel de piso y pasillos amplios en el escenario.', crowd: CROWD.MODERATE,
  },
  {
    id: 'example-b', label: 'Ejemplo B · Escuela', name: 'Escuela de ejemplo',
    location: 'Sector B de la localidad ficticia.',
    reference: 'Entrada lateral junto al patio del escenario.',
    accessibility: 'Rampa por la entrada lateral en el escenario.', crowd: CROWD.LOW,
  },
  {
    id: 'example-c', label: 'Ejemplo C · Biblioteca', name: 'Biblioteca de ejemplo',
    location: 'Sector C de la localidad ficticia.',
    reference: 'Acceso principal por la calle peatonal del escenario.',
    accessibility: 'Acceso con escalones; ruta accesible pendiente de verificar en el escenario.', crowd: CROWD.UNKNOWN,
  },
];

export function E02Consultation() {
  const [stationId, setStationId] = useState(stations[0].id);
  const [crowd, setCrowd] = useState<CrowdState>(stations[0].crowd);
  const station = stations.find(item => item.id === stationId) ?? stations[0];
  const crowdInfo = crowdPresentation[crowd];

  function chooseStation(value: string) {
    const next = stations.find(item => item.id === value);
    if (!next) return;
    setStationId(next.id);
    setCrowd(next.crowd);
  }

  return <div className="e02-consultation">
    <p className="eyebrow">02 / La experiencia</p>
    <span className="status-chip">Ejemplo sintético</span>
    <h2 id="experience-title">Consulta móvil guiada</h2>
    <p>Elige una casilla ficticia, consulta su ficha y explora cómo se presentaría la afluencia en distintos escenarios.</p>
    <p className="small" id="e02-example-help">Los recintos, las ubicaciones y sus condiciones son inventados. No corresponden a casillas reales ni permiten saber dónde te corresponde votar.</p>
    <div className="e02-selector">
      <label htmlFor="e02-station">Casilla ficticia</label>
      <select id="e02-station" name="demo-station" value={station.id} aria-describedby="e02-example-help"
        onChange={event => chooseStation(event.target.value)}>
        {stations.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}
      </select>
    </div>
    <section className="e02-station-card" aria-labelledby="e02-station-name">
      <p className="eyebrow">La ficha del escenario</p>
      <h3 id="e02-station-name">{station.name}</h3>
      <dl>
        <dt>Ubicación de ejemplo</dt><dd>{station.location}</dd>
        <dt>Referencia de acceso</dt><dd>{station.reference}</dd>
        <dt>Horario del escenario</dt><dd>08:00–18:00 h · horario ilustrativo.</dd>
        <dt>Condiciones de accesibilidad</dt><dd>{station.accessibility}</dd>
      </dl>
      <p className="small">Estas condiciones no son una inspección física ni una garantía de accesibilidad.</p>
    </section>
    <fieldset className="e02-crowd-controls" aria-describedby="e02-crowd-help">
      <legend>Simular afluencia</legend>
      <p className="small" id="e02-crowd-help">Cambia el estado para explorar la presentación. Al elegir otra casilla se carga el estado inicial de ese ejemplo.</p>
      <div className="e02-crowd-options">{crowdChoices.map(value => <label key={value}>
        <input type="radio" name="e02-crowd" value={value} checked={crowd === value} onChange={() => setCrowd(value)} />
        <span>{crowdPresentation[value].label}</span>
      </label>)}</div>
    </fieldset>
    <div className="e02-crowd-result" role="status" aria-label="Estado de afluencia simulado" aria-live="polite" aria-atomic="true">
      <p className="eyebrow">Afluencia simulada</p><strong>{crowdInfo.label}</strong><p>{crowdInfo.explanation}</p>
    </div>
    <p className="e02-crowd-warning">No son datos en tiempo real ni estimaciones de espera.</p>
    <p className="small e02-disclaimer">Esta demostración no utiliza mapas externos, geolocalización ni sistemas del INE. No muestra fichas de candidaturas ni rutas de transporte. La selección y los cambios se descartan al salir de esta propuesta o recargar la página.</p>
  </div>;
}
