import { useEffect, useRef, useState } from 'react';
import { Activity, ArrowRight, CircleHelp, Cpu, Download, LoaderCircle, SlidersHorizontal } from 'lucide-react';
import { api } from '../services/api.js';
import { Badge, ErrorNotice, Loading, number, PanelHeader } from '../components/Shared.jsx';
import { SensorChart } from '../components/Charts.jsx';
import { sensorInfo, sensorLabel } from '../data/sensors.js';

export default function JetEngines({ engines, engineId, setEngineId, onPrediction, modelReady }) {
  const [history, setHistory] = useState(null), [cycle, setCycle] = useState(1), [sensor, setSensor] = useState('sensor_2');
  const [error, setError] = useState(''), [result, setResult] = useState(null), [predicting, setPredicting] = useState(false), [retry, setRetry] = useState(0);
  const predictionController = useRef(null);
  useEffect(() => {
    const controller = new AbortController();
    predictionController.current?.abort();
    setHistory(null); setResult(null); setError(''); setPredicting(false);
    api.history(engineId, controller.signal).then(data => { setHistory(data); setCycle(data.latest_cycle); }).catch(err => { if (err.name !== 'AbortError') setError(err.message); });
    return () => { controller.abort(); predictionController.current?.abort(); };
  }, [engineId, retry]);
  function changeCycle(value) { predictionController.current?.abort(); setPredicting(false); setResult(null); setCycle(Number(value)); }
  async function predict() {
    predictionController.current?.abort();
    const controller = new AbortController(); predictionController.current = controller;
    setPredicting(true); setResult(null); setError('');
    try { const data = await api.predict(engineId, cycle, controller.signal); setResult(data); onPrediction(data); }
    catch (err) { if (err.name !== 'AbortError') setError(err.message); }
    finally { if (!controller.signal.aborted) setPredicting(false); }
  }
  const rows = history?.history.filter(row => row.cycle <= cycle) || [];
  const latest = rows.at(-1);
  const selectedSensor = sensorInfo(sensor);
  const download = () => {
    const columns = ['engine_id', 'cycle', 'setting_1', 'setting_2', 'setting_3', ...history.sensors];
    const blob = new Blob([[columns.join(','), ...rows.map(row => columns.map(c => row[c]).join(','))].join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = `FD001-engine-${engineId}-through-${cycle}.csv`; a.click(); URL.revokeObjectURL(url);
  };
  return <>
    <div className="page-intro"><div><p className="eyebrow">JET ENGINE INTELLIGENCE</p><h1>Read the engine<span>.</span></h1><p>Choose an engine, review its readings, and estimate its remaining cycles.</p></div><Badge tone="accent">FD001 · test split</Badge></div>
    <ol className="workflow-steps" aria-label="How to predict"><li><span>1</span>Choose an engine</li><li><span>2</span>Choose an observed cycle</li><li><span>3</span>Predict remaining life</li></ol>
    <section className="engine-toolbar panel"><div className="engine-picker"><span className="equipment-icon"><Cpu size={22}/></span><div><label htmlFor="engine-select">SELECT ENGINE</label><select id="engine-select" value={engineId} onChange={e => setEngineId(Number(e.target.value))}>{engines?.engines.map(engine => <option key={engine.engine_id} value={engine.engine_id}>ENG-{String(engine.engine_id).padStart(3, '0')} · {engine.available_cycles} cycles</option>)}</select></div></div><div className="toolbar-fact"><span>Latest observation</span><strong>{history?.latest_cycle || '—'} <small>cycles</small></strong></div><div className="toolbar-fact"><span>Sensor channels</span><strong>21 <small>measurements</small></strong></div><Badge>Observed history</Badge></section>
    {error && <ErrorNotice message={error} retry={() => setRetry(v => v + 1)}/>}
    {!modelReady && <ErrorNotice message="The engine model is unavailable. Train it with python -m ml.engines.train, restart the backend, and refresh system status."/>}
    {!history ? !error && <Loading text="Loading engine observations…"/> : <>
      <div className="workspace-grid"><section className="panel sensor-panel"><PanelHeader eyebrow="SENSOR READINGS" title="Measurements over time"><button className="icon-button" onClick={download} aria-label="Download observed sensor history"><Download size={16}/></button></PanelHeader><div className="sensor-field"><label htmlFor="sensor-select">Measurement to explore</label><select id="sensor-select" value={sensor} onChange={e => setSensor(e.target.value)}>{history.sensors.map(s => <option key={s} value={s}>{sensorLabel(s)} ({sensorInfo(s).unit})</option>)}</select><p>LPC / HPC = low / high-pressure compressor. LPT / HPT = low / high-pressure turbine.</p></div><div className="sensor-readout"><span className="live-dot"/><span>{selectedSensor.symbol}</span><strong>{number(latest?.[sensor], 3)} <small>{selectedSensor.unit}</small></strong><span className="subtle">at cycle {cycle}</span></div><SensorChart rows={rows} sensor={sensor}/><div className="chart-foot"><span><i className="legend-line"/>Observed measurements</span><span>{rows.length} observations · no future data</span></div>
      <div className="cycle-control"><div><label htmlFor="cycle-range"><SlidersHorizontal size={14}/>Prediction cycle</label><label className="cycle-input-label" htmlFor="cycle-number"><input id="cycle-number" aria-label="Prediction cycle" type="number" min="1" max={history.latest_cycle} value={cycle} onChange={e => changeCycle(Math.min(history.latest_cycle, Math.max(1, Number(e.target.value) || 1)))}/><span>/ {history.latest_cycle}</span></label></div><input id="cycle-range" aria-label="Prediction cycle slider" type="range" min="1" max={history.latest_cycle} value={cycle} onChange={e => changeCycle(e.target.value)}/><div className="range-labels"><span>Cycle 1</span><button className="text-button" onClick={() => changeCycle(history.latest_cycle)}>Use latest cycle · {history.latest_cycle}</button></div><p className="help-copy">The model uses readings up to this cycle. Remaining life is measured in operating cycles, not hours.</p></div></section>
      <section className="panel prediction-panel"><PanelHeader eyebrow="REMAINING USEFUL LIFE" title="Look ahead"><Activity size={19} className="accent-text"/></PanelHeader><div className="prediction-body">{result ? <><Badge tone={result.maintenance_priority.toLowerCase()}>{result.maintenance_priority} priority</Badge><div className="rul-number" data-testid="rul-result">{number(result.predicted_rul, 1)}<span>estimated cycles remaining</span></div><div className="rul-meter"><span className={result.maintenance_priority.toLowerCase()} style={{ width: `${Math.min(100, result.predicted_rul / Math.max(125, result.predicted_rul) * 100)}%` }}/></div><p className="prediction-description">Estimated at observed cycle <strong>{result.current_cycle}</strong> using the engine’s available sensor history.</p><div className="prediction-meta"><span>Inference time<strong>{number(result.inference_ms, 1)} ms</strong></span><span>Model version<strong>v{result.model_version}</strong></span></div></> : <div className="prediction-placeholder"><div className="prediction-target"><Cpu size={34}/></div><h3>The next cycle starts here.</h3><p>Select an observed cycle and run the trained model to estimate remaining useful life.</p></div>}<button className="primary-button prediction-button" onClick={predict} disabled={predicting || !modelReady}>{predicting ? <LoaderCircle className="spin" size={17}/> : <Activity size={17}/>} {predicting ? 'Analyzing engine history…' : 'Predict remaining useful life'}{!predicting && <ArrowRight size={16}/>}</button><div className="prediction-context">ENG-{String(engineId).padStart(3, '0')}<span/>Cycle {cycle}<span/>{rows.length} observations</div></div><div className="prediction-disclaimer"><CircleHelp size={16}/><p>{result ? `Demo priority: critical < ${result.thresholds.critical_below}; elevated < ${result.thresholds.elevated_below}; normal ≥ ${result.thresholds.elevated_below} cycles. ` : ''}Estimates use NASA simulated degradation data. For research; not validated aircraft maintenance guidance.</p></div></section></div>
      <section className="panel operating-panel"><PanelHeader eyebrow={`SNAPSHOT / CYCLE ${cycle}`} title="Operating conditions"><Badge>Available at prediction time</Badge></PanelHeader><div className="operating-grid">{[1, 2, 3].map(i => <div key={i}><span>Operational setting {i}</span><strong className="mono">{number(latest?.[`setting_${i}`], 4)}</strong><small>Raw dataset value</small></div>)}</div></section>
    </>}
  </>;
}
