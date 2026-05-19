import * as React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Button } from '@/components/ui/button';

interface Session {
  jti: string;
  created_at: string;
  expires_at: string;
  ip?: string | null;
  user_agent?: string | null;
  blacklisted: boolean;
}

export function AccountPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery<{ sessions: Session[] }>(
    ['auth', 'sessions'],
    async () => {
      const resp = await apiClient.get<{ sessions: Session[] }>('/auth/sessions/');
      return resp.data;
    },
  );

  const revokeMutation = useMutation({
    mutationFn: async (jti: string) => {
      await apiClient.post('/auth/sessions/', { jti });
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['auth', 'sessions']);
    },
  });

  return (
    <div className="mx-auto max-w-2xl p-6">
      <h1 className="mb-4 text-2xl font-semibold">My Account</h1>
      <section className="mb-8">
        <h2 className="mb-2 text-lg font-medium">Active Sessions</h2>
        {isLoading ? (
          <div>Loading sessions…</div>
        ) : error ? (
          <div className="text-red-600">Failed to load sessions.</div>
        ) : (
          <div className="divide-y rounded-md border">
            {data?.sessions.length === 0 && (
              <div className="p-4 text-muted-foreground">No active sessions.</div>
            )}
            {data?.sessions.map((s) => (
              <div key={s.jti} className="flex items-center justify-between gap-4 p-4">
                <div className="min-w-0 flex-1">
                  <div className="break-all font-mono text-xs">{s.jti}</div>
                  <div className="text-xs text-muted-foreground">
                    Created: {new Date(s.created_at).toLocaleString()} | Expires:{' '}
                    {new Date(s.expires_at).toLocaleString()}
                  </div>
                  {s.ip && <div className="text-xs text-muted-foreground">IP: {s.ip}</div>}
                  {s.user_agent && (
                    <div className="text-xs text-muted-foreground">UA: {s.user_agent}</div>
                  )}
                </div>
                <div>
                  {s.blacklisted ? (
                    <span className="text-xs text-red-500">Revoked</span>
                  ) : (
                    <Button
                      size="sm"
                      variant="destructive"
                      disabled={revokeMutation.isLoading}
                      onClick={() => revokeMutation.mutate(s.jti)}
                    >
                      Revoke
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
