const TABS = [
  { value: 'all', label: 'All' },
  { value: 'open', label: 'Open' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'closed', label: 'Closed' },
]

export default function FilterTabs({ active, onChange, assignmentFilter, onAssignmentChange }) {
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {TABS.map((tab) => (
          <button
            key={tab.value}
            type="button"
            onClick={() => onChange(tab.value)}
            className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${
              active === tab.value
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        {[
          { value: 'all', label: 'All assignments' },
          { value: 'unassigned', label: 'Unassigned' },
          { value: 'mine', label: 'Assigned to Me' },
        ].map((tab) => (
          <button
            key={tab.value}
            type="button"
            onClick={() => onAssignmentChange(tab.value)}
            className={`rounded-full border px-3 py-1.5 text-sm font-medium transition ${
              assignmentFilter === tab.value
                ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                : 'border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  )
}
