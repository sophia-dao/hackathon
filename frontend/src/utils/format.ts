export function formatNumber(value: number, digits = 2): string {
  return value.toFixed(digits);
}

export function trendLabel(current: number, forecast: number): string {
  if (forecast > current + 0.05) return "Rising";
  if (forecast < current - 0.05) return "Falling";
  return "Stable";
}