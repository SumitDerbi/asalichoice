import { ErrorBoundary, type FallbackProps } from 'react-error-boundary';
import type { ReactNode } from 'react';
import { Button } from '@/components/ui/button';

function Fallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div
      role="alert"
      className="mx-auto mt-12 max-w-lg space-y-4 rounded-md border bg-card p-6 text-center"
    >
      <h2 className="text-lg font-semibold">Something went wrong</h2>
      <p className="text-sm text-muted-foreground">
        {error instanceof Error ? error.message : 'Unknown error'}
      </p>
      <Button onClick={resetErrorBoundary}>Try again</Button>
    </div>
  );
}

export function AppErrorBoundary({ children }: { children: ReactNode }) {
  return <ErrorBoundary FallbackComponent={Fallback}>{children}</ErrorBoundary>;
}
