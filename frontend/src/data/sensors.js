import sensors from '../../../shared/sensors.json';

export const SENSOR_METADATA = sensors;
export const sensorInfo = key => sensors.find(sensor => sensor.key === key) || { key, symbol: key, name: key, unit: '' };
export const sensorLabel = key => { const sensor = sensorInfo(key); return `${sensor.name} · ${sensor.symbol}`; };
export function featureLabel(feature) {
  const match = /^(sensor_\d+)(.*)$/.exec(feature);
  if (!match) return feature === 'cycle' ? 'Observed cycle' : feature.replaceAll('_', ' ');
  const suffix = match[2].replace(/_mean_(\d+)/, ' · $1-cycle average').replace(/_std_(\d+)/, ' · $1-cycle variability').replace(/_trend_(\d+)/, ' · $1-cycle trend');
  return `${sensorInfo(match[1]).symbol}${suffix || ' · latest reading'}`;
}
