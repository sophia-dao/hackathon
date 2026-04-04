const BASE = ''

export async function fetchCurrent() {
  const r = await fetch(`${BASE}/gssi/current`)
  if (!r.ok) throw new Error('Failed to fetch current')
  return r.json()
}

export async function fetchHistory() {
  const r = await fetch(`${BASE}/gssi/history`)
  if (!r.ok) throw new Error('Failed to fetch history')
  return r.json()
}

export async function fetchForecast() {
  const r = await fetch(`${BASE}/gssi/forecast`)
  if (!r.ok) throw new Error('Failed to fetch forecast')
  return r.json()
}

export async function fetchDrivers() {
  const r = await fetch(`${BASE}/gssi/drivers`)
  if (!r.ok) throw new Error('Failed to fetch drivers')
  return r.json()
}

export async function fetchSummary() {
  const r = await fetch(`${BASE}/gssi/ai-summary`)
  if (!r.ok) throw new Error('Failed to fetch summary')
  return r.json()
}
