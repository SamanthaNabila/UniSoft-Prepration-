const STATUS_STYLES = {
  open: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-amber-100 text-amber-700',
  resolved: 'bg-green-100 text-green-700',
  closed: 'bg-gray-200 text-gray-600',
}

const STATUS_LABELS = {
  open: 'Open',
  in_progress: 'In Progress',
  resolved: 'Resolved',
  closed: 'Closed',
}

const PRIORITY_STYLES = {
  low: 'bg-emerald-100 text-emerald-700',
  medium: 'bg-amber-100 text-amber-700',
  high: 'bg-red-100 text-red-700',
}

const PRIORITY_LABELS = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
}

export default function StatusBadge({ type, value }) {
  const styles = type === 'status' ? STATUS_STYLES : PRIORITY_STYLES
  const label = type === 'status' ? STATUS_LABELS[value] : PRIORITY_LABELS[value]

  return (
    <span
      className={`inline-flex items-center whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-medium ${
        styles[value] ?? 'bg-gray-100 text-gray-600'
      }`}
    >
      {label ?? value}
    </span>
  )
}
