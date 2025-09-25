# Design Specification: xeroPayslip.pdf

This document outlines the inferred design specifications for the xeroPayslip PDF template, based solely on its textual content and observable structural patterns. A pixel-perfect visual audit is not possible with current tools; this specification serves as a text-based representation of the document's design.

## 1. Document Structure & Layout

*   **Page Format:** Single page, portrait orientation.
*   **Header Block - Employee & Employer Information:**
    *   Employee Name and Address block (e.g., Andrea Kukor, Unit, Street, City, Postcode, Country).
    *   "PAID BY" section with Employer Name, Address, and ABN.
*   **Employment Details Section:**
    *   Heading: "EMPLOYMENT DETAILS".
    *   Key-value pairs: "Pay Frequency", "Annual Salary", "Pay Period", "Payment Date", "Total Earnings", "Net Pay".
*   **Earnings, Tax, and Superannuation Sections (Tabular):**
    *   Consistently structured tables with "THIS PAY" and "YTD" (Year-To-Date) columns.
    *   **SALARY & WAGES Table:**
        *   Contains "RATE" column for ordinary hours.
        *   Includes "Ordinary Hours" and "Other Previous Earnings".
        *   "TOTAL" row summarizes earnings.
    *   **TAX Table:**
        *   Includes "PAYG".
        *   "TOTAL" row summarizes tax.
    *   **SUPERANNUATION Table:**
        *   Includes "SGC - AustralianSuper - [ID]".
        *   "TOTAL" row summarizes superannuation.
*   **Payment Details Section:**
    *   Heading: "PAYMENT DETAILS".
    *   Key-value pairs: "REFERENCE", "AMOUNT" for the payment method (e.g., Pay Cheque).

## 2. Textual Elements & Formatting (Inferred)

*   **General Text:** Standard paragraph text for addresses and descriptive labels.
*   **Headings/Titles:**
    *   "EMPLOYMENT DETAILS", "SALARY & WAGES", "TAX", "SUPERANNUATION", "PAYMENT DETAILS" as main section headings.
*   **Table Headers:** "RATE", "THIS PAY", "YTD", "REFERENCE", "AMOUNT".
*   **Key Information:** Clearly labeled fields like "Pay Frequency:", "Annual Salary:", "Net Pay:", etc.
*   **Currency:** Amounts are prefixed with "$", followed by numerical value.
*   **Date Formats:** "DD/MM/YYYY" for Pay Period and Payment Date.

## 3. Font Metrics & Styles (Inferred limitations)

*   Specific font names, sizes, weights, and colors cannot be ascertained from raw text extraction. However, the consistent formatting and distinct roles of text (e.g., headings, labels, numerical values) imply:
    *   Varying font sizes for hierarchical importance.
    *   Potentially bolding for headings, totals, and key financial figures.
    *   Consistent font family throughout.

## 4. Spacing & Alignment (Inferred limitations)

*   **Line Breaks & Paragraphs:** Clear separation between logical blocks and table rows.
*   **Alignment:** Address blocks are multi-line. Key-value pairs often show a left-aligned label and a right-aligned value. Tables appear columnar with values aligned under their respective headers.
*   **Tabular Structure:** Implies a grid-like layout with defined columns for earnings, tax, and superannuation.

## 5. Image Placement & Color Profiles (Not ascertainable)

*   No images are referenced or inferred from the extracted text. "Xero" branding is implied by the filename but not directly deductible from content.
*   Color profiles cannot be determined from text content. The document is implicitly monochrome (black text on white background) unless external design specifications indicate otherwise.

## 6. Known Deviations/Assumptions

*   This specification is *derived* from text and structural hints; actual visual fidelity cannot be guaranteed or audited without visual comparison tools and explicit design specifications.
*   Exact pixel measurements for spacing, margins, font dimensions are not included.
*   Presence of logos or other graphical elements is not known.