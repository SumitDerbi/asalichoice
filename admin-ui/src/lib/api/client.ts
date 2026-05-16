import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/lib/auth/store';
import { useBranchStore } from '@/lib/branch/store';
import { ApiError, type ApiErrorPayload } from './errors';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

interface RetryableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

/**
 * Axios client wired with:
 *  - JWT access token attached from the auth store on every request,
 *  - automatic refresh on a single 401 (queued so concurrent calls
 *    only refresh once),
 *  - error envelope unwrapping into a typed `ApiError`.
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const access = useAuthStore.getState().accessToken;
  if (access) {
    config.headers = config.headers ?? {};
    (config.headers as Record<string, string>).Authorization = `Bearer ${access}`;
  }
  const branchId = useBranchStore.getState().currentBranchId;
  if (branchId != null) {
    config.headers = config.headers ?? {};
    (config.headers as Record<string, string>)['X-Branch-Id'] = String(branchId);
  }
  return config;
});

let refreshInFlight: Promise<string | null> | null = null;

async function performRefresh(): Promise<string | null> {
  const { refreshToken, setTokens, clear } = useAuthStore.getState();
  if (!refreshToken) {
    clear();
    return null;
  }
  try {
    const resp = await axios.post<{ access: string; refresh?: string }>(
      `${BASE_URL}/auth/refresh/`,
      { refresh: refreshToken },
      { timeout: 10_000 },
    );
    const access = resp.data.access;
    setTokens({ access, refresh: resp.data.refresh ?? refreshToken });
    return access;
  } catch {
    clear();
    return null;
  }
}

function toApiError(err: AxiosError): ApiError {
  const status = err.response?.status ?? 0;
  const data = err.response?.data as { error?: ApiErrorPayload } | undefined;
  if (data?.error?.code && data.error.message) {
    return new ApiError(data.error, status);
  }
  return new ApiError(
    {
      code: status === 0 ? 'API-NETWORK' : `API-HTTP-${status}`,
      message: err.message || 'Request failed',
    },
    status,
  );
}

apiClient.interceptors.response.use(
  (resp) => resp,
  async (err: AxiosError) => {
    const config = err.config as RetryableConfig | undefined;
    if (
      err.response?.status === 401 &&
      config &&
      !config._retry &&
      !config.url?.includes('/auth/')
    ) {
      config._retry = true;
      refreshInFlight ??= performRefresh().finally(() => {
        refreshInFlight = null;
      });
      const newAccess = await refreshInFlight;
      if (newAccess) {
        config.headers = config.headers ?? {};
        (config.headers as Record<string, string>).Authorization = `Bearer ${newAccess}`;
        return apiClient.request(config);
      }
    }
    return Promise.reject(toApiError(err));
  },
);
