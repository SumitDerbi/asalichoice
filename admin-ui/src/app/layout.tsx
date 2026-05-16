import * as React from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { ChevronRight, LogOut, Menu, Moon, Search, Sun } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/lib/auth/store';
import { currentBranch, useBranchStore } from '@/lib/branch/store';
import { useThemeStore } from '@/lib/theme/store';
import { CommandPalette } from './command-palette';
import { ShortcutsOverlay } from './shortcuts-overlay';
import { listModulesByCategory, type ModuleDef } from './module-registry';

const APP_NAME = import.meta.env.VITE_APP_NAME ?? 'AsliChoice Admin';
const APP_VERSION = import.meta.env.VITE_APP_VERSION ?? '0.1.0';

export function AppShell() {
  const [paletteOpen, setPaletteOpen] = React.useState(false);
  const [shortcutsOpen, setShortcutsOpen] = React.useState(false);
  const [sidebarOpen, setSidebarOpen] = React.useState(true);
  const navigate = useNavigate();
  const logout = useAuthStore((s) => s.logout);
  const user = useAuthStore((s) => s.user);
  const toggleTheme = useThemeStore((s) => s.toggleTheme);
  const theme = useThemeStore((s) => s.theme);
  const groups = listModulesByCategory();

  // Track a "g" prefix for `g d` / `g m` navigation shortcuts.
  const goPrefix = React.useRef(false);

  React.useEffect(() => {
    function inField(t: EventTarget | null): boolean {
      const el = t as HTMLElement | null;
      return !!el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable);
    }

    function onKey(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPaletteOpen((v) => !v);
        return;
      }
      if (inField(e.target)) return;

      if (e.key === '?') {
        e.preventDefault();
        setShortcutsOpen((v) => !v);
        return;
      }
      if (e.key === '[') {
        e.preventDefault();
        setSidebarOpen((v) => !v);
        return;
      }
      if (e.key === 't' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        e.preventDefault();
        toggleTheme();
        return;
      }
      if (e.key === 'g' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        goPrefix.current = true;
        window.setTimeout(() => {
          goPrefix.current = false;
        }, 800);
        return;
      }
      if (goPrefix.current) {
        if (e.key === 'd') {
          e.preventDefault();
          navigate('/');
        } else if (e.key === 'm') {
          e.preventDefault();
          navigate('/masters');
        }
        goPrefix.current = false;
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [navigate, toggleTheme]);

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
        <nav className="flex-1 overflow-y-auto p-2">
          {groups.map(({ category, modules }) => (
            <div key={category} className="mb-3">
              {sidebarOpen && (
                <div className="px-3 py-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {category}
                </div>
              )}
              <div className="space-y-1">
                {modules.flatMap((m: ModuleDef) =>
                  (m.nav ?? []).map((item) => (
                    <NavLink
                      key={`${m.id}-${item.to}`}
                      to={item.to}
                      end={item.end}
                      className={({ isActive }) =>
                        cn(
                          'flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
                          isActive
                            ? 'bg-accent text-accent-foreground'
                            : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground',
                        )
                      }
                    >
                      <m.icon className="h-4 w-4 shrink-0" aria-hidden="true" />
                      {sidebarOpen && <span>{item.label}</span>}
                    </NavLink>
                  )),
                )}
              </div>
            </div>
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
          <Breadcrumbs />
          <div className="ml-auto flex items-center gap-2">
            <Button
              variant="outline"
              className="h-9 min-w-[14rem] justify-start text-muted-foreground"
              onClick={() => setPaletteOpen(true)}
              aria-label="Open command palette"
            >
              <Search className="mr-2 h-4 w-4" aria-hidden="true" />
              <span className="flex-1 text-left">Search or run command…</span>
              <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-[10px]">
                Ctrl K
              </kbd>
            </Button>
            <BranchSwitcher />
            <Button
              variant="ghost"
              size="icon"
              aria-label="Toggle theme"
              onClick={() => toggleTheme()}
            >
              {theme === 'dark' ? (
                <Sun className="h-4 w-4" aria-hidden="true" />
              ) : (
                <Moon className="h-4 w-4" aria-hidden="true" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              aria-label="Show keyboard shortcuts"
              onClick={() => setShortcutsOpen(true)}
            >
              ?
            </Button>
            {user && (
              <span className="hidden text-sm text-muted-foreground sm:inline">
                {user.display_name || user.email}
              </span>
            )}
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

function Breadcrumbs() {
  const location = useLocation();
  const segments = location.pathname.split('/').filter(Boolean);
  if (segments.length === 0) {
    return <span className="text-sm font-medium">Dashboard</span>;
  }
  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-sm">
      <NavLink to="/" className="text-muted-foreground hover:text-foreground">
        Home
      </NavLink>
      {segments.map((seg, i) => {
        const to = '/' + segments.slice(0, i + 1).join('/');
        const isLast = i === segments.length - 1;
        return (
          <React.Fragment key={to}>
            <ChevronRight className="h-3 w-3 text-muted-foreground" aria-hidden="true" />
            {isLast ? (
              <span className="font-medium capitalize">{seg}</span>
            ) : (
              <NavLink to={to} className="capitalize text-muted-foreground hover:text-foreground">
                {seg}
              </NavLink>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}

function BranchSwitcher() {
  const branches = useBranchStore((s) => s.branches);
  const setCurrentBranchId = useBranchStore((s) => s.setCurrentBranchId);
  const active = useBranchStore(currentBranch);
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" aria-label="Switch branch">
          {active ? active.code : 'No branch'}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Branches</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {branches.map((b) => (
          <DropdownMenuItem
            key={b.id}
            onSelect={() => setCurrentBranchId(b.id)}
            className={cn(b.id === active?.id && 'bg-accent/50 font-medium')}
          >
            <span className="mr-2 inline-block min-w-[2.5rem] text-xs uppercase tracking-wider text-muted-foreground">
              {b.code}
            </span>
            {b.name}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
