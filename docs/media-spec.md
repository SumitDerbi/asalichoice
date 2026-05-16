# Media Spec

Authoritative size/weight constraints for every kind of file the platform stores. Modules MUST enforce these at the API boundary; the admin UI SHOULD validate client-side and surface friendly errors before upload.

All raster outputs prefer **WebP** with a **JPEG** fallback. PNG only when transparency is required.

## Images

| Use               | Dimensions  | Format            | Max size | Notes                                |
| ----------------- | ----------- | ----------------- | -------- | ------------------------------------ |
| Product thumbnail | 600 × 600   | JPEG / WebP       | 150 KB   | Used in lists, cart, search. Square. |
| Product gallery   | 1200 × 1200 | JPEG / WebP       | 500 KB   | Up to 8 per product. Square.         |
| Banner / hero     | 1920 × 640  | JPEG / WebP       | 600 KB   | Storefront banners. 3:1 ratio.       |
| Brand logo        | 512 × 512   | PNG (transparent) | 100 KB   | Square, transparent background.      |
| Avatar            | 256 × 256   | JPEG / WebP / PNG | 50 KB    | Square, auto-cropped.                |

## Documents

| Use                      | Format              | Max size | Notes                                                   |
| ------------------------ | ------------------- | -------- | ------------------------------------------------------- |
| Invoice / GRN PDF        | PDF                 | 5 MB     | Generated server-side, never uploaded.                  |
| Customer document upload | PDF / JPEG / PNG    | 10 MB    | Configurable per category via site settings (plan 013). |
| Bulk import CSV          | CSV (UTF-8, no BOM) | 20 MB    | Validated row-by-row with line-numbered errors.         |

## Storage layout

```
media/
  products/<id>/thumb.webp
  products/<id>/gallery/<n>.webp
  brands/<id>/logo.png
  banners/<slug>.webp
  avatars/<user-id>.webp
  documents/<category>/<id>/<filename>
```

## Validation

- **Server**: validators in `apps/core/validators.py` enforce dimensions + max size per category. Reject with `API-400` envelope and `details.field` = `image`/`document`.
- **Client**: a thin wrapper around `<input type="file">` reads `File.size`, decodes the image for dimension checks, and rejects before upload. Surfaced through the standard form-error pipeline (see [UI forms](ui/forms.md)).
