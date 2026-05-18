import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { Plus, Search } from 'lucide-react';
import { toast } from 'sonner';
import { ApiError } from '@/lib/api/errors';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { DataTable } from '@/components/shared/data-table';
import { Drawer } from '@/components/shared/drawer';
import { PageHeader } from '@/components/shared/page-header';
import { ConfirmDialog } from '@/components/shared/confirm-dialog';
import { useHasPermission } from '@/lib/auth/use-me';
import {
  useUserCreate,
  useUserDeactivate,
  useUserReactivate,
  useUserUpdate,
  useUsersList,
} from '../api/hooks';
import type { User } from '../api/types';
import type { UserValues } from '../schemas';
import { UserForm } from '../components/user-form';

function StatusBadge({ active }: { active: boolean }) {
  return (
    <span
      className={
        active
          ? 'rounded bg-emerald-50 px-1.5 py-0.5 text-xs text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
          : 'rounded bg-muted px-1.5 py-0.5 text-xs text-muted-foreground'
      }
    >
      {active ? 'Active' : 'Inactive'}
    </span>
  );
}

export function UsersPage() {
  const canManage = useHasPermission('users.manage_user') === true;
  const [search, setSearch] = React.useState('');
  const [includeInactive, setIncludeInactive] = React.useState(false);
  const params = React.useMemo(() => {
    const p: Record<string, string | boolean | undefined> = {};
    if (search) p.search = search;
    if (includeInactive) p.include_inactive = true;
    return p;
  }, [search, includeInactive]);

  const { data, isLoading, isError, error } = useUsersList(params);
  const createMut = useUserCreate();
  const updateMut = useUserUpdate();
  const deactivateMut = useUserDeactivate();
  const reactivateMut = useUserReactivate();

  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [editing, setEditing] = React.useState<User | null>(null);
  const [confirm, setConfirm] = React.useState<User | null>(null);

  const openCreate = () => {
    setEditing(null);
    setDrawerOpen(true);
  };
  const openEdit = (row: User) => {
    setEditing(row);
    setDrawerOpen(true);
  };

  const handleSubmit = async (values: UserValues) => {
    try {
      if (editing) {
        await updateMut.mutateAsync({ id: editing.id, values });
        toast.success('User updated.');
      } else {
        await createMut.mutateAsync(values);
        toast.success('User created.');
      }
      setDrawerOpen(false);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Save failed.');
      throw err;
    }
  };

  const columns: ColumnDef<User, unknown>[] = React.useMemo(
    () => [
      { accessorKey: 'email', header: () => 'Email' },
      {
        accessorKey: 'mobile',
        header: () => 'Mobile',
        cell: ({ row }) => row.original.mobile ?? '—',
      },
      {
        accessorKey: 'employee_code',
        header: () => 'Employee code',
        cell: ({ row }) => row.original.employee_code ?? '—',
      },
      { accessorKey: 'name', header: () => 'Name' },
      {
        id: 'roles',
        header: () => 'Roles',
        cell: ({ row }) => (
          <div className="flex flex-wrap gap-1">
            {row.original.roles.map((r) => (
              <span
                key={`${r.id}-${r.branch_id ?? 'g'}`}
                className="rounded bg-muted px-1.5 py-0.5 text-xs"
                title={r.branch_id ? `Branch #${r.branch_id}` : 'Global'}
              >
                {r.code}
              </span>
            ))}
            {row.original.roles.length === 0 && (
              <span className="text-xs text-muted-foreground">—</span>
            )}
          </div>
        ),
      },
      {
        id: 'status',
        header: () => 'Status',
        cell: ({ row }) => <StatusBadge active={row.original.is_active} />,
      },
      {
        id: 'actions',
        header: () => <span className="sr-only">Actions</span>,
        cell: ({ row }) => {
          const r = row.original;
          return (
            <div className="flex items-center justify-end gap-2">
              <Button size="sm" variant="ghost" onClick={() => openEdit(r)} disabled={!canManage}>
                Edit
              </Button>
              {r.is_active ? (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setConfirm(r)}
                  disabled={!canManage}
                >
                  Deactivate
                </Button>
              ) : (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => reactivateMut.mutate(r.id)}
                  disabled={!canManage}
                >
                  Reactivate
                </Button>
              )}
            </div>
          );
        },
      },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [canManage],
  );

  return (
    <div className="space-y-4">
      <PageHeader
        title="Users"
        description="Identity, roles, and branch access."
        actions={
          <Button onClick={openCreate} disabled={!canManage} size="sm">
            <Plus className="mr-1 h-4 w-4" /> New user
          </Button>
        }
      />
      <div className="flex flex-wrap items-end gap-3">
        <div className="space-y-1">
          <Label htmlFor="users-search" className="text-xs">
            Search
          </Label>
          <div className="relative">
            <Search className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="users-search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-9 pl-7"
              placeholder="email / mobile / employee code"
            />
          </div>
        </div>
        <label className="flex items-center gap-2 text-xs text-muted-foreground">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(e) => setIncludeInactive(e.target.checked)}
            className="h-3.5 w-3.5"
          />
          Include inactive
        </label>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-9 animate-pulse rounded bg-muted/50" />
          ))}
        </div>
      ) : isError ? (
        <p className="text-sm text-destructive">{(error as Error).message ?? 'Error'}</p>
      ) : (
        <DataTable<User, unknown> columns={columns} data={data ?? []} empty="No users yet." />
      )}

      <Drawer
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        title={editing ? 'Edit user' : 'New user'}
      >
        <UserForm
          initial={editing ?? {}}
          onSubmit={handleSubmit}
          onCancel={() => setDrawerOpen(false)}
          submitting={createMut.isPending || updateMut.isPending}
        />
      </Drawer>

      <ConfirmDialog
        open={!!confirm}
        onOpenChange={(open) => (open ? null : setConfirm(null))}
        title="Deactivate user"
        description={`Deactivate ${confirm?.display_name ?? 'this user'}? They will no longer be able to sign in.`}
        confirmLabel="Deactivate"
        onConfirm={async () => {
          if (!confirm) return;
          try {
            await deactivateMut.mutateAsync(confirm.id);
            toast.success('Deactivated.');
          } catch (err) {
            toast.error(err instanceof ApiError ? err.message : 'Delete failed.');
          } finally {
            setConfirm(null);
          }
        }}
      />
    </div>
  );
}
