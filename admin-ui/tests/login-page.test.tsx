import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { Toaster } from 'sonner';
import { LoginPage } from '@/modules/auth/login-page';
import { useAuthStore } from '@/lib/auth/store';
import { apiClient } from '@/lib/api/client';
import { ApiError } from '@/lib/api/errors';

const SAMPLE_USER = {
  id: 1,
  email: 'admin@example.test',
  mobile: '',
  name: 'Admin',
  display_name: 'Admin',
  is_staff: true,
  is_superuser: true,
  is_active: true,
  date_joined: '2025-01-01T00:00:00Z',
};

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <Toaster />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<div>Dashboard Home</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  localStorage.clear();
  useAuthStore.setState({ accessToken: null, refreshToken: null, user: null });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('LoginPage', () => {
  it('shows a validation error when the email is missing', async () => {
    renderLogin();
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    expect(await screen.findByText(/valid email/i)).toBeInTheDocument();
  });

  it('logs in and navigates to the dashboard', async () => {
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({
      data: { access: 'a.b.c', refresh: 'r.r.r', user: SAMPLE_USER },
    } as never);

    renderLogin();
    fireEvent.change(screen.getByLabelText(/^email$/i), {
      target: { value: 'admin@example.test' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'pw' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => expect(screen.getByText('Dashboard Home')).toBeInTheDocument());
    expect(useAuthStore.getState().accessToken).toBe('a.b.c');
  });

  it('surfaces the API error message on bad credentials', async () => {
    vi.spyOn(apiClient, 'post').mockRejectedValueOnce(
      new ApiError({ code: 'API-400', message: 'Invalid email or password.' }, 400),
    );

    renderLogin();
    fireEvent.change(screen.getByLabelText(/^email$/i), {
      target: { value: 'admin@example.test' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrong' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByText(/invalid email or password/i)).toBeInTheDocument();
    expect(useAuthStore.getState().accessToken).toBeNull();
  });
});
