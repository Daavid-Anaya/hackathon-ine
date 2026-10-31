import { useState } from 'react';
import './E05Checklist.css';

const CONDITION = { ACCESS: 'access', BOOTH: 'booth', MAGNIFIER: 'magnifier', BRAILLE: 'braille', PRIORITY: 'priority', REST: 'rest' } as const;
type ConditionId = (typeof CONDITION)[keyof typeof CONDITION];
const STATE = { PRESENT: 'present', ABSENT: 'absent', PENDING: 'pending' } as const;
type ConditionState = (typeof STATE)[keyof typeof STATE];

interface AccessibilityCondition {
  id: ConditionId;
  label: string;
  description: string;
  fix: string;
  verify: string;
}

const conditions: readonly AccessibilityCondition[] = [
  {
    id: CONDITION.ACCESS, label: 'Acceso a nivel o con rampa funcional',
    description: 'Acceso a la casilla en planta baja, sin desniveles pronunciados o con una rampa funcional comprobada.',
    fix: 'Solicitar inspección y estudiar una sede accesible o un acondicionamiento validado. No dar por resuelto el acceso sin revisión física.',
    verify: 'Inspeccionar el recorrido de entrada, los desniveles y, cuando corresponda, la funcionalidad de la rampa.',
  },
  {
    id: CONDITION.BOOTH, label: 'Mampara adaptada',
    description: 'Mampara especial disponible y dispuesta para personas con movilidad reducida o en silla de ruedas.',
    fix: 'Gestionar la dotación y disposición de la mampara especial sin obstruir los accesos.',
    verify: 'Comprobar disponibilidad, ubicación y condiciones de uso de la mampara especial.',
  },
  {
    id: CONDITION.MAGNIFIER, label: 'Lupa de aumento',
    description: 'Lupa disponible para facilitar la lectura de materiales.',
    fix: 'Gestionar la dotación de la lupa y verificar que esté disponible en condiciones de uso.',
    verify: 'Comprobar presencia, estado y disponibilidad de la lupa para su uso.',
  },
  {
    id: CONDITION.BRAILLE, label: 'Plantilla Braille',
    description: 'Plantilla en sistema Braille disponible como apoyo para el sufragio autónomo.',
    fix: 'Gestionar la dotación de la plantilla Braille y revisar su disponibilidad y estado.',
    verify: 'Comprobar que la plantilla Braille correspondiente esté disponible y en condiciones de uso.',
  },
  {
    id: CONDITION.PRIORITY, label: 'Atención preferencial',
    description: 'Organización y señalización para la atención preferencial conforme a los protocolos aplicables.',
    fix: 'Preparar señalización y capacitación del funcionariado para aplicar la atención preferencial.',
    verify: 'Revisar la organización de la atención preferencial y la preparación del funcionariado.',
  },
  {
    id: CONDITION.REST, label: 'Sillas y sombra',
    description: 'Área de descanso con sillas y sombra, próxima al servicio y sin bloquear la circulación.',
    fix: 'Planear sillas y sombra en un espacio seguro, sin obstruir el paso ni los accesos.',
    verify: 'Inspeccionar la disponibilidad de sillas, sombra y condiciones de circulación segura.',
  },
];

const initialStates: Record<ConditionId, ConditionState> = {
  access: STATE.PENDING, booth: STATE.PENDING, magnifier: STATE.PENDING,
  braille: STATE.PENDING, priority: STATE.PENDING, rest: STATE.PENDING,
};

export function E05Checklist() {
  const [states, setStates] = useState(() => ({ ...initialStates }));
  const answers = Object.values(states);
  const present = answers.filter(value => value === STATE.PRESENT).length;
  const absent = answers.filter(value => value === STATE.ABSENT).length;
  const pending = answers.filter(value => value === STATE.PENDING).length;
  const followUp = conditions.filter(item => states[item.id] !== STATE.PRESENT);

  function changeCondition(id: ConditionId, value: string) {
    if (value !== STATE.PRESENT && value !== STATE.ABSENT && value !== STATE.PENDING) return;
    setStates(previous => ({ ...previous, [id]: value }));
  }

  return <div className="e05-checklist">
    <p className="eyebrow">02 / La experiencia</p>
    <span className="status-chip">Ejemplo sintético</span>
    <h2 id="experience-title">Lista de verificación de accesibilidad</h2>
    <h3>Sede ficticia de ejemplo</h3>
    <p>Practica cómo registrar condiciones de una sede. Al empezar, todas están pendientes: eso no significa que estén ausentes.</p>
    <p className="small" id="e05-help">Selecciona Presente, Ausente o Pendiente de verificar en cada condición. Son respuestas del escenario, no observaciones de un inmueble real. La accesibilidad aplica a todas las personas; el perfil P05 no permite inferir una discapacidad.</p>
    <fieldset className="e05-conditions" aria-describedby="e05-help">
      <legend>Condiciones de la sede ficticia</legend>
      {conditions.map(item => <div className="e05-condition" key={item.id}>
        <label htmlFor={`e05-${item.id}`}>{item.label}</label>
        <p className="small" id={`e05-help-${item.id}`}>{item.description}</p>
        <select id={`e05-${item.id}`} name={`demo-${item.id}`} value={states[item.id]} aria-describedby={`e05-help-${item.id}`} onChange={event => changeCondition(item.id, event.target.value)}>
          <option value={STATE.PRESENT}>Presente</option><option value={STATE.ABSENT}>Ausente</option><option value={STATE.PENDING}>Pendiente de verificar</option>
        </select>
      </div>)}
    </fieldset>
    <p className="e05-summary" role="status" aria-label="Resumen de condiciones" aria-live="polite" aria-atomic="true">{`Presentes: ${present}. Ausentes: ${absent}. Pendientes de verificar: ${pending}.`}</p>
    <p className="small">El resumen cuenta respuestas del ejemplo; no es una puntuación de accesibilidad ni el indicador CEAF.</p>
    <section className="e05-follow-up" aria-labelledby="e05-actions-title">
      <h3 id="e05-actions-title">Barreras y acciones pendientes</h3>
      {followUp.length === 0 ? <div className="e05-empty"><h4>Sin pendientes en este ejemplo</h4><p>Las seis condiciones están marcadas como presentes en el escenario. La revisión física e institucional sigue siendo necesaria.</p></div>
        : <ul role="list">{followUp.map(item => <li key={item.id}>
          <h4>{item.label}</h4><p className="e05-state">{states[item.id] === STATE.ABSENT ? 'Barrera declarada en el escenario' : 'Condición por verificar'}</p>
          <p>{states[item.id] === STATE.ABSENT ? item.fix : item.verify}</p>
        </li>)}</ul>}
    </section>
    <p className="e05-warning">No equivale a certificar accesibilidad ni a aprobar una sede real.</p>
    <p className="small e05-disclaimer">Una evaluación real requiere inspección física, revisión de los apoyos y validación institucional. No se consulta SIJE, registra información de personas ni calcula cumplimiento distrital. Las respuestas se descartan al recargar o salir de E05.</p>
  </div>;
}
