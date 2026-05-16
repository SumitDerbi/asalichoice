import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Eye, EyeOff } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { PageHeader } from '@/components/shared/page-header';
import { Button } from '@/components/ui/button';

type Resource =
  | 'system-settings'
  | 'feature-toggles'
  | 'integration-keys'
  | 'social-links'
  | 'contact-info';

interface TabDef {
  key: Resource;
  label: string;
  description: string;
}

const TABS: TabDef[] = [
  {
    key: 'system-settings',
    label: 'Settings',
    description: 'Key/value runtime configuration. Secrets are masked.',
  },
  {
    key: 'feature-toggles',
    label: 'Feature toggles',
    description: 'On/off flags with optional rollout %.',
  },
  {
    key: 'integration-keys',
    label: 'Integration keys',
    description: 'Encrypted credentials per provider. Reveal is audit-logged.',
  },
  { key: 'social-links', label: 'Social links', description: 'Storefront social URLs.' },
  { key: 'contact-info', label: 'Contact info', description: 'Business contact rows.' },
];

interface ApiListResponse<T> {
  results?: T[];
  count?: number;
}

interface SettingRow {
  id: number;
  key: string;
  value_json: unknown;
  scope: string;
  is_secret: boolean;
  description: string;
}

interface ToggleRow {
  id: number;
  key: string;
  enabled: boolean;
  rollout_percentage: number;
  description: string;
}

interface IntegrationRow {
  id: number;
  provider: string;
  key_name: string;
  is_active: boolean;
  value: string;
  description: string;
}

interface SocialRow {
  id: number;
  platform: string;
  url: string;
  is_active: boolean;
}

interface ContactRow {
  id: number;
  label: string;
  email: string;
  phone: string;
  address: string;
  is_primary: boolean;
}

function useResource<T>(resource: Resource) {
  return useQuery<T[]>({
    queryKey: ['system-settings', resource],
    queryFn: async () => {
      const res = await apiClient.get<ApiListResponse<T> | T[]>(`/${resource}/`);
      const body = res.data;
      if (Array.isArray(body)) return body;
      return body.results ?? [];
    },
  });
}

function SettingsTab() {
  const { data, isLoading, isError, error } = useResource<SettingRow>('system-settings');
  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (isError) return <p className="text-sm text-destructive">{(error as Error).message}</p>;
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b text-left text-xs uppercase text-muted-foreground">
          <th className="py-2">Key</th>
          <th className="py-2">Scope</th>
          <th className="py-2">Value</th>
          <th className="py-2">Description</th>
        </tr>
      </thead>
      <tbody>
        {(data ?? []).map((row) => (
          <tr key={row.id} className="border-b">
            <td className="py-2 font-mono text-xs">{row.key}</td>
            <td className="py-2">{row.scope}</td>
            <td className="py-2 font-mono text-xs">
              {row.is_secret ? '••••' : JSON.stringify(row.value_json)}
            </td>
            <td className="py-2 text-muted-foreground">{row.description}</td>
          </tr>
        ))}
        {(data ?? []).length === 0 && (
          <tr>
            <td colSpan={4} className="py-6 text-center text-muted-foreground">
              No settings yet — run <code>seed_settings</code>.
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

function TogglesTab() {
  const { data, isLoading, isError, error } = useResource<ToggleRow>('feature-toggles');
  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (isError) return <p className="text-sm text-destructive">{(error as Error).message}</p>;
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b text-left text-xs uppercase text-muted-foreground">
          <th className="py-2">Key</th>
          <th className="py-2">State</th>
          <th className="py-2">Rollout %</th>
          <th className="py-2">Description</th>
        </tr>
      </thead>
      <tbody>
        {(data ?? []).map((row) => (
          <tr key={row.id} className="border-b">
            <td className="py-2 font-mono text-xs">{row.key}</td>
            <td className="py-2">{row.enabled ? 'on' : 'off'}</td>
            <td className="py-2">{row.rollout_percentage}%</td>
            <td className="py-2 text-muted-foreground">{row.description}</td>
          </tr>
        ))}
        {(data ?? []).length === 0 && (
          <tr>
            <td colSpan={4} className="py-6 text-center text-muted-foreground">
              No toggles yet.
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

function IntegrationRowItem({ row }: { row: IntegrationRow }) {
  const [revealed, setRevealed] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  return (
    <tr className="border-b">
      <td className="py-2 font-mono text-xs">{row.provider}</td>
      <td className="py-2 font-mono text-xs">{row.key_name}</td>
      <td className="py-2 font-mono text-xs">{revealed ?? row.value}</td>
      <td className="py-2">{row.is_active ? 'active' : 'inactive'}</td>
      <td className="py-2">
        {revealed ? (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => setRevealed(null)}
            aria-label="Hide secret"
          >
            <EyeOff className="h-4 w-4" />
          </Button>
        ) : (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={loading}
            onClick={async () => {
              setLoading(true);
              try {
                const res = await apiClient.get<IntegrationRow>(
                  `/integration-keys/${row.id}/reveal/`,
                );
                setRevealed(res.data.value);
              } finally {
                setLoading(false);
              }
            }}
            aria-label="Reveal secret"
          >
            <Eye className="h-4 w-4" />
          </Button>
        )}
      </td>
    </tr>
  );
}

function IntegrationsTab() {
  const { data, isLoading, isError, error } = useResource<IntegrationRow>('integration-keys');
  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (isError) return <p className="text-sm text-destructive">{(error as Error).message}</p>;
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b text-left text-xs uppercase text-muted-foreground">
          <th className="py-2">Provider</th>
          <th className="py-2">Key</th>
          <th className="py-2">Value</th>
          <th className="py-2">Status</th>
          <th className="py-2" />
        </tr>
      </thead>
      <tbody>
        {(data ?? []).map((row) => (
          <IntegrationRowItem key={row.id} row={row} />
        ))}
        {(data ?? []).length === 0 && (
          <tr>
            <td colSpan={5} className="py-6 text-center text-muted-foreground">
              No integration keys configured.
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

function SocialTab() {
  const { data, isLoading } = useResource<SocialRow>('social-links');
  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>;
  return (
    <ul className="space-y-2 text-sm">
      {(data ?? []).map((row) => (
        <li key={row.id} className="flex items-center justify-between border-b pb-2">
          <span className="font-medium capitalize">{row.platform}</span>
          <a
            className="text-primary hover:underline"
            href={row.url}
            target="_blank"
            rel="noreferrer"
          >
            {row.url}
          </a>
        </li>
      ))}
      {(data ?? []).length === 0 && (
        <li className="py-6 text-center text-muted-foreground">No social links yet.</li>
      )}
    </ul>
  );
}

function ContactTab() {
  const { data, isLoading } = useResource<ContactRow>('contact-info');
  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>;
  return (
    <ul className="space-y-3 text-sm">
      {(data ?? []).map((row) => (
        <li key={row.id} className="rounded border p-3">
          <div className="flex items-center justify-between">
            <span className="font-medium">{row.label}</span>
            {row.is_primary && (
              <span className="rounded bg-primary/10 px-2 py-0.5 text-xs text-primary">
                primary
              </span>
            )}
          </div>
          <div className="text-muted-foreground">{row.email}</div>
          <div className="text-muted-foreground">{row.phone}</div>
          <div className="whitespace-pre-line text-muted-foreground">{row.address}</div>
        </li>
      ))}
      {(data ?? []).length === 0 && (
        <li className="py-6 text-center text-muted-foreground">No contact rows yet.</li>
      )}
    </ul>
  );
}

export function SystemSettingsPage() {
  const [active, setActive] = useState<Resource>('system-settings');
  const tab = TABS.find((t) => t.key === active) ?? TABS[0];

  return (
    <div>
      <PageHeader
        title="System Settings"
        description="Site configuration, feature toggles, and integration credentials. Super-admin only."
      />
      <div className="flex flex-wrap gap-2 border-b pb-2">
        {TABS.map((t) => (
          <Button
            key={t.key}
            type="button"
            variant={t.key === active ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActive(t.key)}
          >
            {t.label}
          </Button>
        ))}
      </div>
      <p className="mt-4 text-sm text-muted-foreground">{tab.description}</p>
      <div className="mt-4">
        {active === 'system-settings' && <SettingsTab />}
        {active === 'feature-toggles' && <TogglesTab />}
        {active === 'integration-keys' && <IntegrationsTab />}
        {active === 'social-links' && <SocialTab />}
        {active === 'contact-info' && <ContactTab />}
      </div>
    </div>
  );
}
