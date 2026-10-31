import { useEffect, useRef, useState, type ReactNode } from 'react';
import { proposals, proposalHref, type Proposal } from './proposals';
import { useScrollReveal } from './useScrollReveal';
import { E01Calculator } from './E01Calculator';
import { E02Consultation } from './E02Consultation';
import { E03Territory } from './E03Territory';
import { E04Flow } from './E04Flow';
import { E05Checklist } from './E05Checklist';

const navigation = [
  { path: '/', label: 'Inicio' },
  { path: '/propuestas', label: 'Propuestas' },
  { path: '/evaluacion', label: 'Evaluación' },
  { path: '/evidencia', label: 'Evidencia' },
] as const;

const percent = new Intl.NumberFormat('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const readPath = () => window.location.hash.slice(1) || '/';

function Arrow() {
  return <span aria-hidden="true">↗</span>;
}

function PageHeading({ label, title, children }: { label: string; title: string; children: ReactNode }) {
  return <header className="page-heading">
    <p className="eyebrow">{label}</p>
    <h1 tabIndex={-1}>{title}</h1>
    <p className="lead">{children}</p>
  </header>;
}

function ProposalCard({ proposal }: { proposal: Proposal }) {
  return <a className="proposal-card" href={proposalHref(proposal)} data-reveal data-proposal={proposal.id}>
    <div className="card-top"><span className="code">{proposal.id}</span><span className="card-profile">Perfil {proposal.profile.id}</span></div>
    <h2>{proposal.title}</h2>
    <p>{proposal.summary}</p>
    <div className="card-bottom"><span>Ver propuesta</span><Arrow /></div>
  </a>;
}

function Home() {
  return <>
    <section className="hero">
      <div className="hero-copy">
        <p className="eyebrow">Hackathon INE · Reto 1</p>
        <h1 tabIndex={-1}>De la evidencia a la <em>acción institucional.</em></h1>
        <p className="lead">Cinco propuestas para explorar cómo acercar los servicios electorales a distintas realidades.</p>
        <a className="button" href="#/propuestas">Explorar las propuestas <Arrow /></a>
        <p className="hero-note">Un demostrador académico. No es un servicio oficial del INE.</p>
      </div>
      <aside className="proposal-index" aria-label="Los cinco ejes de propuesta">
        <div className="index-heading"><span className="eyebrow">Una mirada, cinco caminos</span><span className="index-count" aria-hidden="true">05</span></div>
        {proposals.map(proposal => <a key={proposal.id} href={proposalHref(proposal)}>
          <span className="code">{proposal.id}</span><span>{proposal.title}</span><Arrow />
        </a>)}
        <p>Del diagnóstico agregado a propuestas de servicio.</p>
      </aside>
    </section>
    <section className="approach" data-reveal aria-labelledby="approach-title">
      <div><p className="eyebrow">El recorrido</p><h2 id="approach-title">No solo leer una propuesta.<br />Entender cómo se llevaría a la práctica.</h2></div>
      <ol className="steps">
        <li><span>01</span><div><h3>Explorar</h3><p>Conocer qué propone cada intervención y en qué evidencia se apoya.</p></div></li>
        <li><span>02</span><div><h3>Comprender</h3><p>Reconocer los recursos, las condiciones y las autorizaciones que necesita.</p></div></li>
        <li><span>03</span><div><h3>Evaluar</h3><p>Identificar cómo medir la calidad del servicio, sin prometer incrementos del voto.</p></div></li>
      </ol>
    </section>
    <aside className="scope-note" data-reveal><span className="eyebrow">Estado de esta versión</span><p>Las cinco propuestas ya tienen demostración interactiva: cobertura, consulta de casillas ficticias, medidas territoriales, recorrido de votación y lista de accesibilidad. Son ejemplos ilustrativos, no servicios oficiales ni resultados operativos.</p></aside>
  </>;
}

function Catalog() {
  return <>
    <PageHeading label="01 / Propuestas" title="Cinco propuestas. Distintas formas de actuar.">Cada propuesta conecta una intervención institucional con un perfil analítico. Explora su propósito, su implementación y su forma de evaluación.</PageHeading>
    <section className="proposal-grid" aria-label="Catálogo de propuestas">
      {proposals.map(proposal => <ProposalCard key={proposal.id} proposal={proposal} />)}
      <aside className="catalog-note" data-reveal><span className="eyebrow">Un principio compartido</span><h2>Mejorar el servicio.<br />Sin clasificar personas.</h2><p>Los perfiles describen grupos agregados. No permiten atribuir motivaciones ni necesidades a una persona.</p><a className="text-link" href="#/evidencia">Conocer los límites <Arrow /></a></aside>
    </section>
  </>;
}

function ProposalDetail({ proposal }: { proposal: Proposal }) {
  const { profile } = proposal;
  return <>
    <a className="back-link" href="#/propuestas"><span aria-hidden="true">←</span>Volver al catálogo</a>
    <PageHeading label={`${proposal.id} / Perfil ${profile.id}`} title={proposal.title}>{proposal.summary}</PageHeading>
    <div className="detail-layout">
      <div className="detail-content">
        <section className="content-panel" data-reveal><p className="eyebrow">01 / La propuesta</p><h2>Qué se propone</h2><p>{profile.action}</p></section>
        <section className="experience-panel" data-reveal aria-labelledby="experience-title">
          {proposal.id === 'E01' ? <E01Calculator /> : proposal.id === 'E02' ? <E02Consultation /> : proposal.id === 'E03' ? <E03Territory /> : proposal.id === 'E04' ? <E04Flow /> : proposal.id === 'E05' ? <E05Checklist /> : <><p className="eyebrow">02 / La experiencia</p><span className="status-chip">Interacción por implementar</span>
          <h2 id="experience-title">{proposal.interaction}</h2><p>{proposal.experience}</p>
          <p className="small">La futura demostración utilizará ejemplos sintéticos. No consultará sistemas institucionales ni conservará los cambios al salir.</p></>}
        </section>
        <section className="content-panel" data-reveal><p className="eyebrow">03 / Un posible piloto</p><h2>Qué se necesita</h2><dl><dt>Recursos y coordinación</dt><dd>{profile.resources}</dd><dt>Canales propuestos</dt><dd>{profile.channel}</dd></dl><p className="small">Requiere diagnóstico propio, revisión de factibilidad y los instrumentos institucionales aplicables. Esta página no constituye una autorización.</p></section>
        <section className="content-panel" data-reveal><p className="eyebrow">04 / La evaluación</p><h2>{profile.indicator}</h2><p>{profile.indicatorDefinition}</p><p>Si el denominador es cero, corresponde «No aplica», no cero desempeño.</p><a className="text-link" href="#/evaluacion">Ver los indicadores de servicio <Arrow /></a></section>
      </div>
      <aside className="evidence-card" data-reveal>
        <p className="eyebrow">La evidencia de apoyo</p><h2>{profile.name}</h2>
        <p className="evidence-value">{percent.format(profile.participation)}<span>%</span></p>
        <p>Participación conocida en el perfil agregado, CCPC 2024.</p>
        <div className="evidence-divider"><h3>Una hipótesis, no un hallazgo</h3><p>{profile.hypothesis}</p></div>
        <a className="text-link" href="#/evidencia">Evidencia y límites <Arrow /></a>
      </aside>
    </div>
  </>;
}

function Evaluation() {
  return <>
    <PageHeading label="02 / Evaluación" title="Medir el servicio, no prometer votos.">Cada propuesta necesita una medición propia. Estos indicadores evalúan condiciones del servicio; no prueban un efecto causal sobre la participación electoral.</PageHeading>
    <aside className="scope-note" data-reveal><span className="eyebrow">Antes de calcular</span><p>Las fórmulas son propuestas operativas, no resultados observados. Su instrumentación depende de la disponibilidad de campos y del dictamen técnico de cada fuente.</p></aside>
    <section className="indicator-list" aria-label="Indicadores de las cinco propuestas">
      {proposals.map(proposal => <article className="indicator" key={proposal.id} data-reveal>
        <span className="code">{proposal.id}</span><div><h2>{proposal.profile.indicator}</h2><p>{proposal.profile.indicatorDefinition}</p><a className="text-link" href={proposalHref(proposal)}>Consultar la propuesta <Arrow /></a></div>
      </article>)}
    </section>
    <div className="reading-notes" data-reveal><section><h2>«No aplica» no significa cero</h2><p>Con denominador cero no existe una base para calcular el porcentaje. Si sí existe un universo evaluable y ningún caso cumple la condición, el resultado puede ser 0%.</p></section><section><h2>No son un ranking</h2><p>Cobertura, puntualidad y accesibilidad miden aspectos diferentes. No corresponde ordenar las propuestas como si sus porcentajes fueran equivalentes.</p></section></div>
  </>;
}

function Evidence() {
  return <>
    <PageHeading label="03 / Evidencia y límites" title="Lo que sabemos. Lo que falta comprobar.">La evidencia orienta las propuestas. Las hipótesis requieren contraste y las demostraciones no sustituyen una evaluación institucional.</PageHeading>
    <div className="reading-notes evidence-notes">
      <section data-reveal><p className="eyebrow">Evidencia observada</p><h2>Cinco perfiles agregados de 2024</h2><p>El análisis utiliza los Conteos Censales de Participación Ciudadana del INE. La agrupación se ajustó sobre la tasa de participación conocida: SV / (SV + NV).</p><p>Edad, sexo y territorio sirven para describir grupos. No son explicaciones causales ni una clasificación individual de la ciudadanía.</p></section>
      <section data-reveal><p className="eyebrow">Hipótesis operativas</p><h2>Las barreras no fueron medidas</h2><p>Los CCPC no miden horarios laborales, cuidados, discapacidad, motivos de abstención ni tiempos de espera. Estas posibles barreras necesitan evidencia adicional.</p></section>
      <section data-reveal><p className="eyebrow">Demostración</p><h2>Ejemplos, no servicios en operación</h2><p>Esta base no está conectada con SIIRFE, SIJE, SICE ni UTSI. Las interacciones previstas se identificarán como escenarios sintéticos, no como información en tiempo real.</p><p>No se guardará el progreso ni se solicitarán cuentas o datos personales de contacto.</p></section>
      <section data-reveal><p className="eyebrow">Alcance institucional</p><h2>Propuestas sujetas a validación</h2><p>Las referencias normativas y fuentes operativas requieren validación jurídica y técnica. El demostrador no certifica aprobación, presupuesto, viabilidad ni autorización de publicación.</p></section>
    </div>
    <section className="sources" data-reveal><p className="eyebrow">Trazabilidad del proyecto</p><h2>Documentación de respaldo</h2><ul><li><strong>Propuestas institucionales · T10</strong><span>docs/institutional-proposals.md</span></li><li><strong>Interpretación de perfiles · T09</strong><span>docs/profile-interpretation.md</span></li><li><strong>Revisión de divulgación</strong><span>docs/disclosure-review.md</span></li></ul><p className="small">Estas referencias se consultan en el repositorio; el servidor web no publica los documentos internos.</p><a className="text-link" href="https://www.ine.mx/">Consultar el portal del INE <Arrow /></a></section>
  </>;
}

function RouteView({ path }: { path: string }) {
  const ref = useScrollReveal();
  const proposal = proposals.find(item => path === `/propuestas/${item.id}`);
  let content: ReactNode;
  if (path === '/') content = <Home />;
  else if (path === '/propuestas') content = <Catalog />;
  else if (path === '/evaluacion') content = <Evaluation />;
  else if (path === '/evidencia') content = <Evidence />;
  else if (proposal) content = <ProposalDetail proposal={proposal} />;
  else content = <><PageHeading label="Página no encontrada" title="Esta página no existe.">Puedes regresar al inicio o explorar el catálogo de propuestas.</PageHeading><a className="button" href="#/">Volver al inicio <Arrow /></a></>;
  return <div className={proposal?.id === 'E01' ? 'page-content wrapper e01-page' : 'page-content wrapper'} ref={ref}>{content}</div>;
}

export function App() {
  const [path, setPath] = useState(readPath);
  const main = useRef<HTMLElement>(null);
  const previousPath = useRef(path);
  useEffect(() => {
    const updatePath = () => {
      // El enlace de salto usa el fragmento nativo sin cambiar la pantalla actual.
      if (location.hash !== '#contenido') setPath(readPath());
    };
    window.addEventListener('hashchange', updatePath);
    return () => window.removeEventListener('hashchange', updatePath);
  }, []);
  useEffect(() => {
    const heading = main.current?.querySelector('h1');
    document.title = `${heading?.textContent ?? 'Demostrador institucional'} · Reto 1`;
    if (previousPath.current !== path) {
      window.scrollTo(0, 0);
      heading?.focus({ preventScroll: true });
      previousPath.current = path;
    }
  }, [path]);
  return <>
    <a className="skip-link" href="#contenido" onClick={event => {
      event.preventDefault();
      main.current?.focus();
      main.current?.scrollIntoView();
    }}>Saltar al contenido</a>
    <header className="site-header"><div className="header-inner wrapper">
      <a className="brand" href="#/" aria-label="Demostrador institucional, inicio"><span className="brand-symbol" aria-hidden="true">5<span>↗</span></span><span>Propuestas<br /><strong>en acción</strong></span></a>
      <nav aria-label="Navegación principal">{navigation.map(item => <a href={`#${item.path}`} key={item.path} aria-current={(path === item.path || (item.path === '/propuestas' && path.startsWith('/propuestas/'))) ? 'page' : undefined}>{item.label}</a>)}</nav>
    </div></header>
    <main id="contenido" tabIndex={-1} ref={main}><RouteView key={path} path={path} /></main>
    <footer className="site-footer wrapper"><div><strong>Propuestas en acción</strong><p>Demostrador académico · Hackathon INE · Reto 1</p></div><p>No es una plataforma oficial del INE.<br />Borrador local; sin autorización de publicación.</p></footer>
  </>;
}
