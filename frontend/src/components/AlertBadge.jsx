import { alertColor } from '../utils'

export default function AlertBadge({ level, size = 'sm' }) {
  const c = alertColor(level)
  const pad = size === 'lg' ? '6px 16px' : '3px 10px'
  const fs = size === 'lg' ? 14 : 11
  return (
    <span style={{
      background: c.bg,
      color: c.text,
      border: `1px solid ${c.border}`,
      borderRadius: 999,
      padding: pad,
      fontSize: fs,
      fontWeight: 600,
      letterSpacing: '0.05em',
      textTransform: 'uppercase',
      display: 'inline-block',
    }}>{level}</span>
  )
}
