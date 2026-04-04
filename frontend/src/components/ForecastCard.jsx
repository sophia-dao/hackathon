import AlertBadge from './AlertBadge'
import { fmt, TREND_META } from '../utils'

export default function ForecastCard({ forecast, summary }) {
  const trend = TREND_META[summary?.trend] ?? TREND_META.stable

  return (
    <div style={{
      background: '#0d0d14', border: '1px solid #1e1e2e',
      borderRadius: 16, padding: 24, display: 'flex', flexDirection: 'column', gap: 20,
      flex: 1, minWidth: 0,
    }}>
      <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.08em', color: '#6b6b8a', textTransform: 'uppercase' }}>
        AI Forecast
      </div>

      {/* Forecast week */}
      <div style={{
        background: '#13131f', border: '1px solid #2a2a3e',
        borderRadius: 12, padding: '16px',
      }}>
        <div style={{ fontSize: 11, color: '#6b6b8a', marginBottom: 6 }}>Next Week</div>
        <div style={{ fontSize: 28, fontWeight: 700, color: '#fff', marginBottom: 8 }}>
          {fmt(forecast?.predicted_gssi)}
          <span style={{ fontSize: 14, color: '#6b6b8a', marginLeft: 6 }}>GSSI</span>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <AlertBadge level={forecast?.predicted_alert ?? 'Moderate'} />
          <span style={{ fontSize: 12, color: '#6b6b8a' }}>{forecast?.forecast_week?.slice(0, 10)}</span>
        </div>
      </div>

      {/* Trend */}
      <div style={{ display: 'flex', gap: 12 }}>
        <div style={{
          flex: 1, background: '#13131f', border: '1px solid #2a2a3e',
          borderRadius: 12, padding: '14px', textAlign: 'center',
        }}>
          <div style={{ fontSize: 22, color: trend.color, fontWeight: 700 }}>{trend.icon}</div>
          <div style={{ fontSize: 11, color: '#6b6b8a', marginTop: 4 }}>Trend</div>
          <div style={{ fontSize: 13, color: trend.color, fontWeight: 600, marginTop: 2 }}>{trend.label}</div>
        </div>
        <div style={{
          flex: 1, background: '#13131f', border: '1px solid #2a2a3e',
          borderRadius: 12, padding: '14px', textAlign: 'center',
        }}>
          <div style={{ fontSize: 22, color: '#fff', fontWeight: 700 }}>{fmt(summary?.current_gssi)}</div>
          <div style={{ fontSize: 11, color: '#6b6b8a', marginTop: 4 }}>Current</div>
          <AlertBadge level={summary?.current_alert ?? 'Moderate'} />
        </div>
      </div>

      {/* Summary text */}
      {summary?.summary && (
        <div style={{
          background: 'rgba(124,58,237,0.08)', border: '1px solid rgba(124,58,237,0.2)',
          borderRadius: 12, padding: 14,
        }}>
          <div style={{ fontSize: 11, color: '#a78bfa', fontWeight: 600, marginBottom: 6 }}>AI SUMMARY</div>
          <div style={{ fontSize: 13, color: '#cbd5e1', lineHeight: 1.6 }}>{summary.summary}</div>
        </div>
      )}
    </div>
  )
}
