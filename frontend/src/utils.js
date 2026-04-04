export const ALERT_COLORS = {
  Low:      { bg: 'rgba(34,197,94,0.15)',  text: '#22c55e', border: 'rgba(34,197,94,0.3)'  },
  Moderate: { bg: 'rgba(245,158,11,0.15)', text: '#f59e0b', border: 'rgba(245,158,11,0.3)' },
  High:     { bg: 'rgba(249,115,22,0.15)', text: '#f97316', border: 'rgba(249,115,22,0.3)' },
  Critical: { bg: 'rgba(239,68,68,0.15)',  text: '#ef4444', border: 'rgba(239,68,68,0.3)'  },
}

export const TREND_META = {
  improving: { icon: '↓', color: '#22c55e', label: 'Improving' },
  stable:    { icon: '→', color: '#f59e0b', label: 'Stable'    },
  worsening: { icon: '↑', color: '#ef4444', label: 'Worsening' },
}

export function alertColor(level) {
  return ALERT_COLORS[level] ?? ALERT_COLORS.Moderate
}

export function fmt(n, decimals = 2) {
  if (n == null) return '—'
  return Number(n).toFixed(decimals)
}
