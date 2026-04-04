import { fmt, TREND_META, alertColor } from '../utils'
import AlertBadge from './AlertBadge'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

export default function ForecastView({ forecast, summary, history }) {
  const trend = TREND_META[summary?.trend] ?? TREND_META.stable

  const chartData = [
    ...(history ?? []).slice(-8).map(r => ({
      week: String(r.week ?? r.date ?? '').slice(0, 10),
      gssi: Number(r.gssi),
      type: 'historical',
    })),
    {
      week: forecast?.forecast_week?.slice(0, 10) ?? '—',
      gssi: forecast?.predicted_gssi ?? null,
      type: 'forecast',
    },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ fontSize: 20, fontWeight: 700, color: '#fff' }}>Forecast</div>

      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {/* Main forecast card */}
        <div style={{
          background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16,
          padding: 28, flex: 1, minWidth: 260,
        }}>
          <div style={{ fontSize: 11, color: '#6b6b8a', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>Next Week Prediction</div>
          <div style={{ fontSize: 52, fontWeight: 800, color: '#fff', lineHeight: 1 }}>{fmt(forecast?.predicted_gssi)}</div>
          <div style={{ fontSize: 14, color: '#6b6b8a', marginTop: 6, marginBottom: 16 }}>GSSI · {forecast?.forecast_week?.slice(0, 10)}</div>
          <AlertBadge level={forecast?.predicted_alert ?? 'Moderate'} size="lg" />
        </div>

        {/* Trend card */}
        <div style={{
          background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16,
          padding: 28, flex: 1, minWidth: 200,
          display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: 8,
        }}>
          <div style={{ fontSize: 48, color: trend.color }}>{trend.icon}</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: trend.color }}>{trend.label}</div>
          <div style={{ fontSize: 13, color: '#6b6b8a' }}>Outlook trend</div>
        </div>

        {/* Delta card */}
        <div style={{
          background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16,
          padding: 28, flex: 1, minWidth: 200,
          display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 10,
        }}>
          <div style={{ fontSize: 11, color: '#6b6b8a', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Current vs Forecast</div>
          <div>
            <span style={{ fontSize: 13, color: '#6b6b8a' }}>Current </span>
            <span style={{ fontSize: 20, fontWeight: 700, color: '#fff' }}>{fmt(summary?.current_gssi)}</span>
          </div>
          <div>
            <span style={{ fontSize: 13, color: '#6b6b8a' }}>Forecast </span>
            <span style={{ fontSize: 20, fontWeight: 700, color: '#a78bfa' }}>{fmt(forecast?.predicted_gssi)}</span>
          </div>
          <div style={{
            fontSize: 13, color: trend.color, fontWeight: 600,
            background: `${trend.color}18`, borderRadius: 8, padding: '6px 10px', display: 'inline-block',
          }}>
            Δ {fmt((forecast?.predicted_gssi ?? 0) - (summary?.current_gssi ?? 0))}
          </div>
        </div>
      </div>

      {/* Chart: last 8 weeks + forecast */}
      <div style={{ background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16, padding: 24 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#9ca3af', marginBottom: 20 }}>Last 8 Weeks + Forecast</div>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
            <XAxis dataKey="week" tick={{ fill: '#4a4a6a', fontSize: 11 }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fill: '#4a4a6a', fontSize: 11 }} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: '#13131f', border: '1px solid #2a2a3e', borderRadius: 10 }} labelStyle={{ color: '#6b6b8a' }} itemStyle={{ color: '#fff' }} />
            <Line type="monotone" dataKey="gssi" stroke="#f97316" strokeWidth={2} dot={(p) =>
              p.payload.type === 'forecast'
                ? <circle key={p.key} cx={p.cx} cy={p.cy} r={6} fill="#a78bfa" stroke="#0d0d14" strokeWidth={2} />
                : <circle key={p.key} cx={p.cx} cy={p.cy} r={3} fill="#f97316" />
            } />
          </LineChart>
        </ResponsiveContainer>
        <div style={{ display: 'flex', gap: 16, marginTop: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#6b6b8a' }}>
            <div style={{ width: 10, height: 3, background: '#f97316', borderRadius: 2 }} /> Historical
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#6b6b8a' }}>
            <div style={{ width: 10, height: 10, background: '#a78bfa', borderRadius: '50%' }} /> Forecast
          </div>
        </div>
      </div>

      {/* Summary text */}
      {summary?.summary && (
        <div style={{
          background: 'rgba(124,58,237,0.08)', border: '1px solid rgba(124,58,237,0.2)',
          borderRadius: 16, padding: 24,
        }}>
          <div style={{ fontSize: 11, color: '#a78bfa', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 10 }}>AI Summary</div>
          <div style={{ fontSize: 15, color: '#cbd5e1', lineHeight: 1.7 }}>{summary.summary}</div>
        </div>
      )}
    </div>
  )
}
