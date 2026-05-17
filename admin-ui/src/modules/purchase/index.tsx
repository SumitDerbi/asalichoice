import { Truck } from 'lucide-react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import type { ModuleDef } from '@/app/module-registry';
import { PageHeader } from '@/components/shared/page-header';
import { cn } from '@/lib/utils';
import { t } from './lib/i18n';
import { VendorsPage } from './pages/vendors-page';
import { POsPage } from './pages/pos-page';
import { GRNsPage } from './pages/grns-page';
import { InvoicesPage } from './pages/invoices-page';
import { ReturnsPage } from './pages/returns-page';
import { LedgerPage } from './pages/ledger-page';

interface NavLink {
  to: string;
  label: string;
}

const LINKS: NavLink[] = [
  { to: 'vendors', label: t('vendors.title') },
  { to: 'pos', label: t('pos.title') },
  { to: 'grns', label: t('grns.title') },
  { to: 'invoices', label: t('invoices.title') },
  { to: 'returns', label: t('returns.title') },
  { to: 'ledger', label: t('ledger.title') },
];

function PurchaseShell() {
  const location = useLocation();
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-[200px_1fr]">
      <aside>
        <nav className="space-y-0.5">
          {LINKS.map((link) => {
            const active = location.pathname.startsWith(`/purchase/${link.to}`);
            return (
              <Link
                key={link.to}
                to={link.to}
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

function PurchaseIndex() {
  return (
    <div>
      <PageHeader title={t('module.title')} description={t('module.subtitle')} />
      <p className="text-sm text-muted-foreground">
        Select a section from the left to manage vendors and purchase documents.
      </p>
    </div>
  );
}

export function purchaseModule(): ModuleDef {
  return {
    id: 'purchase',
    label: t('module.title'),
    icon: Truck,
    category: 'Operations',
    order: 30,
    routes: [
      {
        path: 'purchase',
        element: <PurchaseShell />,
        children: [
          { index: true, element: <PurchaseIndex /> },
          { path: 'vendors', element: <VendorsPage /> },
          { path: 'pos', element: <POsPage /> },
          { path: 'grns', element: <GRNsPage /> },
          { path: 'invoices', element: <InvoicesPage /> },
          { path: 'returns', element: <ReturnsPage /> },
          { path: 'ledger', element: <LedgerPage /> },
        ],
      },
    ],
    nav: [{ to: '/purchase', label: t('module.title') }],
    commands: [
      {
        id: 'purchase.open',
        label: 'Open purchase',
        group: 'Navigation',
        perform: () => window.location.assign('/purchase'),
      },
      {
        id: 'purchase.vendors',
        label: 'Manage vendors',
        group: 'Purchase',
        perform: () => window.location.assign('/purchase/vendors'),
      },
      {
        id: 'purchase.pos',
        label: 'Purchase orders',
        group: 'Purchase',
        perform: () => window.location.assign('/purchase/pos'),
      },
      {
        id: 'purchase.grns',
        label: 'Goods receipts (GRN)',
        group: 'Purchase',
        perform: () => window.location.assign('/purchase/grns'),
      },
    ],
  };
}
