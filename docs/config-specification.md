# Configuration Specification: `config.ts`

This document provides a detailed specification for the `config.ts` file, which holds global constants for the Financial Document Generator application.

## 1. Overview

The `config.ts` file centralizes all static configuration variables used throughout the Financial Document Generator application. This configuration supports the generation of realistic bank statements and payslips by providing default values, bank-specific information, validation rules, and UI settings from a single source.

> **Note:** This repository maintains the functional specification only. The concrete `config.ts` implementation lives in the downstream Financial Document Generator codebase; there is no `config.ts` checked into this documentation repo.

The configuration is exported as a typed TypeScript object, ensuring type safety across the codebase and supporting key application features including:

- **Bank Statement Generation**: Default BSB numbers, bank information, and transaction categories ([see `docs/Bank_Statement_Comprehensive_Guide_Combined.md`](docs/Bank_Statement_Comprehensive_Guide_Combined.md))
- **Payslip Generation**: Pay frequency mappings and validation rules ([see `docs/Payslip_Streamlined_Documentation.md`](docs/Payslip_Streamlined_Documentation.md))
- **PDF Generation**: Document formatting and layout options ([see `docs/Puppeteer_PDF_Generation_Guide.md`](docs/Puppeteer_PDF_Generation_Guide.md))
- **Location Services**: Google Places API integration for realistic merchant locations ([see `docs/Google_Places_API_Complete_Integration.md`](docs/Google_Places_API_Complete_Integration.md))

## 2. Configuration Object: `CONFIG`

The `CONFIG` object contains the following top-level properties:

| Key               | Type   | Description                                             |
| ----------------- | ------ | ------------------------------------------------------- |
| `DEFAULT_BSB`     | String | The default BSB number for Australian banks.            |
| `BANK_INFO`       | Object | Contains static details about the banking institution.  |
| `MERCHANTS`       | Array  | A list of default merchant names for transaction data.  |
| `PAY_FREQUENCIES` | Object | Maps pay frequency labels to their yearly occurrences.    |
| `ACCOUNT_TYPES`   | Array  | A list of available account type strings.               |
| `PDF_OPTIONS`     | Object | Configuration settings for PDF generation.              |
| `VALIDATION`      | Object | Defines validation rules for user input forms.          |
| `UI`              | Object | Constants that control user interface behavior and format. |

---

### 2.1 `DEFAULT_BSB`

The default Bank-State-Branch (BSB) number used for pre-filling relevant fields in bank statement generation.

-   **Type:** `String`
-   **Example:** `'082-465'` (NAB Bank BSB)
-   **Related Documentation:** [Bank Statement Generation Rules](docs/Bank_Statement_Comprehensive_Guide_Combined.md#bank-specific-details)

### 2.2 `BANK_INFO`

An object containing static information about the bank, used for generating bank statements and payslips.

| Property        | Type   | Description                   | Example                             |
| --------------- | ------ | ----------------------------- | ----------------------------------- |
| `name`          | String | Full legal name of the bank.  | `'National Australia Bank Limited'` |
| `abn`           | String | Australian Business Number.   | `'12 004 044 937'`                  |
| `afsl`          | String | Australian Financial Services Licence. | `'230686'`                          |
| `creditLicence` | String | Australian Credit Licence.    | `'230686'`                          |
| **Related Documentation:** [Bank-Specific Details](docs/Bank_Statement_Comprehensive_Guide_Combined.md#bank-specific-details)

### 2.3 `MERCHANTS`

A list of predefined merchant names used to generate random transaction descriptions in bank statements.

-   **Type:** `Array<String>`
-   **Example:** `['COLES BONDI JUNCTION', 'UBER TRIP', 'BP CONNECT SYDNEY CBD', 'STARBUCKS BONDI', 'ANYTIME FITNESS SURRY HILLS']`
-   **Related Documentation:** [Transaction Categories](docs/Bank_Statement_Comprehensive_Guide_Combined.md#transaction-categories) and [Merchant Localization](docs/Google_Places_API_Complete_Integration.md#transaction-generation-integration)

### 2.4 `PAY_FREQUENCIES`

An object mapping pay frequency labels to the number of pay periods in a year. This is used for payroll calculations in payslip generation and bank statement income entries.

| Property      | Type   | Description                  |
| ------------- | ------ | ---------------------------- |
| `weekly`      | Number | 52 pay periods per year.     |
| `fortnightly` | Number | 26 pay periods per year.     |
| `monthly`     | Number | 12 pay periods per year.     |
| **Related Documentation:** [Payroll Details](docs/Payslip_Streamlined_Documentation.md#payroll-details) and [Income Transactions](docs/Bank_Statement_Comprehensive_Guide_Combined.md#income-transactions)

### 2.5 `ACCOUNT_TYPES`

A list of default account types available for selection in the UI, used for bank statement generation.

-   **Type:** `Array<String>`
-   **Example:** `['Transaction Account', 'Savings Account', 'Classic Banking', 'iSaver', 'Smart Access', 'Low Rate MC']`
-   **Related Documentation:** [Bank-Specific Details](docs/Bank_Statement_Comprehensive_Guide_Combined.md#bank-specific-details)

### 2.6 `PDF_OPTIONS`

An object containing settings for the PDF generation library (Puppeteer), used for generating bank statements and payslips.

| Property          | Type   | Description                                           | Example                                                 |
| ----------------- | ------ | ----------------------------------------------------- | ------------------------------------------------------- |
| `format`          | String | The paper format for the generated PDF.               | `'A4'`                                                  |
| `printBackground` | Boolean| Whether to print background graphics.                 | `true`                                                  |
| `margin`          | Object | Page margin settings for A4 format.                   | `{ top: '20mm', right: '15mm', bottom: '20mm', left: '15mm' }` |
| `preferCSSPageSize` | Boolean| Use CSS page size over format property.             | `true`                                                  |
| **Related Documentation:** [A4 Document Generation](docs/Puppeteer_PDF_Generation_Guide.md#a4-document-generation)

### 2.7 `VALIDATION`

An object defining rules for validating user input in forms for bank statement and payslip generation.

| Property           | Type   | Description                                    | Example    |
| ------------------ | ------ | ---------------------------------------------- | ---------- |
| `maxNameLength`    | Number | Maximum character length for name fields.      | `100`      |
| `maxAddressLength` | Number | Maximum character length for address fields.   | `500`      |
| `minBalance`       | Number | The minimum allowable account balance.         | `-100000`  |
| `maxBalance`       | Number | The maximum allowable account balance.         | `1000000`  |
| `maxIncome`        | Number | The maximum allowable income value.            | `10000000` |
| `abnFormat`        | String | Expected format for ABN validation.            | `'XX XXX XXX XXX'` |
| `bsbFormat`        | String | Expected format for BSB validation.            | `'XXX-XXX'` |
| **Related Documentation:** [Validation Rules](docs/Payslip_Streamlined_Documentation.md#validation-rules) and [User Input Specification](docs/Bank_Statement_Comprehensive_Guide_Combined.md#user-input-specification)

### 2.8 `UI`

An object containing constants that control the behavior and appearance of the user interface for the Financial Document Generator.

| Property         | Type   | Description                                           | Example    |
| ---------------- | ------ | ----------------------------------------------------- | ---------- |
| `maxBatchSize`   | Number | Maximum number of documents in a single batch generation. | `10`       |
| `defaultBatchCount` | Number | Default number of documents to generate in a batch. | `3`        |
| `dateFormat`     | String | The locale string for formatting dates (Australian format). | `'en-AU'`  |
| `currencyFormat` | String | The locale string for formatting currency (Australian dollars). | `'en-AU'`  |
| `maxPayslips`   | Number | Maximum number of payslips to generate in a series. | `5`        |
| `defaultStatementDays` | Number | Default number of days for statement period.       | `90`       |
| **Related Documentation:** [User Input Specification](docs/Bank_Statement_Comprehensive_Guide_Combined.md#user-input-specification) and [Configuration Options](docs/Payslip_Streamlined_Documentation.md#configuration-options)

## 3. Export Mechanism

The `CONFIG` object is exported as the default export from the `config.ts` module, making it consumable by other TypeScript files using standard ES module `import` statements. This configuration is used throughout the Financial Document Generator application for:

- **Bank Statement Generation**: Providing default values for BSB numbers, bank information, and merchant data
- **Payslip Generation**: Supplying pay frequency mappings and validation rules
- **PDF Generation**: Configuring Puppeteer options for document output
- **Form Validation**: Enforcing input constraints across the application
- **UI Components**: Setting default values and formatting options

**Example Usage:**
```typescript
import CONFIG from './config';

// Access bank information for statement generation
const bankName = CONFIG.BANK_INFO.name;
const defaultBSB = CONFIG.DEFAULT_BSB;

// Use PDF options for document generation
const pdfConfig = CONFIG.PDF_OPTIONS;

// Validate user input against configured limits
if (income > CONFIG.VALIDATION.maxIncome) {
  // Handle validation error
}
```

**Downstream Implementation Touchpoints (maintained outside this repository):**
- Transaction generation services reference merchant/category constants when building statements.
- Payslip form components consume pay-frequency and validation settings to ensure alignment with statements.
- PDF rendering utilities apply the `PDF_OPTIONS` block for layout configuration.
- Geocoding integration layers re-use location-related configuration to stay consistent with Places guidance.
