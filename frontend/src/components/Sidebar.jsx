import { LayoutDashboard, TrendingUp, Bell, BarChart2, Globe, Layers, Settings } from 'lucide-react'

const items = [
  { icon: LayoutDashboard, tab: 'dashboard', label: 'Dashboard' },
  { icon: Globe,           tab: 'overview',  label: 'Overview'  },
  { icon: TrendingUp,      tab: 'forecast',  label: 'Forecast'  },
  { icon: Bell,            tab: 'alerts',    label: 'Alerts'    },
  { icon: BarChart2,       tab: 'drivers',   label: 'Drivers'   },
  { icon: Layers,          tab: 'system',    label: 'System'    },
]

export default function Sidebar({ activeTab, onTabChange }) {
  return (
    <aside style={{
      width: 64,
      background: '#0d0d14',
      borderRight: '1px solid #1e1e2e',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '20px 0',
      gap: 8,
      flexShrink: 0,
    }}>
      <div style={{
        width: 36, height: 36,
        background: 'linear-gradient(135deg, #7c3aed, #f97316)',
        borderRadius: 10,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 16, fontWeight: 700, color: '#fff',
        marginBottom: 24,
      }}>G</div>

      {items.map(({ icon: Icon, tab, label }) => {
        const active = activeTab === tab
        return (
          <button
            key={tab}
            title={label}
            onClick={() => onTabChange(tab)}
            style={{
              width: 40, height: 40,
              background: active ? 'rgba(124,58,237,0.2)' : 'transparent',
              border: active ? '1px solid rgba(124,58,237,0.4)' : '1px solid transparent',
              borderRadius: 10,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer',
              color: active ? '#a78bfa' : '#4a4a6a',
              transition: 'all 0.2s',
            }}
          >
            <Icon size={18} />
          </button>
        )
      })}

      <div style={{ flex: 1 }} />
      <button style={{
        width: 40, height: 40,
        background: 'transparent', border: '1px solid transparent',
        borderRadius: 10, cursor: 'pointer', color: '#4a4a6a',
      }}>
        <Settings size={18} />
      </button>
    </aside>
  )
}
