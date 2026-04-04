import AlertBadge from './AlertBadge'
import { fmt, alertColor } from '../utils'

const LEVEL_ORDER = ['Critical', 'High', 'Moderate', 'Low']

export default function AlertsView({ history }) {
  const rows = [...(history ?? [])].reverse()

  const counts = rows.reduce((acc, r) => {
    const l = r.alert ?? 'Moderate'
    acc[l] = (acc[l] ?? 0) + 1
    return acc
  }, {})

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ fontSize: 20, fontWeight: 700, color: '#fff' }}>Alerts</div>

      {/* Summary row */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {LEVEL_ORDER.map(level => {
          const c = alertColor(level)
          return (
            <div key={level} style={{
              background: '#0d0d14', border: `1px solid ${c.border}`,
              borderRadius: 14, padding: '18px 24px', flex: 1, minWidth: 120,
            }}>
              <div style={{ fontSize: 32, fontWeight: 800, color: c.text }}>{counts[level] ?? 0}</div>
              <div style={{ fontSize: 11, color: '#6b6b8a', textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 4 }}>{level}</div>
            </div>
          )
        })}
      </div>

      {/* Full history table */}
      <div style={{ background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #1e1e2e', fontSize: 13, fontWeight: 600, color: '#6b6b8a', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
          <span>WEEK</span><span>GSSI</span><span>ALERT</span>
        </div>
        <div style={{ maxHeight: 460, overflowY: 'auto' }}>
          {rows.map((row, i) => {
            const week = String(row.week ?? row.date ?? '').slice(0, 10)
            const c = alertColor(row.alert ?? 'Moderate')
            return (
              <div key={i} style={{
                display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8,
                padding: '14px 20px',
                borderBottom: '1px solid #13131f',
                background: i % 2 === 0 ? 'transparent' : '#0a0a0f',
                alignItems: 'center',
              }}>
                <span style={{ fontSize: 13, color: '#e2e8f0' }}>{week}</span>
                <span style={{ fontSize: 13, color: '#fff', fontWeight: 600 }}>{fmt(row.gssi)}</span>
                <AlertBadge level={row.alert ?? 'Moderate'} />
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
