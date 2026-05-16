import type { z } from 'zod';

/**
 * Build a form-level validator function from a Zod schema. Returns a record
 * of field path -> first error message, suitable for use as TanStack Form's
 * ``validators.onChange`` / ``onSubmit`` return value.
 *
 * Only top-level fields are flattened (good enough for the admin forms in
 * this codebase). Nested object paths can be wired by callers when needed.
 */
export function zodFormValidator<TSchema extends z.ZodTypeAny>(schema: TSchema) {
  return ({ value }: { value: unknown }) => {
    const result = schema.safeParse(value);
    if (result.success) return undefined;

    const fields: Record<string, string> = {};
    for (const issue of result.error.issues) {
      const key = String(issue.path[0] ?? '');
      if (key && !fields[key]) {
        fields[key] = issue.message;
      }
    }
    // TanStack Form expects either a string (form-level) or an object keyed
    // by field name when used at form-level.
    return { fields };
  };
}

/**
 * Validate a single value against a Zod schema and return the first error
 * message, or ``undefined`` when valid. Use inside per-field validators.
 */
export function zodFieldValidator<TSchema extends z.ZodTypeAny>(schema: TSchema) {
  return ({ value }: { value: unknown }) => {
    const result = schema.safeParse(value);
    if (result.success) return undefined;
    return result.error.issues[0]?.message ?? 'Invalid value';
  };
}
