import AlertBadge from './AlertBadge'
import { fmt, TREND_META, alertColor } from '../utils'
import {
  ResponsiveContainer, RadialBarChart, RadialBar, PolarAngleAxis,
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
} from 'recharts'

function StatRow({ label, value, color }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '12px 0', borderBottom: '1px solid #1e1e2e',
    }}>
      <span style={{ fontSize: 13, color: '#9ca3af' }}>{label}</span>
      <span style={{ fontSize: 13, fontWeight: 600, color: color ?? '#fff' }}>{value}</span>
    </div>
  )
}

export default function OverviewView({ current, forecast, summary, history }) {
  const trend = TREND_META[summary?.trend] ?? TREND_META.stable
  const ac = alertColor(current?.alert ?? 'Moderate')

  // Normalise GSSI to 0-100 for gauge display
  const gssiMin = -2, gssiMax = 3
  const gssiPct = Math.min(100, Math.max(0,
    ((current?.gssi ?? 0) - gssiMin) / (gssiMax - gssiMin) * 100
  ))

  const gaugeData = [{ value: gssiPct, fill: ac.text }]

  const sparkData = (history ?? []).slice(-12).map(r => ({
    week: String(r.week ?? r.date ?? '').slice(5, 10),
    gssi: Number(r.gssi),
  }))

  const totalWeeks = (history ?? []).length
  const alertCounts = (history ?? []).reduce((acc, r) => {
    const l = r.alert ?? 'Moderate'
    acc[l] = (acc[l] ?? 0) + 1
    return acc
  }, {})
  const dominantAlert = Object.entries(alertCounts).sort((a, b) => b[1] - a[1])[0]?.[0] ?? '—'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div style={{ fontSize: 20, fontWeight: 700, color: '#fff' }}>Overview</div>

      {/* Top row */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>

        {/* GSSI Gauge */}
        <div style={{
          background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16,
          padding: 28, flex: 1, minWidth: 220,
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
        }}>
          <div style={{ fontSize: 11, color: '#6b6b8a', textTransform: 'uppercase', letterSpacing: '0.08em' }}>GSSI Gauge</div>
          <div style={{ position: 'relative', width: 180, height: 130 }}>
            {/* Arc only — taller container so the arc ends don't overlap the label */}
            <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: 110 }}>
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart
                  cx="50%" cy="100%" innerRadius="65%" outerRadius="95%"
                  startAngle={180} endAngle={0} data={gaugeData}
                >
                  <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                  <RadialBar dataKey="value" background={{ fill: '#1e1e2e' }} cornerRadius={6} />
                </RadialBarChart>
              </ResponsiveContainer>
            </div>
            {/* Label sits below the arc */}
            <div style={{
              position: 'absolute', bottom: 0, left: '50%', transform: 'translateX(-50%)',
              textAlign: 'center', whiteSpace: 'nowrap',
            }}>
              <div style={{ fontSize: 26, fontWeight: 800, color: ac.text, lineHeight: 1 }}>{fmt(current?.gssi)}</div>
              <div style={{ fontSize: 11, color: '#6b6b8a', marginTop: 2 }}>GSSI</div>
            </div>
          </div>
          <AlertBadge level={current?.alert ?? 'Moderate'} size="lg" />
        </div>

        {/* Summary text */}
        <div style={{
          background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16,
          padding: 28, flex: 2, minWidth: 280,
        }}>
          <div style={{ fontSize: 11, color: '#a78bfa', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600, marginBottom: 14 }}>AI Summary</div>
          <div style={{ fontSize: 15, color: '#e2e8f0', lineHeight: 1.8, marginBottom: 20 }}>
            {summary?.ai_summary ?? (summary
              ? `GSSI is currently ${summary.current_gssi?.toFixed(2)} (${summary.current_alert}). Next week is forecast at ${summary.predicted_gssi?.toFixed(2)} (${summary.predicted_alert}), indicating a ${summary.trend} supply chain outlook.`
              : '—')}
          </div>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            <div style={{ background: '#13131f', borderRadius: 10, padding: '10px 16px' }}>
              <div style={{ fontSize: 11, color: '#6b6b8a' }}>Trend</div>
              <div style={{ fontSize: 15, fontWeight: 700, color: trend.color, marginTop: 2 }}>{trend.icon} {trend.label}</div>
            </div>
            <div style={{ background: '#13131f', borderRadius: 10, padding: '10px 16px' }}>
              <div style={{ fontSize: 11, color: '#6b6b8a' }}>Forecast</div>
              <div style={{ fontSize: 15, fontWeight: 700, color: '#a78bfa', marginTop: 2 }}>{fmt(forecast?.predicted_gssi)} GSSI</div>
            </div>
            <div style={{ background: '#13131f', borderRadius: 10, padding: '10px 16px' }}>
              <div style={{ fontSize: 11, color: '#6b6b8a' }}>Next Week</div>
              <div style={{ fontSize: 15, fontWeight: 700, color: '#fff', marginTop: 2 }}>{forecast?.forecast_week?.slice(0, 10) ?? '—'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendation cards */}
      {summary?.ai_recommendations && (() => {
        const cards = [
          { key: 'investors', label: 'Investor Strategy',       color: '#34d399', sub: 'Portfolio & asset allocation' },
          { key: 'risk',      label: 'Risk Management',         color: '#fb7185', sub: 'Corporations & financial institutions' },
          { key: 'policy',    label: 'Policy Response',         color: '#38bdf8', sub: 'Regulators & governments' },
        ]
        return (
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            {cards.map(({ key, label, color, sub }) => (
              <div key={key} style={{ background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16, padding: 28, flex: 1, minWidth: 260 }}>
                <div style={{ marginBottom: 18 }}>
                  <div style={{ fontSize: 11, color, textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>{label}</div>
                  <div style={{ fontSize: 11, color: '#6b6b8a', marginTop: 3 }}>{sub}</div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {(summary.ai_recommendations[key] ?? []).map((item, i) => (
                    <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'flex-start', background: '#13131f', borderRadius: 10, padding: '12px 16px' }}>
                      <span style={{ color, fontWeight: 700, flexShrink: 0 }}>→</span>
                      <span style={{ fontSize: 13, color: '#e2e8f0', lineHeight: 1.6 }}>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )
      })()}

      {/* Sparkline + Stats */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>

        {/* 12-week sparkline */}
        <div style={{
          background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16,
          padding: 24, flex: 2, minWidth: 280,
        }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#9ca3af', marginBottom: 16 }}>Last 12 Weeks</div>
          <ResponsiveContainer width="100%" height={140}>
            <AreaChart data={sparkData} margin={{ top: 4, right: 4, left: -30, bottom: 0 }}>
              <defs>
                <linearGradient id="ovGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={ac.text} stopOpacity={0.25} />
                  <stop offset="95%" stopColor={ac.text} stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
              <XAxis dataKey="week" tick={{ fill: '#4a4a6a', fontSize: 10 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: '#4a4a6a', fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ background: '#13131f', border: '1px solid #2a2a3e', borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: '#6b6b8a' }} itemStyle={{ color: '#fff' }}
              />
              <Area type="monotone" dataKey="gssi" stroke={ac.text} strokeWidth={2} fill="url(#ovGrad)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Key stats */}
        <div style={{
          background: '#0d0d14', border: '1px solid #1e1e2e', borderRadius: 16,
          padding: '24px 28px', flex: 1, minWidth: 220,
        }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#9ca3af', marginBottom: 4 }}>Key Statistics</div>
          <StatRow label="Current GSSI"   value={fmt(current?.gssi)}           color={ac.text} />
          <StatRow label="Current Alert"  value={current?.alert ?? '—'}        color={ac.text} />
          <StatRow label="Forecast GSSI"  value={fmt(forecast?.predicted_gssi)} color="#a78bfa" />
          <StatRow label="Forecast Alert" value={forecast?.predicted_alert ?? '—'} />
          <StatRow label="Trend"          value={`${trend.icon} ${trend.label}`} color={trend.color} />
          <StatRow label="Weeks of Data"  value={totalWeeks} />
          <StatRow label="Most Common Alert" value={dominantAlert} />
        </div>
      </div>
    </div>
  )
}
