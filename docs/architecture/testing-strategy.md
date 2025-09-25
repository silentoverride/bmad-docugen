# Testing Strategy
```
E2E Tests
/        \
Integration Tests
/            \
Frontend Unit  Backend Unit
```

## Test Organization
```text
apps/admin/__tests__/
├─ components/
├─ hooks/
├─ fixtures/
└─ setup-tests.ts
```
```text
apps/api/tests/
├─ routes/
├─ services/
├─ repositories/
├─ fixtures/
└─ setup.ts
```
```text
tests/e2e/
├─ specs/
├─ fixtures/
├─ commands/
└─ setup.ts
```

## Test Examples
```typescript
import { render, screen } from '@testing-library/react';
import { BundleRunCard } from '@/components/runs/bundle-run-card';
import runFixture from '../fixtures/bundle-run.json';

describe('BundleRunCard', () => {
  it('shows run metadata and status badge', () => {
    const onSelect = vi.fn();
    render(<BundleRunCard run={runFixture} onSelect={onSelect} />);
    expect(screen.getByText(/Run #/)).toBeInTheDocument();
    screen.getByRole('button').click();
    expect(onSelect).toHaveBeenCalledWith(runFixture.id);
  });
});
```

```typescript
import { buildTestServer } from '../setup';
import configurationFixture from '../fixtures/configuration.json';

describe('POST /api/v1/bundles', () => {
  const app = buildTestServer();

  beforeAll(async () => {
    await app.ready();
    await app.prisma.configuration.create({ data: configurationFixture });
  });

  afterAll(() => app.close());

  it('queues a bundle run and returns 202', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/v1/bundles',
      headers: { authorization: 'Bearer test-token-with-bundle.write' },
      payload: { configurationId: configurationFixture.id },
    });

    expect(response.statusCode).toBe(202);
  });
});
```

```typescript
import { test, expect } from '@playwright/test';
import { runCli } from '../commands/cli';

test('operator launches bundle and reviewer approves', async ({ page }) => {
  await runCli(['bundle', 'launch', '--config', 'tests/fixtures/seeds/sample-applicant.json']);
  await page.goto('http://localhost:3000');
  await page.getByRole('button', { name: /Run #/ }).first().click();
  await expect(page.getByText('Validations')).toBeVisible();
  await page.getByRole('button', { name: 'Override validation' }).click();
  await page.getByLabel('Justification').fill('Manual review based on NAB docs');
  await page.getByRole('button', { name: 'Submit override' }).click();
  await expect(page.getByText('Run status: completed')).toBeVisible();
});
```
