import { Boxes } from 'lucide-react';
import { PageHeader } from '@/components/shared/page-header';
import type { ModuleDef } from '@/app/module-registry';

function MastersPlaceholder() {
  return (
    <div>
      <PageHeader
        title="Masters"
        description="Customers, vendors, products, and other master records. Wired in module M03."
      />
      <p className="text-sm text-muted-foreground">No masters configured yet.</p>
    </div>
  );
}

export function mastersModule(): ModuleDef {
  return {
    id: 'masters',
    label: 'Masters',
    icon: Boxes,
    category: 'Catalog',
    order: 10,
    routes: [{ path: 'masters', element: <MastersPlaceholder /> }],
    nav: [{ to: '/masters', label: 'Masters' }],
    commands: [
      {
        id: 'masters.open',
        label: 'Open masters',
        group: 'Navigation',
        perform: () => {
          window.location.assign('/masters');
        },
      },
    ],
  };
}
