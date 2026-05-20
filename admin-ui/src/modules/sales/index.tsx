import { Receipt } from 'lucide-react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import type { ModuleDef } from '@/app/module-registry';
import { PageHeader } from '@/components/shared/page-header';
import { cn } from '@/lib/utils';
import { t } from './lib/i18n';
import { SalesListPage } from './pages/sales-list-page';
import { SaleDetailPage } from './pages/sale-detail-page';
import { SaleEntryPage } from './pages/sale-entry-page';
import { DiscountsPage } from './pages/discounts-page';

interface NavLink {
  to: string;
  label: string;
}

const LINKS: NavLink[] = [
  { to: '', label: t('sales.title') },
  { to: 'discounts', label: t('discounts.title') },
];

function SalesShell() {
  const location = useLocation();
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-[200px_1fr]">
      <aside>
        <nav className="space-y-0.5">
          {LINKS.map((link) => {
            const target = link.to ? `/sales/${link.to}` : '/sales';
            const active =
              link.to === ''
                ? location.pathname === '/sales' ||
                  /^\/sales\/(\d+|new|b2b)/.test(location.pathname)
                : location.pathname.startsWith(target);
            return (
              <Link
                key={link.to || 'root'}
                to={target}
                className={cn(
                  'block rounded px-2 py-1.5 text-sm text-foreground hover:bg-muted',
                  active && 'bg-muted font-medium',
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <main>
        <Outlet />
      </main>
    </div>
  );
}

function SalesIndex() {
  return (
    <div>
      <PageHeader title={t('module.title')} description={t('module.subtitle')} />
      <SalesListPage />
    </div>
  );
}

export function salesModule(): ModuleDef {
  return {
    id: 'sales',
    label: t('module.title'),
    icon: Receipt,
    category: 'Operations',
    order: 40,
    routes: [
      {
        path: 'sales',
        element: <SalesShell />,
        children: [
          { index: true, element: <SalesIndex /> },
          { path: 'new', element: <SaleEntryPage origin="POS" /> },
          { path: 'b2b', element: <SaleEntryPage origin="B2B" /> },
          { path: 'discounts', element: <DiscountsPage /> },
          { path: ':id', element: <SaleDetailPage /> },
        ],
      },
    ],
    nav: [{ to: '/sales', label: t('module.title') }],
    commands: [
      {
        id: 'sales.open',
        label: 'Open sales',
        group: 'Navigation',
        perform: () => window.location.assign('/sales'),
      },
      {
        id: 'sales.new',
        label: 'New sale',
        group: 'Sales',
        perform: () => window.location.assign('/sales/new'),
      },
      {
        id: 'sales.b2b',
        label: 'New B2B sale',
        group: 'Sales',
        perform: () => window.location.assign('/sales/b2b'),
      },
      {
        id: 'sales.discounts',
        label: 'Discounts',
        group: 'Sales',
        perform: () => window.location.assign('/sales/discounts'),
      },
    ],
  };
}
