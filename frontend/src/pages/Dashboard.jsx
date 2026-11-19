import { Activity, Cpu, Gauge, Layers, Upload } from 'lucide-react';
import { Badge, Metric, number, PanelHeader } from '../components/Shared.jsx';

export function RecentPredictions({ recent, onSelect }) {
  return recent.length ? <div className="table-scroll"><table><thead><tr><th>Engine</th><th>Observed cycle</th><th>Cycles remaining</th><th>Priority</th><th/></tr></thead><tbody>{recent.slice(0, 8).map((prediction, i) => <tr key={`${prediction.timestamp}-${i}`}>
    <td>ENG-{String(prediction.engine_id).padStart(3, '0')}</td><td>{prediction.current_cycle}</td><td className="bright">{number(prediction.predicted_rul, 1)}</td><td><Badge tone={prediction.maintenance_priority.toLowerCase()}>{prediction.maintenance_priority}</Badge></td><td><button className="text-button" aria-label={`Open engine ${prediction.engine_id}`} onClick={() => onSelect(prediction.engine_id)}>View engine</button></td>
  </tr>)}</tbody></table></div> : <div className="empty-recent"><Activity size={22}/><p>No predictions yet. Choose an engine to get started.</p></div>;
}

export default function Dashboard({ modelReady, metrics, engines, recent, navigate, selectEngine }) {
  return <>
    <div className="page-intro"><div><h1>Overview</h1><p>Engine health and remaining life.</p></div></div>
    <div className="metric-grid overview-metrics"><Metric label="Available engines" value={number(engines?.engines.length)} icon={Layers}/><Metric label="Test mean absolute error" value={number(metrics?.mae, 2)} unit="cycles" icon={Gauge}/><Metric label="Model" value={modelReady ? 'Ready' : 'Unavailable'} icon={Cpu}/></div>
    <div className="home-actions"><section className="panel home-action"><Activity size={24}/><h2>Jet engines</h2><p>Choose an engine and predict its remaining cycles.</p><button className="primary-button" onClick={() => navigate('engines')}>Open engine workspace</button></section><section className="panel home-action"><Upload size={24}/><h2>Upload a log</h2><p>Analyze your own FD001-compatible sensor data.</p><button className="secondary-button" onClick={() => navigate('upload')}>Upload an engine log</button></section></div>
    <section className="panel"><PanelHeader title="Recent predictions"><span className="subtle">{recent.length} completed</span></PanelHeader><RecentPredictions recent={recent} onSelect={selectEngine}/></section>
  </>;
}
