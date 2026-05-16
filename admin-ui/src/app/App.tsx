import * as React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import type { ReactElement } from 'react';
import { AppShell } from './layout';
import { AppErrorBoundary } from './error-boundary';
import { ForbiddenPage, NotFoundPage } from './status-pages';
import { LoginPage } from '@/modules/auth/login-page';
import { useAuthStore } from '@/lib/auth/store';
import { listRoutes } from './module-registry';
import { registerAllModules } from './register-modules';

registerAllModules();

function RequireAuth({ children }: { children: ReactElement }) {
  const access = useAuthStore((s) => s.accessToken);
  const user = useAuthStore((s) => s.user);
  const bootstrap = useAuthStore((s) => s.bootstrap);

  React.useEffect(() => {
    if (access && !user) {
      void bootstrap();
    }
  }, [access, user, bootstrap]);

  if (!access) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  const moduleRoutes = listRoutes();
  return (
    <AppErrorBoundary>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/403" element={<ForbiddenPage />} />
        <Route
          element={
            <RequireAuth>
              <AppShell />
            </RequireAuth>
          }
        >
          {moduleRoutes.map((r, i) =>
            r.index ? (
              <Route key={`idx-${i}`} index element={r.element} />
            ) : (
              <Route key={r.path ?? `p-${i}`} path={r.path} element={r.element} />
            ),
          )}
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </AppErrorBoundary>
  );
}
