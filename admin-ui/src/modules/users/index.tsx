import { Users } from 'lucide-react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import type { ModuleDef } from '@/app/module-registry';
import { cn } from '@/lib/utils';
import { UsersPage } from './pages/users-page';
import { RolesPage } from './pages/roles-page';
import { PermissionsPage } from './pages/permissions-page';

const LINKS: Array<{ to: string; label: string }> = [
  { to: 'users', label: 'Users' },
  { to: 'roles', label: 'Roles' },
  { to: 'permissions', label: 'Permissions' },
];

function UsersShell() {
  const location = useLocation();
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-[200px_1fr]">
      <aside className="space-y-1">
        {LINKS.map((link) => {
          const active = location.pathname.startsWith(`/people/${link.to}`);
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
      </aside>
      <main>
        <Outlet />
      </main>
    </div>
  );
}

export function usersModule(): ModuleDef {
  return {
    id: 'users',
    label: 'Users & Roles',
    icon: Users,
    category: 'People',
    order: 5,
    routes: [
      {
        path: 'people',
        element: <UsersShell />,
        children: [
          { index: true, element: <UsersPage /> },
          { path: 'users', element: <UsersPage /> },
          { path: 'roles', element: <RolesPage /> },
          { path: 'permissions', element: <PermissionsPage /> },
        ],
      },
    ],
    nav: [{ to: '/people', label: 'Users & Roles' }],
    commands: [
      {
        id: 'people.users',
        label: 'Open users',
        group: 'People',
        perform: () => window.location.assign('/people/users'),
      },
      {
        id: 'people.roles',
        label: 'Open roles',
        group: 'People',
        perform: () => window.location.assign('/people/roles'),
      },
      {
        id: 'people.permissions',
        label: 'Open permissions',
        group: 'People',
        perform: () => window.location.assign('/people/permissions'),
      },
    ],
  };
}
