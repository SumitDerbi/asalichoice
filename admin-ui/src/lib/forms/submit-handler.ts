import { toast } from 'sonner';
import { ApiError } from '@/lib/api/errors';
import { mapApiErrorToFields, type FieldErrors } from './api-error';

interface SubmitOptions<TValues, TResult> {
  /** Async operation that performs the request. */
  action: (values: TValues) => Promise<TResult>;
  /** Called on 2xx. */
  onSuccess?: (result: TResult) => void;
  /**
   * Called once API field errors have been mapped. Use to update form state
   * (e.g. ``form.setFieldMeta``). Return ``true`` if the error was fully
   * handled and no toast should appear.
   */
  onFieldErrors?: (fields: FieldErrors) => boolean | void;
  /** Toast message on success. Pass ``null`` to skip. */
  successMessage?: string | null;
  /** Known field names — see ``mapApiErrorToFields``. */
  knownFields?: readonly string[];
}

/**
 * Standard submit wrapper. Calls ``action(values)``, fires a success toast,
 * and on ApiError maps the envelope to field errors plus an optional
 * form-level toast.
 *
 * Returns ``true`` when the action succeeded so callers can navigate or
 * close drawers.
 */
export async function runSubmit<TValues, TResult>(
  values: TValues,
  options: SubmitOptions<TValues, TResult>,
): Promise<boolean> {
  try {
    const result = await options.action(values);
    if (options.successMessage !== null) {
      toast.success(options.successMessage ?? 'Saved.');
    }
    options.onSuccess?.(result);
    return true;
  } catch (err) {
    const mapped = mapApiErrorToFields(err, { knownFields: options.knownFields });
    const handled = options.onFieldErrors?.(mapped.fields) === true;
    if (!handled && mapped.formMessage) {
      toast.error(mapped.formMessage);
    } else if (!handled && !mapped.formMessage && !(err instanceof ApiError)) {
      toast.error('Unexpected error. Please try again.');
    }
    return false;
  }
}
