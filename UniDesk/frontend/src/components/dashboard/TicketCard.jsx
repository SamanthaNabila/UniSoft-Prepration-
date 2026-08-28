import { Link } from "react-router-dom";
import StatusBadge from "../common/StatusBadge";

export default function TicketCard({ ticket }) {
  const snippet =
    ticket.description.length > 120
      ? `${ticket.description.slice(0, 120)}...`
      : ticket.description;

  return (
    <Link
      to={`/tickets/${ticket.id}`}
      className="block rounded-lg border border-gray-200 bg-white p-4 transition hover:border-indigo-300 hover:shadow-sm"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium text-gray-900">{ticket.title}</h3>
        <StatusBadge type="priority" value={ticket.priority} />
      </div>
      <p className="mt-1 text-sm text-gray-500">{snippet}</p>
      <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-xs text-gray-400">
        <div className="flex items-center gap-2">
          <StatusBadge type="status" value={ticket.status} />
          <span>
            by {ticket.created_by_name} -{" "}
            {ticket.assigned_to_name
              ? `Assigned to ${ticket.assigned_to_name}`
              : "Unassigned"}
          </span>
        </div>
        <span>{new Date(ticket.created_at).toLocaleString()}</span>
      </div>
    </Link>
  );
}
