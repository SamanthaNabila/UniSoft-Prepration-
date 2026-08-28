const TABS = [
  { value: 'all', label: 'All' },
  { value: 'unassigned', label: 'Unassigned' },
  { value: 'me', label: 'Assigned to Me' },
]

export default function AssignmentFilterTabs({ active, onChange, showAssignedToMe }) {
  const visibleTabs = showAssignedToMe
    ? TABS
    : TABS.filter((tab) => tab.value !== 'me')

  return (
    <div className="flex flex-wrap gap-2">
      {visibleTabs.map((tab) => (
        <button
          key={tab.value}
          type="button"
          onClick={() => onChange(tab.value)}
          className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${
            active === tab.value
              ? 'bg-slate-800 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}
