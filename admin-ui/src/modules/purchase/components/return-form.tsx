import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form } from '@/lib/forms';
import { FieldShell } from '@/lib/forms/field';
import { ApiError } from '@/lib/api/errors';
import { apiClient } from '@/lib/api/client';
import { usePurchaseCollectionAction, usePurchaseList } from '../api/hooks';
import type { GRN, GRNItem, PurchaseReturn } from '../api/types';
import { RemoteSelect } from './remote-select';
import { t } from '../lib/i18n';

interface Props {
  onClose: () => void;
}

interface LineRow {
  grn_item: number;
  product: number | null;
  qty: string;
  reason: string;
}

export function PurchaseReturnForm({ onClose }: Props) {
  const [grnId, setGrnId] = React.useState<number | null>(null);
  const [prNo, setPrNo] = React.useState('');
  const [reason, setReason] = React.useState('');
  const [rows, setRows] = React.useState<LineRow[]>([]);

  // Fetch full GRN detail to read items
  const { data: grnDetail } = useQuery<GRN, Error>({
    queryKey: ['purchase', 'grn-detail', grnId],
    enabled: !!grnId,
    queryFn: async () => {
      const res = await apiClient.get<GRN>(`/purchase/grns/${grnId}/`);
      return res.data;
    },
  });

  React.useEffect(() => {
    const items = grnDetail?.items ?? [];
    setRows(
      items.map((it: GRNItem) => ({
        grn_item: it.id,
        product: it.product,
        qty: '0',
        reason: '',
      })),
    );
  }, [grnDetail?.id, grnDetail?.items]);

  const mut = usePurchaseCollectionAction<PurchaseReturn>('returns', 'create-from-grn');

  const submit = async () => {
    if (!grnId || !prNo) {
      toast.error('GRN and PR number are required.');
      return;
    }
    const filtered = rows.filter((r) => Number(r.qty || '0') > 0);
    if (!filtered.length) {
      toast.error('At least one line with qty > 0 is required.');
      return;
    }
    try {
      await mut.mutateAsync({
        grn: grnId,
        pr_no: prNo,
        reason,
        items: filtered,
      });
      toast.success('Purchase return created.');
      onClose();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Save failed.');
    }
  };

  // Limit GRN options to approved ones
  const { data: approvedGrns } = usePurchaseList<GRN>('grns', { status: 'APPROVED' });

  return (
    <Form
      onSubmit={(e) => {
        e.preventDefault();
        void submit();
      }}
    >
      <div className="grid grid-cols-2 gap-3">
        <FieldShell id="pr_no" label="PR No.">
          <Input value={prNo} onChange={(e) => setPrNo(e.target.value)} />
        </FieldShell>
        <FieldShell id="grn" label="From GRN">
          <RemoteSelect
            endpoint="purchase/grns"
            params={{ status: 'APPROVED' }}
            labelFn={(r: GRN) => r.grn_no}
            value={grnId}
            onChange={setGrnId}
          />
        </FieldShell>
        <FieldShell id="reason" label="Reason" className="col-span-2">
          <Input value={reason} onChange={(e) => setReason(e.target.value)} />
        </FieldShell>
      </div>

      <div className="space-y-2 rounded border p-3">
        <strong className="text-sm">Lines to return</strong>
        {!grnId ? (
          <p className="text-xs text-muted-foreground">Select a GRN to load lines.</p>
        ) : !rows.length ? (
          <p className="text-xs text-muted-foreground">
            {approvedGrns?.length ? 'Loading…' : 'No items on selected GRN.'}
          </p>
        ) : (
          <table className="w-full text-xs">
            <thead className="text-left text-muted-foreground">
              <tr>
                <th>Product</th>
                <th>Return qty</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={r.grn_item} className="align-top">
                  <td className="py-1">{r.product ?? '—'}</td>
                  <td className="pr-2">
                    <Input
                      className="h-9 w-20"
                      value={r.qty}
                      onChange={(e) =>
                        setRows((p) =>
                          p.map((x, j) => (j === i ? { ...x, qty: e.target.value } : x)),
                        )
                      }
                    />
                  </td>
                  <td>
                    <Input
                      className="h-9"
                      value={r.reason}
                      onChange={(e) =>
                        setRows((p) =>
                          p.map((x, j) => (j === i ? { ...x, reason: e.target.value } : x)),
                        )
                      }
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="flex justify-end gap-2 border-t pt-3">
        <Button type="button" variant="outline" onClick={onClose} disabled={mut.isPending}>
          {t('common.cancel')}
        </Button>
        <Button type="submit" disabled={mut.isPending}>
          {mut.isPending ? t('common.loading') : t('common.save')}
        </Button>
      </div>
    </Form>
  );
}
