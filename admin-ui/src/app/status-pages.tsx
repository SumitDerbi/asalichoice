import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

export function NotFoundPage() {
  return (
    <div className="mx-auto mt-16 max-w-md space-y-3 text-center">
      <p className="text-5xl font-bold text-muted-foreground">404</p>
      <h1 className="text-xl font-semibold">Page not found</h1>
      <p className="text-sm text-muted-foreground">
        The page you are looking for does not exist or has been moved.
      </p>
      <Button asChild>
        <Link to="/">Go to dashboard</Link>
      </Button>
    </div>
  );
}

export function ForbiddenPage() {
  return (
    <div className="mx-auto mt-16 max-w-md space-y-3 text-center">
      <p className="text-5xl font-bold text-muted-foreground">403</p>
      <h1 className="text-xl font-semibold">Access denied</h1>
      <p className="text-sm text-muted-foreground">
        You do not have permission to view this page. Contact your administrator if you believe this
        is a mistake.
      </p>
      <Button asChild>
        <Link to="/">Back to dashboard</Link>
      </Button>
    </div>
  );
}
