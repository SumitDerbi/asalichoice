import * as React from 'react';
import { Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Camera, CameraOff, ScanLine, Search, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api/client';
import { ApiError } from '@/lib/api/errors';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { PageHeader } from '@/components/shared/page-header';
import type { Barcode } from '../api/types';

interface ScanResult {
  at: number;
  value: string;
  ok: boolean;
  barcode?: Barcode;
  error?: string;
}

// Browser-native BarcodeDetector type (Chromium-only).
interface DetectedCode {
  rawValue: string;
}
interface BarcodeDetectorLike {
  detect(source: CanvasImageSource): Promise<DetectedCode[]>;
}
interface BarcodeDetectorCtor {
  new (options?: { formats?: string[] }): BarcodeDetectorLike;
  getSupportedFormats?(): Promise<string[]>;
}

const SUPPORTED_FORMATS = ['ean_13', 'upc_a', 'upc_e', 'code_128', 'code_39', 'qr_code'];

export function BarcodeScannerPage() {
  const [value, setValue] = React.useState('');
  const [history, setHistory] = React.useState<ScanResult[]>([]);
  const inputRef = React.useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const resolveMut = useMutation<Barcode, ApiError, string>({
    mutationFn: async (raw) => {
      const res = await apiClient.get<Barcode>(
        `/catalog/barcodes/resolve/?value=${encodeURIComponent(raw)}`,
      );
      return res.data;
    },
  });

  const handleLookup = React.useCallback(
    async (raw: string) => {
      const v = raw.trim();
      if (!v) return;
      try {
        const barcode = await resolveMut.mutateAsync(v);
        setHistory((h) => [{ at: Date.now(), value: v, ok: true, barcode }, ...h].slice(0, 20));
        toast.success(`Found: ${barcode.value}`);
      } catch (err) {
        const msg = err instanceof ApiError ? err.message : 'Lookup failed.';
        setHistory((h) => [{ at: Date.now(), value: v, ok: false, error: msg }, ...h].slice(0, 20));
        toast.error(msg);
      } finally {
        setValue('');
        inputRef.current?.focus();
      }
    },
    [resolveMut],
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Barcode scanner"
        description="Scan or type a barcode value to resolve it to its product or variant."
      />

      <div className="rounded-md border bg-card p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleLookup(value);
          }}
          className="flex items-end gap-2"
        >
          <div className="flex-1 space-y-1.5">
            <Label htmlFor="barcode-input">Barcode</Label>
            <Input
              id="barcode-input"
              ref={inputRef}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="Scan with a USB scanner or type, then press Enter…"
              autoComplete="off"
              autoFocus
            />
          </div>
          <Button type="submit" disabled={resolveMut.isPending || !value.trim()}>
            <Search className="mr-1 h-4 w-4" />
            Look up
          </Button>
        </form>
      </div>

      <CameraScanner onDetect={handleLookup} disabled={resolveMut.isPending} />

      <div>
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-sm font-medium">Recent scans</h2>
          {history.length > 0 ? (
            <Button variant="ghost" size="sm" onClick={() => setHistory([])}>
              <Trash2 className="mr-1 h-3.5 w-3.5" />
              Clear
            </Button>
          ) : null}
        </div>
        {history.length === 0 ? (
          <div className="rounded-md border border-dashed p-3 text-sm text-muted-foreground">
            No scans yet.
          </div>
        ) : (
          <ul className="divide-y rounded-md border">
            {history.map((s, i) => (
              <li
                key={`${s.at}-${i}`}
                className="flex items-center justify-between gap-3 px-3 py-2 text-sm"
              >
                <span className="flex-1">
                  <span className="font-mono">{s.value}</span>
                  {s.ok ? (
                    <span className="ml-2 text-xs text-emerald-600">{s.barcode?.type}</span>
                  ) : (
                    <span className="ml-2 text-xs text-rose-600">{s.error}</span>
                  )}
                </span>
                {s.ok && s.barcode ? (
                  <span className="flex gap-2 text-xs">
                    {s.barcode.product ? (
                      <Link
                        className="text-primary hover:underline"
                        to={`/catalog/products/${s.barcode.product}`}
                      >
                        Product #{s.barcode.product}
                      </Link>
                    ) : null}
                    {s.barcode.variant ? (
                      <Link className="text-primary hover:underline" to={`/catalog/variants`}>
                        Variant #{s.barcode.variant}
                      </Link>
                    ) : null}
                  </span>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

/**
 * Optional webcam scanner using the browser-native ``BarcodeDetector``.
 * Silently degrades to a hint when the API is unavailable.
 */
function CameraScanner({
  onDetect,
  disabled,
}: {
  onDetect: (value: string) => void;
  disabled: boolean;
}) {
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const streamRef = React.useRef<MediaStream | null>(null);
  const rafRef = React.useRef<number | null>(null);
  const detectorRef = React.useRef<BarcodeDetectorLike | null>(null);
  const lastSeen = React.useRef<{ value: string; at: number }>({ value: '', at: 0 });

  const [active, setActive] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const Ctor = (globalThis as unknown as { BarcodeDetector?: BarcodeDetectorCtor }).BarcodeDetector;
  const supported = typeof Ctor === 'function';

  const stop = React.useCallback(() => {
    if (rafRef.current != null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    if (streamRef.current) {
      for (const t of streamRef.current.getTracks()) t.stop();
      streamRef.current = null;
    }
    if (videoRef.current) videoRef.current.srcObject = null;
    setActive(false);
  }, []);

  React.useEffect(() => stop, [stop]);

  const start = React.useCallback(async () => {
    if (!supported || !Ctor) return;
    setError(null);
    try {
      detectorRef.current = new Ctor({ formats: SUPPORTED_FORMATS });
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setActive(true);
      const loop = async () => {
        if (!videoRef.current || !detectorRef.current) return;
        try {
          const codes = await detectorRef.current.detect(videoRef.current);
          if (codes && codes.length > 0) {
            const raw = codes[0].rawValue;
            // Debounce identical reads (1s window) to avoid spamming the API.
            const now = Date.now();
            if (raw && (raw !== lastSeen.current.value || now - lastSeen.current.at > 1500)) {
              lastSeen.current = { value: raw, at: now };
              onDetect(raw);
            }
          }
        } catch {
          // Ignore per-frame decode errors.
        }
        rafRef.current = requestAnimationFrame(loop);
      };
      rafRef.current = requestAnimationFrame(loop);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Camera unavailable.');
      stop();
    }
  }, [Ctor, supported, onDetect, stop]);

  if (!supported) {
    return (
      <div className="rounded-md border border-dashed bg-muted/30 p-3 text-xs text-muted-foreground">
        Camera scanning requires a browser with the BarcodeDetector API (Chromium-based). Use a USB
        scanner above instead.
      </div>
    );
  }

  return (
    <div className="rounded-md border bg-card p-4">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-sm font-medium">Camera</h2>
        {active ? (
          <Button variant="ghost" size="sm" onClick={stop}>
            <CameraOff className="mr-1 h-4 w-4" />
            Stop
          </Button>
        ) : (
          <Button variant="ghost" size="sm" onClick={start} disabled={disabled}>
            <Camera className="mr-1 h-4 w-4" />
            Start
          </Button>
        )}
      </div>
      <div className="relative aspect-video w-full max-w-md overflow-hidden rounded border bg-black">
        <video ref={videoRef} className="h-full w-full object-cover" muted playsInline>
          <track kind="captions" />
        </video>
        {active ? (
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
            <ScanLine className="h-8 w-8 text-emerald-300/80" />
          </div>
        ) : null}
      </div>
      {error ? <p className="mt-2 text-xs text-rose-600">{error}</p> : null}
    </div>
  );
}
