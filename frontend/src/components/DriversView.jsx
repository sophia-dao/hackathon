import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from 'recharts'

const FEATURE_LABELS = {
  freight_cost:      'Freight Cost',
  supplier_delay:    'Supplier Delay',
  oil_price:         'Oil Price',
  market_volatility: 'Market Volatility',
  inventory_stress:  'Inventory Stress',
}

const COLORS = ['#f97316', '#a78bfa', '#38bdf8', '#34d399', '#fb7185']

export default function DriversView({ drivers }) {
  const data = (drivers ?? []).map((d, i) => ({
    ...d,
    label: FEATURE_LABELS[d.feature] ?? d.feature,
    abs: Math.abs(d.correlation),
    color: COLORS[i % COLORS.length],
  }))

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ fontSize: 20, fontWeight: 700, color: '#fff' }}>Drivers</div>

      {/* Stat cards */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {data.map((d, i) => (
          <div key={i} style={{
            background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 14,
            padding: '18px 22px', flex: 1, minWidth: 140,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
              <div style={{ width: 8, height: 8, borderRadius: 2, background: d.color }} />
              <span style={{
                fontSize: 11, color: d.impact === 'positive' ? '#22c55e' : '#ef4444',
                fontWeight: 600,
              }}>{d.impact === 'positive' ? '↑ Positive' : '↓ Negative'}</span>
            </div>
            <div style={{ fontSize: 26, fontWeight: 800, color: d.color }}>{d.abs.toFixed(2)}</div>
            <div style={{ fontSize: 12, color: '#6b6b8a', marginTop: 4 }}>{d.label}</div>
          </div>
        ))}
      </div>

      {/* Bar chart */}
      <div style={{ background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16, padding: 24 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#9ca3af', marginBottom: 20 }}>Correlation with GSSI (absolute)</div>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
            <XAxis dataKey="label" tick={{ fill: '#9ca3af', fontSize: 12 }} tickLine={false} axisLine={false} />
            <YAxis domain={[0, 1]} tick={{ fill: '#4a4a6a', fontSize: 11 }} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{ background: '#13131f', border: '1px solid #2a2a3e', borderRadius: 10 }}
              labelStyle={{ color: '#9ca3af', marginBottom: 4 }}
              formatter={(v, _, p) => [v.toFixed(4), `${p.payload.impact} impact`]}
            />
            <Bar dataKey="abs" radius={[6, 6, 0, 0]} maxBarSize={60}>
              {data.map((d, i) => <Cell key={i} fill={d.color} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Table */}
      <div style={{ background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16, overflow: 'hidden' }}>
        <div style={{ padding: '14px 20px', borderBottom: '1px solid #1e1e2e', fontSize: 12, fontWeight: 600, color: '#6b6b8a', display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 8 }}>
          <span>INDICATOR</span><span>CORRELATION</span><span>IMPACT</span>
        </div>
        {data.map((d, i) => (
          <div key={i} style={{
            display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 8,
            padding: '14px 20px', borderBottom: '1px solid #13131f',
            background: i % 2 === 0 ? 'transparent' : '#0a0a0f',
            alignItems: 'center',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 8, height: 8, borderRadius: 2, background: d.color, flexShrink: 0 }} />
              <span style={{ fontSize: 13, color: '#e2e8f0' }}>{d.label}</span>
            </div>
            <span style={{ fontSize: 13, color: d.color, fontWeight: 600 }}>{d.correlation.toFixed(4)}</span>
            <span style={{ fontSize: 12, color: d.impact === 'positive' ? '#22c55e' : '#ef4444', fontWeight: 600 }}>
              {d.impact === 'positive' ? '↑ Positive' : '↓ Negative'}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
