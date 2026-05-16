/**
 * Shared render helper for Vitest + React Testing Library.
 *
 * Use `renderWithProviders(<MyComponent />)` to render with a fresh
 * `QueryClient` and `MemoryRouter`. Override individual providers by
 * passing options.
 */

import * as React from 'react';
import { render, type RenderOptions, type RenderResult } from '@testing-library/react';
import { MemoryRouter, type MemoryRouterProps } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export interface RenderWithProvidersOptions extends Omit<RenderOptions, 'wrapper'> {
  initialEntries?: MemoryRouterProps['initialEntries'];
  queryClient?: QueryClient;
}

export interface RenderWithProvidersResult extends RenderResult {
  queryClient: QueryClient;
}

export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0, staleTime: 0 },
      mutations: { retry: false },
    },
  });
}

export function renderWithProviders(
  ui: React.ReactElement,
  options: RenderWithProvidersOptions = {},
): RenderWithProvidersResult {
  const { initialEntries = ['/'], queryClient = createTestQueryClient(), ...rest } = options;
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>{children}</MemoryRouter>
    </QueryClientProvider>
  );
  const result = render(ui, { wrapper: Wrapper, ...rest });
  return { ...result, queryClient };
}

export * from '@testing-library/react';
