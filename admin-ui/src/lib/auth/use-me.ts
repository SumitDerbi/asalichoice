import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { useAuthStore, type AuthUser } from '@/lib/auth/store';

/**
 * Fetches the canonical user envelope from ``/api/v1/auth/me/``.
 *
 * The response includes resolved permissions and accessible branches —
 * always derive permission checks from this query instead of inspecting
 * the cached auth store, which only has the last login snapshot.
 */
export function useMe(): UseQueryResult<AuthUser, Error> {
  const token = useAuthStore((s) => s.accessToken);
  return useQuery<AuthUser, Error>({
    queryKey: ['auth', 'me'],
    enabled: Boolean(token),
    staleTime: 60_000,
    queryFn: async () => {
      const resp = await apiClient.get<AuthUser>('/auth/me/');
      return resp.data;
    },
  });
}

/**
 * Returns ``true`` when the current user holds *all* of the supplied
 * permission codes. Superusers (``permissions`` contains ``"*"``) always
 * resolve true. Returns ``undefined`` while the ``/me`` query is in
 * flight so callers can render a loading state.
 */
export function useHasPermission(codes: string | string[]): boolean | undefined {
  const { data, isLoading } = useMe();
  if (isLoading || !data) return undefined;
  const required = Array.isArray(codes) ? codes : [codes];
  if (required.length === 0) return true;
  if (data.is_superuser) return true;
  const owned = new Set(data.permissions ?? []);
  if (owned.has('*')) return true;
  return required.every((code) => owned.has(code));
}

/**
 * Returns the list of branch IDs the current user can access. An empty
 * list means **no restriction** (superuser / staff with no explicit
 * scoping). Returns ``undefined`` while the query is loading.
 */
export function useUserBranches(): number[] | undefined {
  const { data, isLoading } = useMe();
  if (isLoading || !data) return undefined;
  return (data.branches ?? []).map((b) => b.branch_id);
}
