export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export type PrimaryIdentifier = 'EMAIL' | 'MOBILE' | 'EMP_CODE';

export interface UserRoleRef {
  id: number;
  code: string;
  branch_id: number | null;
}

export interface User {
  id: number;
  email: string;
  mobile: string | null;
  employee_code: string | null;
  name: string;
  display_name: string;
  primary_identifier: PrimaryIdentifier;
  is_staff: boolean;
  is_superuser: boolean;
  is_active: boolean;
  date_joined: string;
  roles: UserRoleRef[];
}

export interface UserInput {
  email: string;
  mobile?: string | null;
  employee_code?: string | null;
  name?: string;
  primary_identifier?: PrimaryIdentifier;
  is_staff?: boolean;
  is_active?: boolean;
  password?: string;
  role_ids?: number[];
}

export interface Permission {
  id: number;
  code: string;
  name: string;
  module: string;
  description: string;
  is_active: boolean;
}

export interface Role {
  id: number;
  code: string;
  name: string;
  description: string;
  is_system: boolean;
  permission_ids: number[];
  is_active: boolean;
}

export interface RoleInput {
  code: string;
  name: string;
  description?: string;
  permission_ids?: number[];
}

export interface UserRoleAssignment {
  id: number;
  user: number;
  role: number;
  role_code: string;
  branch: number | null;
  branch_id: number | null;
  is_active: boolean;
}

export interface UserBranchAccess {
  id: number;
  user: number;
  branch: number;
  is_default: boolean;
  is_active: boolean;
}
