# Frontend Architecture
## Component Architecture
```text
apps/admin/
├─ app/
│  ├─ (dashboard)/
│  │  ├─ layout.tsx
│  │  ├─ page.tsx
│  │  ├─ bundle/[bundleId]/
│  │  │  ├─ page.tsx
│  │  │  ├─ manifest/page.tsx
│  │  │  ├─ artefacts/page.tsx
│  │  │  ├─ _components/
│  │  │  └─ _hooks/
│  │  │  └─ loader.ts
│  │  ├─ configurations/
│  │  └─ telemetry/
│  ├─ api/
│  └─ (public)/login/page.tsx
├─ components/
├─ hooks/
├─ lib/
├─ providers/
├─ styles/
└─ tests/
```

```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StatusBadge } from '@/components/runs/status-badge';
import { formatDistanceToNow } from 'date-fns';
import type { components } from '@/types/openapi';

type DocumentBundleRun = components['schemas']['DocumentBundleRun'];

interface BundleRunCardProps {
  run: DocumentBundleRun;
  onSelect: (id: string) => void;
}

export function BundleRunCard({ run, onSelect }: BundleRunCardProps) {
  const completedAgo = run.completedAt
    ? formatDistanceToNow(new Date(run.completedAt), { addSuffix: true })
    : 'in progress';

  return (
    <Card
      role="button"
      tabIndex={0}
      onClick={() => onSelect(run.id)}
      onKeyDown={(event) => event.key === 'Enter' && onSelect(run.id)}
      className="transition hover:border-primary focus-visible:ring"
      aria-label={`Bundle ${run.id} status ${run.status}`}
    >
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-base font-semibold">Run #{run.id.slice(0, 8)}</CardTitle>
        <StatusBadge status={run.status} />
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground space-y-1">
        <p>Seed hash: {run.seedHash.slice(0, 12)}…</p>
        <p>Triggered by: {run.triggeredBy.id}</p>
        <p>Completed: {completedAgo}</p>
      </CardContent>
    </Card>
  );
}
```

## State Management Architecture
```typescript
import { QueryClient } from '@tanstack/react-query';
import { cookies } from 'next/headers';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
});

export const runQueryKeys = {
  all: ['runs'] as const,
  list: (filters?: Record<string, unknown>) => ['runs', filters] as const,
  detail: (bundleId: string) => ['runs', bundleId] as const,
  validations: (bundleId: string) => ['runs', bundleId, 'validations'] as const,
};

export function getSessionToken() {
  return cookies().get('docugen_session')?.value ?? null;
}
```

- TanStack Query owns all server state; session tokens live in HttpOnly cookies issued by NextAuth/Keycloak.
- WebSocket handlers optimistically update queries via `setQueryData`, invalidating specific keys if payloads appear stale.
- Query stale times differentiate telemetry (5s) from reference data (60s).
- UI filters persist in URL params; user prefs stored in scoped local store that never holds secrets.
- Playwright preloads query cache using fixtures to keep UI regression tests deterministic.
- Local React state is updated immutably with `setState` spread patterns—never mutate objects or arrays in place.

## Routing Architecture
```text
app/
├─ layout.tsx
├─ middleware.ts
├─ (public)/login/page.tsx
├─ (dashboard)/
│  ├─ layout.tsx
│  ├─ page.tsx
│  ├─ bundle/[bundleId]/
│  │  ├─ page.tsx
│  │  ├─ manifest/page.tsx
│  │  ├─ artefacts/page.tsx
│  │  ├─ _components/
│  │  └─ _hooks/
│  ├─ configurations/page.tsx
│  ├─ telemetry/page.tsx
│  └─ settings/tokens/page.tsx
```

```typescript
import { decodeJwtAndRoles } from '@/lib/auth-token';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { DashboardShell } from '@/components/layout/dashboard-shell';

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const token = cookies().get('docugen_session')?.value;
  if (!token) {
    redirect('/login?reason=session-expired');
  }

  const session = await decodeJwtAndRoles(token);

  if (!session.roles.includes('bundle.read')) {
    redirect('/login?reason=insufficient-permissions');
  }

  return <DashboardShell session={session}>{children}</DashboardShell>;
}
```

## Frontend Services Layer
```typescript
import ky from 'ky';
import mitt from 'mitt';
import { getSessionToken } from '@/lib/session-token';
import { toastEmitter } from '@/lib/toast-emitter';

export const apiEvents = mitt<{ unauthorized: void }>();

export const apiClient = ky.create({
  prefixUrl: process.env.NEXT_PUBLIC_BUNDLE_API_BASE ?? 'http://localhost:8080',
  timeout: 10_000,
  hooks: {
    beforeRequest: [async (request) => {
      const token = await getSessionToken();
      if (!token) return;
      request.headers.set('Authorization', `Bearer ${token}`);
      request.headers.set('Accept', 'application/json');
    }],
    afterResponse: [
      async (_request, _options, response) => {
        if (response.status === 401) {
          apiEvents.emit('unauthorized');
          return;
        }

        if (response.status === 429) {
          toastEmitter.emit('toast', {
            title: 'Throttled',
            description: 'Too many requests. Please retry shortly.',
            variant: 'destructive',
          });
        }

        if (response.status >= 500) {
          toastEmitter.emit('toast', {
            title: 'Server error',
            description: 'DocuGen backend encountered an issue. Check telemetry dashboards.',
            variant: 'destructive',
          });
        }
      },
    ],
  },
});
```

```typescript
import { apiClient } from '@/lib/api-client';
import type { operations } from '@/types/openapi';

type FetchBundleRunsResponse = operations['getBundles']['responses']['200']['content']['application/json'];

export async function fetchBundleRuns(params?: { status?: string; since?: string }) {
  const search = new URLSearchParams();
  if (params?.status) search.set('status', params.status);
  if (params?.since) search.set('since', params.since);

  return apiClient
    .get(`api/v1/bundles${search.toString() ? `?${search}` : ''}`)
    .json<FetchBundleRunsResponse>();
}

export async function triggerBundle(configurationId: string) {
  const response = await apiClient.post('api/v1/bundles', {
    json: { configurationId },
  });

  return response.json<operations['launchBundle']['responses']['202']['content']['application/json']>();
}
```
