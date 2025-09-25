# Data Models
## DocumentBundleRun
**Purpose:** Represents a deterministic execution that produces the NAB-aligned artefact bundle, tying together inputs, validations, outputs, and audit trails.

**Key Attributes:**
- `id`: `UUID`
- `seedHash`: `string`
- `status`: `BundleStatus`
- `triggeredBy`: `ActorRef`
- `startedAt`: `Date`
- `completedAt`: `Date | null`
- `manifestId`: `UUID`
- `runParameters`: `RunParameters`

```typescript
export interface DocumentBundleRun {
  id: string;
  seedHash: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'blocked';
  triggeredBy: ActorRef;
  startedAt: Date;
  completedAt: Date | null;
  manifestId: string;
  runParameters: RunParameters;
}
```

**Relationships:** Belongs to a `ConfigurationSet`, owns `Manifest`, `DocumentArtefact`, `ValidationResult`, and `AuditLogEntry` collections.

## ConfigurationSet
**Purpose:** Captures normalized seed inputs, selected accounts, date ranges, and rendering options defining how a bundle run should execute.

```typescript
export interface ConfigurationSet {
  id: string;
  seedSource: 'uploaded' | 'fixture' | 'api';
  accounts: AccountConfig[];
  renderOptions: RenderOptions;
  createdBy: ActorRef;
}
```

## ApplicantProfile
```typescript
export interface ApplicantProfile {
  id: string;
  fullName: string;
  dateOfBirth: Date;
  primaryEmployerId: string | null;
  addresses: Address[];
}
```

## FinancialAccount
```typescript
export interface FinancialAccount {
  id: string;
  applicantId: string;
  institution: BankInstitution;
  accountNumberMasked: string;
  currency: string;
}
```

## AccountSnapshot
```typescript
export interface AccountSnapshot {
  id: string;
  bundleRunId: string;
  accountId: string;
  period: DateRange;
  openingBalance: number;
  closingBalance: number;
}
```

## TransactionRecord
```typescript
export interface TransactionRecord {
  id: string;
  snapshotId: string;
  merchantId: string | null;
  amount: number;
  occurredAt: Date;
  description: string;
}
```

## MerchantProfile
```typescript
export interface MerchantProfile {
  id: string;
  name: string;
  placesId: string | null;
  category: string;
  address: Address;
}
```

## PayslipRecord
```typescript
export interface PayslipRecord {
  id: string;
  bundleRunId: string;
  employerId: string;
  period: DateRange;
  grossPay: number;
  netPay: number;
  taxWithheld: number;
  superContribution: number;
}
```

## EmployerProfile
```typescript
export interface EmployerProfile {
  id: string;
  legalName: string;
  abn: string;
  address: Address;
  placesId: string | null;
}
```

## DocumentArtefact
```typescript
export interface DocumentArtefact {
  id: string;
  bundleRunId: string;
  type: 'bank_statement' | 'payslip' | 'proof_of_balance';
  storageKey: string;
  checksum: string;
  renderVersion: string;
}
```

## Manifest
```typescript
export interface Manifest {
  id: string;
  bundleRunId: string;
  hash: string;
  signature: string;
  signingKeyId: string;
  createdAt: Date;
  metadata: ManifestMetadata;
}
```

## ValidationResult
```typescript
export interface ValidationResult {
  id: string;
  bundleRunId: string;
  ruleCode: string;
  severity: 'info' | 'warning' | 'error';
  status: 'pass' | 'fail' | 'blocked';
  details: ValidationDetails;
}
```

## AuditLogEntry
```typescript
export interface AuditLogEntry {
  id: string;
  bundleRunId: string;
  actor: ActorRef;
  action: string;
  timestamp: Date;
  payload: Record<string, unknown>;
}
```
