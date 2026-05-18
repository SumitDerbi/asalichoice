import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { Plus } from 'lucide-react';
import { toast } from 'sonner';
import { ApiError } from '@/lib/api/errors';
import { Button } from '@/components/ui/button';
import { DataTable } from '@/components/shared/data-table';
import { Drawer } from '@/components/shared/drawer';
import { PageHeader } from '@/components/shared/page-header';
import { ConfirmDialog } from '@/components/shared/confirm-dialog';
import { useHasPermission } from '@/lib/auth/use-me';
import { useRoleCreate, useRoleDeactivate, useRoleUpdate, useRolesList } from '../api/hooks';
import type { Role } from '../api/types';
import type { RoleValues } from '../schemas';
import { RoleForm } from '../components/role-form';

export function RolesPage() {
  const canManage = useHasPermission('users.manage_role') === true;
  const { data, isLoading, isError, error } = useRolesList({ include_inactive: true });
  const createMut = useRoleCreate();
  const updateMut = useRoleUpdate();
  const deactivateMut = useRoleDeactivate();

  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [editing, setEditing] = React.useState<Role | null>(null);
  const [confirm, setConfirm] = React.useState<Role | null>(null);

  const openCreate = () => {
    setEditing(null);
    setDrawerOpen(true);
  };
  const openEdit = (row: Role) => {
    setEditing(row);
    setDrawerOpen(true);
  };

  const handleSubmit = async (values: RoleValues) => {
    try {
      if (editing) {
        await updateMut.mutateAsync({ id: editing.id, values });
        toast.success('Role updated.');
      } else {
        await createMut.mutateAsync(values);
        toast.success('Role created.');
      }
      setDrawerOpen(false);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Save failed.');
      throw err;
    }
  };

  const columns: ColumnDef<Role, unknown>[] = React.useMemo(
    () => [
      { accessorKey: 'code', header: () => 'Code' },
      { accessorKey: 'name', header: () => 'Name' },
      {
        accessorKey: 'description',
        header: () => 'Description',
        cell: ({ row }) => (
          <span className="text-muted-foreground">{row.original.description || '—'}</span>
        ),
      },
      {
        id: 'permissions',
        header: () => 'Permissions',
        cell: ({ row }) => (
          <span className="text-xs text-muted-foreground">
            {row.original.permission_ids.length}
          </span>
        ),
      },
      {
        id: 'kind',
        header: () => 'Kind',
        cell: ({ row }) =>
          row.original.is_system ? (
            <span className="rounded bg-blue-50 px-1.5 py-0.5 text-xs text-blue-700">System</span>
          ) : (
            <span className="rounded bg-muted px-1.5 py-0.5 text-xs">Custom</span>
          ),
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
              {!r.is_system && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setConfirm(r)}
                  disabled={!canManage}
                >
                  Delete
                </Button>
              )}
            </div>
          );
        },
      },
    ],

    [canManage],
  );

  return (
    <div className="space-y-4">
      <PageHeader
        title="Roles"
        description="Bundles of permissions assignable to users."
        actions={
          <Button onClick={openCreate} disabled={!canManage} size="sm">
            <Plus className="mr-1 h-4 w-4" /> New role
          </Button>
        }
      />
      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-9 animate-pulse rounded bg-muted/50" />
          ))}
        </div>
      ) : isError ? (
        <p className="text-sm text-destructive">{(error as Error).message ?? 'Error'}</p>
      ) : (
        <DataTable<Role, unknown> columns={columns} data={data ?? []} empty="No roles yet." />
      )}

      <Drawer
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        title={editing ? `Edit role: ${editing.code}` : 'New role'}
      >
        <RoleForm
          initial={editing ?? {}}
          onSubmit={handleSubmit}
          onCancel={() => setDrawerOpen(false)}
          submitting={createMut.isPending || updateMut.isPending}
        />
      </Drawer>

      <ConfirmDialog
        open={!!confirm}
        onOpenChange={(open) => (open ? null : setConfirm(null))}
        title="Delete role"
        description={`Delete role ${confirm?.code}? Users assigned to it will lose its permissions.`}
        confirmLabel="Delete"
        onConfirm={async () => {
          if (!confirm) return;
          try {
            await deactivateMut.mutateAsync(confirm.id);
            toast.success('Role deleted.');
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
