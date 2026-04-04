import { useEffect, useState } from 'react'
import { RefreshCw } from 'lucide-react'
import Sidebar from './components/Sidebar'
import MetricCard from './components/MetricCard'
import AlertBadge from './components/AlertBadge'
import HistoryChart from './components/HistoryChart'
import ForecastCard from './components/ForecastCard'
import DriversChart from './components/DriversChart'
import RecentAlerts from './components/RecentAlerts'
import ForecastView from './components/ForecastView'
import AlertsView from './components/AlertsView'
import DriversView from './components/DriversView'
import OverviewView from './components/OverviewView'
import SystemView from './components/SystemView'
import { fetchCurrent, fetchHistory, fetchForecast, fetchDrivers, fetchSummary } from './api'
import { fmt, TREND_META } from './utils'

const TAB_TITLES = {
  dashboard: 'Live Monitoring',
  overview:  'Overview',
  forecast:  'Forecast',
  alerts:    'Alerts',
  drivers:   'Drivers',
  system:    'System',
}

function Spinner() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1, flexDirection: 'column', gap: 16, minHeight: 300 }}>
      <div style={{
        width: 48, height: 48, border: '3px solid #1e1e2e',
        borderTop: '3px solid #f97316', borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      <div style={{ color: '#6b6b8a', fontSize: 14 }}>Running pipeline… this may take a moment</div>
    </div>
  )
}

export default function App() {
  const [data, setData]             = useState(null)
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [activeTab, setActiveTab]   = useState('dashboard')

  async function load() {
    try {
      setError(null)
      const [current, histRes, forecast, driversRes, summary] = await Promise.all([
        fetchCurrent(),
        fetchHistory(),
        fetchForecast(),
        fetchDrivers(),
        fetchSummary(),
      ])
      setData({ current, history: histRes.history, forecast, drivers: driversRes.drivers, summary })
    } catch (e) {
      setError(e.message)
    }
  }

  useEffect(() => {
    let cancelled = false
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load().finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  async function handleRefresh() {
    setRefreshing(true)
    await load()
    setRefreshing(false)
  }

  const trend = TREND_META[data?.summary?.trend] ?? TREND_META.stable

  return (
    <div style={{ display: 'flex', width: '100%', minHeight: '100vh' }}>
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'auto', minWidth: 0 }}>
        {/* Header */}
        <header style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '14px 28px', borderBottom: '1px solid #1e1e2e',
          background: '#0a0a0f', position: 'sticky', top: 0, zIndex: 10,
          flexShrink: 0,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: '#6b6b8a' }}>
            <span
              onClick={() => setActiveTab('system')}
              style={{ cursor: 'pointer', transition: 'color 0.15s' }}
              onMouseEnter={e => e.target.style.color = '#e2e8f0'}
              onMouseLeave={e => e.target.style.color = '#6b6b8a'}
            >System</span>
            <span style={{ color: '#2a2a3e' }}>›</span>
            <span
              onClick={() => setActiveTab('overview')}
              style={{ cursor: 'pointer', transition: 'color 0.15s' }}
              onMouseEnter={e => e.target.style.color = '#e2e8f0'}
              onMouseLeave={e => e.target.style.color = '#6b6b8a'}
            >Overview</span>
            <span style={{ color: '#2a2a3e' }}>›</span>
            <span style={{ color: '#e2e8f0', fontWeight: 500 }}>{TAB_TITLES[activeTab]}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {data?.current && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: '#6b6b8a' }}>
                <span>Week ending {String(data.current.week).slice(0, 10)}</span>
                <AlertBadge level={data.current.alert} />
              </div>
            )}
            <button onClick={handleRefresh} disabled={refreshing || loading} style={{
              display: 'flex', alignItems: 'center', gap: 8,
              background: 'linear-gradient(135deg, #7c3aed, #9333ea)',
              color: '#fff', border: 'none', borderRadius: 10,
              padding: '8px 18px', fontSize: 13, fontWeight: 600,
              cursor: (refreshing || loading) ? 'not-allowed' : 'pointer',
              opacity: (refreshing || loading) ? 0.7 : 1,
            }}>
              <RefreshCw size={14} style={{ animation: refreshing ? 'spin 0.8s linear infinite' : 'none' }} />
              {refreshing ? 'Refreshing…' : 'Refresh'}
            </button>
          </div>
        </header>

        {/* Main */}
        <main style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20, flex: 1 }}>
          {loading && <Spinner />}

          {error && !loading && (
            <div style={{
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: 12, padding: '16px 20px', color: '#ef4444', fontSize: 14,
            }}>
              ⚠ Failed to load data: {error}
              <div style={{ color: '#9ca3af', fontSize: 12, marginTop: 6 }}>
                Make sure <code style={{ background: '#1e1e2e', padding: '1px 6px', borderRadius: 4 }}>uvicorn app.main:app --reload</code> is running on port 8000.
              </div>
            </div>
          )}

          {data && activeTab === 'dashboard' && (
            <>
              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                <MetricCard
                  icon="📊"
                  label="GSSI Score"
                  value={fmt(data.current?.gssi)}
                  accentColor="#f97316"
                  sub={<><span style={{ fontSize: 14 }}>↗</span>&nbsp;Current index value</>}
                />
                <MetricCard
                  icon="🔮"
                  label="Forecast GSSI"
                  value={fmt(data.forecast?.predicted_gssi)}
                  accentColor="#a78bfa"
                  sub={<>Week of {data.forecast?.forecast_week?.slice(0, 10)}</>}
                />
                <MetricCard
                  icon="🚨"
                  label="Alert Level"
                  value={data.current?.alert ?? '—'}
                  accentColor={
                    data.current?.alert === 'Critical' ? '#ef4444' :
                    data.current?.alert === 'High'     ? '#f97316' :
                    data.current?.alert === 'Moderate' ? '#f59e0b' : '#22c55e'
                  }
                >
                  <div style={{ marginTop: 4 }}>
                    <AlertBadge level={data.current?.alert ?? 'Moderate'} />
                  </div>
                </MetricCard>
                <MetricCard
                  icon="📈"
                  label="Outlook"
                  value={trend.label}
                  accentColor={trend.color}
                  sub={<><span style={{ color: trend.color }}>{trend.icon}</span>&nbsp;Supply chain trend</>}
                />
              </div>

              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                <HistoryChart data={data.history} />
                <ForecastCard forecast={data.forecast} summary={data.summary} />
              </div>

              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                <DriversChart drivers={data.drivers} />
                <RecentAlerts history={data.history} />
              </div>
            </>
          )}

          {data && activeTab === 'overview' && (
            <OverviewView current={data.current} forecast={data.forecast} summary={data.summary} history={data.history} />
          )}

          {data && activeTab === 'forecast' && (
            <ForecastView forecast={data.forecast} summary={data.summary} history={data.history} />
          )}

          {data && activeTab === 'alerts' && (
            <AlertsView history={data.history} />
          )}

          {data && activeTab === 'drivers' && (
            <DriversView drivers={data.drivers} />
          )}

          {activeTab === 'system' && <SystemView />}
        </main>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
