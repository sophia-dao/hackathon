import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine,
} from 'recharts'
import AlertBadge from './AlertBadge'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{
      background: '#13131f', border: '1px solid #2a2a3e',
      borderRadius: 10, padding: '10px 14px', fontSize: 13,
    }}>
      <div style={{ color: '#6b6b8a', marginBottom: 4 }}>{label}</div>
      <div style={{ color: '#fff', fontWeight: 700 }}>GSSI {Number(d.gssi).toFixed(2)}</div>
      {d.alert && <div style={{ marginTop: 4 }}><AlertBadge level={d.alert} /></div>}
    </div>
  )
}

export default function HistoryChart({ data }) {
  const formatted = (data ?? []).map(row => ({
    ...row,
    week: row.week ? String(row.week).slice(0, 10) : row.date?.slice(0, 10),
    gssi: Number(row.gssi),
  }))

  return (
    <div style={{
      background: '#0d0d14', border: '1px solid #1e1e2e',
      borderRadius: 16, padding: '24px', flex: 2, minWidth: 0,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.08em', color: '#6b6b8a', textTransform: 'uppercase', marginBottom: 4 }}>
            Historical GSSI
          </div>
          <div style={{ fontSize: 20, fontWeight: 700, color: '#fff' }}>
            Supply Chain Stress Index Over Time
          </div>
        </div>
        <div style={{
          background: 'rgba(249,115,22,0.1)', border: '1px solid rgba(249,115,22,0.3)',
          borderRadius: 8, padding: '4px 12px', fontSize: 12, color: '#f97316',
        }}>Weekly</div>
      </div>

      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={formatted} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="gssiGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#f97316" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#f97316" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
          <XAxis dataKey="week" tick={{ fill: '#4a4a6a', fontSize: 11 }} tickLine={false} axisLine={false}
            interval={Math.ceil((formatted.length || 1) / 8)} />
          <YAxis tick={{ fill: '#4a4a6a', fontSize: 11 }} tickLine={false} axisLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={0} stroke="#2a2a3e" strokeDasharray="4 4" />
          <Area
            type="monotone" dataKey="gssi"
            stroke="#f97316" strokeWidth={2}
            fill="url(#gssiGrad)" dot={false} activeDot={{ r: 5, fill: '#f97316' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
