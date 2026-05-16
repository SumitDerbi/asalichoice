import { describe, expect, it, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '@/app/App';
import { useAuthStore } from '@/lib/auth/store';

function renderApp(initialEntries: string[] = ['/']) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={initialEntries}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

function signIn() {
  useAuthStore.setState({
    accessToken: 'fake-access',
    refreshToken: 'fake-refresh',
    user: {
      id: 1,
      email: 'admin@example.com',
      mobile: '',
      name: 'Admin',
      display_name: 'Admin',
      is_staff: true,
      is_superuser: true,
      is_active: true,
      date_joined: '2026-05-15T00:00:00Z',
    },
  });
}

describe('App shell', () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.classList.remove('dark');
    useAuthStore.setState({ accessToken: null, refreshToken: null, user: null });
  });

  it('renders sidebar categories and breadcrumbs when authenticated', () => {
    signIn();
    renderApp(['/']);
    expect(screen.getByText(/^Operations$/i)).toBeInTheDocument();
    expect(screen.getByText(/^Catalog$/i)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /^Dashboard$/i })).toBeInTheDocument();
  });

  it('opens the command palette with Ctrl+K', async () => {
    signIn();
    renderApp(['/']);
    await act(async () => {
      fireEvent.keyDown(window, { key: 'k', ctrlKey: true });
    });
    expect(await screen.findByPlaceholderText(/type a command or search/i)).toBeInTheDocument();
  });

  it('toggles dark theme with the t hotkey and persists it', async () => {
    signIn();
    renderApp(['/']);
    await act(async () => {
      fireEvent.keyDown(window, { key: 't' });
    });
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(window.localStorage.getItem('asalichoice.theme.v1')).toContain('"theme":"dark"');
  });

  it('persists branch selection via the switcher', async () => {
    signIn();
    renderApp(['/']);
    const user = userEvent.setup();
    await user.click(screen.getByRole('button', { name: /switch branch/i }));
    // dropdown menu items are portaled; assert via accessible name
    const wh1 = await screen.findByText(/warehouse 1/i);
    await user.click(wh1);
    expect(window.localStorage.getItem('asalichoice.branch.v1')).toContain('"currentBranchId":2');
  });

  it('renders a 404 page for unknown routes when authenticated', () => {
    signIn();
    renderApp(['/this-route-does-not-exist']);
    expect(screen.getByText(/404/)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /page not found/i })).toBeInTheDocument();
  });
});
