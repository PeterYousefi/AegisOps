import type { AuditEvent } from "@/lib/types";
import { formatDateTime, humanize } from "@/lib/format";
import { EmptyState } from "@/components/ui/empty-state";

/** Append-only audit timeline for an incident. */
export function AuditTimeline({ events }: { events: AuditEvent[] }) {
  return (
    <section aria-labelledby="audit-heading">
      <h2 id="audit-heading" className="mb-3 text-lg font-semibold">
        Audit timeline
      </h2>
      {events.length === 0 ? (
        <EmptyState title="No audit events yet" />
      ) : (
        <ol className="space-y-2">
          {events.map((event) => (
            <li
              key={event.id}
              className="flex flex-wrap items-baseline gap-x-2 rounded-md border border-gray-100 p-2 text-sm"
            >
              <span className="font-medium text-gray-900">
                {humanize(event.event_type)}
              </span>
              <span className="text-gray-500">
                by {event.actor_type}:{event.actor_id}
              </span>
              {event.previous_state && event.new_state ? (
                <span className="text-gray-500">
                  ({event.previous_state} → {event.new_state})
                </span>
              ) : null}
              <span className="ml-auto text-xs text-gray-400">
                {formatDateTime(event.created_at)}
              </span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
