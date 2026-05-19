import * as React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Trash2, Upload, Image as ImageIcon } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api/client';
import { ApiError } from '@/lib/api/errors';
import type { ProductImage } from '../api/types';

interface Props {
  productId: number | null | undefined;
}

const MAX_DIMENSION = 1600;
const JPEG_QUALITY = 0.85;
const MAX_BYTES_AFTER = 2 * 1024 * 1024; // 2 MB target after resize

/**
 * Client-side resize: scales image so longest edge <= MAX_DIMENSION,
 * re-encodes as JPEG. Returns the original file untouched if it's
 * already small enough or not a raster format we can decode.
 */
async function resizeImage(file: File): Promise<File> {
  if (!file.type.startsWith('image/') || file.type === 'image/svg+xml') return file;
  let bitmap: ImageBitmap;
  try {
    bitmap = await createImageBitmap(file);
  } catch {
    return file;
  }
  const { width, height } = bitmap;
  const longest = Math.max(width, height);
  const needsResize = longest > MAX_DIMENSION || file.size > MAX_BYTES_AFTER;
  if (!needsResize) {
    bitmap.close?.();
    return file;
  }
  const scale = Math.min(1, MAX_DIMENSION / longest);
  const w = Math.round(width * scale);
  const h = Math.round(height * scale);
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    bitmap.close?.();
    return file;
  }
  ctx.drawImage(bitmap, 0, 0, w, h);
  bitmap.close?.();
  const blob: Blob | null = await new Promise((resolve) =>
    canvas.toBlob(resolve, 'image/jpeg', JPEG_QUALITY),
  );
  if (!blob) return file;
  const base = file.name.replace(/\.[^.]+$/, '');
  return new File([blob], `${base}.jpg`, { type: 'image/jpeg', lastModified: Date.now() });
}

export function ProductMediaTab({ productId }: Props) {
  const qc = useQueryClient();
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [queue, setQueue] = React.useState<
    Array<{ name: string; status: 'pending' | 'uploading' | 'done' | 'error'; error?: string }>
  >([]);

  const enabled = typeof productId === 'number' && productId > 0;

  const listQuery = useQuery<ProductImage[], Error>({
    queryKey: ['catalog', 'images', { product: productId }],
    enabled,
    queryFn: async () => {
      const res = await apiClient.get<{ results?: ProductImage[] } | ProductImage[]>(
        `/catalog/images/?product=${productId}`,
      );
      return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
    },
  });

  const uploadMut = useMutation<ProductImage, Error, File>({
    mutationFn: async (file) => {
      const fd = new FormData();
      fd.append('product', String(productId));
      fd.append('image', file, file.name);
      fd.append('position', String(listQuery.data?.length ?? 0));
      fd.append('alt', '');
      const res = await apiClient.post<ProductImage>(`/catalog/images/`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    },
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['catalog', 'images', { product: productId }] }),
  });

  const deleteMut = useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.delete(`/catalog/images/${id}/`);
    },
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ['catalog', 'images', { product: productId }] }),
  });

  const handleFiles = async (files: FileList | null) => {
    if (!enabled || !files || files.length === 0) return;
    const items = Array.from(files);
    setQueue(items.map((f) => ({ name: f.name, status: 'pending' as const })));
    for (let i = 0; i < items.length; i += 1) {
      setQueue((q) => q.map((row, idx) => (idx === i ? { ...row, status: 'uploading' } : row)));
      try {
        const resized = await resizeImage(items[i]);
        await uploadMut.mutateAsync(resized);
        setQueue((q) => q.map((row, idx) => (idx === i ? { ...row, status: 'done' } : row)));
      } catch (err) {
        const msg = err instanceof ApiError ? err.message : (err as Error).message;
        setQueue((q) =>
          q.map((row, idx) => (idx === i ? { ...row, status: 'error', error: msg } : row)),
        );
        toast.error(`Upload failed: ${items[i].name} — ${msg}`);
      }
    }
    toast.success('Image upload complete.');
    setTimeout(() => setQueue([]), 2000);
    if (inputRef.current) inputRef.current.value = '';
  };

  if (!enabled) {
    return (
      <div className="rounded-md border border-dashed bg-muted/40 p-4 text-sm text-muted-foreground">
        Save this product first, then re-open to upload images.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div
        className="flex flex-col items-center justify-center rounded-md border border-dashed bg-muted/40 p-6 text-center"
        onDragOver={(e) => {
          e.preventDefault();
        }}
        onDrop={(e) => {
          e.preventDefault();
          void handleFiles(e.dataTransfer.files);
        }}
      >
        <ImageIcon className="mb-2 h-6 w-6 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">
          Drag &amp; drop images here, or click to choose. Large images are auto-resized to{' '}
          {MAX_DIMENSION}px before upload.
        </p>
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          onChange={(e) => void handleFiles(e.target.files)}
        />
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="mt-3"
          onClick={() => inputRef.current?.click()}
        >
          <Upload className="mr-1 h-4 w-4" />
          Choose images
        </Button>
      </div>

      {queue.length > 0 && (
        <ul className="space-y-1 text-xs">
          {queue.map((row, idx) => (
            <li key={idx} className="flex items-center justify-between">
              <span className="truncate">{row.name}</span>
              <span
                className={
                  row.status === 'done'
                    ? 'text-emerald-600'
                    : row.status === 'error'
                      ? 'text-red-600'
                      : 'text-muted-foreground'
                }
              >
                {row.status === 'error' ? row.error : row.status}
              </span>
            </li>
          ))}
        </ul>
      )}

      {listQuery.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : listQuery.isError ? (
        <p className="text-sm text-red-600">Failed to load images.</p>
      ) : (listQuery.data ?? []).length === 0 ? (
        <p className="text-sm text-muted-foreground">No images yet.</p>
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
          {(listQuery.data ?? []).map((img) => (
            <div key={img.id} className="group relative overflow-hidden rounded-md border bg-card">
              <img
                src={img.image}
                alt={img.alt || ''}
                className="aspect-square w-full object-cover"
                loading="lazy"
              />
              <div className="flex items-center justify-between p-1 text-xs">
                <span className="truncate text-muted-foreground">pos {img.position}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-6 px-1 text-red-600 hover:text-red-700"
                  disabled={deleteMut.isPending}
                  onClick={async () => {
                    if (!confirm('Delete this image?')) return;
                    try {
                      await deleteMut.mutateAsync(img.id);
                      toast.success('Image deleted.');
                    } catch (err) {
                      toast.error(err instanceof ApiError ? err.message : 'Delete failed.');
                    }
                  }}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
