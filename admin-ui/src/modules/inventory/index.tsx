import { Boxes } from 'lucide-react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import type { ModuleDef } from '@/app/module-registry';
import { PageHeader } from '@/components/shared/page-header';
import { cn } from '@/lib/utils';
import { t } from './lib/i18n';
import { StockPage } from './pages/stock-page';
import { BatchesPage } from './pages/batches-page';
import { LedgerPage } from './pages/ledger-page';
import { ReservationsPage } from './pages/reservations-page';
import { TransfersPage } from './pages/transfers-page';
import { AdjustmentsPage } from './pages/adjustments-page';
import { WastagePage } from './pages/wastage-page';
import { CountsPage } from './pages/counts-page';

interface NavLink {
  to: string;
  label: string;
}

const LINKS: NavLink[] = [
  { to: 'stock', label: t('stock.title') },
  { to: 'batches', label: t('batches.title') },
  { to: 'ledger', label: t('ledger.title') },
  { to: 'reservations', label: t('reservations.title') },
  { to: 'transfers', label: t('transfers.title') },
  { to: 'adjustments', label: t('adjustments.title') },
  { to: 'wastage', label: t('wastage.title') },
  { to: 'counts', label: t('counts.title') },
];

function InventoryShell() {
  const location = useLocation();
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-[200px_1fr]">
      <aside>
        <nav className="space-y-0.5">
          {LINKS.map((link) => {
            const active = location.pathname.startsWith(`/inventory/${link.to}`);
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

function InventoryIndex() {
  return (
    <div>
      <PageHeader title={t('module.title')} description={t('module.subtitle')} />
      <p className="text-sm text-muted-foreground">
        Select a section from the left to view stock, batches, ledger, transfers and more.
      </p>
    </div>
  );
}

export function inventoryModule(): ModuleDef {
  return {
    id: 'inventory',
    label: t('module.title'),
    icon: Boxes,
    category: 'Operations',
    order: 35,
    routes: [
      {
        path: 'inventory',
        element: <InventoryShell />,
        children: [
          { index: true, element: <InventoryIndex /> },
          { path: 'stock', element: <StockPage /> },
          { path: 'batches', element: <BatchesPage /> },
          { path: 'ledger', element: <LedgerPage /> },
          { path: 'reservations', element: <ReservationsPage /> },
          { path: 'transfers', element: <TransfersPage /> },
          { path: 'adjustments', element: <AdjustmentsPage /> },
          { path: 'wastage', element: <WastagePage /> },
          { path: 'counts', element: <CountsPage /> },
        ],
      },
    ],
    nav: [{ to: '/inventory', label: t('module.title') }],
    commands: [
      {
        id: 'inventory.open',
        label: 'Open inventory',
        group: 'Navigation',
        perform: () => window.location.assign('/inventory'),
      },
      {
        id: 'inventory.stock',
        label: 'Stock on hand',
        group: 'Inventory',
        perform: () => window.location.assign('/inventory/stock'),
      },
      {
        id: 'inventory.ledger',
        label: 'Inventory ledger',
        group: 'Inventory',
        perform: () => window.location.assign('/inventory/ledger'),
      },
      {
        id: 'inventory.transfers',
        label: 'Branch transfers',
        group: 'Inventory',
        perform: () => window.location.assign('/inventory/transfers'),
      },
    ],
  };
}
