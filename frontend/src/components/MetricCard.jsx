export default function MetricCard({ label, value, sub, accentColor = '#f97316', children }) {
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
      <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.08em', color: accentColor, textTransform: 'uppercase' }}>{label}</div>
      <div style={{ fontSize: 32, fontWeight: 700, color: '#fff', lineHeight: 1.1 }}>{value}</div>
      {sub && (
        <div style={{ fontSize: 12, color: '#6b6b8a', display: 'flex', alignItems: 'center', gap: 4 }}>
          {sub}
        </div>
      )}
      {children}
    </div>
  )
}
