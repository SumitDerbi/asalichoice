import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { InventoryListPage } from '../components/inventory-list-page';
import type { Stock } from '../api/types';
import { t } from '../lib/i18n';

export function StockPage() {
  const [branch, setBranch] = React.useState('');
  const [product, setProduct] = React.useState('');
  const params = React.useMemo(
    () => ({
      ...(branch && { branch: Number(branch) }),
      ...(product && { product: Number(product) }),
    }),
    [branch, product],
  );

  const columns: ColumnDef<Stock, unknown>[] = [
    { accessorKey: 'branch', header: () => t('common.branch') },
    { accessorKey: 'product', header: () => t('common.product') },
    { accessorKey: 'variant', header: () => t('common.variant') },
    { accessorKey: 'qty_on_hand', header: () => t('stock.qty_on_hand') },
    { accessorKey: 'qty_reserved', header: () => t('stock.qty_reserved') },
    {
      id: 'qty_available',
      header: () => t('stock.qty_available'),
      cell: ({ row }) => {
        const onHand = Number(row.original.qty_on_hand);
        const reserved = Number(row.original.qty_reserved);
        return (onHand - reserved).toFixed(3);
      },
    },
    { accessorKey: 'reorder_point', header: () => t('stock.reorder_point') },
  ];

  return (
    <InventoryListPage<Stock>
      endpoint="stock"
      title={t('stock.title')}
      subtitle="Snapshot of stock on hand by branch, product and variant."
      columns={columns}
      extraParams={params}
      filters={
        <>
          <div className="space-y-1">
            <Label className="text-xs" htmlFor="stock-branch">
              Branch ID
            </Label>
            <Input
              id="stock-branch"
              value={branch}
              onChange={(e) => setBranch(e.target.value.replace(/[^0-9]/g, ''))}
              className="h-9 w-28"
              placeholder="e.g. 1"
            />
          </div>
          <div className="space-y-1">
            <Label className="text-xs" htmlFor="stock-product">
              Product ID
            </Label>
            <Input
              id="stock-product"
              value={product}
              onChange={(e) => setProduct(e.target.value.replace(/[^0-9]/g, ''))}
              className="h-9 w-28"
              placeholder="e.g. 12"
            />
          </div>
        </>
      }
    />
  );
}
