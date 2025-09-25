# Design Specification: NABTransactionListing.pdf

This document outlines the inferred design specifications for the NABTransactionListing PDF template, based solely on its textual content and observable structural patterns. A pixel-perfect visual audit is not possible with current tools; this specification serves as a text-based representation of the document's design.

## 1. Document Structure & Layout

*   **Page Format:** Multi-page, portrait orientation.
*   **Header Block:**
    *   Title: "Transaction Listing", prominently placed.
    *   Date/Time: "Date Created: [Mon DD, YYYY HH:MM:SS AM/PM]"
*   **Account Balance Summary Section:**
    *   Heading: "Account Balance Summary".
    *   Key-value pairs: "Opening Balance", "Total Credits", "Total Debits", "Closing Balance" with corresponding currency amounts.
*   **Transaction Listing Period Section:**
    *   Headings: "Transaction Listing starts", "Transaction Listing ends" with corresponding dates.
*   **Account Details Section:**
    *   Heading: "Account Details".
    *   Key-value pairs: "Account Type", "BSB Number", "Account Number".
*   **Transaction Details Table:**
    *   Heading: "Transaction Details".
    *   Table Headers: "Date", "Particulars", "Debits", "Credits", "Balance".
    *   Each row contains transaction data corresponding to the headers.
*   **Footer Block (Repeated per page):**
    *   Page numbering: "Page X Of Y" (right-aligned, bottom).
    *   Heading: "Important".
    *   Bullet-point or numbered list of disclaimers (e.g., "This provisional list is not a statement of account.", "It may include transactions...", "It may not include all transactions...", "With the exception of cheque serial numbers...", "Inclusion of a debit...").
    *   Legal disclaimer: "National Australia Bank Limited ABN...", "AFSL and Australian Credit Licence..."

## 2. Textual Elements & Formatting (Inferred)

*   **General Text:** Standard paragraph text for information blocks and disclaimers.
*   **Headings/Titles:**
    *   "Transaction Listing" as primary title.
    *   "Account Balance Summary", "Transaction Listing starts/ends", "Account Details", "Transaction Details", "Important" as sub-headings or section titles.
*   **Table Data:** Dates, particulars, and currency amounts.
*   **Currency:** Amounts are prefixed with "$", numerical value, and "CR" for credit or "DR" for debit where applicable.
*   **Date Formats:**
    *   "Date Created": "Mon DD, YYYY HH:MM:SS AM/PM"
    *   Transaction Dates: "DD Mon YY"

## 3. Font Metrics & Styles (Inferred limitations)

*   Specific font names, sizes, weights, and colors cannot be ascertained from raw text extraction. However, the consistent formatting and distinct roles of text (e.g., titles, sub-headings, table headers, body) imply:
    *   Varying font sizes for hierarchical importance.
    *   Potentially bolding for headings and table headers.
    *   Consistent font family throughout.

## 4. Spacing & Alignment (Inferred limitations)

*   **Line Breaks & Paragraphs:** Clear separation between logical blocks and table rows.
*   **Alignment:** Key-value pairs and table columns suggest consistent alignment. Dates and balances in tables appear right-aligned or columnar.
*   **Table Structure:** Implies a grid-like layout with defined columns.

## 5. Image Placement & Color Profiles (Not ascertainable)

*   No images are referenced or inferred from the extracted text.
*   Color profiles cannot be determined from text content. The document is implicitly monochrome (black text on white background) unless external design specifications indicate otherwise.

## 6. Known Deviations/Assumptions

*   This specification is *derived* from text and structural hints; actual visual fidelity cannot be guaranteed or audited without visual comparison tools and explicit design specifications.
*   Exact pixel measurements for spacing, margins, font dimensions are not included.
*   Presence of logos or other graphical elements is not known.