import * as React from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { PageHeader } from '@/components/shared/page-header';
import { ApiError } from '@/lib/api/errors';
import { useImportProducts, type ImportResponse } from '../api/hooks';
import { useCanImport } from '../lib/use-permission';
import { t } from '../lib/i18n';

export function ImportPage() {
  const canImport = useCanImport();
  const [file, setFile] = React.useState<File | null>(null);
  const [dryRun, setDryRun] = React.useState(true);
  const [result, setResult] = React.useState<ImportResponse | null>(null);
  const importMut = useImportProducts();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      toast.error(t('import.no_file'));
      return;
    }
    try {
      const data = await importMut.mutateAsync({ file, dryRun });
      setResult(data);
      toast.success(
        data.committed
          ? `Imported ${data.created} of ${data.total} rows.`
          : `Dry run: ${data.valid} valid / ${data.total} rows.`,
      );
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Import failed.');
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader title={t('import.title')} description={t('import.subtitle')} />
      <form onSubmit={onSubmit} className="space-y-4 rounded border bg-card p-4">
        <div className="space-y-1.5">
          <Label htmlFor="csv">{t('import.choose_file')}</Label>
          <Input
            id="csv"
            type="file"
            accept=".csv,text/csv"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            disabled={!canImport || importMut.isPending}
          />
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={dryRun}
            onChange={(e) => setDryRun(e.target.checked)}
            disabled={importMut.isPending}
          />
          {t('import.dry_run')}
        </label>
        <Button type="submit" disabled={!canImport || importMut.isPending || !file}>
          {importMut.isPending ? '…' : t('import.run')}
        </Button>
      </form>

      {result && (
        <div className="rounded border bg-card p-4">
          <h3 className="mb-2 text-sm font-semibold">Result</h3>
          <dl className="grid grid-cols-4 gap-3 text-sm">
            <Stat label={t('import.result.total')} value={result.total} />
            <Stat label={t('import.result.valid')} value={result.valid} />
            <Stat label={t('import.result.created')} value={result.created} />
            <Stat label={t('import.result.errors')} value={result.errors.length} />
          </dl>
          {result.errors.length > 0 && (
            <div className="mt-3 max-h-64 overflow-auto rounded border bg-muted/30 p-2 text-xs">
              <table className="w-full">
                <thead>
                  <tr className="text-left">
                    <th className="pr-2">Row</th>
                    <th className="pr-2">Error</th>
                  </tr>
                </thead>
                <tbody>
                  {result.errors.map((err) => (
                    <tr key={err.row}>
                      <td className="pr-2 font-mono">{err.row}</td>
                      <td className="pr-2 text-destructive">{err.error}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="text-xl font-semibold">{value}</dd>
    </div>
  );
}
