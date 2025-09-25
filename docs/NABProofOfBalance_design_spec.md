# Design Specification: NABProofOfBalance.pdf

This document outlines the inferred design specifications for the NABProofOfBalance PDF template, based solely on its textual content and observable structural patterns. A pixel-perfect visual audit is not possible with current tools; this specification serves as a text-based representation of the document's design.

## 1. Document Structure & Layout

* **Page Format:** Single page, portrait orientation.
* **Header Block:**
  * Left-aligned customer address block (e.g., MR LORIN ZAHRA-NEWMAN, street, city, postcode, country).
  * Title: "Statement of Account Balances", centrally or prominently placed.
  * Date/Time: "Date created: [DD Month YYYY HH:MM:SS AM/PM]"
* **Main Content Area - Information & Disclaimers:**
  * Heading: "Information about this statement".
  * Bullet-point list for general information (e.g., available balance definition, currency, confidentiality notice).
* **Main Content Area - Account Balances:**
  * Section Heading: "Transaction Account" repeated (suggests sub-sections or categories).
  * Structured display for each account:
    * "BSB: [BSB Number]"
    * "Account No: [Account Number]"
    * "Current Balance: [Currency Amount]"
    * "Available Balance: [Currency Amount]"
    * Account balances include "CR" for credit where applicable.
* **Footer Block:**
  * Legal disclaimer: "National Australia Bank Limited ABN...", "AFSL and Australian Credit Licence..."
  * Page numbering: "Page 1 Of 1" (right-aligned, bottom).

## 2. Textual Elements & Formatting (Inferred)

* **General Text:** Standard paragraph text for information blocks.
* **Headings/Titles:**
  * "Statement of Account Balances" appears as a primary title.
  * "Transaction Account" and "Information about this statement" appear as sub-headings.
* **Key Information:** BSB, Account No, Current Balance, Available Balance are clearly labeled.
* **Currency:** Amounts are prefixed with "$", followed by numerical value.
* **Date Format:** "DD Month YYYY HH:MM:SS AM/PM".

## 3. Font Metrics & Styles (Inferred limitations)

* Specific font names, sizes, weights, and colors cannot be ascertained from raw text extraction. However, the consistent formatting and distinct roles of text (e.g., titles vs. body) imply:
  * Varying font sizes for hierarchical importance (Title > Sub-heading > Body).
  * Potentially bolding for labels (e.g., "BSB:", "Account No:").
  * Consistent font family throughout.

## 4. Spacing & Alignment (Inferred limitations)

* **Line Breaks & Paragraphs:** Clear separation between logical blocks of information.
* **Indentation:** Bullet points suggest indentation.
* **Alignment:** Address block and main title are distinct in their implied alignment. Key-value pairs for account details appear aligned.

## 5. Image Placement & Color Profiles (Not ascertainable)

* No images are referenced or inferred from the extracted text.
* Color profiles cannot be determined from text content. The document is implicitly monochrome (black text on white background) unless external design specifications indicate otherwise.

## 6. Known Deviations/Assumptions

* This specification is *derived* from text and structural hints; actual visual fidelity cannot be guaranteed or audited without visual comparison tools and explicit design specifications.
* Exact pixel measurements for spacing, margins, font dimensions are not included.
* Presence of logos or other graphical elements is not known.
