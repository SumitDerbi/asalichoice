import * as React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { Boxes, LayoutDashboard, LogOut, Menu, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/lib/auth/store';
import { CommandPalette } from './command-palette';
import { ShortcutsOverlay } from './shortcuts-overlay';

const APP_NAME = import.meta.env.VITE_APP_NAME ?? 'AsliChoice Admin';
const APP_VERSION = import.meta.env.VITE_APP_VERSION ?? '0.1.0';

interface NavItem {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const PRIMARY_NAV: NavItem[] = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/masters', label: 'Masters', icon: Boxes },
];

export function AppShell() {
  const [paletteOpen, setPaletteOpen] = React.useState(false);
  const [shortcutsOpen, setShortcutsOpen] = React.useState(false);
  const [sidebarOpen, setSidebarOpen] = React.useState(true);
  const navigate = useNavigate();
  const logout = useAuthStore((s) => s.logout);
  const user = useAuthStore((s) => s.user);

  React.useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const target = e.target as HTMLElement | null;
      const inField =
        target &&
        (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable);

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPaletteOpen((v) => !v);
        return;
      }
      if (!inField && e.key === '?') {
        e.preventDefault();
        setShortcutsOpen((v) => !v);
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  return (
    <div className="flex h-full min-h-screen w-full">
      <aside
        className={cn(
          'flex flex-col border-r bg-card transition-all duration-200',
          sidebarOpen ? 'w-60' : 'w-16',
        )}
        aria-label="Primary navigation"
      >
        <div className="flex h-14 items-center gap-2 border-b px-4">
          <span className="font-semibold tracking-tight">{sidebarOpen ? APP_NAME : 'AC'}</span>
        </div>
        <nav className="flex-1 space-y-1 p-2">
          {PRIMARY_NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
                  isActive
                    ? 'bg-accent text-accent-foreground'
                    : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground',
                )
              }
            >
              <item.icon className="h-4 w-4 shrink-0" aria-hidden="true" />
              {sidebarOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>
        <div className="border-t p-2 text-xs text-muted-foreground">
          {sidebarOpen && <span>v{APP_VERSION}</span>}
        </div>
      </aside>

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="flex h-14 items-center gap-2 border-b bg-background px-4">
          <Button
            variant="ghost"
            size="icon"
            aria-label="Toggle sidebar"
            onClick={() => setSidebarOpen((v) => !v)}
          >
            <Menu className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button
            variant="outline"
            className="h-9 min-w-[16rem] justify-start text-muted-foreground"
            onClick={() => setPaletteOpen(true)}
            aria-label="Open command palette"
          >
            <Search className="mr-2 h-4 w-4" aria-hidden="true" />
            <span className="flex-1 text-left">Search or run command…</span>
            <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-[10px]">
              Ctrl K
            </kbd>
          </Button>
          <div className="ml-auto flex items-center gap-2">
            {user && (
              <span className="hidden text-sm text-muted-foreground sm:inline">
                {user.display_name || user.email}
              </span>
            )}
            <Button variant="ghost" size="sm" onClick={() => setShortcutsOpen(true)}>
              ?
            </Button>
            <Button variant="ghost" size="icon" aria-label="Sign out" onClick={handleLogout}>
              <LogOut className="h-4 w-4" aria-hidden="true" />
            </Button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>

      <CommandPalette open={paletteOpen} onOpenChange={setPaletteOpen} />
      <ShortcutsOverlay open={shortcutsOpen} onOpenChange={setShortcutsOpen} />
    </div>
  );
}
