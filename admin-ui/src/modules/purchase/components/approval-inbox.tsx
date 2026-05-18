import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { usePurchaseList } from '../api/hooks';
import type { PurchaseOrder, GRN } from '../api/types';

/**
 * Topbar bell that surfaces pending approvals across POs (PENDING_APPROVAL)
 * and GRNs (SUBMITTED). Lazily refreshes via TanStack Query (default 60s
 * staleTime).
 */
export function ApprovalInbox() {
  const navigate = useNavigate();
  const [open, setOpen] = React.useState(false);
  const ref = React.useRef<HTMLDivElement>(null);

  const { data: pos } = usePurchaseList<PurchaseOrder>('pos', { status: 'PENDING_APPROVAL' });
  const { data: grns } = usePurchaseList<GRN>('grns', { status: 'SUBMITTED' });
  const count = (pos?.length ?? 0) + (grns?.length ?? 0);

  React.useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <Button
        variant="ghost"
        size="icon"
        aria-label={`Pending approvals (${count})`}
        onClick={() => setOpen((v) => !v)}
      >
        <Bell className="h-4 w-4" aria-hidden="true" />
        {count > 0 && (
          <span
            className="absolute -right-0.5 -top-0.5 rounded-full bg-rose-600 px-1 text-[10px] font-medium text-white"
            aria-hidden="true"
          >
            {count > 99 ? '99+' : count}
          </span>
        )}
      </Button>
      {open && (
        <div className="absolute right-0 top-full z-50 mt-1 w-80 rounded-md border bg-popover p-2 text-sm shadow-md">
          <div className="border-b pb-1 font-medium">Pending approvals</div>
          {!count && <p className="py-2 text-xs text-muted-foreground">All caught up.</p>}
          {(pos ?? []).length > 0 && (
            <div className="py-1">
              <div className="text-xs font-medium text-muted-foreground">Purchase orders</div>
              <ul className="space-y-0.5">
                {pos!.slice(0, 5).map((p) => (
                  <li key={p.id}>
                    <button
                      type="button"
                      className="w-full rounded px-1.5 py-1 text-left text-xs hover:bg-muted"
                      onClick={() => {
                        setOpen(false);
                        navigate('/purchase/pos');
                      }}
                    >
                      <span className="font-mono">{p.po_no}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {(grns ?? []).length > 0 && (
            <div className="py-1">
              <div className="text-xs font-medium text-muted-foreground">GRNs</div>
              <ul className="space-y-0.5">
                {grns!.slice(0, 5).map((g) => (
                  <li key={g.id}>
                    <button
                      type="button"
                      className="w-full rounded px-1.5 py-1 text-left text-xs hover:bg-muted"
                      onClick={() => {
                        setOpen(false);
                        navigate('/purchase/grns');
                      }}
                    >
                      <span className="font-mono">{g.grn_no}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
