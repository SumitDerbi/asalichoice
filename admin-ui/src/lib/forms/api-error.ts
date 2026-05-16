import { ApiError } from '@/lib/api/errors';

/**
 * Structured field errors recovered from an API error envelope. Keys are
 * top-level field names; values are user-visible messages.
 */
export type FieldErrors = Record<string, string>;

/**
 * Result of mapping an API error to form state. ``fields`` holds per-field
 * errors that should be displayed inline. ``formMessage`` is the fallback
 * message to surface as a toast or form-level banner.
 */
export interface MappedApiError {
  fields: FieldErrors;
  formMessage: string;
}

interface MapOptions {
  /**
   * Treat these top-level field names as known. Unknown keys returned by the
   * server are collapsed into the form-level message. Pass ``undefined`` to
   * accept every key.
   */
  knownFields?: readonly string[];
}

/**
 * Map an API error envelope ``{ error: { code, message, details } }`` to a
 * per-field error map plus a fallback message.
 *
 * Recognises two conventions for ``details``:
 *   1. ``{ fields: { email: 'Required' } }`` (preferred, per
 *      ``docs/api/conventions.md``).
 *   2. ``{ email: ['Required'] }`` (DRF ``ValidationError`` raw shape, also
 *      accepted for ergonomic mapping at the boundary).
 */
export function mapApiErrorToFields(error: unknown, options: MapOptions = {}): MappedApiError {
  const fallback = 'Unexpected error. Please try again.';
  if (!(error instanceof ApiError)) {
    return {
      fields: {},
      formMessage: error instanceof Error && error.message ? error.message : fallback,
    };
  }

  const fields: FieldErrors = {};
  const details = error.details ?? {};
  const rawFields = (details as { fields?: unknown }).fields;

  if (rawFields && typeof rawFields === 'object' && !Array.isArray(rawFields)) {
    for (const [key, value] of Object.entries(rawFields as Record<string, unknown>)) {
      const message = extractMessage(value);
      if (message) fields[key] = message;
    }
  } else if (details && typeof details === 'object') {
    for (const [key, value] of Object.entries(details as Record<string, unknown>)) {
      if (key === 'fields') continue;
      const message = extractMessage(value);
      if (message) fields[key] = message;
    }
  }

  // Drop unknown keys when ``knownFields`` is provided so stray server
  // payloads don't silently disappear into a void.
  let unknownLeak = false;
  if (options.knownFields) {
    const allowed = new Set(options.knownFields);
    for (const key of Object.keys(fields)) {
      if (!allowed.has(key)) {
        unknownLeak = true;
        delete fields[key];
      }
    }
  }

  const hasFieldErrors = Object.keys(fields).length > 0;
  const formMessage = hasFieldErrors && !unknownLeak ? '' : error.message || fallback;

  return { fields, formMessage };
}

function extractMessage(value: unknown): string | null {
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) {
    for (const item of value) {
      const msg = extractMessage(item);
      if (msg) return msg;
    }
    return null;
  }
  if (value && typeof value === 'object' && 'message' in value) {
    const message = (value as { message?: unknown }).message;
    if (typeof message === 'string') return message;
  }
  return null;
}
