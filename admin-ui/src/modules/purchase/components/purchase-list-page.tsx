import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { Plus, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { DataTable } from '@/components/shared/data-table';
import { Drawer } from '@/components/shared/drawer';
import { PageHeader } from '@/components/shared/page-header';
import { usePurchaseList, type PurchaseEndpoint, type ListParams } from '../api/hooks';
import { t } from '../lib/i18n';

interface PurchaseListPageProps<TRow extends { id: number }> {
  endpoint: PurchaseEndpoint;
  title: string;
  subtitle?: string;
  searchField?: string | null;
  filters?: Array<{
    label: string;
    param: string;
    options: Array<{ value: string; label: string }>;
  }>;
  extraParams?: ListParams;
  columns: ColumnDef<TRow, unknown>[];
  /** When set, renders a "Create" toolbar button that opens a drawer with this content. */
  renderCreate?: (close: () => void) => React.ReactNode;
  /** Permission gate for the create button. */
  canCreate?: boolean;
  toolbar?: React.ReactNode;
}

export function PurchaseListPage<TRow extends { id: number }>(props: PurchaseListPageProps<TRow>) {
  const {
    endpoint,
    title,
    subtitle,
    searchField,
    filters,
    extraParams,
    columns,
    renderCreate,
    canCreate,
    toolbar,
  } = props;

  const [search, setSearch] = React.useState('');
  const [filterValues, setFilterValues] = React.useState<Record<string, string>>({});
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  const params = React.useMemo(() => {
    const p: ListParams = { ...(extraParams ?? {}) };
    if (search && searchField) p[searchField] = search;
    for (const [k, v] of Object.entries(filterValues)) {
      if (v) p[k] = v;
    }
    return p;
  }, [search, searchField, filterValues, extraParams]);

  const { data, isLoading, isError, error } = usePurchaseList<TRow>(endpoint, params);

  return (
    <div className="space-y-4">
      <PageHeader
        title={title}
        description={subtitle}
        actions={
          renderCreate ? (
            <Button size="sm" disabled={!canCreate} onClick={() => setDrawerOpen(true)}>
              <Plus className="mr-1 h-4 w-4" />
              {t('common.create')}
            </Button>
          ) : null
        }
      />

      <div className="flex flex-wrap items-end gap-3">
        {searchField && (
          <div className="space-y-1">
            <Label className="text-xs" htmlFor={`pur-search-${endpoint}`}>
              {t('common.search')}
            </Label>
            <div className="relative">
              <Search className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              <Input
                id={`pur-search-${endpoint}`}
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
              onChange={(e) => setFilterValues((p) => ({ ...p, [f.param]: e.target.value }))}
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
        <DataTable<TRow, unknown> columns={columns} data={data ?? []} empty="No rows." />
      )}

      {renderCreate && (
        <Drawer open={drawerOpen} onOpenChange={setDrawerOpen} title={t('common.create')}>
          {renderCreate(() => setDrawerOpen(false))}
        </Drawer>
      )}
    </div>
  );
}

const STATUS_COLORS: Record<string, string> = {
  DRAFT: 'bg-amber-50 text-amber-700',
  PENDING_APPROVAL: 'bg-blue-50 text-blue-700',
  SUBMITTED: 'bg-blue-50 text-blue-700',
  APPROVED: 'bg-emerald-50 text-emerald-700',
  PARTIAL: 'bg-sky-50 text-sky-700',
  RECEIVED: 'bg-emerald-50 text-emerald-700',
  POSTED: 'bg-emerald-50 text-emerald-700',
  PAID: 'bg-emerald-100 text-emerald-800',
  PART_PAID: 'bg-sky-50 text-sky-700',
  REJECTED: 'bg-rose-50 text-rose-700',
  CANCELLED: 'bg-zinc-100 text-zinc-600',
  CLOSED: 'bg-zinc-100 text-zinc-600',
};

export function StatusBadge({ value }: { value: string }) {
  const cls = STATUS_COLORS[value] ?? 'bg-zinc-100 text-zinc-700';
  return <span className={`rounded px-1.5 py-0.5 text-xs ${cls}`}>{value}</span>;
}
