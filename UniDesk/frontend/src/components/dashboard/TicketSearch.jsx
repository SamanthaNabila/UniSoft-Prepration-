export default function TicketSearch({ value, onChange }) {
  return (
    <div>
      <label htmlFor="ticket-search" className="sr-only">
        Search tickets
      </label>
      <input
        id="ticket-search"
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Search tickets..."
        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
      />
    </div>
  );
}
