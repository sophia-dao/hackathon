import AlertBadge from './AlertBadge'
import { fmt } from '../utils'

export default function RecentAlerts({ history }) {
  const recent = [...(history ?? [])].reverse().slice(0, 6)

  return (
    <div style={{
      background: '#0d0d14', border: '1px solid #1e1e2e',
      borderRadius: 16, padding: 24, flex: 1, minWidth: 0,
    }}>
      <div style={{ marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.08em', color: '#6b6b8a', textTransform: 'uppercase', marginBottom: 4 }}>
            Recent Weeks
          </div>
          <div style={{ fontSize: 18, fontWeight: 700, color: '#fff' }}>Alert History</div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {recent.map((row, i) => {
          const week = (row.week ?? row.date ?? '').toString().slice(0, 10)
          return (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              background: '#13131f', border: '1px solid #2a2a3e',
              borderRadius: 10, padding: '12px 14px',
            }}>
              <div>
                <div style={{ fontSize: 13, color: '#fff', fontWeight: 600 }}>{week}</div>
                <div style={{ fontSize: 12, color: '#6b6b8a', marginTop: 2 }}>GSSI {fmt(row.gssi)}</div>
              </div>
              <AlertBadge level={row.alert ?? 'Moderate'} />
            </div>
          )
        })}
      </div>
    </div>
  )
}
