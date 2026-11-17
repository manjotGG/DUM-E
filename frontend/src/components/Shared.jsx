import { ArrowUpRight, LoaderCircle, AlertTriangle, Cpu, Activity } from 'lucide-react';

export const number = (value, digits = 0) => Number.isFinite(value) ? value.toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits }) : '—';
export function Badge({ children, tone = 'muted' }) { return <span className={`badge ${tone}`}><span className="badge-dot"/>{children}</span>; }
export function Loading({ text = 'Loading data…' }) { return <div className="empty-state" role="status"><LoaderCircle className="spin" size={24}/><p>{text}</p></div>; }
export function ErrorNotice({ message, retry }) { return <div className="error-notice" role="alert"><AlertTriangle size={18}/><span>{message}</span>{retry && <button onClick={retry}>Retry</button>}</div>; }
export function Metric({ label, value, unit, detail, icon: Icon = Activity }) { return <article className="metric-card"><div className="metric-top"><span>{label}</span><Icon size={17}/></div><div className="metric-value">{value}{unit && ' '}<span>{unit}</span></div><p>{detail}</p></article>; }
export function PanelHeader({ eyebrow, title, children }) { return <div className="panel-heading"><div>{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h2>{title}</h2></div>{children}</div>; }
export function Action({ children, onClick }) { return <button className="text-button" onClick={onClick}>{children}<ArrowUpRight size={16}/></button>; }

export function EngineDiagram() {
  return <svg className="engine-diagram" viewBox="0 0 490 270" role="img" aria-label="Technical illustration of a turbofan engine">
    <defs><linearGradient id="engineFill" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#73e8d2" stopOpacity=".15"/><stop offset="1" stopColor="#73e8d2" stopOpacity=".01"/></linearGradient><pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="#8fbfb5" strokeOpacity=".08"/></pattern></defs>
    <rect x="0" y="0" width="490" height="270" fill="url(#grid)"/>
    <g fill="url(#engineFill)" stroke="#72d9c8" strokeWidth="1.1"><path d="M115 66L290 84L403 110V160L290 187L115 205Z"/><ellipse cx="115" cy="135" rx="62" ry="89"/><ellipse cx="115" cy="135" rx="49" ry="73"/><ellipse cx="115" cy="135" rx="13" ry="20"/><path d="M403 110L450 120V150L403 160Z"/><path d="M185 73V197M213 76V193M243 79V190M272 82V187M301 86V184M327 92V178M352 98V172M376 104V166"/>
      {Array.from({ length: 16 }, (_, i) => <path key={i} d="M115 115Q145 91 131 65" transform={`rotate(${i * 22.5} 115 135)`}/>)}
    </g><g stroke="#72d9c8" strokeOpacity=".4" fill="none" strokeDasharray="4 5"><path d="M18 135H475M115 24V246M290 57V216"/><path d="M186 197L219 234H368M350 98L386 46H461"/></g><g fill="#78bbae" fontFamily="monospace" fontSize="9"><text x="371" y="38">HPC / DEGRADATION</text><text x="225" y="248">FD001 · TURBOFAN</text><text x="20" y="30">SECTION A—A</text></g>
  </svg>;
}

export function ModuleStatus() { return <div className="module-status"><Cpu size={18}/><div><strong>FD001 inference engine</strong><span>Historical data · on-demand prediction</span></div></div>; }
