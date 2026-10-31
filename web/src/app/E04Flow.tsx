import { useState } from 'react';
import './E04Flow.css';

interface FlowStage {
  id: string;
  title: string;
  purpose: string;
  layout: string;
  support: string;
}

const stages: readonly FlowStage[] = [
  {
    id: 'access', title: 'Orientación y acceso',
    purpose: 'Explorar cómo distinguir la entrada y orientar hacia la mesa correspondiente sin bloquear el recorrido.',
    layout: 'Señalización diferenciada, accesos despejados y circulación compatible con personas con movilidad reducida.',
    support: 'Capacitación modular para orientar con claridad y trato respetuoso; coordinación con CAE para dudas operativas.',
  },
  {
    id: 'table', title: 'Mesa de atención',
    purpose: 'Reconocer el espacio de trabajo del funcionariado y su relación con el resto del circuito.',
    layout: 'Mobiliario dispuesto para distinguir la mesa de atención del paso hacia los espacios de votación, sin obstruir la circulación.',
    support: 'Iluminación adecuada, mobiliario ergonómico y preparación mediante simulacros. Este ejemplo no captura credenciales ni datos personales.',
  },
  {
    id: 'voting', title: 'Espacio de votación',
    purpose: 'Explorar una disposición que proteja la privacidad y mantenga accesibles los materiales reglamentarios.',
    layout: 'Canceles reglamentarios y cancel portátil de accesibilidad disponibles, sin bloquear el tránsito hacia las urnas. No se propone aumentar su número desde este esquema.',
    support: 'Preparación en el uso de materiales y orientación accesible, respetando el secreto del voto y las reglas institucionales aplicables.',
  },
  {
    id: 'exit', title: 'Urnas y salida',
    purpose: 'Distinguir el tramo hacia las urnas y la salida, sin representar un procedimiento electoral completo.',
    layout: 'Señalización hacia las urnas y la salida, con revisión de cruces de circulación y pasos libres.',
    support: 'Refrigerio, condiciones de trabajo y acompañamiento de CAE durante la jornada y el escrutinio, sujetos a coordinación y recursos institucionales.',
  },
];

export function E04Flow() {
  const [selectedId, setSelectedId] = useState(stages[0].id);
  const selectedIndex = stages.findIndex(item => item.id === selectedId);
  const selected = stages[selectedIndex];

  return <div className="e04-flow">
    <p className="eyebrow">02 / La experiencia</p>
    <span className="status-chip">Esquema ilustrativo</span>
    <h2 id="experience-title">Recorrido visual interactivo</h2>
    <p>Selecciona una etapa para explorar la organización del espacio y los apoyos propuestos al funcionariado de casilla.</p>
    <p className="small">El orden es una síntesis visual. Consulta el detalle de la etapa debajo del esquema o a su lado en pantallas amplias.</p>
    <p className="small">No es un plano real ni un protocolo electoral oficial.</p>
    <div className="e04-layout">
      <ol className="e04-steps" role="list" aria-label="Etapas del recorrido">
        {stages.map((stage, index) => <li key={stage.id}>
          <button type="button" aria-label={`Etapa ${index + 1}: ${stage.title}`} aria-pressed={selectedId === stage.id} aria-controls="e04-stage-detail" onClick={() => setSelectedId(stage.id)}>
            <span className="e04-number" aria-hidden="true">0{index + 1}</span><span>{stage.title}</span>
          </button>
          {index < stages.length - 1 ? <span className="e04-connector" aria-hidden="true">↓</span> : null}
        </li>)}
      </ol>
      <section className="e04-stage-panel" id="e04-stage-detail" aria-labelledby="e04-stage-title">
        <p className="eyebrow">Etapa en detalle</p><h3 id="e04-stage-title">{selected.title}</h3><p>{selected.purpose}</p>
        <dl><dt>Distribución del espacio</dt><dd>{selected.layout}</dd><dt>Apoyo al funcionariado</dt><dd>{selected.support}</dd></dl>
      </section>
    </div>
    <p className="e04-status" role="status" aria-label="Etapa seleccionada" aria-live="polite" aria-atomic="true">Etapa {selectedIndex + 1} de {stages.length}: {selected.title}.</p>
    <section className="e04-conditions" aria-labelledby="e04-conditions-title">
      <h3 id="e04-conditions-title">Antes de un piloto</h3>
      <ul><li>Revisión y aprobación institucional de la guía de distribución y de los materiales de capacitación.</li><li>Inspección del inmueble, accesos, circulación y materiales reglamentarios; el esquema no sustituye esa revisión.</li><li>Presupuesto y coordinación para mobiliario, iluminación, refrigerio y acompañamiento al funcionariado.</li></ul>
    </section>
    <p className="e04-warning">Este esquema no mide filas ni estima tiempos de espera.</p>
    <p className="small e04-disclaimer">Tampoco calcula TAP ni demuestra mejoras en la permanencia del funcionariado o en el voto. No consulta SICE ni registra información personal. La etapa seleccionada se descarta al recargar o salir de E04.</p>
  </div>;
}
