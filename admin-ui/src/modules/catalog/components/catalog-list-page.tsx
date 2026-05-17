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
  useCatalogCreate,
  useCatalogDelete,
  useCatalogList,
  useCatalogUpdate,
  type CatalogEndpoint,
} from '../api/hooks';
import { t } from '../lib/i18n';

interface RenderFormArgs<TRow, TInput> {
  initial: Partial<TRow>;
  onSubmit: (values: TInput) => Promise<void>;
  submitting: boolean;
  onCancel: () => void;
}

export interface CatalogListPageProps<TRow extends { id: number; is_active?: boolean }, TInput> {
  endpoint: CatalogEndpoint;
  title: string;
  subtitle?: string;
  canManage: boolean;
  searchField?: string | null;
  filters?: Array<{
    label: string;
    param: string;
    options: Array<{ value: string; label: string }>;
  }>;
  columns: ColumnDef<TRow, unknown>[];
  renderForm: (args: RenderFormArgs<TRow, TInput>) => React.ReactNode;
  extraActions?: (row: TRow) => React.ReactNode;
  toolbar?: React.ReactNode;
  /** Hide the soft-delete column entirely (for endpoints without is_active semantics). */
  hideStatus?: boolean;
}

export function CatalogListPage<TRow extends { id: number; is_active?: boolean }, TInput>(
  props: CatalogListPageProps<TRow, TInput>,
) {
  const {
    endpoint,
    title,
    subtitle,
    canManage,
    searchField,
    filters,
    columns,
    renderForm,
    extraActions,
    toolbar,
    hideStatus,
  } = props;

  const [search, setSearch] = React.useState('');
  const [filterValues, setFilterValues] = React.useState<Record<string, string>>({});
  const [includeInactive, setIncludeInactive] = React.useState(false);
  const params = React.useMemo(() => {
    const p: Record<string, string | boolean | undefined> = {};
    if (search && searchField) p[searchField] = search;
    if (includeInactive) p.include_inactive = true;
    for (const [k, v] of Object.entries(filterValues)) {
      if (v) p[k] = v;
    }
    return p;
  }, [search, searchField, includeInactive, filterValues]);

  const { data, isLoading, isError, error } = useCatalogList<TRow>(endpoint, params);
  const createMut = useCatalogCreate<TRow, TInput>(endpoint);
  const updateMut = useCatalogUpdate<TRow, TInput>(endpoint);
  const deleteMut = useCatalogDelete(endpoint);

  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [editing, setEditing] = React.useState<TRow | null>(null);
  const [confirm, setConfirm] = React.useState<TRow | null>(null);

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
      toast.error(err instanceof ApiError ? err.message : 'Save failed.');
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
          {extraActions?.(r)}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setEditing(r);
              setDrawerOpen(true);
            }}
            disabled={!canManage}
          >
            {t('common.edit')}
          </Button>
          {!hideStatus && (
            <Button size="sm" variant="ghost" onClick={() => setConfirm(r)} disabled={!canManage}>
              {t('common.archive')}
            </Button>
          )}
        </div>
      );
    },
  };

  const statusColumn: ColumnDef<TRow, unknown> = {
    id: 'status',
    header: () => t('common.status'),
    cell: ({ row }) => {
      const active = row.original.is_active ?? true;
      return (
        <span
          className={
            active
              ? 'rounded bg-emerald-50 px-1.5 py-0.5 text-xs text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
              : 'rounded bg-muted px-1.5 py-0.5 text-xs text-muted-foreground'
          }
        >
          {active ? t('common.active') : t('common.inactive')}
        </span>
      );
    },
  };

  const allColumns = React.useMemo(
    () => (hideStatus ? [...columns, actionsColumn] : [...columns, statusColumn, actionsColumn]),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [columns, canManage, hideStatus],
  );

  return (
    <div className="space-y-4">
      <PageHeader
        title={title}
        description={subtitle}
        actions={
          <Button
            onClick={() => {
              setEditing(null);
              setDrawerOpen(true);
            }}
            disabled={!canManage}
            size="sm"
          >
            <Plus className="mr-1 h-4 w-4" />
            {t('common.create')}
          </Button>
        }
      />

      <div className="flex flex-wrap items-end gap-3">
        {searchField && (
          <div className="space-y-1">
            <Label htmlFor="catalog-search" className="text-xs">
              {t('common.search')}
            </Label>
            <div className="relative">
              <Search className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              <Input
                id="catalog-search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="h-9 pl-7"
                placeholder={t('common.search')}
              />
            </div>
          </div>
        )}
        {filters?.map((f) => (
          <div key={f.param} className="space-y-1">
            <Label className="text-xs">{f.label}</Label>
            <select
              value={filterValues[f.param] ?? ''}
              onChange={(e) => setFilterValues((prev) => ({ ...prev, [f.param]: e.target.value }))}
              className="h-9 rounded-md border border-input bg-background px-2 text-sm"
            >
              <option value="">—</option>
              {f.options.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
        ))}
        {!hideStatus && (
          <label className="flex items-center gap-2 text-xs text-muted-foreground">
            <input
              type="checkbox"
              checked={includeInactive}
              onChange={(e) => setIncludeInactive(e.target.checked)}
              className="h-3.5 w-3.5"
            />
            {t('common.include_inactive')}
          </label>
        )}
        {toolbar}
      </div>

      {isLoading ? (
        <div className="space-y-2" aria-label="Loading">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-9 animate-pulse rounded bg-muted/50" />
          ))}
        </div>
      ) : isError ? (
        <p className="text-sm text-destructive">{(error as Error)?.message ?? t('common.error')}</p>
      ) : (
        <DataTable<TRow, unknown> columns={allColumns} data={data ?? []} empty="No rows." />
      )}

      <Drawer
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        title={editing ? t('common.edit') : t('common.create')}
      >
        {renderForm({
          initial: editing ?? {},
          onSubmit: handleSubmit,
          submitting: createMut.isPending || updateMut.isPending,
          onCancel: () => setDrawerOpen(false),
        })}
      </Drawer>

      <ConfirmDialog
        open={!!confirm}
        onOpenChange={(open) => (open ? null : setConfirm(null))}
        title={t('common.archive')}
        description={`Archive record #${confirm?.id ?? ''}? It will be hidden from list views.`}
        confirmLabel={t('common.archive')}
        onConfirm={async () => {
          if (!confirm) return;
          try {
            await deleteMut.mutateAsync(confirm.id);
            toast.success('Archived.');
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
