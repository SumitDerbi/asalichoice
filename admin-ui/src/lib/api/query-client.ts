import { QueryClient } from '@tanstack/react-query';
import { ApiError } from './errors';

/**
 * Default TanStack Query client. Conservative defaults aligned with
 * plans/_conventions.md §6 (caching + UX) — modules can override
 * `staleTime` per resource as needed.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      gcTime: 5 * 60_000,
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
          return false;
        }
        return failureCount < 1;
      },
    },
    mutations: {
      retry: 0,
    },
  },
});
