import * as React from 'react';
import { PageHeader } from '@/components/shared/page-header';
import { usePermissionsList } from '../api/hooks';
import type { Permission } from '../api/types';

function groupByModule(perms: Permission[]): Record<string, Permission[]> {
  const out: Record<string, Permission[]> = {};
  for (const p of perms) (out[p.module] ??= []).push(p);
  return out;
}

export function PermissionsPage() {
  const { data, isLoading, isError, error } = usePermissionsList();
  const grouped = React.useMemo(() => groupByModule(data ?? []), [data]);

  return (
    <div className="space-y-4">
      <PageHeader
        title="Permissions"
        description="Read-only catalog seeded from each module's permissions.py."
      />
      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : isError ? (
        <p className="text-sm text-destructive">{(error as Error).message ?? 'Error'}</p>
      ) : (
        <div className="space-y-4">
          {Object.keys(grouped)
            .sort()
            .map((mod) => (
              <div key={mod} className="space-y-1 rounded border p-3">
                <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  {mod}
                </h3>
                <ul className="space-y-0.5 text-xs">
                  {grouped[mod].map((p) => (
                    <li key={p.id} className="flex gap-3">
                      <code className="min-w-[16rem] text-muted-foreground">{p.code}</code>
                      <span>{p.name}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
