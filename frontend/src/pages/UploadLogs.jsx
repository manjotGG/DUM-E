import { useEffect, useRef, useState } from 'react';
import { Upload, FileText, Download, Activity, CheckCircle2, LoaderCircle } from 'lucide-react';
import { api } from '../services/api.js';
import { Badge, ErrorNotice, number, PanelHeader } from '../components/Shared.jsx';
import { SensorChart } from '../components/Charts.jsx';
import PredictionExplanation from '../components/PredictionExplanation.jsx';
import { SENSOR_METADATA, sensorInfo, sensorLabel } from '../data/sensors.js';

export default function UploadLogs({ modelReady, report, onReport }) {
  const [file, setFile] = useState(null), [schema, setSchema] = useState(null), [error, setError] = useState(''), [busy, setBusy] = useState(false);
  const [selectedId, setSelectedId] = useState(report?.predictions[0]?.engine_id || null), [sensor, setSensor] = useState('sensor_2'), [dragging, setDragging] = useState(false);
  const controller = useRef(null), input = useRef(null);
  useEffect(() => { const request = new AbortController(); api.logSchema(request.signal).then(setSchema).catch(e => { if (e.name !== 'AbortError') setError(e.message); }); return () => { request.abort(); controller.current?.abort(); }; }, []);
  function chooseFile(candidate) {
    controller.current?.abort(); setBusy(false); setError(''); onReport(null); setFile(null);
    if (!candidate) return;
    if (!/\.(csv|txt|tsv|log)$/i.test(candidate.name)) { setError('Choose a CSV, TXT, TSV, or LOG file. Download the sample to see the required format.'); return; }
    if (candidate.size > 10 * 1024 * 1024) { setError('This file exceeds the 10 MB upload limit. Split it into smaller logs.'); return; }
    setFile(candidate);
  }
  async function analyze() {
    controller.current?.abort(); const request = new AbortController(); controller.current = request;
    setBusy(true); setError(''); onReport(null);
    try { const data = await api.analyzeLog(file, request.signal); setSelectedId(data.predictions[0].engine_id); onReport({ ...data, filename: file.name }); }
    catch (e) { if (e.name !== 'AbortError') setError(e.message); }
    finally { if (!request.signal.aborted) setBusy(false); }
  }
  const activeHistory = report?.histories.find(engine => engine.engine_id === selectedId);
  const activePrediction = report?.predictions.find(engine => engine.engine_id === selectedId);
  const downloadResults = () => {
    const columns = ['engine_id', 'current_cycle', 'observations', 'predicted_rul', 'rul_unit', 'maintenance_priority', 'model_version'];
    const csv = [columns.join(','), ...report.predictions.map(p => columns.map(key => p[key]).join(','))].join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' })); const a = document.createElement('a'); a.href = url; a.download = 'DUM-E-upload-predictions.csv'; a.click(); URL.revokeObjectURL(url);
  };
  return <>
    <div className="page-intro"><div><h1>Upload an engine log</h1><p>Get remaining-life estimates from your own FD001-compatible sensor history.</p></div></div>
    <ol className="workflow-steps" aria-label="How to analyze a log"><li><span>1</span>Prepare at least 15 cycles</li><li><span>2</span>Choose a log file</li><li><span>3</span>Analyze & review results</li></ol>
    <div className="upload-layout"><section className="panel upload-panel"><PanelHeader eyebrow="YOUR LOG FILE" title="Choose data to analyze"/><div className={`drop-zone ${dragging ? 'dragging' : ''}`} onDragOver={event => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={event => { event.preventDefault(); setDragging(false); chooseFile(event.dataTransfer.files[0]); }}>
      <Upload size={32}/><h2>{file ? file.name : 'Drop your engine log here'}</h2><p>{file ? `${number(file.size / 1024, 1)} KB · ready to validate` : 'CSV, TXT, TSV, or LOG · up to 10 MB'}</p><input ref={input} id="log-file" className="sr-only" type="file" accept=".csv,.txt,.tsv,.log" aria-label="Choose engine log file" onChange={event => { chooseFile(event.target.files[0]); event.target.value = ''; }}/><label className="secondary-button file-label" htmlFor="log-file">{file ? 'Choose another file' : 'Browse files'}</label>
    </div><div className="upload-actions"><button className="primary-button" onClick={analyze} disabled={!file || !modelReady || busy || !schema}>{busy ? <LoaderCircle size={17} className="spin"/> : <Activity size={17}/>} {busy ? 'Analyzing your log…' : 'Analyze log & predict'}</button><p>Files are processed for this request and are not saved on the server.</p></div>{!modelReady && <div className="upload-inline-error"><ErrorNotice message="The trained model is unavailable. Start the backend with its model artifact and refresh system status."/></div>}</section>
    <section className="panel upload-requirements"><PanelHeader eyebrow="BEFORE YOU UPLOAD" title="What your log needs"/><div className="requirement-item"><CheckCircle2/><div><strong>15 or more consecutive cycles per engine</strong><p>One row per cycle, in increasing order. Include all available history for each engine. A later starting cycle is accepted.</p></div></div><div className="requirement-item"><CheckCircle2/><div><strong>26 numeric columns per row</strong><p>Engine ID, cycle, 3 operating settings, and 21 C-MAPSS sensor readings. Keep the original NASA units.</p></div></div><div className="requirement-item"><CheckCircle2/><div><strong>FD001-compatible engine data</strong><p>One operating condition and HPC degradation. This model has not been validated for other equipment or C-MAPSS subsets.</p></div></div><a className="secondary-button" href={api.sampleLogUrl} download><Download size={15}/>Download sample log</a><p className="sample-note">Sample: the 31 supplied observations of FD001 test engine 1.</p><details className="schema-details"><summary>See column order & sensor names</summary><p>CSV headers may use the names below or sensor_1 through sensor_21. Headerless text files must use this exact order.</p><code>engine_id, cycle, setting_1, setting_2, setting_3</code><div className="schema-sensors">{SENSOR_METADATA.map((s, i) => <div key={s.key}><span>{i + 6}</span><strong>{s.symbol}</strong><span>{s.name} ({s.unit})</span></div>)}</div><p>Maximum {number(schema?.maximum_rows || 30000)} rows and {schema?.maximum_engines || 200} engines. Missing values, gaps, duplicates, and nonnumeric entries are rejected.</p></details></section></div>
    {error && <ErrorNotice message={error}/>}
    {report && <><section className="panel upload-results"><PanelHeader eyebrow="ANALYSIS COMPLETE" title={`${report.engines_analyzed} engine${report.engines_analyzed === 1 ? '' : 's'} analyzed`}><button className="secondary-button" onClick={downloadResults}><Download size={15}/>Export predictions</button></PanelHeader><div className="upload-summary"><FileText size={16}/><span>{report.filename} · {number(report.rows)} observations</span><Badge tone="normal">Actual model inference</Badge></div><div className="table-scroll"><table><thead><tr><th>Uploaded engine</th><th>Latest cycle</th><th>Observations</th><th>Estimated cycles remaining</th><th>Demo priority</th><th/></tr></thead><tbody>{report.predictions.map(prediction => <tr key={prediction.engine_id} className={selectedId === prediction.engine_id ? 'selected-row' : ''}><td>Engine {prediction.engine_id}</td><td>{prediction.current_cycle}</td><td>{prediction.observations}</td><td><strong>{number(prediction.predicted_rul, 1)}</strong> cycles</td><td><Badge tone={prediction.maintenance_priority.toLowerCase()}>{prediction.maintenance_priority}</Badge></td><td><button className="text-button" onClick={() => setSelectedId(prediction.engine_id)} aria-label={`View readings for uploaded engine ${prediction.engine_id}`}>View readings</button></td></tr>)}</tbody></table></div><div className="panel-foot">{report.compatibility_note} Remaining cycles are point estimates; demonstration priority thresholds are not validated maintenance limits.</div></section>
    {activePrediction && <div className="panel explanation-panel"><PanelHeader title={`Uploaded engine ${selectedId} · Cycle ${activePrediction.current_cycle}`}/><PredictionExplanation prediction={activePrediction} onSelectSensor={key => { setSensor(key); document.getElementById('upload-sensor-select')?.focus(); }}/></div>}
    {activeHistory && <section className="panel uploaded-chart"><PanelHeader eyebrow={`UPLOADED ENGINE ${selectedId}`} title="Explore your sensor readings"><Badge>{activePrediction.observations} observed cycles</Badge></PanelHeader><div className="sensor-field"><label htmlFor="upload-sensor-select">Measurement to explore</label><select id="upload-sensor-select" value={sensor} onChange={event => setSensor(event.target.value)}>{SENSOR_METADATA.map(s => <option key={s.key} value={s.key}>{sensorLabel(s.key)} ({s.unit})</option>)}</select></div><div className="sensor-readout"><span className="live-dot"/><span>{sensorInfo(sensor).symbol}</span><strong>{number(activeHistory.history.at(-1)?.[sensor], 3)} <small>{sensorInfo(sensor).unit}</small></strong></div><SensorChart rows={activeHistory.history} sensor={sensor}/><div className="chart-foot"><span>Readings from your uploaded log</span><span>{activeHistory.chart_truncated ? 'Chart shows the latest 500 cycles; inference used all uploaded history.' : 'All uploaded observations shown.'}</span></div></section>}</>}
  </>;
}
