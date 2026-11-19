import { LoaderCircle, AlertTriangle, Activity } from 'lucide-react';

export const number = (value, digits = 0) => Number.isFinite(value) ? value.toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits }) : '—';
export function Badge({ children, tone = 'muted' }) { return <span className={`badge ${tone}`}><span className="badge-dot"/>{children}</span>; }
export function Loading({ text = 'Loading data…' }) { return <div className="empty-state" role="status"><LoaderCircle className="spin" size={24}/><p>{text}</p></div>; }
export function ErrorNotice({ message, retry }) { return <div className="error-notice" role="alert"><AlertTriangle size={18}/><span>{message}</span>{retry && <button onClick={retry}>Retry</button>}</div>; }
export function Metric({ label, value, unit, detail, icon: Icon = Activity }) { return <article className="metric-card"><div className="metric-top"><span>{label}</span><Icon size={17}/></div><div className="metric-value">{value}{unit && ' '}<span>{unit}</span></div>{detail && <p>{detail}</p>}</article>; }
export function PanelHeader({ eyebrow, title, children }) { return <div className="panel-heading"><div>{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h2>{title}</h2></div>{children}</div>; }
export function Action({ children, onClick }) { return <button className="text-button" onClick={onClick}>{children}</button>; }
