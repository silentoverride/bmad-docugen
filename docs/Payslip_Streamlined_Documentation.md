# Payslip Generator Documentation

## Related Documentation Navigation

### Primary Integration Documents
- **[Bank Statement Generator](Bank_Statement_Comprehensive_Guide_Combined.md)**: Core transaction rules and alignment requirements
- **[Google Places API Integration](Google_Places_API_Complete_Integration.md)**: Location-based transaction generation
- **[Puppeteer PDF Generation](Puppeteer_PDF_Generation_Guide.md)**: Document rendering and formatting
- **[Configuration Specification](config-specification.md)**: System configuration and validation rules

### Key Reference Sections
- [Transaction Rules Compliance](#transaction-rules-compliance)
- [Bank Statement Alignment](#bank-statement-alignment)
- [Cross-Referencing Guidelines](#cross-referencing-guidelines)

---

## Overview

This documentation covers the Mock Payslip Generator system, which creates realistic Australian payslips based on Xero's format with critical alignment to bank statement income entries. The system includes a React form component, calculation engine, and PDF generation capabilities, ensuring payslip data accurately corresponds to bank statement transactions to prevent discrepancies.

### Key Features
- Generates series of 5 payslips (current + 2 prior + 2 future periods)
- Integrates with Bank Statement Generator (shared company/employee data)
- Auto-calculates tax, superannuation, and deductions using ATO rates
- Supports multiple pay frequencies and employment types
- Pixel-perfect recreation of Xero payslip layout
- **Bank Statement Alignment**: Ensures payslip dates, amounts, descriptions, and deductions match bank statement entries

## Business Rules & Logic

### General Principles
- **Shared Data**: Company name, employee name/address, annual income, and pay frequency sync with Bank Statement Generator
- **User Input**: Most fields have defaults but allow overrides
- **Auto-Calculations**: Tax, superannuation, and YTD figures calculated automatically
- **Series Generation**: Creates 5 payslips centered on the "current" period
- **Bank Statement Alignment**: Payslip data must accurately correspond to income entries on bank statements, including dates, amounts, descriptions, and deductions to prevent discrepancies

### Bank Statement Alignment

#### Date Alignment
- **Pay Period End Dates**: Must align with salary deposit dates on bank statements (e.g., Fridays for weekly/fortnightly, 15th or preceding Friday for monthly)
- **Payment Dates**: Payslip payment dates should match the transaction dates on bank statements
- **Period Consistency**: Ensure pay periods do not overlap or create gaps that could cause discrepancies

#### Amount Alignment
- **Net Salary**: Payslip net income must exactly match the salary credit amount on bank statements
- **Deductions Breakdown**: Tax, superannuation, and other deductions on payslips should reflect the net calculation
- **YTD Consistency**: Year-to-date figures should align with cumulative bank statement deposits

#### Description Alignment
- **Employer Details**: Payslip employer information should match bank statement salary credit descriptions
- **Reference Numbers**: Include consistent reference numbers between payslips and bank statements
- **Transaction Types**: Clearly distinguish between salary credits, deductions, and adjustments

#### Deductions and Adjustments
- **Tax Deductions**: PAYG tax amounts should correspond to withheld amounts on bank statements
- **Superannuation**: Super contributions should match any separate transfers or deductions
- **Other Deductions**: Levies, loans, or other withholdings must be accurately reflected

#### Verification Rules
- **Cross-Reference Checks**: Compare payslip net amounts against bank statement credits
- **Period Matching**: Ensure each payslip period has a corresponding bank statement entry
- **Discrepancy Prevention**: Validate calculations to prevent rounding or calculation errors

### Income Calculation Alignment

**Net Salary Tiers** (Reference: [Bank Statement Income Rules](Bank_Statement_Comprehensive_Guide_Combined.md#income))
- ≤$50,000: 80% net ratio
- ≤$100,000: 70% net ratio
- ≤$180,000: 65% net ratio
- >$180,000: 60% net ratio

**Date Synchronization** (Reference: [Payment Date Rules](Bank_Statement_Comprehensive_Guide_Combined.md#income))
- Weekly/Fortnightly: Fridays
- Monthly: 15th or preceding Friday

**Variance Constraints** (Reference: [General Principles](Bank_Statement_Comprehensive_Guide_Combined.md#general-principles))
- Consistent amounts for recurring items (coffee, rent, gym, etc.)
- Variable amounts for groceries, petrol, occasional expenses
- Applied once per statement for recurring items

### Shared Terminology

| Term | Bank Statement Context | Payslip Context | Alignment Rule |
|------|----------------------|-----------------|---------------|
| Net Salary | Calculated income after deductions | Final payment amount | Must match exactly |
| Pay Period | Transaction date range | Earnings period | End dates must align |
| Variance | Amount fluctuation rules | Calculation precision | Must use same rounding |
| Reference Number | Transaction identifier | Payment reference | Must be consistent |
| Employer Details | Salary credit source | Company information | Must match exactly |
| YTD Figures | Cumulative deposits | Year-to-date earnings | Must align mathematically |

### Alignment Validation Checklist

- [ ] Pay period end dates match bank statement deposit dates
- [ ] Net salary amounts align with transaction credits
- [ ] Employer details consistent between documents
- [ ] Reference numbers match across systems
- [ ] Tax deductions correspond to withheld amounts
- [ ] Superannuation matches separate transfers
- [ ] YTD figures align with cumulative deposits
- [ ] Variance rules applied consistently
- [ ] Date synchronization follows Friday rules
- [ ] Income tier calculations match net ratios

## Transaction Rules Compliance

All payslip calculations must comply with the transaction rules defined in the Bank Statement Generator. This section provides direct references to ensure alignment.

### Income Calculation Rules Compliance

**Reference**: [Bank Statement Income Rules](Bank_Statement_Comprehensive_Guide_Combined.md#income)

The payslip generator must use the exact same net salary calculation tiers as defined in the bank statement transaction rules:

- **≤$50,000 annual income**: Net salary = 80% of gross
- **≤$100,000 annual income**: Net salary = 70% of gross
- **≤$180,000 annual income**: Net salary = 65% of gross
- **>$180,000 annual income**: Net salary = 60% of gross

### Date Synchronization Rules

**Reference**: [Payment Date Rules](Bank_Statement_Comprehensive_Guide_Combined.md#income)

Pay period end dates and payment dates must align with bank statement deposit schedules:

- **Weekly pays**: Pay period ends on Friday, payment on following Monday
- **Fortnightly pays**: Pay period ends on Friday (every 2 weeks), payment on following Monday
- **Monthly pays**: Pay period ends on 15th of month (or preceding Friday if 15th is weekend)

### Variance and Amount Rules

**Reference**: [General Principles](Bank_Statement_Comprehensive_Guide_Combined.md#general-principles)

- Recurring deductions (tax, superannuation) must be consistent across pay periods
- Variable amounts for occasional expenses must follow the same variance rules
- Rounding rules must match between payslip and bank statement calculations

### Payslip Structure

#### Company Details
- **Company Name**: Default "GlobalTech Solutions" (shared with Bank Statement)
- **ABN**: Default "53 004 085 616" (format: XX XXX XXX XXX)
- **Address**: Default "Level 10, 700 Bourke St, Docklands VIC 3008"
- **Company Logo**: File upload field in payroll section allowing users to upload company logo image (PNG/JPG formats supported, rendered on payslip header)

#### Payroll Details
- **Employment Status**: Full Time/Part Time/Casual
- **Pay Frequency**: Weekly/Fortnightly/Monthly (affects period calculations)
- **Pay Period**: Start/End dates calculated based on frequency
- **Payment Date**: Business day following period end (frequency-dependent)
- **Pay Run**: "X of Y" format for financial year tracking

#### Employee Details
- **Name**: Default "JOHN A CITIZEN" (shared with Bank Statement)
- **Address**: Default "456 Oak Avenue, Newtown NSW 2042" (shared with Bank Statement)

#### Earnings Calculation
- **Model**: Gross income derived from annual salary across pay frequencies
- **Superannuation Handling**: If salary includes super, it's extracted first
- **Rate Types**: Annual/Monthly/Fortnightly/Weekly (base), Daily/Hourly (derived)

#### Tax & Deductions
- **PAYG Tax**: Auto-calculated using ATO tables for selected financial year
- **Tax Scenarios**: Resident/Non-resident/Backpacker/No tax-free threshold
- **Tax Offsets**: LITO, LAMITO, MAWTO automatically applied
- **Medicare Levy**: 2.0% standard rate with low-income threshold reduction
- **Student Loans**: HELP/SFSS repayments based on income thresholds
- **Other Levies**: Temporary Budget Repair levy when applicable

#### Superannuation
- **Rate**: SG rate for financial year (e.g., 11.5% FY2025, 12.0% FY2026)
- **Calculation**: Based on Ordinary Time Earnings
- **Concessional Cap**: Limits concessional tax treatment
- **Division 293**: 15% tax on high-income earners exceeding threshold

#### Year-to-Date (YTD)
- **Calculation**: Current period amount × Pay Run number
- **Example**: $2000 gross × Pay Run "3 of 26" = $6000 YTD Gross

## Technical Specifications

### Document Layout
- **Format**: A4 Portrait (210mm × 297mm)
- **Margins**: 15mm all sides
- **Font**: Arial family (headings 14pt bold, body 10pt)
- **Colors**: Black text on white background, light gray accents

### Table Structures
- **Earnings Table**: Description/Rate/Hours/Amount/YTD columns
- **Tax Table**: Description/Amount/YTD columns
- **Superannuation Table**: Description/Amount/YTD columns
- **Styling**: 1px solid borders, right-aligned currency values

### Key Components
- **PayslipGeneratorForm.tsx**: Main React component
- **payslipCalculationEngine.ts**: Calculation utilities
- **usePayslipCalculations.ts**: React hook for state management

## Calculation Engine

### Core Data Structures

```typescript
interface PayCycleAmounts {
    a: number; // Annual
    m: number; // Monthly
    f: number; // Fortnightly
    w: number; // Weekly
}

interface Bracket {
    from: number;
    to: number;
    type: "percent" | "fixed" | "rate";
    nearest: number;
    value: number | string;
    incremental?: string | boolean;
}

interface IncomeData {
    annuated: boolean;
    PAYG: boolean;
    salary: number;
    hpd: number;        // Hours per day
    dpw: number;        // Days per week
    wpy: number;        // Weeks per year
    hpw: number;        // Hours per week
    superannuationRate: number;
    includesSuperannuation: boolean;
    backpacker: boolean;
    nonResident: boolean;
    noTaxfree: boolean;
    HELP: boolean;
    SFSS: boolean;
    withhold: boolean;
    yearIndex: number;
    year: string;
    payCycle?: string;

    // Annual figures
    division293: number;
    otherTaxesAndLevies: number;
    lito: number;
    lamito: number;

    // Pay cycle figures
    income: PayCycleAmounts;
    taxableIncome: PayCycleAmounts;
    net: PayCycleAmounts;
    superannuation: PayCycleAmounts;
    incomeTax: PayCycleAmounts;
    grossTax: PayCycleAmounts;
    otherTax: PayCycleAmounts;
    offsets: PayCycleAmounts;
    medicare: PayCycleAmounts;
    levies: PayCycleAmounts;
    help: PayCycleAmounts;
    sfss: PayCycleAmounts;
    deductions: PayCycleAmounts;
}
```

### Key Calculation Functions

#### Income Derivation Logic

```typescript
function getIncome(): void {
    // Handle different pay cycle types
    if (incomeData.payCycle === "daily") {
        // Daily: Salary × Days per Week × Weeks per Year
        incomeData.income.a = incomeData.salary * incomeData.dpw * incomeData.wpy;
    } else if (incomeData.payCycle === "hourly" || incomeData.payCycle === "hourly_day") {
        // Hourly: Salary × Hours per Day × Days per Week × Weeks per Year
        incomeData.income.a = incomeData.salary * incomeData.hpd * incomeData.dpw * incomeData.wpy;
    } else if (incomeData.payCycle === "hourly_week") {
        // Hourly weekly: Salary × Hours per Week × Weeks per Year
        incomeData.income.a = incomeData.salary * incomeData.hpw * incomeData.wpy;
    } else {
        // Standard cycles: Use salary as provided for that period
        incomeData.income.a = incomeData.salary;
    }

    // Spread to other pay cycles
    spreadAnnualAmounts(incomeData.income);
}

function spreadAnnualAmounts(obj: PayCycleAmounts): void {
    obj.m = obj.a / 12;        // Monthly
    obj.f = obj.a / 26;        // Fortnightly
    obj.w = obj.a / 52;        // Weekly
}
```

#### Tax Calculation with ATO Brackets

```typescript
function calculateIncomeTax(): void {
    const taxYear = taxData[incomeData.yearIndex];
    const brackets = incomeData.nonResident ? taxYear.taxNonResident.brackets :
                   incomeData.backpacker ? taxYear.taxBackpacker?.brackets || taxYear.tax.brackets :
                   incomeData.noTaxfree ? taxYear.taxNoFreeThreshold.brackets :
                   taxYear.tax.brackets;

    // Calculate tax using progressive brackets
    let remainingIncome = incomeData.taxableIncome.a;
    let tax = 0;

    for (const bracket of brackets) {
        if (remainingIncome <= 0) break;

        const bracketWidth = bracket.to - bracket.from;
        const taxableInBracket = Math.min(remainingIncome, bracketWidth);

        if (bracket.type === "percent") {
            tax += taxableInBracket * (bracket.value as number / 100);
        } else if (bracket.type === "fixed") {
            tax += bracket.value as number;
        }

        remainingIncome -= taxableInBracket;
    }

    // Apply to all pay cycles
    incomeData.incomeTax.a = tax;
    spreadAnnualAmounts(incomeData.incomeTax);
}
```

#### Superannuation Calculation

```typescript
function calculateSuperannuation(): void {
    const rate = taxData[incomeData.yearIndex].superannuation.brackets[0].value as number / 100;
    const grossIncome = incomeData.income.a;

    // Handle superannuation inclusion
    let superBase = grossIncome;
    if (incomeData.includesSuperannuation) {
        // Extract super from gross if included
        superBase = grossIncome / (1 + rate);
        incomeData.income.a = superBase;
        spreadAnnualAmounts(incomeData.income);
    }

    // Calculate superannuation amount
    incomeData.superannuation.a = superBase * rate;

    // Apply concessional cap
    const cap = taxData[incomeData.yearIndex].superannuation.concessionalCap;
    if (incomeData.superannuation.a > cap) {
        incomeData.superannuation.a = cap;
    }

    spreadAnnualAmounts(incomeData.superannuation);
}
```

### Utility Functions

#### Price Formatting

```typescript
function formatPrice(price: number, negative: boolean, brackets?: boolean): string {
    if (negative && price !== 0) {
        return '$' + price.formatMoney(2, '.', ',') + "";
    }

    let formattedPrice: string;
    if (price >= 0 && !negative) {
        formattedPrice = '$' + price.formatMoney(2, '.', ',');
    } else if (price === 0) {
        formattedPrice = '$' + (0).formatMoney(2, '.', ',');
    } else {
        formattedPrice = '-$' + (-1 * price).formatMoney(2, '.', ',');
    }

    if (brackets) {
        formattedPrice = `(${formattedPrice})`;
    }

    return formattedPrice;
}

Number.prototype.formatMoney = function (c: number, d: string, t: string): string {
    let n = this,
        cNew = isNaN(c = Math.abs(c)) ? 2 : c,
        dNew = d === undefined ? "," : d,
        tNew = t === undefined ? "." : t,
        s = n < 0 ? "-" : "",
        i = parseInt(n.toFixed(cNew)).toString(),
        j = i.length > 3 ? i.length % 3 : 0;
    return s + (j ? i.substr(0, j) + tNew : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + tNew) + (cNew ? dNew + Math.abs(Number(n) - Number(i)).toFixed(cNew).slice(2) : "");
};
```

#### Input Validation

```typescript
function validate(): void {
    validateInputNumber("#income", 0, 10000000000, 0);
    validateInputNumber("#dpw", 0, 7, 0);
    validateInputNumber("#hpd", 0, 24, 0);
    validateInputNumber("#hpw", 0, 24 * 7, 0);
    validateInputNumber("#wpy", 0, 52, 0);
}

function validateInputNumber(id: string, min: number, max: number, reset: number): void {
    const value = $(id).val() as string;
    $(id).val(validateNumber(value, min, max, reset));
}

function validateNumber(value: string, min: number, max: number, reset: number): string {
    while (value) {
        if (!isNaN(Number(value))) break;
        value = value.toString().slice(0, -1);
    }
    if (!value) return reset.toString();
    let numValue = parseFloat(value);
    numValue = numValue < min ? min : numValue;
    numValue = numValue > max ? max : numValue;
    return numValue.toString().replace(/^0+/, '');
}
```

#### Debounced Calculation

```typescript
function debounce<F extends (...args: any[]) => any>(func: F, wait: number, immediate: boolean = false): (...args: Parameters<F>) => void {
    let timeout: number | null;
    return function(this: ThisParameterType<F>, ...args: Parameters<F>): void {
        const context = this;
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        if (timeout) clearTimeout(timeout);
        timeout = window.setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

const efficientCalculate = debounce(function () {
    calculate();
}, 1);
```

### Key Calculation Functions

#### Income Derivation
- **Annual/Monthly/Fortnightly/Weekly**: Direct use of provided salary
- **Daily**: `Salary × Days per Week × Weeks per Year`
- **Hourly**: `Salary × Hours per Week × Weeks per Year`

#### Tax Calculation
- Uses ATO tax brackets and rates for selected financial year
- Applies progressive tax rates based on taxable income
- Includes tax offsets and Medicare levy calculations

#### Superannuation Calculation
- `Gross Income × Superannuation Rate`
- Subject to concessional contributions cap
- Division 293 tax for high earners

### Financial Year Support
- Supports multiple tax years with different rates
- Automatic rate updates based on selected year
- Handles tax rule changes between years

## Implementation Details

### Dependencies
- React for UI components
- TypeScript for type safety
- jQuery/Tooltipster for UI interactions
- PDF generation library for output

### Key Files
- `payroll.ts`: Core calculation logic and types
- `PayslipGeneratorForm.tsx`: Main form component
- `payslipCalculationEngine.ts`: Calculation utilities
- `usePayslipCalculations.ts`: State management hook

### Integration Points
- **Bank Statement Generator**: Shared data fields (company name, employee details, annual income, pay frequency) with automatic synchronization to ensure payslip data aligns with bank statement income entries
- **ATO Tax Tables**: External tax rate data for accurate PAYG calculations
- **PDF Generation**: Output formatting with pixel-perfect Xero layout
- **Form Validation**: Input sanitization and business rules enforcement
- **Date Synchronization**: Pay period dates must align with bank statement salary deposit dates
- **Amount Verification**: Net salary amounts must match bank statement credit amounts exactly

### Validation Rules
- ABN format: XX XXX XXX XXX (11 digits)
- Salary ranges: 0 to 10 billion
- Pay cycle constraints: Logical period calculations
- Business day adjustments for payment dates

## Usage Guidelines

### For Developers
1. Import calculation engine and types
2. Initialize IncomeData with user inputs
3. Call calculation functions in sequence
4. Format output using provided utilities
5. Handle edge cases (non-residents, backpackers)

### For Business Users
1. Select pay frequency and employment details
2. Enter salary and superannuation preferences
3. Choose tax year and residency status
4. Upload company logo (optional, for payslip branding)
5. Review auto-calculated values
6. Generate payslip series

### Configuration Options
- Financial year selection
- Tax residency settings
- Superannuation inclusion
- Student loan obligations
- Custom calculation overrides
- Company logo upload (PNG/JPG formats for payslip branding)

### Cross-Referencing Guidelines

#### For Business Users
1. **Date Verification**: Compare payslip pay period end dates with bank statement salary deposit dates
2. **Amount Matching**: Ensure payslip net income exactly matches bank statement credit amounts
3. **Description Consistency**: Verify employer details and reference numbers match between documents
4. **Deduction Alignment**: Cross-check tax and superannuation amounts with any separate transactions
5. **YTD Validation**: Confirm year-to-date figures align with cumulative bank statement deposits

#### For Developers
1. **Synchronization Checks**: Implement validation to ensure shared data remains consistent
2. **Date Alignment Logic**: Build rules to match pay periods with bank statement deposit schedules
3. **Amount Precision**: Use exact decimal calculations to prevent rounding discrepancies
4. **Reference Generation**: Create consistent reference numbers across both systems
5. **Error Prevention**: Add validation rules to flag potential misalignments before generation

#### Common Discrepancy Prevention
- **Frequency Matching**: Ensure pay frequency settings match bank statement deposit patterns
- **Tax Year Consistency**: Verify financial year settings align between systems
- **Superannuation Handling**: Confirm super inclusion/exclusion matches bank statement transfers
- **Rounding Rules**: Apply consistent rounding to prevent cent-level discrepancies
- **Period Boundaries**: Validate pay periods don't overlap or create gaps

## Appendix

### ATO Tax Rates (FY2024-2025 Example)
- 0% on first $18,200
- 19% on $18,201-$45,000
- 32.5% on $45,001-$135,000
- 37% on $135,001-$190,000
- 45% on $190,001+

### Superannuation Guarantee Rates
- FY2024: 11.0%
- FY2025: 11.5%
- FY2026: 12.0%

### Key Thresholds
- Medicare Levy Threshold: $24,276
- HELP/SFSS Threshold: Varies by income bracket
- Division 293 Threshold: $110,000 + super contributions