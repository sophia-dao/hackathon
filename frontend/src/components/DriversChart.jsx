import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from 'recharts'

const FEATURE_LABELS = {
  freight_cost:       'Freight Cost',
  supplier_delay:     'Supplier Delay',
  oil_price:          'Oil Price',
  market_volatility:  'Market Volatility',
  inventory_stress:   'Inventory Stress',
}

const BAR_COLORS = ['#f97316', '#a78bfa', '#38bdf8', '#34d399', '#fb7185']

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{
      background: '#13131f', border: '1px solid #2a2a3e',
      borderRadius: 10, padding: '10px 14px', fontSize: 13,
    }}>
      <div style={{ color: '#fff', fontWeight: 600 }}>{d.label}</div>
      <div style={{ color: '#6b6b8a', marginTop: 2 }}>
        Correlation: <span style={{ color: payload[0].color }}>{d.correlation}</span>
      </div>
      <div style={{ color: '#6b6b8a', marginTop: 2 }}>Impact: {d.impact}</div>
    </div>
  )
}

export default function DriversChart({ drivers }) {
  const data = (drivers ?? []).map((d, i) => ({
    ...d,
    label: FEATURE_LABELS[d.feature] ?? d.feature,
    abs: Math.abs(d.correlation),
    color: BAR_COLORS[i % BAR_COLORS.length],
  }))

  return (
    <div style={{
      background: '#0d0d14', border: '1px solid #1e1e2e',
      borderRadius: 16, padding: 24, flex: 1, minWidth: 0,
    }}>
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.08em', color: '#6b6b8a', textTransform: 'uppercase', marginBottom: 4 }}>
          Top Drivers
        </div>
        <div style={{ fontSize: 18, fontWeight: 700, color: '#fff' }}>Contributing Indicators</div>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 10, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" horizontal={false} />
          <XAxis type="number" domain={[0, 1]} tick={{ fill: '#4a4a6a', fontSize: 11 }} tickLine={false} axisLine={false} />
          <YAxis type="category" dataKey="label" tick={{ fill: '#9ca3af', fontSize: 12 }} tickLine={false} axisLine={false} width={120} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
          <Bar dataKey="abs" radius={[0, 6, 6, 0]} maxBarSize={20}>
            {data.map((d, i) => <Cell key={i} fill={d.color} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginTop: 16 }}>
        {data.map((d, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
            <div style={{ width: 8, height: 8, borderRadius: 2, background: d.color }} />
            <span style={{ color: '#9ca3af' }}>{d.label}</span>
            <span style={{
              color: d.impact === 'positive' ? '#22c55e' : '#ef4444',
              fontSize: 11,
            }}>{d.impact === 'positive' ? '↑' : '↓'}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
