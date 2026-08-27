const CARDS = [
  { key: 'total', label: 'Total' },
  { key: 'open', label: 'Open' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'resolved', label: 'Resolved' },
  { key: 'closed', label: 'Closed' },
]

export default function MetricsBar({ stats }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
      {CARDS.map((card) => (
        <div
          key={card.key}
          className="rounded-lg border border-gray-200 bg-white p-4 text-center"
        >
          <p className="text-2xl font-semibold text-gray-900">
            {stats?.[card.key] ?? 0}
          </p>
          <p className="text-xs text-gray-500">{card.label}</p>
        </div>
      ))}
    </div>
  )
}
