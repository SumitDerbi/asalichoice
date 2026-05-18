import { Package } from 'lucide-react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import type { ModuleDef } from '@/app/module-registry';
import { PageHeader } from '@/components/shared/page-header';
import { cn } from '@/lib/utils';
import { t } from './lib/i18n';
import { ProductsPage } from './pages/products-page';
import { BundlesPage } from './pages/bundles-page';
import { PricesPage } from './pages/prices-page';
import { ImportPage } from './pages/import-page';
import { VariantsPage } from './pages/variants-page';
import { BarcodesPage } from './pages/barcodes-page';
import { AttributesPage } from './pages/attributes-page';
import { AvailabilityPage } from './pages/availability-page';

interface NavLink {
  to: string;
  label: string;
}

const LINKS: NavLink[] = [
  { to: 'products', label: t('products.title') },
  { to: 'variants', label: t('variants.title') },
  { to: 'barcodes', label: t('barcodes.title') },
  { to: 'attributes', label: t('attributes.title') },
  { to: 'availability', label: t('availability.title') },
  { to: 'prices', label: t('prices.title') },
  { to: 'bundles', label: t('bundles.title') },
  { to: 'import', label: t('import.title') },
];

function CatalogShell() {
  const location = useLocation();
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-[200px_1fr]">
      <aside>
        <nav className="space-y-0.5">
          {LINKS.map((link) => {
            const active = location.pathname.startsWith(`/catalog/${link.to}`);
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

function CatalogIndex() {
  return (
    <div>
      <PageHeader title={t('module.title')} description={t('module.subtitle')} />
      <p className="text-sm text-muted-foreground">
        Select a section from the left to manage catalog records.
      </p>
    </div>
  );
}

export function catalogModule(): ModuleDef {
  return {
    id: 'catalog',
    label: t('module.title'),
    icon: Package,
    category: 'Catalog',
    order: 20,
    routes: [
      {
        path: 'catalog',
        element: <CatalogShell />,
        children: [
          { index: true, element: <CatalogIndex /> },
          { path: 'products', element: <ProductsPage /> },
          { path: 'variants', element: <VariantsPage /> },
          { path: 'barcodes', element: <BarcodesPage /> },
          { path: 'attributes', element: <AttributesPage /> },
          { path: 'availability', element: <AvailabilityPage /> },
          { path: 'bundles', element: <BundlesPage /> },
          { path: 'prices', element: <PricesPage /> },
          { path: 'import', element: <ImportPage /> },
        ],
      },
    ],
    nav: [{ to: '/catalog', label: t('module.title') }],
    commands: [
      {
        id: 'catalog.open',
        label: 'Open catalog',
        group: 'Navigation',
        perform: () => window.location.assign('/catalog'),
      },
      {
        id: 'catalog.create-product',
        label: 'Create product',
        group: 'Catalog',
        perform: () => window.location.assign('/catalog/products'),
      },
      {
        id: 'catalog.import-products',
        label: 'Import products (CSV)',
        group: 'Catalog',
        perform: () => window.location.assign('/catalog/import'),
      },
    ],
  };
}
