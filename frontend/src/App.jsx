import { lazy, Suspense, useCallback, useEffect, useState } from 'react';
import { Activity, BookOpen, ChevronRight, Gauge, LayoutDashboard, Layers, Menu, RefreshCw, Upload, Target, X } from 'lucide-react';
import { api } from './services/api.js';
import { Badge, ErrorNotice, Loading } from './components/Shared.jsx';
import Dashboard from './pages/Dashboard.jsx';
const JetEngines = lazy(() => import('./pages/JetEngines.jsx'));
const Analytics = lazy(() => import('./pages/Analytics.jsx'));
const UploadLogs = lazy(() => import('./pages/UploadLogs.jsx'));
const Performance = lazy(() => import('./pages/Performance.jsx'));
const Milling = lazy(() => import('./pages/Milling.jsx'));

const navigation = [{ id: 'overview', label: 'Overview', icon: LayoutDashboard }, { id: 'engines', label: 'Jet engines', icon: Activity }, { id: 'upload', label: 'Upload engine log', icon: Upload }, { id: 'performance', label: 'Model performance', icon: Target }, { id: 'analytics', label: 'Model analytics', icon: Gauge }, { id: 'milling', label: 'Milling machines', icon: Layers }];
const readPage = () => navigation.some(item => item.id === window.location.hash.slice(1)) ? window.location.hash.slice(1) : 'overview';

export default function App() {
  const [page, setPage] = useState(readPage), [mobileMenu, setMobileMenu] = useState(false), [engineId, setEngineId] = useState(1);
  const [health, setHealth] = useState(null), [engines, setEngines] = useState(null), [metrics, setMetrics] = useState(null), [recent, setRecent] = useState([]);
  const [uploadReport, setUploadReport] = useState(null);
  const [loading, setLoading] = useState(true), [errors, setErrors] = useState([]);
  const load = useCallback(async () => {
    setLoading(true); setErrors([]);
    const results = await Promise.allSettled([api.health(), api.engines(), api.metrics()]);
    [setHealth, setEngines, setMetrics].forEach((setter, i) => setter(results[i].status === 'fulfilled' ? results[i].value : null));
    setErrors(results.filter(result => result.status === 'rejected').map(result => result.reason.message)); setLoading(false);
  }, []);
  useEffect(() => { load(); }, [load]);
  useEffect(() => { const handle = () => { setPage(readPage()); setMobileMenu(false); }; window.addEventListener('hashchange', handle); return () => window.removeEventListener('hashchange', handle); }, []);
  function navigate(next) { window.location.hash = next; setPage(next); setMobileMenu(false); window.scrollTo(0, 0); }
  function selectEngine(id) { setEngineId(id); navigate('engines'); }
  function onPrediction(data) { setRecent(previous => [{ ...data, timestamp: Date.now() }, ...previous].slice(0, 30)); }
  const healthy = health?.status === 'healthy';
  return <div className="app-shell">
    {mobileMenu && <button className="nav-backdrop" aria-label="Close navigation" onClick={() => setMobileMenu(false)}/>}
    <aside className={`sidebar ${mobileMenu ? 'open' : ''}`}>
      <button className="brand" onClick={() => navigate('overview')} aria-label="DUM-E overview"><span className="brand-mark">D</span><div>DUM-E<span>Predictive maintenance</span></div></button>
      <button className="close-nav icon-button" aria-label="Close navigation" onClick={() => setMobileMenu(false)}><X size={20}/></button>
      <nav aria-label="Main navigation">{navigation.map(item => <button key={item.id} onClick={() => navigate(item.id)} className={`nav-item ${page === item.id ? 'active' : ''}`} aria-current={page === item.id ? 'page' : undefined}><item.icon size={18}/>{item.label}</button>)}</nav>
      <div className="sidebar-bottom"><div className="source-card"><strong>NASA C-MAPSS</strong><p>FD001 dataset</p><Badge tone={health?.dataset_loaded ? 'normal' : 'muted'}>{health?.dataset_loaded ? 'Dataset loaded' : 'Data unavailable'}</Badge></div><a className="docs-link" href="/docs" target="_blank" rel="noreferrer"><BookOpen size={17}/>API documentation</a></div>
    </aside>
    <div className="main-shell"><header className="topbar"><div className="breadcrumb"><button className="mobile-menu icon-button" aria-label="Open navigation" onClick={() => setMobileMenu(true)}><Menu size={21}/></button><span>DUM-E</span><ChevronRight size={13}/><strong>{navigation.find(item => item.id === page)?.label}</strong></div><div className="topbar-right"><Badge tone={healthy ? 'normal' : 'muted'}>{loading ? 'Connecting' : healthy ? 'System ready' : 'System degraded'}</Badge><button className="icon-button" onClick={load} disabled={loading} aria-label="Refresh system status"><RefreshCw size={16} className={loading ? 'spin' : ''}/></button></div></header><main>
      {errors.map((error, i) => <ErrorNotice key={i} message={error} retry={load}/>)}
      <Suspense fallback={<Loading/>}>{loading ? <Loading text="Loading dashboard…"/> : page === 'overview' ? <Dashboard modelReady={health?.engine_model_loaded} metrics={metrics} engines={engines} recent={recent} navigate={navigate} selectEngine={selectEngine}/> : page === 'engines' ? engines ? <JetEngines engines={engines} engineId={engineId} setEngineId={setEngineId} onPrediction={onPrediction} modelReady={health?.engine_model_loaded}/> : <ErrorNotice message="Engine data unavailable. Check the backend and dataset configuration." retry={load}/> : page === 'upload' ? <UploadLogs modelReady={health?.engine_model_loaded} report={uploadReport} onReport={setUploadReport}/> : page === 'performance' ? <Performance metrics={metrics} navigate={navigate}/> : page === 'analytics' ? <Analytics metrics={metrics}/> : <Milling navigate={navigate}/>}</Suspense>
      <footer className="main-footer">DUM-E · NASA C-MAPSS FD001 · Research use</footer>
    </main></div>
  </div>;
}
