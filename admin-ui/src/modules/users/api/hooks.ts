export function useUserResendInvite() {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.post(`/users/users/${id}/resend_invite/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  });
}
import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type {
  Paginated,
  Permission,
  Role,
  RoleInput,
  User,
  UserBranchAccess,
  UserInput,
  UserRoleAssignment,
} from './types';

type ListParams = Record<string, string | number | boolean | undefined>;

function qs(params?: ListParams): string {
  if (!params) return '';
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v == null || v === '') continue;
    search.set(k, String(v));
  }
  const s = search.toString();
  return s ? `?${s}` : '';
}

async function fetchList<T>(path: string, params?: ListParams): Promise<T[]> {
  const res = await apiClient.get<Paginated<T> | T[]>(`${path}${qs(params)}`);
  return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------

export function useUsersList(
  params?: ListParams,
  options?: Omit<UseQueryOptions<User[], Error>, 'queryKey' | 'queryFn'>,
) {
  return useQuery<User[], Error>({
    queryKey: ['users', 'list', params ?? {}],
    queryFn: () => fetchList<User>('/users/users/', params),
    ...options,
  });
}

export function useUserCreate() {
  const qc = useQueryClient();
  return useMutation<User, Error, UserInput>({
    mutationFn: async (values) => (await apiClient.post<User>('/users/users/', values)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  });
}

export function useUserUpdate() {
  const qc = useQueryClient();
  return useMutation<User, Error, { id: number; values: Partial<UserInput> }>({
    mutationFn: async ({ id, values }) =>
      (await apiClient.patch<User>(`/users/users/${id}/`, values)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  });
}

export function useUserDeactivate() {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.delete(`/users/users/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  });
}

export function useUserReactivate() {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.patch(`/users/users/${id}/`, { is_active: true });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  });
}

// ---------------------------------------------------------------------------
// Roles
// ---------------------------------------------------------------------------

export function useRolesList(params?: ListParams) {
  return useQuery<Role[], Error>({
    queryKey: ['roles', 'list', params ?? {}],
    queryFn: () => fetchList<Role>('/users/roles/', params),
  });
}

export function useRoleCreate() {
  const qc = useQueryClient();
  return useMutation<Role, Error, RoleInput>({
    mutationFn: async (values) => (await apiClient.post<Role>('/users/roles/', values)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['roles'] }),
  });
}

export function useRoleUpdate() {
  const qc = useQueryClient();
  return useMutation<Role, Error, { id: number; values: Partial<RoleInput> }>({
    mutationFn: async ({ id, values }) =>
      (await apiClient.patch<Role>(`/users/roles/${id}/`, values)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['roles'] }),
  });
}

export function useRoleDeactivate() {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.delete(`/users/roles/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['roles'] }),
  });
}

// ---------------------------------------------------------------------------
// Permissions (read-only catalog)
// ---------------------------------------------------------------------------

export function usePermissionsList() {
  return useQuery<Permission[], Error>({
    queryKey: ['permissions', 'list'],
    queryFn: () => fetchList<Permission>('/users/permissions/'),
    staleTime: 5 * 60_000,
  });
}

// ---------------------------------------------------------------------------
// UserRole assignments
// ---------------------------------------------------------------------------

export function useUserRolesList(userId?: number) {
  return useQuery<UserRoleAssignment[], Error>({
    queryKey: ['user-roles', userId ?? 'all'],
    enabled: userId !== undefined,
    queryFn: () => fetchList<UserRoleAssignment>('/users/user-roles/', { user: userId }),
  });
}

export function useUserRoleCreate() {
  const qc = useQueryClient();
  return useMutation<
    UserRoleAssignment,
    Error,
    { user: number; role: number; branch?: number | null }
  >({
    mutationFn: async (values) =>
      (await apiClient.post<UserRoleAssignment>('/users/user-roles/', values)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['user-roles'] });
      qc.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useUserRoleDelete() {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.delete(`/users/user-roles/${id}/`);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['user-roles'] });
      qc.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

// ---------------------------------------------------------------------------
// UserBranchAccess
// ---------------------------------------------------------------------------

export function useBranchAccessList(userId?: number) {
  return useQuery<UserBranchAccess[], Error>({
    queryKey: ['branch-access', userId ?? 'all'],
    enabled: userId !== undefined,
    queryFn: () => fetchList<UserBranchAccess>('/users/branch-access/', { user: userId }),
  });
}

export function useBranchAccessCreate() {
  const qc = useQueryClient();
  return useMutation<
    UserBranchAccess,
    Error,
    { user: number; branch: number; is_default?: boolean }
  >({
    mutationFn: async (values) =>
      (await apiClient.post<UserBranchAccess>('/users/branch-access/', values)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['branch-access'] }),
  });
}

export function useBranchAccessDelete() {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.delete(`/users/branch-access/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['branch-access'] }),
  });
}

export function useBranchAccessSetDefault() {
  const qc = useQueryClient();
  return useMutation<void, Error, { user_id: number; branch_id: number }>({
    mutationFn: async (values) => {
      await apiClient.post('/users/branch-access/set-default/', values);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['branch-access'] }),
  });
}
