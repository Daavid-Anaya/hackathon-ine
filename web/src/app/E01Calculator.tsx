import { useState } from 'react';
import './E01Calculator.css';

const EXAMPLE = { total: '100', extended: '25' } as const;
const countFormat = new Intl.NumberFormat('es-MX');
const percentFormat = new Intl.NumberFormat('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 });

function parseCount(value: string) {
  const text = value.trim();
  if (!/^\d+$/.test(text)) return null;
  const count = Number(text);
  return Number.isSafeInteger(count) ? count : null;
}

export function E01Calculator() {
  const [totalInput, setTotalInput] = useState<string>(EXAMPLE.total);
  const [extendedInput, setExtendedInput] = useState<string>(EXAMPLE.extended);
  const [touched, setTouched] = useState({ total: false, extended: false });
  const total = parseCount(totalInput);
  const extended = parseCount(extendedInput);
  const countError = 'Introduce un conteo entero no negativo y dentro del rango de cálculo seguro, sin decimales ni notación científica.';
  const totalError = total === null ? countError : '';
  const extendedError = extended === null ? countError
    : total !== null && extended > total ? 'Los trámites en horario extendido no pueden superar el total.' : '';
  const showTotalError = touched.total && Boolean(totalError);
  const showExtendedError = (touched.extended || touched.total) && Boolean(extendedError);
  const valid = total !== null && extended !== null && !extendedError;

  return <div className="e01-calculator">
    <p className="eyebrow">02 / La experiencia</p>
    <span className="status-chip">Ejemplo sintético</span>
    <h2 id="experience-title">Calculadora de cobertura TCHE</h2>
    <p>Explora qué proporción de trámites se realizó en horario extendido. El ejemplo inicial contiene 100 trámites, de los cuales 25 se atendieron en sábado, domingo o turno vespertino.</p>
    <p className="small" id="e01-scope">Utiliza los mismos MAC seleccionados y el mismo período para ambos conteos. Cuenta cada trámite una sola vez, aunque cumpla más de una condición.</p>
    <form noValidate aria-label="Datos del escenario E01" aria-describedby="e01-scope" onSubmit={event => event.preventDefault()}>
      <div className="e01-field">
        <label htmlFor="e01-total">Total de trámites</label>
        <input id="e01-total" name="total" type="text" inputMode="numeric" autoComplete="off" spellCheck={false}
          value={totalInput} onChange={event => setTotalInput(event.target.value)}
          onBlur={() => setTouched(previous => ({ ...previous, total: true }))}
          aria-invalid={showTotalError} aria-describedby={`e01-total-help${showTotalError ? ' e01-total-error' : ''}`} />
        <p className="e01-help" id="e01-total-help">Incluye todos los horarios de atención, también los extendidos.</p>
        {showTotalError ? <p className="e01-error" id="e01-total-error">{totalError}</p> : null}
      </div>
      <div className="e01-field">
        <label htmlFor="e01-extended">Trámites en horario extendido</label>
        <input id="e01-extended" name="extended" type="text" inputMode="numeric" autoComplete="off" spellCheck={false}
          value={extendedInput} onChange={event => setExtendedInput(event.target.value)}
          onBlur={() => setTouched(previous => ({ ...previous, extended: true }))}
          aria-invalid={showExtendedError} aria-describedby={`e01-extended-help${showExtendedError ? ' e01-extended-error' : ''}`} />
        <p className="e01-help" id="e01-extended-help">Son una parte del total, no trámites adicionales.</p>
        {showExtendedError ? <p className="e01-error" id="e01-extended-error">{extendedError}</p> : null}
      </div>
    </form>
    <div className="e01-result">
      <h3>Tasa de cobertura en horario extendido</h3>
      <div role="status" aria-label="Resultado TCHE" aria-live="polite" aria-atomic="true">
        {!valid ? 'Revisa los datos para calcular la cobertura.' : total === 0 ? <>
          <strong>No aplica</strong><p>No hay trámites en el período del escenario. No existe un denominador para calcular la cobertura.</p>
        </> : <>
          <strong>{percentFormat.format((extended / total) * 100)}%</strong>
          <p>{countFormat.format(extended)} de {countFormat.format(total)} trámites del escenario se realizaron en horario extendido.</p>
        </>}
      </div>
      <p className="e01-formula">TCHE = 100 × trámites en horario extendido / total de trámites</p>
    </div>
    <p className="small e01-disclaimer">El resultado se actualiza al editar los conteos. Es una ilustración de cobertura del servicio, no un dato observado ni una predicción del voto. No se consulta SIIRFE ni se guardan tus cambios al salir de esta propuesta o recargar la página.</p>
  </div>;
}
