export default function MetricCard({ icon, label, value, sub, accentColor = '#f97316', children }) {
  return (
    <div style={{
      background: '#0d0d14',
      border: '1px solid #1e1e2e',
      borderRadius: 16,
      padding: '20px 24px',
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      flex: 1,
      minWidth: 0,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: `${accentColor}22`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 18,
        }}>{icon}</div>
        <span style={{ color: '#3a3a5c', fontSize: 18 }}>ⓘ</span>
      </div>
      <div style={{ fontSize: 32, fontWeight: 700, color: '#fff', lineHeight: 1.1 }}>{value}</div>
      <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.08em', color: '#6b6b8a', textTransform: 'uppercase' }}>{label}</div>
      {sub && (
        <div style={{ fontSize: 12, color: accentColor, display: 'flex', alignItems: 'center', gap: 4 }}>
          {sub}
        </div>
      )}
      {children}
    </div>
  )
}
