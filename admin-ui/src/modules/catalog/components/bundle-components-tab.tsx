import * as React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Trash2, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api/client';
import { ApiError } from '@/lib/api/errors';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { BundleComponent, Product } from '../api/types';

interface BundleComponentsTabProps {
  bundleId: number | null | undefined;
}

const DECIMAL_RE = /^\d+(\.\d{1,3})?$/;

export function BundleComponentsTab({ bundleId }: BundleComponentsTabProps) {
  const qc = useQueryClient();
  const [search, setSearch] = React.useState('');
  const [debouncedSearch, setDebouncedSearch] = React.useState('');
  const [selectedProduct, setSelectedProduct] = React.useState<Product | null>(null);
  const [quantity, setQuantity] = React.useState('1');

  // Debounce the product search.
  React.useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search.trim()), 250);
    return () => clearTimeout(t);
  }, [search]);

  const componentsQuery = useQuery<BundleComponent[]>({
    queryKey: ['catalog', 'bundle-components', { bundle: bundleId }],
    queryFn: async () => {
      const res = await apiClient.get(`/catalog/bundle-components/?bundle=${bundleId}`);
      return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
    },
    enabled: bundleId != null,
  });

  const productSearchQuery = useQuery<Product[]>({
    queryKey: ['catalog', 'products', 'bundle-picker', debouncedSearch],
    queryFn: async () => {
      const res = await apiClient.get(
        `/catalog/products/?q=${encodeURIComponent(debouncedSearch)}`,
      );
      const rows: Product[] = Array.isArray(res.data) ? res.data : (res.data.results ?? []);
      return rows.slice(0, 8);
    },
    enabled: debouncedSearch.length >= 2,
  });

  const componentIds = React.useMemo(
    () => new Set((componentsQuery.data ?? []).map((c) => c.product)),
    [componentsQuery.data],
  );

  const addMut = useMutation<BundleComponent, Error, { product: number; quantity: string }>({
    mutationFn: async (values) => {
      const res = await apiClient.post('/catalog/bundle-components/', {
        bundle: bundleId,
        product: values.product,
        quantity: values.quantity,
      });
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['catalog', 'bundle-components'] }),
  });

  const updateMut = useMutation<BundleComponent, Error, { id: number; quantity: string }>({
    mutationFn: async ({ id, quantity }) => {
      const res = await apiClient.patch(`/catalog/bundle-components/${id}/`, { quantity });
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['catalog', 'bundle-components'] }),
  });

  const deleteMut = useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.delete(`/catalog/bundle-components/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['catalog', 'bundle-components'] }),
  });

  if (bundleId == null) {
    return (
      <div className="rounded-md border border-dashed bg-muted/30 p-4 text-sm text-muted-foreground">
        Save the bundle first to add components.
      </div>
    );
  }

  const handleAdd = async () => {
    if (!selectedProduct) {
      toast.error('Pick a product to add.');
      return;
    }
    if (!DECIMAL_RE.test(quantity)) {
      toast.error('Quantity must be a number with up to 3 decimal places.');
      return;
    }
    try {
      await addMut.mutateAsync({ product: selectedProduct.id, quantity });
      toast.success('Component added.');
      setSelectedProduct(null);
      setSearch('');
      setDebouncedSearch('');
      setQuantity('1');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Add failed.');
    }
  };

  const rows = componentsQuery.data ?? [];

  return (
    <div className="space-y-4">
      <div className="space-y-2 rounded-md border bg-muted/20 p-3">
        <div className="text-sm font-medium">Add component</div>
        {selectedProduct ? (
          <div className="flex items-center justify-between rounded border bg-background px-3 py-2 text-sm">
            <span>
              <span className="font-medium">{selectedProduct.sku}</span>
              <span className="text-muted-foreground"> — {selectedProduct.name}</span>
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSelectedProduct(null);
                setSearch('');
              }}
            >
              Change
            </Button>
          </div>
        ) : (
          <div className="space-y-1.5">
            <Label>Search product (SKU, code, name)</Label>
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Type at least 2 characters…"
            />
            {productSearchQuery.isFetching ? (
              <div className="text-xs text-muted-foreground">Searching…</div>
            ) : null}
            {debouncedSearch.length >= 2 && (productSearchQuery.data?.length ?? 0) > 0 ? (
              <ul className="max-h-48 overflow-y-auto rounded border bg-background text-sm">
                {productSearchQuery.data!.map((p) => {
                  const already = componentIds.has(p.id);
                  return (
                    <li key={p.id}>
                      <button
                        type="button"
                        disabled={already}
                        onClick={() => setSelectedProduct(p)}
                        className="flex w-full items-center justify-between px-3 py-1.5 text-left hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        <span>
                          <span className="font-medium">{p.sku}</span>{' '}
                          <span className="text-muted-foreground">— {p.name}</span>
                        </span>
                        {already ? (
                          <span className="text-xs text-muted-foreground">already added</span>
                        ) : null}
                      </button>
                    </li>
                  );
                })}
              </ul>
            ) : null}
            {debouncedSearch.length >= 2 &&
            !productSearchQuery.isFetching &&
            (productSearchQuery.data?.length ?? 0) === 0 ? (
              <div className="text-xs text-muted-foreground">No matches.</div>
            ) : null}
          </div>
        )}
        <div className="flex items-end gap-2">
          <div className="space-y-1.5">
            <Label>Quantity</Label>
            <Input
              type="text"
              inputMode="decimal"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="w-24"
            />
          </div>
          <Button
            type="button"
            onClick={handleAdd}
            disabled={!selectedProduct || addMut.isPending}
            size="sm"
          >
            <Plus className="mr-1 h-4 w-4" />
            Add
          </Button>
        </div>
      </div>

      <div>
        <div className="mb-2 text-sm font-medium">Components ({rows.length})</div>
        {componentsQuery.isLoading ? (
          <div className="text-sm text-muted-foreground">Loading…</div>
        ) : rows.length === 0 ? (
          <div className="rounded-md border border-dashed p-3 text-sm text-muted-foreground">
            No components yet.
          </div>
        ) : (
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b text-left text-xs uppercase text-muted-foreground">
                <th className="py-1.5">Product ID</th>
                <th className="py-1.5">Quantity</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {rows.map((c) => (
                <BundleComponentRow
                  key={c.id}
                  component={c}
                  onPatch={(q) => updateMut.mutateAsync({ id: c.id, quantity: q })}
                  onDelete={() => deleteMut.mutateAsync(c.id)}
                />
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function BundleComponentRow({
  component,
  onPatch,
  onDelete,
}: {
  component: BundleComponent;
  onPatch: (quantity: string) => Promise<unknown>;
  onDelete: () => Promise<unknown>;
}) {
  const [qty, setQty] = React.useState(component.quantity);
  const [busy, setBusy] = React.useState(false);

  React.useEffect(() => {
    setQty(component.quantity);
  }, [component.quantity]);

  const commit = async () => {
    if (qty === component.quantity) return;
    if (!DECIMAL_RE.test(qty)) {
      toast.error('Quantity must be a number with up to 3 decimal places.');
      setQty(component.quantity);
      return;
    }
    setBusy(true);
    try {
      await onPatch(qty);
      toast.success('Quantity updated.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Update failed.');
      setQty(component.quantity);
    } finally {
      setBusy(false);
    }
  };

  return (
    <tr className="border-b last:border-0">
      <td className="py-1.5 pr-2 align-middle">#{component.product}</td>
      <td className="py-1.5 pr-2 align-middle">
        <Input
          type="text"
          inputMode="decimal"
          value={qty}
          onChange={(e) => setQty(e.target.value)}
          onBlur={commit}
          disabled={busy}
          className="h-8 w-24"
        />
      </td>
      <td className="py-1.5 text-right">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={async () => {
            setBusy(true);
            try {
              await onDelete();
              toast.success('Component removed.');
            } catch (err) {
              toast.error(err instanceof ApiError ? err.message : 'Delete failed.');
            } finally {
              setBusy(false);
            }
          }}
          disabled={busy}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </td>
    </tr>
  );
}
