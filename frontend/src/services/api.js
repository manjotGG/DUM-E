const base = import.meta.env.VITE_API_BASE_URL || '';

export async function request(path, options = {}) {
  let response;
  try { response = await fetch(`${base}${path}`, options); }
  catch (error) { if (error.name === 'AbortError') throw error; throw new Error('Cannot reach DUM-E. Start the backend and try again.'); }
  let body;
  try { body = await response.json(); } catch { throw new Error('The API returned an unreadable response. Check that the backend is running.'); }
  if (!response.ok) {
    const detail = body.detail;
    throw new Error(typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map(item => item.msg).join('; ') : 'The request could not be completed.');
  }
  return body;
}

export const api = {
  health: () => request('/health'),
  engines: () => request('/api/engines'),
  metrics: () => request('/api/engines/metrics'),
  logSchema: signal => request('/api/engines/log-schema', { signal }),
  sampleLogUrl: `${base}/api/engines/sample-log`,
  analyzeLog: (file, signal) => request('/api/engines/analyze-log', { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: file, signal }),
  history: (id, signal) => request(`/api/engines/${id}/history`, { signal }),
  predict: (id, cycle, signal) => request('/api/engines/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine_id: id, cycle }), signal }),
};
