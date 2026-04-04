import type { DriverContribution } from "../../types/gssi";

interface DriverCardProps {
  drivers: DriverContribution[];
}

export default function DriverCard({ drivers }: DriverCardProps) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Top Drivers</h2>

      <div className="space-y-4">
        {drivers.map((driver) => (
          <div key={driver.name}>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="text-gray-700">{driver.name}</span>
              <span className="font-medium text-gray-900">
                {(driver.contribution * 100).toFixed(0)}%
              </span>
            </div>

            <div className="h-2 w-full rounded-full bg-gray-100">
              <div
                className="h-2 rounded-full bg-gray-900"
                style={{ width: `${driver.contribution * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}