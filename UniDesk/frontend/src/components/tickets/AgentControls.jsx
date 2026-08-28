import { useState } from "react";

const STATUS_OPTIONS = ["open", "in_progress", "resolved", "closed"];
const PRIORITY_OPTIONS = ["low", "medium", "high"];

export default function AgentControls({
  ticket,
  agents,
  onUpdate,
  onAssignmentUpdate,
}) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleChange(field, value) {
    setSaving(true);
    setError("");
    try {
      await onUpdate({ [field]: value });
    } catch (err) {
      setError(err.response?.data?.detail ?? "Failed to update ticket.");
    } finally {
      setSaving(false);
    }
  }

  async function handleAssignmentChange(value) {
    setSaving(true);
    setError("");
    try {
      await onAssignmentUpdate(value);
    } catch (err) {
      setError(err.response?.data?.detail ?? "Failed to update assignment.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-900">
        Agent Controls
      </h3>
      <div className="flex flex-wrap gap-4">
        <label className="flex flex-col gap-1 text-sm text-gray-600">
          Status
          <select
            value={ticket.status}
            onChange={(event) => handleChange("status", event.target.value)}
            disabled={saving}
            className="rounded-md border border-gray-300 px-2 py-1 text-sm"
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option.replace("_", " ")}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm text-gray-600">
          Priority
          <select
            value={ticket.priority}
            onChange={(event) => handleChange("priority", event.target.value)}
            disabled={saving}
            className="rounded-md border border-gray-300 px-2 py-1 text-sm"
          >
            {PRIORITY_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm text-gray-600">
          Assigned agent
          <select
            value={ticket.assigned_to ?? ""}
            onChange={(event) =>
              handleAssignmentChange(
                event.target.value ? Number(event.target.value) : null,
              )
            }
            disabled={saving}
            className="rounded-md border border-gray-300 px-2 py-1 text-sm"
          >
            <option value="">Unassigned</option>
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );
}
