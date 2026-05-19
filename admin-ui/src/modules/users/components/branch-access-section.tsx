import * as React from 'react';
import { toast } from 'sonner';
import { Trash2 } from 'lucide-react';
import { ApiError } from '@/lib/api/errors';
import { Button } from '@/components/ui/button';
import { useMasterList } from '@/modules/masters/api/hooks';
import type { Branch } from '@/modules/masters/api/types';
import {
  useBranchAccessCreate,
  useBranchAccessDelete,
  useBranchAccessList,
  useBranchAccessSetDefault,
} from '../api/hooks';

interface Props {
  userId: number;
}

export function BranchAccessSection({ userId }: Props) {
  const { data: rows, isLoading } = useBranchAccessList(userId);
  const { data: branches } = useMasterList<Branch>('branches');
  const createMut = useBranchAccessCreate();
  const deleteMut = useBranchAccessDelete();
  const setDefaultMut = useBranchAccessSetDefault();

  const [selected, setSelected] = React.useState<number | ''>('');

  const assignedIds = React.useMemo(() => new Set((rows ?? []).map((r) => r.branch)), [rows]);
  const available = React.useMemo(
    () => (branches ?? []).filter((b) => !assignedIds.has(b.id) && b.is_active),
    [branches, assignedIds],
  );

  const branchById = React.useMemo(() => {
    const m = new Map<number, Branch>();
    for (const b of branches ?? []) m.set(b.id, b);
    return m;
  }, [branches]);

  const handleAdd = async () => {
    if (selected === '') return;
    try {
      await createMut.mutateAsync({ user: userId, branch: Number(selected) });
      setSelected('');
      toast.success('Branch added.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to add branch.');
    }
  };

  const handleRemove = async (id: number) => {
    try {
      await deleteMut.mutateAsync(id);
      toast.success('Branch removed.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to remove branch.');
    }
  };

  const handleSetDefault = async (branchId: number) => {
    try {
      await setDefaultMut.mutateAsync({ user_id: userId, branch_id: branchId });
      toast.success('Default branch updated.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to set default.');
    }
  };

  return (
    <div className="space-y-1.5">
      <span className="text-sm font-medium">Branch access</span>
      <div className="rounded border p-2">
        {isLoading ? (
          <p className="text-xs text-muted-foreground">Loading…</p>
        ) : (rows ?? []).length === 0 ? (
          <p className="text-xs text-muted-foreground">
            No branches assigned. User has access to all branches.
          </p>
        ) : (
          <ul className="space-y-1">
            {(rows ?? []).map((row) => {
              const branch = branchById.get(row.branch);
              return (
                <li key={row.id} className="flex items-center justify-between gap-2 text-sm">
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      name={`default-branch-${userId}`}
                      checked={row.is_default}
                      onChange={() => handleSetDefault(row.branch)}
                      disabled={setDefaultMut.isPending}
                      aria-label={`Set ${branch?.code ?? `#${row.branch}`} as default`}
                    />
                    <span className="font-medium">{branch?.code ?? `#${row.branch}`}</span>
                    <span className="text-muted-foreground">{branch?.name ?? ''}</span>
                    {row.is_default && (
                      <span className="rounded bg-emerald-50 px-1.5 py-0.5 text-xs text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
                        Default
                      </span>
                    )}
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleRemove(row.id)}
                    disabled={deleteMut.isPending}
                    aria-label="Remove branch"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </li>
              );
            })}
          </ul>
        )}

        {available.length > 0 && (
          <div className="mt-2 flex items-center gap-2">
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value === '' ? '' : Number(e.target.value))}
              className="flex h-9 flex-1 rounded-md border border-input bg-background px-3 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              aria-label="Add branch"
            >
              <option value="">Add branch…</option>
              {available.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.code} — {b.name}
                </option>
              ))}
            </select>
            <Button size="sm" onClick={handleAdd} disabled={selected === '' || createMut.isPending}>
              Add
            </Button>
          </div>
        )}
      </div>
      <p className="text-xs text-muted-foreground">
        Leave empty to grant access to all branches. The default branch is auto-selected at sign-in.
      </p>
    </div>
  );
}
