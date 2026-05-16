import * as React from 'react';
import { Boxes } from 'lucide-react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import type { ModuleDef } from '@/app/module-registry';
import { PageHeader } from '@/components/shared/page-header';
import { cn } from '@/lib/utils';
import { t } from './lib/i18n';
import { BranchesPage } from './pages/branches-page';
import { DepartmentsPage } from './pages/departments-page';
import { DesignationsPage } from './pages/designations-page';
import { UnitsOfMeasurePage } from './pages/uom-page';
import { TaxesPage } from './pages/taxes-page';
import { HsnPage } from './pages/hsn-page';
import { PaymentModesPage } from './pages/payment-modes-page';
import { CategoriesPage } from './pages/categories-page';
import { BrandsPage } from './pages/brands-page';
import { WarehousesPage } from './pages/warehouses-page';
import { ZonesPage } from './pages/zones-page';
import { CountriesPage } from './pages/countries-page';
import { StatesPage } from './pages/states-page';
import { CitiesPage } from './pages/cities-page';
import { PincodesPage } from './pages/pincodes-page';

interface NavLink {
  to: string;
  label: string;
  group: 'Org' | 'Geo' | 'Catalog' | 'Finance';
}

const LINKS: NavLink[] = [
  { to: 'branches', label: t('branches.title'), group: 'Org' },
  { to: 'departments', label: t('departments.title'), group: 'Org' },
  { to: 'designations', label: t('designations.title'), group: 'Org' },
  { to: 'warehouses', label: t('warehouses.title'), group: 'Org' },
  { to: 'countries', label: t('countries.title'), group: 'Geo' },
  { to: 'states', label: t('states.title'), group: 'Geo' },
  { to: 'cities', label: t('cities.title'), group: 'Geo' },
  { to: 'pincodes', label: t('pincodes.title'), group: 'Geo' },
  { to: 'zones', label: t('zones.title'), group: 'Geo' },
  { to: 'categories', label: t('categories.title'), group: 'Catalog' },
  { to: 'brands', label: t('brands.title'), group: 'Catalog' },
  { to: 'uom', label: t('uom.title'), group: 'Catalog' },
  { to: 'taxes', label: t('taxes.title'), group: 'Finance' },
  { to: 'hsn', label: t('hsn.title'), group: 'Finance' },
  { to: 'payment-modes', label: t('payment_modes.title'), group: 'Finance' },
];

function MasterShell() {
  const location = useLocation();
  const groups = React.useMemo(() => {
    const order: NavLink['group'][] = ['Org', 'Geo', 'Catalog', 'Finance'];
    return order.map((g) => ({ name: g, links: LINKS.filter((l) => l.group === g) }));
  }, []);

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-[220px_1fr]">
      <aside className="space-y-4">
        {groups.map((g) => (
          <div key={g.name} className="space-y-1">
            <div className="px-2 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
              {g.name}
            </div>
            <nav className="space-y-0.5">
              {g.links.map((link) => {
                const active = location.pathname.startsWith(`/masters/${link.to}`);
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
          </div>
        ))}
      </aside>
      <main>
        <Outlet />
      </main>
    </div>
  );
}

function MasterIndex() {
  return (
    <div>
      <PageHeader title={t('module.title')} description={t('module.subtitle')} />
      <p className="text-sm text-muted-foreground">
        Select a master from the left to manage records.
      </p>
    </div>
  );
}

export function mastersModule(): ModuleDef {
  return {
    id: 'masters',
    label: t('module.title'),
    icon: Boxes,
    category: 'Catalog',
    order: 10,
    routes: [
      {
        path: 'masters',
        element: <MasterShell />,
        children: [
          { index: true, element: <MasterIndex /> },
          { path: 'branches', element: <BranchesPage /> },
          { path: 'departments', element: <DepartmentsPage /> },
          { path: 'designations', element: <DesignationsPage /> },
          { path: 'uom', element: <UnitsOfMeasurePage /> },
          { path: 'taxes', element: <TaxesPage /> },
          { path: 'hsn', element: <HsnPage /> },
          { path: 'payment-modes', element: <PaymentModesPage /> },
          { path: 'categories', element: <CategoriesPage /> },
          { path: 'brands', element: <BrandsPage /> },
          { path: 'warehouses', element: <WarehousesPage /> },
          { path: 'zones', element: <ZonesPage /> },
          { path: 'countries', element: <CountriesPage /> },
          { path: 'states', element: <StatesPage /> },
          { path: 'cities', element: <CitiesPage /> },
          { path: 'pincodes', element: <PincodesPage /> },
        ],
      },
    ],
    nav: [{ to: '/masters', label: t('module.title') }],
    commands: [
      {
        id: 'masters.open',
        label: 'Open masters',
        group: 'Navigation',
        perform: () => window.location.assign('/masters'),
      },
      {
        id: 'masters.create-branch',
        label: 'Create branch',
        group: 'Masters',
        perform: () => window.location.assign('/masters/branches'),
      },
      {
        id: 'masters.create-category',
        label: 'Create category',
        group: 'Masters',
        perform: () => window.location.assign('/masters/categories'),
      },
      {
        id: 'masters.manage-taxes',
        label: 'Manage taxes',
        group: 'Masters',
        perform: () => window.location.assign('/masters/taxes'),
      },
    ],
  };
}
