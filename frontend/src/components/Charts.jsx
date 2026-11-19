import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ScatterChart, Scatter, ReferenceLine, BarChart, Bar, Cell } from 'recharts';
import { sensorInfo, sensorLabel } from '../data/sensors.js';

const grid = '#e2e5e9';
const tick = { fill: '#667085', fontSize: 11 };
const tooltip = { background: '#ffffff', border: '1px solid #d0d5dd', borderRadius: 8, color: '#1f2937', fontSize: 12 };
export function SensorChart({ rows, sensor }) {
  const info = sensorInfo(sensor);
  return <div className="chart-container" role="img" aria-label={`${sensorLabel(sensor)} measurements through ${rows.at(-1)?.cycle || 0} observed cycles`}><ResponsiveContainer width="100%" height="100%"><LineChart data={rows} margin={{ top: 16, right: 20, bottom: 12, left: 0 }}>
    <CartesianGrid stroke={grid} vertical={false}/><XAxis dataKey="cycle" tick={tick} axisLine={false} tickLine={false} minTickGap={30} label={{ value: 'Operational cycle', position: 'insideBottom', offset: -8, fill: '#667085', fontSize: 11 }}/><YAxis domain={['auto', 'auto']} tick={tick} axisLine={false} tickLine={false} width={65} tickFormatter={v => Number(v.toFixed(2))}/><Tooltip contentStyle={tooltip} labelFormatter={v => `Cycle ${v}`} formatter={v => [`${Number(v).toFixed(4)} ${info.unit}`, info.name]}/><Line type="linear" dataKey={sensor} stroke="#3569ae" strokeWidth={1.8} dot={false} activeDot={{ r: 4 }} isAnimationActive={false}/>
  </LineChart></ResponsiveContainer></div>;
}

export function EvaluationScatter({ points }) {
  const maximum = Math.ceil(Math.max(...points.map(p => Math.max(p.actual_rul, p.predicted_rul))) / 25) * 25;
  return <div className="chart-container"><ResponsiveContainer width="100%" height="100%"><ScatterChart margin={{ top: 15, right: 25, bottom: 22, left: 5 }}><CartesianGrid stroke={grid}/><XAxis type="number" dataKey="actual_rul" name="Actual RUL" domain={[0, maximum]} tick={tick} axisLine={false} tickLine={false} label={{ value: 'Official RUL (cycles)', position: 'insideBottom', offset: -15, fill: '#667085', fontSize: 11 }}/><YAxis type="number" dataKey="predicted_rul" name="Predicted RUL" domain={[0, maximum]} tick={tick} axisLine={false} tickLine={false} width={45}/><Tooltip contentStyle={tooltip} cursor={{ strokeDasharray: '3 3' }} formatter={(v, name) => [Number(v).toFixed(1), name]}/><ReferenceLine segment={[{ x: 0, y: 0 }, { x: maximum, y: maximum }]} stroke="#72839a" strokeDasharray="5 5"/><Scatter data={points} fill="#3569ae" fillOpacity={.75} isAnimationActive={false}/></ScatterChart></ResponsiveContainer></div>;
}

export function ErrorChart({ bins }) {
  const data = bins.map(b => ({ ...b, range: `${Math.round(b.lower)}…${Math.round(b.upper)}` }));
  return <div className="chart-container"><ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{ top: 15, right: 15, bottom: 15, left: -20 }}><CartesianGrid stroke={grid} vertical={false}/><XAxis dataKey="range" tick={{ ...tick, fontSize: 9 }} axisLine={false} tickLine={false} interval={2}/><YAxis tick={tick} allowDecimals={false} axisLine={false} tickLine={false}/><Tooltip contentStyle={tooltip} formatter={v => [v, 'Engines']}/><Bar dataKey="count" radius={[3, 3, 0, 0]} isAnimationActive={false}>{data.map((b, i) => <Cell key={i} fill={b.upper < 0 ? '#8a9fbc' : '#3569ae'}/>)}</Bar></BarChart></ResponsiveContainer></div>;
}
