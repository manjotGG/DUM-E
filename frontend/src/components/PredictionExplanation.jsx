import { number } from './Shared.jsx';

const signed = (value, digits = 1) => `${value > 0 ? '+' : value < 0 ? '−' : ''}${number(Math.abs(value), digits)}`;

export default function PredictionExplanation({ prediction, onSelectSensor }) {
  const explanation = prediction?.explanation;
  if (!explanation?.available) return <section className="prediction-explanation"><h3>Prediction explanation</h3><p>{explanation?.summary || 'Sensor contributions are unavailable for this estimate.'}</p></section>;
  const sensors = explanation.sensor_contributions;
  const lowering = sensors.filter(sensor => sensor.contribution_cycles < -0.05).slice(0, 3);
  const low = prediction.predicted_rul < prediction.thresholds.elevated_below;
  const others = Object.values(explanation.other_contributions).reduce((sum, value) => sum + value, 0);
  return <section className="prediction-explanation" aria-label="Prediction explanation">
    <h3>{low ? 'Why is the remaining life low?' : 'What influenced this estimate?'}</h3>
    <p>{low ? `The estimate is below the ${number(prediction.thresholds.elevated_below)}-cycle priority threshold. ` : ''}{lowering.length ? `${lowering[0].name} (${lowering[0].symbol}) has the largest downward sensor contribution.` : 'No sensor has a significant net downward contribution; cycle and operating settings also influence the result.'}</p>
    {lowering.length > 0 && <ul className="sensor-reasons">{lowering.map(sensor => <li key={sensor.key}>
      <div className="reason-heading"><button className="sensor-reason-link" onClick={() => onSelectSensor(sensor.key)} aria-label={`Show ${sensor.symbol} sensor readings`}>{sensor.name} <span>({sensor.symbol})</span></button><strong>{signed(sensor.contribution_cycles)} <small>cycles</small></strong></div>
      <p>Reading: {number(sensor.reading, 3)} {sensor.unit}{sensor.observed_window > 1 && ` · Change over ${sensor.observed_window} observations: ${signed(sensor.recent_change, 3)} ${sensor.unit}`}</p>
    </li>)}</ul>}
    <p className="explanation-baseline">Model baseline: <strong>{number(explanation.baseline_cycles, 1)} cycles</strong>. Cycle and operating settings together: {signed(others)} cycles.</p>
    <details className="contribution-details"><summary>All sensor contributions</summary><ul>{sensors.map(sensor => <li key={sensor.key}><span>{sensor.name} ({sensor.symbol})</span><strong>{signed(sensor.contribution_cycles)}</strong></li>)}</ul><p>Values are in cycles. Baseline + all sensors + cycle and settings = {number(explanation.raw_prediction_cycles, 1)} cycles{explanation.raw_prediction_cycles < 0 ? ', clipped to zero' : ''}.</p></details>
    <p className="explanation-note">Impact includes each sensor’s reading and history features, relative to the model baseline. It explains the model’s estimate, not a confirmed physical fault.</p>
  </section>;
}
