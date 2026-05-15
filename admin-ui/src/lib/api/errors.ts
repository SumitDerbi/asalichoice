/**
 * API error envelope, per plans/_conventions.md §5.
 *
 *   { "error": { "code": "AUTH-001", "message": "...", "details": {...} } }
 */
export interface ApiErrorPayload {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export class ApiError extends Error {
  public readonly code: string;
  public readonly status: number;
  public readonly details?: Record<string, unknown>;

  constructor(payload: ApiErrorPayload, status: number) {
    super(payload.message);
    this.name = 'ApiError';
    this.code = payload.code;
    this.status = status;
    this.details = payload.details;
  }
}
