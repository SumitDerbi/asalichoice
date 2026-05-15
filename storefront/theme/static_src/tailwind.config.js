/**
 * Tailwind CSS configuration for the AsliChoice storefront theme.
 *
 * Scans Wagtail templates (theme/, apps/website/, apps/blog/) and Python
 * files that contain class names (e.g. block.Meta.template references) so
 * Tailwind's JIT engine sees every utility used.
 *
 * Build:
 *   npm --prefix theme/static_src run tailwind:build   # one-shot, minified
 *   npm --prefix theme/static_src run tailwind:watch   # local dev
 *
 * Output: theme/static/theme/css/output.css
 */
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../templates/**/*.html",
    "../../apps/**/templates/**/*.html",
    "../../apps/**/*.py",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
    require("@tailwindcss/forms"),
  ],
};
