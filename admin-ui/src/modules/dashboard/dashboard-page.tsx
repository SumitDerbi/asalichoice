import { PageHeader } from '@/components/shared/page-header';

export function DashboardPage() {
  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Welcome to AsliChoice Admin. Real widgets land with module M13 (reports & dashboards)."
      />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {['Sales today', 'Open orders', 'Low stock', 'Pending GRN'].map((label) => (
          <div key={label} className="rounded-lg border bg-card p-4 shadow-sm">
            <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
            <div className="mt-2 text-2xl font-semibold">—</div>
          </div>
        ))}
      </div>
    </div>
  );
}
