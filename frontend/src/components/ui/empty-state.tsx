/**
 * Reusable empty-state block for lists and panels with no content.
 */
export function EmptyState({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center">
      <p className="text-sm font-medium text-gray-900">{title}</p>
      {description ? (
        <p className="mt-1 text-sm text-gray-600">{description}</p>
      ) : null}
    </div>
  );
}
