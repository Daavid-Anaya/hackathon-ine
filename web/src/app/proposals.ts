import { civicData } from '../data/profiles.js';

interface ProposalPresentation {
  id: string;
  title: string;
  summary: string;
  interaction: string;
  experience: string;
}

const presentations: readonly ProposalPresentation[] = [
  {
    id: 'E01', title: 'Flexibilidad en credencialización',
    summary: 'Acercar los trámites a los horarios y espacios de la vida cotidiana.',
    interaction: 'Calculadora de cobertura',
    experience: 'Explorar un ejemplo de trámites en horario extendido y comprender cómo se calcula su cobertura.',
  },
  {
    id: 'E02', title: 'Información y certidumbre logística',
    summary: 'Hacer más clara la información para planear una visita a la casilla.',
    interaction: 'Consulta móvil guiada',
    experience: 'Recorrer una consulta de casilla ficticia con información de acceso y estados de afluencia simulados.',
  },
  {
    id: 'E03', title: 'Cercanía territorial y comunitaria',
    summary: 'Explorar medidas de acceso e información desde el contexto de una comunidad.',
    interaction: 'Explorador territorial',
    experience: 'Recorrer un caso territorial ficticio y relacionar barreras de acceso con medidas y canales comunitarios.',
  },
  {
    id: 'E04', title: 'Flujo en casillas y apoyo al funcionariado',
    summary: 'Organizar el recorrido de votación y respaldar a quienes hacen posible la jornada.',
    interaction: 'Recorrido visual interactivo',
    experience: 'Explorar las etapas de votación, la organización del espacio y los apoyos al funcionariado, sin predecir tiempos de espera.',
  },
  {
    id: 'E05', title: 'Accesibilidad universal',
    summary: 'Identificar barreras físicas y condiciones necesarias para una atención accesible.',
    interaction: 'Lista de verificación',
    experience: 'Revisar una sede ficticia y reconocer condiciones presentes, ausentes o pendientes. No constituye una certificación.',
  },
];

export const proposals = presentations.map((presentation, index) => {
  const profile = civicData.profiles[index];
  if (!profile || profile.id !== `P0${index + 1}`) throw new Error('Correspondencia de perfiles no válida.');
  return { ...presentation, profile };
});

export type Proposal = (typeof proposals)[number];
export const proposalHref = (proposal: Proposal) => `#/propuestas/${proposal.id}`;
