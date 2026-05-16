import { http, HttpResponse } from 'msw';

const BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

interface AnyRow {
  id: number;
  is_active: boolean;
  [key: string]: unknown;
}

/**
 * In-memory store used by MSW handlers so tests can exercise the full
 * list/create/edit/deactivate flow without coupling to a fixture file.
 */
function makeStore(initial: AnyRow[]) {
  let nextId = initial.reduce((m, r) => Math.max(m, r.id), 0) + 1;
  let rows = initial.slice();

  return {
    list: (params: URLSearchParams) => {
      const includeInactive = params.get('include_inactive') === 'true';
      const search = params.get('search')?.toLowerCase() ?? '';
      let out = rows;
      if (!includeInactive) out = out.filter((r) => r.is_active);
      if (search) {
        out = out.filter((r) =>
          Object.values(r).some((v) => typeof v === 'string' && v.toLowerCase().includes(search)),
        );
      }
      return { count: out.length, next: null, previous: null, results: out };
    },
    create: (body: Record<string, unknown>) => {
      const row: AnyRow = {
        id: nextId++,
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        ...body,
      };
      rows = [...rows, row];
      return row;
    },
    update: (id: number, body: Record<string, unknown>) => {
      rows = rows.map((r) =>
        r.id === id ? { ...r, ...body, updated_at: new Date().toISOString() } : r,
      );
      return rows.find((r) => r.id === id);
    },
    deactivate: (id: number) => {
      rows = rows.map((r) => (r.id === id ? { ...r, is_active: false } : r));
    },
    reset: (next: AnyRow[]) => {
      rows = next.slice();
      nextId = rows.reduce((m, r) => Math.max(m, r.id), 0) + 1;
    },
  };
}

export const departmentsStore = makeStore([
  { id: 1, code: 'OPS', name: 'Operations', description: '', is_active: true },
  { id: 2, code: 'FIN', name: 'Finance', description: '', is_active: true },
]);

export const branchesStore = makeStore([
  { id: 1, code: 'HQ', name: 'Head Office', type: 'HQ', parent: null, is_active: true },
  { id: 2, code: 'WH1', name: 'Warehouse 1', type: 'WAREHOUSE', parent: null, is_active: true },
]);

function listHandler(endpoint: string, store: ReturnType<typeof makeStore>) {
  return http.get(`${BASE}/master/${endpoint}/`, ({ request }) => {
    const url = new URL(request.url);
    return HttpResponse.json(store.list(url.searchParams));
  });
}

function createHandler(endpoint: string, store: ReturnType<typeof makeStore>) {
  return http.post(`${BASE}/master/${endpoint}/`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    if (!body.code || !body.name) {
      return HttpResponse.json(
        {
          error: {
            code: 'MST-001',
            message: 'Validation failed.',
            details: { fields: { code: 'Code is required.' } },
          },
        },
        { status: 400 },
      );
    }
    return HttpResponse.json(store.create(body), { status: 201 });
  });
}

function patchHandler(endpoint: string, store: ReturnType<typeof makeStore>) {
  return http.patch(`${BASE}/master/${endpoint}/:id/`, async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    const updated = store.update(Number(params.id), body);
    if (!updated) return new HttpResponse(null, { status: 404 });
    return HttpResponse.json(updated);
  });
}

function deleteHandler(endpoint: string, store: ReturnType<typeof makeStore>) {
  return http.delete(`${BASE}/master/${endpoint}/:id/`, ({ params }) => {
    store.deactivate(Number(params.id));
    return new HttpResponse(null, { status: 204 });
  });
}

export const masterHandlers = [
  listHandler('departments', departmentsStore),
  createHandler('departments', departmentsStore),
  patchHandler('departments', departmentsStore),
  deleteHandler('departments', departmentsStore),

  listHandler('branches', branchesStore),
  createHandler('branches', branchesStore),
  patchHandler('branches', branchesStore),
  deleteHandler('branches', branchesStore),
];
