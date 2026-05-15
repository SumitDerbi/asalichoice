import { Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './layout';
import { LoginPage } from '@/modules/auth/login-page';
import { DashboardPage } from '@/modules/dashboard/dashboard-page';
import { useAuthStore } from '@/lib/auth/store';
import type { ReactElement } from 'react';

function RequireAuth({ children }: { children: ReactElement }) {
  const access = useAuthStore((s) => s.accessToken);
  if (!access) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="/masters" element={<PlaceholderPage title="Masters" />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
      <p className="text-sm text-muted-foreground">
        This module will be implemented in a later phase. See <code>plans/phase-1-modules/</code>.
      </p>
    </div>
  );
}
