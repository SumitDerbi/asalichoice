import * as React from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Save, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { PageHeader } from '@/components/shared/page-header';
import { apiClient } from '@/lib/api/client';
import { ApiError } from '@/lib/api/errors';
import { RemoteSelectField } from '@/modules/masters/components/select-field';
import { useCanManagePrices } from '../lib/use-permission';
import type { ProductPrice } from '../api/types';

type EditableRow = {
  /** Synthetic key for React; equals `db-<id>` for existing rows or `new-<n>` for additions. */
  key: string;
  id: number | null;
  product: number | null;
  variant: number | null;
  branch: number;
  mrp: string;
  sale_price: string;
  cost_price: string;
  valid_from: string;
  valid_to: string;
  /** True when user has edited fields relative to the loaded snapshot. */
  dirty: boolean;
  /** True when user has marked the row for deletion. */
  deleted: boolean;
};

const DECIMAL_RE = /^\d+(\.\d{1,2})?$/;

function toRow(p: ProductPrice): EditableRow {
  return {
    key: `db-${p.id}`,
    id: p.id,
    product: p.product,
    variant: p.variant,
    branch: p.branch,
    mrp: p.mrp,
    sale_price: p.sale_price,
    cost_price: p.cost_price ?? '',
    valid_from: p.valid_from,
    valid_to: p.valid_to ?? '',
    dirty: false,
    deleted: false,
  };
}

interface MinimalFieldState<T> {
  name: string;
  state: { value: T; meta: { errors: string[] } };
  handleChange(value: T): void;
  handleBlur(): void;
}

/**
 * Adapter that lets us reuse `RemoteSelectField` (which expects a TanStack
 * Form field) for a plain controlled number input.
 */
function makeBranchField(value: number, onChange: (v: number) => void): MinimalFieldState<number> {
  return {
    name: 'branch',
    state: { value, meta: { errors: [] } },
    handleChange: (v) => onChange(v),
    handleBlur: () => {},
  };
}

export function PricesBulkPage() {
  const canManage = useCanManagePrices();
  const qc = useQueryClient();
  const [branchId, setBranchId] = React.useState<number>(0);
  const [rows, setRows] = React.useState<EditableRow[]>([]);
  const [saving, setSaving] = React.useState(false);

  const enabled = branchId > 0;

  const query = useQuery<ProductPrice[], Error>({
    queryKey: ['catalog', 'prices', 'bulk', { branch: branchId }],
    enabled,
    queryFn: async () => {
      const res = await apiClient.get<{ results?: ProductPrice[] } | ProductPrice[]>(
        `/catalog/prices/?branch=${branchId}`,
      );
      return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
    },
  });

  React.useEffect(() => {
    if (query.data) setRows(query.data.map(toRow));
  }, [query.data]);

  const dirtyCount = rows.filter((r) => r.dirty && !r.deleted).length;
  const deletedCount = rows.filter((r) => r.deleted && r.id != null).length;
  const newCount = rows.filter((r) => r.id == null && !r.deleted).length;
  const hasChanges = dirtyCount + deletedCount + newCount > 0;

  const updateCell = <K extends keyof EditableRow>(
    key: string,
    field: K,
    value: EditableRow[K],
  ) => {
    setRows((prev) => prev.map((r) => (r.key === key ? { ...r, [field]: value, dirty: true } : r)));
  };

  const toggleDelete = (key: string) => {
    setRows((prev) =>
      prev.map((r) =>
        r.key === key
          ? r.id == null
            ? r // physically remove new-unsaved rows below
            : { ...r, deleted: !r.deleted }
          : r,
      ),
    );
  };

  const removeNewRow = (key: string) => {
    setRows((prev) => prev.filter((r) => r.key !== key));
  };

  const addRow = () => {
    if (!enabled) return;
    setRows((prev) => [
      ...prev,
      {
        key: `new-${Date.now()}-${prev.length}`,
        id: null,
        product: null,
        variant: null,
        branch: branchId,
        mrp: '',
        sale_price: '',
        cost_price: '',
        valid_from: new Date().toISOString().slice(0, 10),
        valid_to: '',
        dirty: true,
        deleted: false,
      },
    ]);
  };

  const validate = (r: EditableRow): string | null => {
    if (r.product == null && r.variant == null) return 'product or variant required';
    if (r.product != null && r.variant != null) return 'pick exactly one of product/variant';
    if (!DECIMAL_RE.test(r.mrp)) return 'mrp must be decimal';
    if (!DECIMAL_RE.test(r.sale_price)) return 'sale_price must be decimal';
    if (r.cost_price && !DECIMAL_RE.test(r.cost_price)) return 'cost_price must be decimal';
    if (!r.valid_from) return 'valid_from required';
    return null;
  };

  const handleSave = async () => {
    if (!enabled) return;
    setSaving(true);
    const toCreate = rows.filter((r) => r.id == null && !r.deleted);
    const toUpdate = rows.filter((r) => r.id != null && r.dirty && !r.deleted);
    const toDelete = rows.filter((r) => r.id != null && r.deleted);

    for (const r of [...toCreate, ...toUpdate]) {
      const err = validate(r);
      if (err) {
        toast.error(`Row error: ${err}`);
        setSaving(false);
        return;
      }
    }

    const payload = (r: EditableRow) => ({
      product: r.product,
      variant: r.variant,
      branch: r.branch,
      mrp: r.mrp,
      sale_price: r.sale_price,
      cost_price: r.cost_price || null,
      valid_from: r.valid_from,
      valid_to: r.valid_to || null,
    });

    const tasks: Array<Promise<unknown>> = [
      ...toCreate.map((r) => apiClient.post('/catalog/prices/', payload(r))),
      ...toUpdate.map((r) => apiClient.patch(`/catalog/prices/${r.id}/`, payload(r))),
      ...toDelete.map((r) => apiClient.delete(`/catalog/prices/${r.id}/`)),
    ];
    const results = await Promise.allSettled(tasks);
    const failed = results.filter((r) => r.status === 'rejected');
    setSaving(false);
    if (failed.length) {
      const first = failed[0] as PromiseRejectedResult;
      const msg = first.reason instanceof ApiError ? first.reason.message : 'Some rows failed.';
      toast.error(`${failed.length} row(s) failed: ${msg}`);
    } else {
      toast.success(`Saved ${tasks.length} row(s).`);
    }
    qc.invalidateQueries({ queryKey: ['catalog', 'prices'] });
  };

  return (
    <div className="space-y-4">
      <PageHeader title="Bulk price editor" description="Edit many prices at once for a branch." />

      <div className="flex items-end gap-3">
        <div className="w-72">
          <Label className="text-xs">Branch</Label>
          <RemoteSelectField
            field={makeBranchField(branchId, (v) => setBranchId(v ?? 0))}
            label=""
            endpoint="branches"
            getLabel={(r) => `${r.code} — ${r.name}`}
            allowEmpty={false}
          />
        </div>
        <Button type="button" variant="outline" onClick={addRow} disabled={!enabled || !canManage}>
          <Plus className="mr-1 h-4 w-4" /> Add row
        </Button>
        <Button
          type="button"
          onClick={() => void handleSave()}
          disabled={!enabled || !canManage || !hasChanges || saving}
        >
          <Save className="mr-1 h-4 w-4" />
          {saving
            ? 'Saving…'
            : `Save changes${hasChanges ? ` (${dirtyCount + newCount + deletedCount})` : ''}`}
        </Button>
      </div>

      {!enabled ? (
        <p className="text-sm text-muted-foreground">Pick a branch to load prices.</p>
      ) : query.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : query.isError ? (
        <p className="text-sm text-red-600">Failed to load prices.</p>
      ) : (
        <div className="overflow-x-auto rounded-md border">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-2 py-2">Product ID</th>
                <th className="px-2 py-2">Variant ID</th>
                <th className="px-2 py-2">MRP</th>
                <th className="px-2 py-2">Sale price</th>
                <th className="px-2 py-2">Cost</th>
                <th className="px-2 py-2">Valid from</th>
                <th className="px-2 py-2">Valid to</th>
                <th className="px-2 py-2"></th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-2 py-6 text-center text-muted-foreground">
                    No prices. Click “Add row” to create one.
                  </td>
                </tr>
              ) : (
                rows.map((r) => (
                  <tr
                    key={r.key}
                    className={
                      r.deleted
                        ? 'bg-red-50/60 line-through opacity-60'
                        : r.dirty
                          ? 'bg-amber-50/60'
                          : ''
                    }
                  >
                    <td className="px-1 py-1">
                      <Input
                        className="h-8"
                        type="number"
                        value={r.product ?? ''}
                        disabled={r.deleted || !canManage}
                        onChange={(e) =>
                          updateCell(
                            r.key,
                            'product',
                            e.target.value ? Number(e.target.value) : null,
                          )
                        }
                      />
                    </td>
                    <td className="px-1 py-1">
                      <Input
                        className="h-8"
                        type="number"
                        value={r.variant ?? ''}
                        disabled={r.deleted || !canManage}
                        onChange={(e) =>
                          updateCell(
                            r.key,
                            'variant',
                            e.target.value ? Number(e.target.value) : null,
                          )
                        }
                      />
                    </td>
                    <td className="px-1 py-1">
                      <Input
                        className="h-8"
                        value={r.mrp}
                        disabled={r.deleted || !canManage}
                        onChange={(e) => updateCell(r.key, 'mrp', e.target.value)}
                      />
                    </td>
                    <td className="px-1 py-1">
                      <Input
                        className="h-8"
                        value={r.sale_price}
                        disabled={r.deleted || !canManage}
                        onChange={(e) => updateCell(r.key, 'sale_price', e.target.value)}
                      />
                    </td>
                    <td className="px-1 py-1">
                      <Input
                        className="h-8"
                        value={r.cost_price}
                        disabled={r.deleted || !canManage}
                        onChange={(e) => updateCell(r.key, 'cost_price', e.target.value)}
                      />
                    </td>
                    <td className="px-1 py-1">
                      <Input
                        className="h-8"
                        type="date"
                        value={r.valid_from}
                        disabled={r.deleted || !canManage}
                        onChange={(e) => updateCell(r.key, 'valid_from', e.target.value)}
                      />
                    </td>
                    <td className="px-1 py-1">
                      <Input
                        className="h-8"
                        type="date"
                        value={r.valid_to}
                        disabled={r.deleted || !canManage}
                        onChange={(e) => updateCell(r.key, 'valid_to', e.target.value)}
                      />
                    </td>
                    <td className="px-1 py-1 text-right">
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        className="h-7 px-1 text-red-600 hover:text-red-700"
                        disabled={!canManage}
                        onClick={() => (r.id == null ? removeNewRow(r.key) : toggleDelete(r.key))}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
