/**
 * Smoke test for the shared `renderWithProviders` + MSW server.
 * Proves QueryClient + Router are wired and HTTP traffic is intercepted.
 */

import { describe, expect, it } from 'vitest';
import { useQuery } from '@tanstack/react-query';
import { http, HttpResponse } from 'msw';
import { renderWithProviders, screen, waitFor } from '@/test/utils';
import { server } from '@/test/mocks/server';
import { apiClient } from '@/lib/api/client';

function Ping() {
  const { data, error } = useQuery({
    queryKey: ['ping'],
    queryFn: async () => {
      const res = await apiClient.get<{ status: string }>('/health/');
      return res.data;
    },
  });
  if (error) return <p>error: {(error as Error).message}</p>;
  return <p>{data ? `ok: ${data.status}` : 'loading'}</p>;
}

describe('renderWithProviders + MSW', () => {
  it('intercepts a GET and resolves through React Query', async () => {
    const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
    server.use(http.get(`${base}/health/`, () => HttpResponse.json({ status: 'ok' })));

    renderWithProviders(<Ping />);

    await waitFor(() => {
      expect(screen.getByText(/^ok: ok$/)).toBeInTheDocument();
    });
  });
});
