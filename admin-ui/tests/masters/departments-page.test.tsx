import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { fireEvent, screen, waitFor } from '@testing-library/react';
import { Toaster } from 'sonner';
import { renderWithProviders } from '@/test/utils';
import { departmentsStore } from '@/test/mocks/master-handlers';
import { DepartmentsPage } from '@/modules/masters/pages/departments-page';
import { useAuthStore } from '@/lib/auth/store';

const ADMIN = {
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

beforeEach(() => {
  useAuthStore.setState({
    accessToken: 'token',
    refreshToken: 'r',
    user: ADMIN,
  });
  departmentsStore.reset([
    { id: 1, code: 'OPS', name: 'Operations', description: '', is_active: true },
    { id: 2, code: 'FIN', name: 'Finance', description: '', is_active: true },
  ]);
});

afterEach(() => {
  useAuthStore.setState({ accessToken: null, refreshToken: null, user: null });
});

describe('DepartmentsPage', () => {
  it('renders rows fetched from the API', async () => {
    renderWithProviders(
      <>
        <Toaster />
        <DepartmentsPage />
      </>,
    );

    expect(await screen.findByText('OPS')).toBeInTheDocument();
    expect(screen.getByText('Operations')).toBeInTheDocument();
    expect(screen.getByText('FIN')).toBeInTheDocument();
  });

  it('opens the create drawer and submits a new record', async () => {
    renderWithProviders(
      <>
        <Toaster />
        <DepartmentsPage />
      </>,
    );

    fireEvent.click(await screen.findByRole('button', { name: /create/i }));

    const codeInput = await screen.findByLabelText(/code/i);
    fireEvent.change(codeInput, { target: { value: 'HR' } });
    fireEvent.change(screen.getByLabelText(/^name$/i), { target: { value: 'Human Resources' } });

    fireEvent.click(screen.getByRole('button', { name: /^save$/i }));

    await waitFor(() => expect(screen.getByText('Human Resources')).toBeInTheDocument());
  });

  it('shows empty state when there are no rows', async () => {
    departmentsStore.reset([]);
    renderWithProviders(<DepartmentsPage />);
    expect(await screen.findByText(/no records yet/i)).toBeInTheDocument();
  });

  it('deactivates a record (soft-delete)', async () => {
    renderWithProviders(
      <>
        <Toaster />
        <DepartmentsPage />
      </>,
    );

    await screen.findByText('OPS');
    const deactivateBtns = screen.getAllByRole('button', { name: /^deactivate/i });
    fireEvent.click(deactivateBtns[0]);

    // Confirm dialog
    const confirmBtn = await screen.findByRole('button', { name: /^deactivate$/i });
    fireEvent.click(confirmBtn);

    await waitFor(() => expect(screen.queryByText('OPS')).not.toBeInTheDocument());
  });
});
