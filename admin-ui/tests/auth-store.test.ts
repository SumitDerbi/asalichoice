import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
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

beforeEach(() => {
  localStorage.clear();
  useAuthStore.setState({ accessToken: null, refreshToken: null, user: null });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('useAuthStore.login', () => {
  it('persists tokens + user on success', async () => {
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({
      data: { access: 'a.b.c', refresh: 'r.r.r', user: SAMPLE_USER },
    } as never);

    const user = await useAuthStore.getState().login('admin@example.test', 'pw');

    expect(user.email).toBe('admin@example.test');
    expect(useAuthStore.getState().accessToken).toBe('a.b.c');
    expect(useAuthStore.getState().refreshToken).toBe('r.r.r');
    expect(useAuthStore.getState().user).toEqual(SAMPLE_USER);

    const stored = JSON.parse(localStorage.getItem('asalichoice.auth.v1') ?? '{}');
    expect(stored.access).toBe('a.b.c');
    expect(stored.user.email).toBe('admin@example.test');
  });

  it('propagates ApiError on bad credentials and leaves state empty', async () => {
    vi.spyOn(apiClient, 'post').mockRejectedValueOnce(
      new ApiError({ code: 'API-400', message: 'Invalid email or password.' }, 400),
    );

    await expect(
      useAuthStore.getState().login('admin@example.test', 'wrong'),
    ).rejects.toBeInstanceOf(ApiError);

    expect(useAuthStore.getState().accessToken).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
  });
});

describe('useAuthStore.logout', () => {
  it('clears local state even when the server call fails', async () => {
    useAuthStore.setState({
      accessToken: 'a.b.c',
      refreshToken: 'r.r.r',
      user: SAMPLE_USER,
    });
    vi.spyOn(apiClient, 'post').mockRejectedValueOnce(
      new ApiError({ code: 'API-401', message: 'expired' }, 401),
    );

    await useAuthStore.getState().logout();

    expect(useAuthStore.getState().accessToken).toBeNull();
    expect(useAuthStore.getState().refreshToken).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
  });
});
