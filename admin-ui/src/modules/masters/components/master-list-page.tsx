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
import {
  useMasterCreate,
  useMasterDelete,
  useMasterList,
  useMasterReactivate,
  useMasterUpdate,
  type MasterEndpoint,
} from '../api/hooks';
import { useCanManage } from '../lib/use-has-permission';
import { t } from '../lib/i18n';

interface RenderFormArgs<TRow, TInput> {
  initial: Partial<TRow>;
  onSubmit: (values: TInput) => Promise<void>;
  submitting: boolean;
  onCancel: () => void;
}

export interface MasterListPageProps<TRow extends { id: number; is_active: boolean }, TInput> {
  endpoint: MasterEndpoint;
  /** Permission domain (`branch`, `tax`, …) used with `useCanManage`. */
  permissionDomain: string;
  title: string;
  subtitle?: string;
  /** Field name used by the search box. Pass null to hide search. */
  searchField?: string | null;
  /** Columns shown in the list. The `actions` column is appended. */
  columns: ColumnDef<TRow, unknown>[];
  /** Drawer body renderer for create/edit. */
  renderForm: (args: RenderFormArgs<TRow, TInput>) => React.ReactNode;
  /** Optional toolbar slot rendered next to Create. */
  toolbar?: React.ReactNode;
}

/**
 * Compact list + drawer-form HOC shared by every master entity.
 *
 * - Search via `?search=` (when `searchField` is given).
 * - Toggle inactive rows via `?include_inactive=true`.
 * - Deactivate (soft-delete) + Reactivate actions inline.
 */
export function MasterListPage<TRow extends { id: number; is_active: boolean }, TInput>(
  props: MasterListPageProps<TRow, TInput>,
) {
  const { endpoint, permissionDomain, title, subtitle, searchField, columns, renderForm, toolbar } =
    props;

  const canManage = useCanManage(permissionDomain);
  const [search, setSearch] = React.useState('');
  const [includeInactive, setIncludeInactive] = React.useState(false);
  const params = React.useMemo(() => {
    const p: Record<string, string | boolean | undefined> = {};
    if (search && searchField) p[searchField] = search;
    if (includeInactive) p.include_inactive = true;
    return p;
  }, [search, searchField, includeInactive]);

  const { data, isLoading, isError, error } = useMasterList<TRow>(endpoint, params);
  const createMut = useMasterCreate<TRow, TInput>(endpoint);
  const updateMut = useMasterUpdate<TRow, TInput>(endpoint);
  const deleteMut = useMasterDelete(endpoint);
  const reactivateMut = useMasterReactivate(endpoint);

  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [editing, setEditing] = React.useState<TRow | null>(null);
  const [confirm, setConfirm] = React.useState<TRow | null>(null);

  const openCreate = () => {
    setEditing(null);
    setDrawerOpen(true);
  };
  const openEdit = (row: TRow) => {
    setEditing(row);
    setDrawerOpen(true);
  };

  const handleSubmit = async (values: TInput) => {
    try {
      if (editing) {
        await updateMut.mutateAsync({ id: editing.id, values });
        toast.success(`${title.replace(/s$/, '')} updated.`);
      } else {
        await createMut.mutateAsync(values);
        toast.success(`${title.replace(/s$/, '')} created.`);
      }
      setDrawerOpen(false);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Save failed.';
      toast.error(message);
      throw err;
    }
  };

  const actionsColumn: ColumnDef<TRow, unknown> = {
    id: 'actions',
    header: () => <span className="sr-only">{t('common.actions')}</span>,
    cell: ({ row }) => {
      const r = row.original;
      return (
        <div className="flex items-center justify-end gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => openEdit(r)}
            disabled={!canManage}
            aria-label={`Edit ${r.id}`}
          >
            {t('common.edit')}
          </Button>
          {r.is_active ? (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setConfirm(r)}
              disabled={!canManage}
              aria-label={`Deactivate ${r.id}`}
            >
              {t('common.deactivate')}
            </Button>
          ) : (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => reactivateMut.mutate(r.id)}
              disabled={!canManage}
              aria-label={`Reactivate ${r.id}`}
            >
              {t('common.reactivate')}
            </Button>
          )}
        </div>
      );
    },
  };

  const statusColumn: ColumnDef<TRow, unknown> = {
    id: 'status',
    header: () => t('common.status'),
    cell: ({ row }) => (
      <span
        className={
          row.original.is_active
            ? 'rounded bg-emerald-50 px-1.5 py-0.5 text-xs text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
            : 'rounded bg-muted px-1.5 py-0.5 text-xs text-muted-foreground'
        }
      >
        {row.original.is_active ? t('common.active') : t('common.inactive')}
      </span>
    ),
  };

  const allColumns = React.useMemo(
    () => [...columns, statusColumn, actionsColumn],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [columns, canManage],
  );

  return (
    <div className="space-y-4">
      <PageHeader
        title={title}
        description={subtitle}
        actions={
          <Button onClick={openCreate} disabled={!canManage} size="sm">
            <Plus className="mr-1 h-4 w-4" />
            {t('common.create')}
          </Button>
        }
      />

      <div className="flex flex-wrap items-end gap-3">
        {searchField && (
          <div className="space-y-1">
            <Label htmlFor="master-search" className="text-xs">
              {t('common.search')}
            </Label>
            <div className="relative">
              <Search className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              <Input
                id="master-search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="h-9 pl-7"
                placeholder={t('common.search')}
              />
            </div>
          </div>
        )}
        <label className="flex items-center gap-2 text-xs text-muted-foreground">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(e) => setIncludeInactive(e.target.checked)}
            className="h-3.5 w-3.5"
          />
          {t('common.include_inactive')}
        </label>
        {toolbar}
      </div>

      {isLoading ? (
        <SkeletonTable />
      ) : isError ? (
        <p className="text-sm text-destructive">{(error as Error).message ?? t('common.error')}</p>
      ) : (
        <DataTable<TRow, unknown>
          columns={allColumns}
          data={data ?? []}
          empty={t('common.empty')}
        />
      )}

      <DrawerHost
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        title={editing ? t('common.edit') : t('common.create')}
        body={renderForm({
          initial: editing ?? {},
          onSubmit: handleSubmit,
          submitting: createMut.isPending || updateMut.isPending,
          onCancel: () => setDrawerOpen(false),
        })}
      />

      <ConfirmDialog
        open={!!confirm}
        onOpenChange={(open) => (open ? null : setConfirm(null))}
        title={t('common.deactivate')}
        description={`Deactivate ${confirm?.id ? `record #${confirm.id}` : 'this record'}? It will be hidden from list views.`}
        confirmLabel={t('common.deactivate')}
        onConfirm={async () => {
          if (!confirm) return;
          try {
            await deleteMut.mutateAsync(confirm.id);
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

function SkeletonTable() {
  return (
    <div className="space-y-2" aria-label="Loading">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="h-9 animate-pulse rounded bg-muted/50" />
      ))}
    </div>
  );
}

function DrawerHost({
  open,
  onOpenChange,
  title,
  body,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  title: string;
  body: React.ReactNode;
}) {
  return (
    <Drawer open={open} onOpenChange={onOpenChange} title={title}>
      {body}
    </Drawer>
  );
}
