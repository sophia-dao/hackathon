import type { AlertLevel } from "../types/gssi";

export function getAlertClasses(alert: AlertLevel): string {
  switch (alert) {
    case "Low":
      return "bg-green-100 text-green-700 border-green-200";
    case "Moderate":
      return "bg-yellow-100 text-yellow-700 border-yellow-200";
    case "High":
      return "bg-orange-100 text-orange-700 border-orange-200";
    case "Critical":
      return "bg-red-100 text-red-700 border-red-200";
    default:
      return "bg-gray-100 text-gray-700 border-gray-200";
  }
}