import { useEffect, useState } from 'react'

const ENDPOINTS = [
  { label: 'Health Check',  path: '/health',        description: 'API server status' },
  { label: 'Current GSSI',  path: '/gssi/current',  description: 'Latest GSSI + alert' },
  { label: 'History',       path: '/gssi/history',  description: 'Historical GSSI data' },
  { label: 'Forecast',      path: '/gssi/forecast', description: 'Next-week LSTM forecast' },
  { label: 'Drivers',       path: '/gssi/drivers',  description: 'Top contributing indicators' },
  { label: 'Summary',       path: '/gssi/summary',  description: 'AI-generated macro summary' },
]

const PIPELINE_STAGES = [
  { label: 'Data Ingestion',    detail: 'FRED API · Yahoo Finance · GDELT · Google Trends',  icon: '📡' },
  { label: 'Preprocessing',     detail: 'Resample weekly · Fill missing · Clip outliers · Scale', icon: '🔧' },
  { label: 'GSSI Computation',  detail: 'Weighted sum of normalized indicators',               icon: '📊' },
  { label: 'Sequence Building', detail: '8-week lookback windows for LSTM input',              icon: '🧱' },
  { label: 'LSTM Forecast',     detail: 'Univariate · 64-unit LSTM · 50 epochs',               icon: '🤖' },
  { label: 'Alert Labeling',    detail: 'Low / Moderate / High / Critical thresholds',         icon: '🚨' },
  { label: 'Analytics',         detail: 'Driver correlation · Trend detection · Summary',      icon: '🧠' },
]

const DATA_SOURCES = [
  { name: 'FRED API',         series: ['DCOILWTICO (Oil)', 'FRGEXPUSM649NCIS (Freight)', 'DTCDFNA066MNFRBPHI (Delivery Time)'], color: '#38bdf8' },
  { name: 'Yahoo Finance',    series: ['S&P 500 (^GSPC)', 'Dow Jones (^DJI)', 'NASDAQ (^IXIC)'],                                color: '#a78bfa' },
  { name: 'GDELT News',       series: ['Supply chain article count (weekly)'],                                                  color: '#34d399' },
  { name: 'Google Trends',    series: ['trend_supply_chain', 'trend_shipping_delays'],                                          color: '#f97316' },
]

function StatusDot({ status }) {
  const colors = { ok: '#22c55e', error: '#ef4444', checking: '#f59e0b' }
  return (
    <div style={{
      width: 8, height: 8, borderRadius: '50%',
      background: colors[status] ?? '#6b6b8a',
      boxShadow: status === 'ok' ? `0 0 6px ${colors.ok}` : 'none',
      flexShrink: 0,
    }} />
  )
}

export default function SystemView() {
  const [statuses, setStatuses] = useState(
    Object.fromEntries(ENDPOINTS.map(e => [e.path, 'checking']))
  )
  const [responseTimes, setResponseTimes] = useState({})

  useEffect(() => {
    ENDPOINTS.forEach(({ path }) => {
      const t0 = performance.now()
      fetch(path)
        .then(r => {
          const ms = Math.round(performance.now() - t0)
          setStatuses(s => ({ ...s, [path]: r.ok ? 'ok' : 'error' }))
          setResponseTimes(t => ({ ...t, [path]: ms }))
        })
        .catch(() => setStatuses(s => ({ ...s, [path]: 'error' })))
    })
  }, [])

  const allOk = Object.values(statuses).every(s => s === 'ok')
  const anyChecking = Object.values(statuses).some(s => s === 'checking')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ fontSize: 20, fontWeight: 700, color: '#fff' }}>System</div>

      {/* Overall health banner */}
      <div style={{
        background: anyChecking ? 'rgba(245,158,11,0.08)' : allOk ? 'rgba(34,197,94,0.08)' : 'rgba(239,68,68,0.08)',
        border: `1px solid ${anyChecking ? 'rgba(245,158,11,0.3)' : allOk ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`,
        borderRadius: 14, padding: '16px 22px',
        display: 'flex', alignItems: 'center', gap: 14,
      }}>
        <StatusDot status={anyChecking ? 'checking' : allOk ? 'ok' : 'error'} />
        <div>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#fff' }}>
            {anyChecking ? 'Checking endpoints…' : allOk ? 'All systems operational' : 'Some endpoints are down'}
          </div>
          <div style={{ fontSize: 12, color: '#6b6b8a', marginTop: 2 }}>
            FastAPI · Uvicorn · http://127.0.0.1:8000
          </div>
        </div>
      </div>

      {/* Endpoint status table */}
      <div style={{ background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16, overflow: 'hidden' }}>
        <div style={{ padding: '16px 22px', borderBottom: '1px solid #1e1e2e', fontSize: 13, fontWeight: 600, color: '#9ca3af' }}>
          API Endpoints
        </div>
        {ENDPOINTS.map(({ label, path, description }) => (
          <div key={path} style={{
            display: 'grid', gridTemplateColumns: '16px 1fr 1fr auto',
            alignItems: 'center', gap: 14,
            padding: '14px 22px', borderBottom: '1px solid #13131f',
          }}>
            <StatusDot status={statuses[path]} />
            <div>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#e2e8f0' }}>{label}</div>
              <div style={{ fontSize: 12, color: '#6b6b8a', marginTop: 2 }}>{description}</div>
            </div>
            <code style={{
              fontSize: 12, color: '#4a4a6a',
              background: '#13131f', padding: '2px 8px', borderRadius: 6,
              justifySelf: 'start',
            }}>GET {path}</code>
            <div style={{ fontSize: 12, color: '#6b6b8a', textAlign: 'right', whiteSpace: 'nowrap' }}>
              {responseTimes[path] != null ? `${responseTimes[path]} ms` : '—'}
            </div>
          </div>
        ))}
      </div>

      {/* Pipeline stages + Data sources */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>

        {/* Pipeline */}
        <div style={{ background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16, padding: 24, flex: 1, minWidth: 280 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#9ca3af', marginBottom: 16 }}>Pipeline Architecture</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            {PIPELINE_STAGES.map(({ label, detail, icon }, i) => (
              <div key={i} style={{ display: 'flex', gap: 14, position: 'relative' }}>
                {/* connector line */}
                {i < PIPELINE_STAGES.length - 1 && (
                  <div style={{
                    position: 'absolute', left: 17, top: 36, width: 2, height: 'calc(100% - 8px)',
                    background: '#1e1e2e',
                  }} />
                )}
                <div style={{
                  width: 36, height: 36, borderRadius: 10, flexShrink: 0,
                  background: '#13131f', border: '1px solid #2a2a3e',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 16, zIndex: 1,
                }}>{icon}</div>
                <div style={{ paddingBottom: 20 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#e2e8f0', marginTop: 8 }}>{label}</div>
                  <div style={{ fontSize: 12, color: '#6b6b8a', marginTop: 2 }}>{detail}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Data sources */}
        <div style={{ background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16, padding: 24, flex: 1, minWidth: 260 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#9ca3af', marginBottom: 16 }}>Data Sources</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {DATA_SOURCES.map(({ name, series, color }) => (
              <div key={name} style={{
                background: '#13131f', border: '1px solid #2a2a3e',
                borderRadius: 12, padding: '14px 16px',
                borderLeft: `3px solid ${color}`,
              }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: '#fff', marginBottom: 8 }}>{name}</div>
                {series.map(s => (
                  <div key={s} style={{ fontSize: 12, color: '#6b6b8a', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div style={{ width: 4, height: 4, borderRadius: '50%', background: color, flexShrink: 0 }} />
                    {s}
                  </div>
                ))}
              </div>
            ))}
          </div>

          {/* Tech stack */}
          <div style={{ marginTop: 20 }}>
            <div style={{ fontSize: 12, color: '#6b6b8a', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Tech Stack</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {['FastAPI', 'TensorFlow/Keras', 'Pandas', 'NumPy', 'scikit-learn', 'Uvicorn', 'React', 'Recharts'].map(t => (
                <span key={t} style={{
                  background: '#1e1e2e', color: '#9ca3af',
                  borderRadius: 6, padding: '4px 10px', fontSize: 12,
                }}>{t}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
