import { create } from 'zustand';
import { apiClient } from '@/lib/api/client';
import { ApiError } from '@/lib/api/errors';

/**
 * Auth store — owns JWT tokens and the current user.
 *
 * Plan 006 wires real login/logout against `/api/v1/auth/`. The shape
 * stays compatible with the day-zero placeholder so the API client and
 * router are unchanged.
 */
export interface AuthUser {
  id: number;
  email: string;
  mobile: string;
  employee_code?: string;
  primary_identifier?: string;
  name: string;
  display_name: string;
  is_staff: boolean;
  is_superuser: boolean;
  is_active: boolean;
  date_joined: string;
  permissions?: string[];
  branches?: Array<{ branch_id: number; is_default: boolean }>;
}

interface LoginResponse {
  access: string;
  refresh: string;
  user: AuthUser;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  setTokens: (tokens: { access: string; refresh: string }) => void;
  setUser: (user: AuthUser | null) => void;
  clear: () => void;
  login: (identifier: string, password: string) => Promise<AuthUser>;
  loginWithOTP: (identifier: string, code: string) => Promise<AuthUser>;
  requestOTP: (
    identifier: string,
    channel?: 'SMS' | 'EMAIL' | 'WHATSAPP',
  ) => Promise<{
    channel: string;
    expires_at: string;
    identifier: string;
  }>;
  logout: () => Promise<void>;
  bootstrap: () => Promise<void>;
}

const STORAGE_KEY = 'asalichoice.auth.v1';

interface PersistedShape {
  access: string | null;
  refresh: string | null;
  user: AuthUser | null;
}

function readPersisted(): PersistedShape {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { access: null, refresh: null, user: null };
    const parsed = JSON.parse(raw) as Partial<PersistedShape>;
    return {
      access: parsed.access ?? null,
      refresh: parsed.refresh ?? null,
      user: parsed.user ?? null,
    };
  } catch {
    return { access: null, refresh: null, user: null };
  }
}

function writePersisted(payload: PersistedShape) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch {
    // localStorage may be unavailable (private mode); ignore.
  }
}

const initial = readPersisted();

export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: initial.access,
  refreshToken: initial.refresh,
  user: initial.user,

  setTokens: ({ access, refresh }) => {
    writePersisted({ access, refresh, user: get().user });
    set({ accessToken: access, refreshToken: refresh });
  },

  setUser: (user) => {
    writePersisted({
      access: get().accessToken,
      refresh: get().refreshToken,
      user,
    });
    set({ user });
  },

  clear: () => {
    writePersisted({ access: null, refresh: null, user: null });
    set({ accessToken: null, refreshToken: null, user: null });
  },

  login: async (identifier, password) => {
    const resp = await apiClient.post<LoginResponse>('/auth/login/', {
      identifier,
      password,
    });
    const { access, refresh, user } = resp.data;
    writePersisted({ access, refresh, user });
    set({ accessToken: access, refreshToken: refresh, user });
    return user;
  },

  loginWithOTP: async (identifier, code) => {
    const resp = await apiClient.post<LoginResponse>('/auth/otp/verify/', {
      identifier,
      code,
      purpose: 'LOGIN',
    });
    const { access, refresh, user } = resp.data;
    writePersisted({ access, refresh, user });
    set({ accessToken: access, refreshToken: refresh, user });
    return user;
  },

  requestOTP: async (identifier, channel) => {
    const payload: Record<string, unknown> = { identifier, purpose: 'LOGIN' };
    if (channel) payload.preferred_channel = channel;
    const resp = await apiClient.post<{ channel: string; expires_at: string; identifier: string }>(
      '/auth/otp/request/',
      payload,
    );
    return resp.data;
  },

  logout: async () => {
    const refresh = get().refreshToken;
    try {
      if (refresh) {
        await apiClient.post('/auth/logout/', { refresh });
      }
    } catch (err) {
      // A failed/expired refresh token still ends the session locally.
      if (!(err instanceof ApiError)) throw err;
    } finally {
      writePersisted({ access: null, refresh: null, user: null });
      set({ accessToken: null, refreshToken: null, user: null });
    }
  },

  bootstrap: async () => {
    if (!get().accessToken) return;
    try {
      const resp = await apiClient.get<AuthUser>('/auth/me/');
      get().setUser(resp.data);
    } catch (err) {
      if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
        get().clear();
        return;
      }
      throw err;
    }
  },
}));
