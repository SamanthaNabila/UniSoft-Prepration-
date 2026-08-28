import { useEffect, useState } from "react";
import Navbar from "../components/common/Navbar";
import MetricsBar from "../components/dashboard/MetricsBar";
import FilterTabs from "../components/dashboard/FilterTabs";
import AssignmentFilterTabs from "../components/dashboard/AssignmentFilterTabs";
import TicketSearch from "../components/dashboard/TicketSearch";
import TicketCard from "../components/dashboard/TicketCard";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function DashboardView() {
  const { user } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState("all");
  const [assignmentFilter, setAssignmentFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    setIsLoading(true);
    setError("");

    const params = new URLSearchParams();
    if (filter !== "all") params.set("status", filter);
    if (assignmentFilter !== "all") params.set("assigned_to", assignmentFilter);
    const query = params.toString() ? `?${params.toString()}` : "";

    Promise.all([api.get(`/tickets${query}`), api.get("/tickets/stats")])
      .then(([ticketsRes, statsRes]) => {
        if (ignore) return;
        setTickets(ticketsRes.data);
        setStats(statsRes.data);
      })
      .catch(() => {
        if (!ignore) setError("Failed to load tickets.");
      })
      .finally(() => {
        if (!ignore) setIsLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [filter, assignmentFilter]);

  const normalizedSearch = search.trim().toLowerCase();
  const visibleTickets = normalizedSearch
    ? tickets.filter((ticket) =>
        [ticket.title, ticket.description, ticket.created_by_name].some(
          (value) => value?.toLowerCase().includes(normalizedSearch),
        ),
      )
    : tickets;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="mx-auto max-w-5xl space-y-6 px-4 py-6">
        <MetricsBar stats={stats} />
        <TicketSearch value={search} onChange={setSearch} />
        <FilterTabs active={filter} onChange={setFilter} />
        <AssignmentFilterTabs
          active={assignmentFilter}
          onChange={setAssignmentFilter}
          showAssignedToMe={user?.role === "support_agent"}
        />

        {error && <p className="text-sm text-red-600">{error}</p>}
        {isLoading ? (
          <p className="text-sm text-gray-400">Loading tickets...</p>
        ) : visibleTickets.length === 0 ? (
          <p className="text-sm text-gray-400">
            {normalizedSearch
              ? "No tickets match your search."
              : "No tickets found for this view."}
          </p>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {visibleTickets.map((ticket) => (
              <TicketCard key={ticket.id} ticket={ticket} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
