import * as React from 'react';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { runSubmit } from './submit-handler';
import type { FieldErrors } from './api-error';

interface InlineEditCellProps<TValue> {
  /** Current persisted value. */
  value: TValue;
  /** PATCH the row on blur. Reject with ApiError to roll back. */
  onCommit: (next: TValue) => Promise<unknown>;
  /** Optional input ``type`` (default ``text``). */
  type?: React.HTMLInputTypeAttribute;
  /** Format the persisted value for display. */
  format?: (value: TValue) => string;
  /** Parse the raw input value back to ``TValue``. */
  parse?: (raw: string) => TValue;
  /**
   * Optional name for the cell — used as ``aria-label`` and as the only
   * recognised ``knownFields`` entry when mapping API errors.
   */
  name?: string;
  className?: string;
  disabled?: boolean;
}

/**
 * Editable table cell. Renders read-only text until clicked/focused, then
 * swaps to an ``<Input>``. On blur/Enter it calls ``onCommit`` with
 * optimistic UI: the cell shows the new value immediately and rolls back
 * to the previous value if ``onCommit`` throws.
 *
 * On rollback any ApiError message bubbles up through ``runSubmit`` so the
 * user sees a toast.
 */
export function InlineEditCell<TValue>({
  value,
  onCommit,
  type = 'text',
  format,
  parse,
  name,
  className,
  disabled,
}: InlineEditCellProps<TValue>) {
  const [editing, setEditing] = React.useState(false);
  const [draft, setDraft] = React.useState<string>(() => formatValue(value, format));
  const [optimistic, setOptimistic] = React.useState<TValue>(value);
  const [submitting, setSubmitting] = React.useState(false);
  const lastCommitted = React.useRef<TValue>(value);

  // Note: no auto-sync from ``value`` on prop change. Optimistic state
  // wins until commit/rollback. Callers that need to force-reset after an
  // external refetch should remount the cell (e.g. ``key={row.version}``).

  async function commit() {
    setEditing(false);
    const next = parse ? parse(draft) : (draft as unknown as TValue);
    if (Object.is(next, lastCommitted.current)) return;

    const previous = lastCommitted.current;
    setOptimistic(next);
    setSubmitting(true);

    const ok = await runSubmit(next, {
      action: (val) => onCommit(val),
      knownFields: name ? [name] : undefined,
      successMessage: null,
      onFieldErrors: (errors: FieldErrors) => {
        return Boolean(name && errors[name]);
      },
    });

    setSubmitting(false);
    if (!ok) {
      // Roll back optimistic state.
      setOptimistic(previous);
      setDraft(formatValue(previous, format));
      return;
    }
    lastCommitted.current = next;
  }

  if (!editing) {
    return (
      <button
        type="button"
        aria-label={name ? `Edit ${name}` : 'Edit cell'}
        onClick={() => !disabled && setEditing(true)}
        disabled={disabled || submitting}
        className={cn(
          'block w-full cursor-text rounded px-1 text-left hover:bg-muted/40',
          submitting && 'opacity-60',
          className,
        )}
      >
        {formatValue(optimistic, format) || <span className="text-muted-foreground">--</span>}
      </button>
    );
  }

  return (
    <Input
      autoFocus
      type={type}
      value={draft}
      onChange={(e) => setDraft(e.target.value)}
      onBlur={commit}
      onKeyDown={(e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          (e.target as HTMLInputElement).blur();
        } else if (e.key === 'Escape') {
          e.preventDefault();
          setDraft(formatValue(lastCommitted.current, format));
          setEditing(false);
        }
      }}
      className={cn('h-8', className)}
      aria-label={name}
    />
  );
}

function formatValue<TValue>(value: TValue, format?: (v: TValue) => string): string {
  if (format) return format(value);
  if (value == null) return '';
  return String(value);
}
