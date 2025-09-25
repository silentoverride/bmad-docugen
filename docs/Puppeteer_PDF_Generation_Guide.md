# Comprehensive Guide to Puppeteer for Pixel-Perfect PDF Generation

## Introduction

Puppeteer is a powerful Node.js library developed by Google that provides a high-level API to control headless Chrome or Chromium browsers. It excels at generating pixel-perfect PDF documents by leveraging the full rendering capabilities of modern web browsers. This guide explores the comprehensive use of Puppeteer for PDF generation, covering setup, configuration, advanced techniques, and real-world applications.

### Why Puppeteer for PDF Generation?

- **Pixel-Perfect Rendering**: Utilizes Chromium's rendering engine for accurate layout reproduction
- **CSS Support**: Full support for modern CSS including flexbox, grid, and advanced styling
- **JavaScript Execution**: Handles dynamic content and client-side rendering
- **Headless Operation**: Runs without UI, perfect for server environments
- **Extensive Customization**: Granular control over PDF output parameters

## Setup and Installation

### Prerequisites

- Node.js (version 14 or higher recommended)
- npm or yarn package manager
- Basic knowledge of JavaScript/TypeScript

### Installation

```bash
npm install puppeteer
# or
yarn add puppeteer
```

For production environments, consider using `puppeteer-core` with your own Chromium installation:

```bash
npm install puppeteer-core
```

### Basic Setup

```javascript
const puppeteer = require('puppeteer');

async function generatePDF() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Your PDF generation logic here

  await browser.close();
}
```

## Configuration Options

### Launch Options

```javascript
const browser = await puppeteer.launch({
  headless: true, // Run in headless mode
  args: [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--no-first-run',
    '--no-zygote',
    '--single-process', // For CI/CD environments
    '--disable-gpu'
  ],
  ignoreHTTPSErrors: true,
  timeout: 60000
});
```

### PDF Generation Options

```javascript
await page.pdf({
  path: 'output.pdf',
  format: 'A4',
  printBackground: true,
  margin: {
    top: '1cm',
    right: '1cm',
    bottom: '1cm',
    left: '1cm'
  },
  displayHeaderFooter: true,
  headerTemplate: '<div style="font-size: 10px; text-align: center;">Header</div>',
  footerTemplate: '<div style="font-size: 10px; text-align: center;"><span class="pageNumber"></span></div>',
  preferCSSPageSize: true,
  landscape: false
});
```

## Advanced Techniques for Layout Control

### CSS Page Breaks

```css
.page-break {
  page-break-before: always;
}

.page-break-after {
  page-break-after: always;
}

.avoid-break {
  page-break-inside: avoid;
}
```

### Custom Page Sizes

```javascript
await page.pdf({
  width: '8.5in',
  height: '11in',
  // or
  format: 'Letter'
});
```

### A4 Document Generation

A4 is the most commonly used paper size worldwide (210mm × 297mm or 8.27in × 11.69in). Here are best practices for generating A4 PDFs:

#### Basic A4 Configuration

```javascript
await page.pdf({
  format: 'A4',
  printBackground: true,
  margin: {
    top: '20mm',
    right: '15mm',
    bottom: '20mm',
    left: '15mm'
  },
  preferCSSPageSize: true
});
```

#### A4-Specific CSS Setup

```css
/* A4 page dimensions in CSS */
@page {
  size: A4;
  margin: 20mm 15mm;
}

/* Content area calculations for A4 */
.a4-content {
  width: calc(210mm - 30mm); /* A4 width minus margins */
  min-height: calc(297mm - 40mm); /* A4 height minus margins */
  margin: 0 auto;
  font-size: 11pt; /* Optimal reading size for A4 */
  line-height: 1.4;
}

/* A4 print styles */
@media print {
  body {
    font-family: 'Times New Roman', serif;
    font-size: 12pt;
    line-height: 1.5;
    color: #000;
  }

  .a4-page-break {
    page-break-before: always;
  }

  .a4-no-break {
    page-break-inside: avoid;
  }
}
```

#### A4 Layout Optimization

```javascript
// Set optimal viewport for A4 rendering
await page.setViewport({
  width: 794, // A4 width in pixels at 96 DPI
  height: 1123, // A4 height in pixels at 96 DPI
  deviceScaleFactor: 1
});

// A4-specific content preparation
await page.evaluate(() => {
  // Add A4-specific classes
  document.body.classList.add('a4-document');

  // Optimize content for A4 dimensions
  const content = document.querySelector('.content');
  if (content) {
    content.style.maxWidth = '170mm'; // Leave room for margins
    content.style.margin = '0 auto';
  }
});
```

#### A4 Header and Footer Templates

```javascript
await page.pdf({
  format: 'A4',
  displayHeaderFooter: true,
  headerTemplate: `
    <div style="
      font-size: 10pt;
      font-family: Arial, sans-serif;
      width: 100%;
      text-align: center;
      border-bottom: 1px solid #ccc;
      padding-bottom: 5mm;
      margin-bottom: 5mm;
    ">
      <span>Company Name</span>
      <span style="float: right;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
    </div>
  `,
  footerTemplate: `
    <div style="
      font-size: 8pt;
      font-family: Arial, sans-serif;
      width: 100%;
      text-align: center;
      border-top: 1px solid #ccc;
      padding-top: 3mm;
      margin-top: 5mm;
      color: #666;
    ">
      Generated on ${new Date().toLocaleDateString()}
    </div>
  `,
  margin: {
    top: '25mm', // Account for header
    bottom: '20mm', // Account for footer
    left: '15mm',
    right: '15mm'
  }
});
```

#### A4 Table Handling

```css
/* A4-optimized table styles */
.a4-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10pt;
  margin-bottom: 10mm;
}

.a4-table th,
.a4-table td {
  border: 1px solid #ddd;
  padding: 3mm 2mm;
  text-align: left;
  word-wrap: break-word;
}

/* Prevent table row breaks */
.a4-table tr {
  page-break-inside: avoid;
}

/* Handle long tables across A4 pages */
.a4-table-long {
  /* Allow table to break across pages */
}

.a4-table-long thead {
  display: table-header-group;
}

.a4-table-long tbody {
  display: table-row-group;
}
```

#### A4 Image Optimization

```javascript
// Optimize images for A4 printing
await page.evaluate(() => {
  const images = document.querySelectorAll('img');

  images.forEach(img => {
    // Ensure images fit within A4 content area
    if (img.naturalWidth > 550) { // ~170mm at 96 DPI
      img.style.maxWidth = '170mm';
      img.style.height = 'auto';
    }

    // Add print-specific image styles
    img.style.imageRendering = '-webkit-optimize-contrast';
    img.style.imageRendering = 'crisp-edges';
  });
});
```

#### A4 Font Recommendations

```css
/* A4-optimized typography */
.a4-document {
  font-family: 'Times New Roman', serif;
  font-size: 12pt;
  line-height: 1.4;
  color: #000;
}

/* Headings for A4 */
.a4-document h1 {
  font-size: 18pt;
  font-weight: bold;
  margin: 15mm 0 8mm 0;
  page-break-after: avoid;
}

.a4-document h2 {
  font-size: 14pt;
  font-weight: bold;
  margin: 12mm 0 6mm 0;
  page-break-after: avoid;
}

.a4-document h3 {
  font-size: 12pt;
  font-weight: bold;
  margin: 10mm 0 4mm 0;
  page-break-after: avoid;
}

/* Paragraph spacing for A4 */
.a4-document p {
  margin-bottom: 4mm;
  text-align: justify;
  text-justify: inter-word;
}
```

#### A4 Performance Tips

```javascript
// A4-specific performance optimizations
const browser = await puppeteer.launch({
  args: [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    // Optimize for A4 rendering
    '--force-device-scale-factor=1',
    '--high-dpi-support=1'
  ]
});

// Set A4-optimized viewport
await page.setViewport({
  width: 794,
  height: 1123,
  deviceScaleFactor: 1
});
```

#### Common A4 Issues and Solutions

**Issue**: Content overflowing A4 boundaries
```css
/* Solution: Use CSS containment */
.a4-container {
  contain: layout style paint;
  max-width: 170mm;
  margin: 0 auto;
}
```

**Issue**: Fonts not rendering properly on A4
```javascript
// Solution: Ensure font loading
await page.evaluate(() => {
  return document.fonts.ready;
});
```

**Issue**: Images not fitting A4 layout
```css
/* Solution: Responsive images for A4 */
.a4-image {
  max-width: 100%;
  height: auto;
  object-fit: contain;
}
```

#### A4 Document Validation

```javascript
// Validate A4 document dimensions
await page.evaluate(() => {
  const body = document.body;
  const styles = window.getComputedStyle(body);

  // Check if content fits A4
  const contentWidth = body.scrollWidth;
  const contentHeight = body.scrollHeight;

  // A4 dimensions in pixels at 96 DPI
  const a4Width = 794;
  const a4Height = 1123;

  console.log('Content dimensions:', contentWidth, contentHeight);
  console.log('A4 dimensions:', a4Width, a4Height);

  if (contentWidth > a4Width || contentHeight > a4Height) {
    console.warn('Content may overflow A4 page boundaries');
  }
});
```

### Multi-Column Layouts

```css
.multi-column {
  column-count: 2;
  column-gap: 20px;
  column-rule: 1px solid #ccc;
}
```

### Table of Contents Generation

```javascript
// Generate TOC dynamically
await page.evaluate(() => {
  const headings = document.querySelectorAll('h1, h2, h3');
  const toc = document.createElement('div');
  toc.className = 'toc';

  headings.forEach((heading, index) => {
    const link = document.createElement('a');
    link.href = `#heading-${index}`;
    link.textContent = heading.textContent;
    heading.id = `heading-${index}`;
    toc.appendChild(link);
  });

  document.body.insertBefore(toc, document.body.firstChild);
});
```

## Handling Dynamic Content

### Waiting for Content

```javascript
// Wait for specific element
await page.waitForSelector('.dynamic-content');

// Wait for network idle
await page.waitForLoadState('networkidle0');

// Wait for custom condition
await page.waitForFunction(() => {
  return document.querySelectorAll('.item').length > 10;
});
```

### Injecting Dynamic Data

```javascript
await page.evaluate((data) => {
  // Inject data into the page
  document.querySelector('#user-name').textContent = data.name;
  document.querySelector('#invoice-total').textContent = data.total;

  // Handle arrays
  const itemsContainer = document.querySelector('#items');
  data.items.forEach(item => {
    const itemElement = document.createElement('div');
    itemElement.innerHTML = `<span>${item.name}</span><span>${item.price}</span>`;
    itemsContainer.appendChild(itemElement);
  });
}, dynamicData);
```

### Handling Asynchronous Operations

```javascript
await page.exposeFunction('onDataLoaded', (data) => {
  // Handle data when loaded
  console.log('Data loaded:', data);
});

await page.evaluate(() => {
  // Simulate async operation
  setTimeout(() => {
    window.onDataLoaded({ status: 'complete' });
  }, 1000);
});
```

## Performance Optimization

### Browser Configuration

```javascript
const browser = await puppeteer.launch({
  args: [
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor',
    '--font-render-hinting=none',
    '--disable-extensions',
    '--disable-plugins',
    '--disable-images', // If images aren't needed
    '--disable-javascript', // If JS isn't needed
    '--no-sandbox'
  ]
});
```

### Page Optimization

```javascript
await page.setViewport({
  width: 1200,
  height: 800,
  deviceScaleFactor: 1
});

// Disable unnecessary resources
await page.setRequestInterception(true);
page.on('request', (req) => {
  if (req.resourceType() === 'image' && !req.url().includes('logo')) {
    req.abort();
  } else {
    req.continue();
  }
});
```

### Memory Management

```javascript
// Close pages after use
await page.close();

// Use browser pool for multiple PDFs
const browserPool = [];
for (let i = 0; i < 3; i++) {
  browserPool.push(await puppeteer.launch());
}

// Reuse browsers
const browser = browserPool.pop();
// ... generate PDF
browserPool.push(browser);
```

## Troubleshooting Common Issues

### Font Rendering Issues

**Problem**: Fonts not rendering correctly in PDF

**Solutions**:
```javascript
// Ensure fonts are loaded
await page.addStyleTag({
  content: `
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
  `
});

// Wait for fonts to load
await page.evaluate(() => {
  return document.fonts.ready;
});
```

### Layout Breaking

**Problem**: Content overflowing or breaking unexpectedly

**Solutions**:
```css
/* Use CSS containment */
.pdf-content {
  contain: layout style paint;
}

/* Control widows and orphans */
p {
  widows: 2;
  orphans: 2;
}
```

### Performance Issues

**Problem**: PDF generation taking too long

**Solutions**:
```javascript
// Increase timeout
await page.pdf({
  timeout: 120000 // 2 minutes
});

// Use faster format
await page.pdf({
  format: 'A4',
  printBackground: false // Skip background rendering
});
```

### Memory Leaks

**Problem**: Browser consuming too much memory

**Solutions**:
```javascript
// Close browser after each PDF
await browser.close();

// Or reuse browser with page cleanup
await page.evaluate(() => {
  // Clear DOM
  document.body.innerHTML = '';
});
```

## Real-World Examples

### Invoice Generation

```javascript
const puppeteer = require('puppeteer');

async function generateInvoice(invoiceData) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { display: flex; justify-content: space-between; margin-bottom: 30px; }
        .invoice-details { margin-bottom: 30px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .total { font-weight: bold; font-size: 18px; }
      </style>
    </head>
    <body>
      <div class="header">
        <div>
          <h1>Invoice #${invoiceData.number}</h1>
          <p>Date: ${invoiceData.date}</p>
        </div>
        <div>
          <p>From: ${invoiceData.from}</p>
          <p>To: ${invoiceData.to}</p>
        </div>
      </div>

      <div class="invoice-details">
        <table>
          <thead>
            <tr>
              <th>Description</th>
              <th>Quantity</th>
              <th>Unit Price</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            ${invoiceData.items.map(item => `
              <tr>
                <td>${item.description}</td>
                <td>${item.quantity}</td>
                <td>$${item.unitPrice}</td>
                <td>$${item.total}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div class="total">
        <p>Total: $${invoiceData.total}</p>
      </div>
    </body>
    </html>
  `;

  await page.setContent(html);
  await page.pdf({
    path: `invoice-${invoiceData.number}.pdf`,
    format: 'A4',
    printBackground: true,
    margin: { top: '1cm', right: '1cm', bottom: '1cm', left: '1cm' }
  });

  await browser.close();
}
```

### Report Creation

```javascript
async function generateReport(reportData) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Load report template
  await page.goto('file://' + __dirname + '/templates/report.html');

  // Inject data
  await page.evaluate((data) => {
    document.querySelector('#title').textContent = data.title;
    document.querySelector('#date').textContent = data.date;

    // Generate charts using Chart.js or similar
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: data.chartData
    });

    // Add report sections
    const sectionsContainer = document.querySelector('#sections');
    data.sections.forEach(section => {
      const sectionElement = document.createElement('div');
      sectionElement.className = 'section';
      sectionElement.innerHTML = `
        <h2>${section.title}</h2>
        <p>${section.content}</p>
      `;
      sectionsContainer.appendChild(sectionElement);
    });
  }, reportData);

  await page.pdf({
    path: 'report.pdf',
    format: 'A4',
    landscape: true,
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div style="font-size: 10px; text-align: center;">Company Report</div>',
    footerTemplate: '<div style="font-size: 10px; text-align: center;"><span class="pageNumber"></span> of <span class="totalPages"></span></div>'
  });

  await browser.close();
}
```

### Responsive Design Rendering

```javascript
async function generateResponsivePDF(url, outputPath) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Test different viewport sizes
  const viewports = [
    { width: 1920, height: 1080, name: 'desktop' },
    { width: 768, height: 1024, name: 'tablet' },
    { width: 375, height: 667, name: 'mobile' }
  ];

  for (const viewport of viewports) {
    await page.setViewport({
      width: viewport.width,
      height: viewport.height,
      deviceScaleFactor: 1
    });

    await page.goto(url, { waitUntil: 'networkidle0' });

    await page.pdf({
      path: `${outputPath}-${viewport.name}.pdf`,
      format: 'A4',
      printBackground: true,
      preferCSSPageSize: true
    });
  }

  await browser.close();
}
```

## Best Practices for High-Fidelity Output

### CSS Optimization

```css
/* Use print-specific styles */
@media print {
  .no-print { display: none; }
  .page-break { page-break-before: always; }
  body { -webkit-print-color-adjust: exact; }
}

/* Optimize for PDF rendering */
* {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### Font Management

```javascript
// Load custom fonts
await page.addStyleTag({
  content: `
    @font-face {
      font-family: 'CustomFont';
      src: url('data:font/woff2;base64,${fontData}') format('woff2');
    }
  `
});
```

### Image Optimization

```javascript
// Ensure images are loaded
await page.waitForSelector('img', { visible: true });

// Optimize image rendering
await page.addStyleTag({
  content: `
    img {
      max-width: 100%;
      height: auto;
      image-rendering: -webkit-optimize-contrast;
    }
  `
});
```

## Integrating with Headless Browsers

### Docker Integration

```dockerfile
FROM node:16-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo-gobject2 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libgconf-2-4 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    wget \
    xdg-utils

# Set Puppeteer skip download
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

CMD ["npm", "start"]
```

### Cloud Deployment

```javascript
// For AWS Lambda
const chromium = require('chrome-aws-lambda');

async function generatePDFLambda() {
  const browser = await puppeteer.launch({
    args: chromium.args,
    executablePath: await chromium.executablePath,
    headless: chromium.headless
  });

  // PDF generation logic

  await browser.close();
}
```

## Managing Fonts and Styles

### Font Loading Strategies

```javascript
// Method 1: Web fonts
await page.addStyleTag({
  content: `
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    body { font-family: 'Inter', sans-serif; }
  `
});

// Method 2: Local fonts
await page.addStyleTag({
  content: `
    @font-face {
      font-family: 'CustomFont';
      src: url('${fontUrl}') format('woff2');
    }
  `
});

// Method 3: Base64 encoded fonts
const fontData = fs.readFileSync('fonts/custom.woff2').toString('base64');
await page.addStyleTag({
  content: `
    @font-face {
      font-family: 'CustomFont';
      src: url('data:font/woff2;base64,${fontData}') format('woff2');
    }
  `
});
```

### Style Optimization

```javascript
// Inject critical CSS
await page.addStyleTag({
  content: `
    .pdf-content {
      font-family: 'Arial', sans-serif;
      line-height: 1.4;
      color: #333;
    }
    .header { margin-bottom: 20px; }
    .footer { margin-top: 20px; }
  `
});

// Remove unnecessary styles
await page.evaluate(() => {
  const styles = document.querySelectorAll('link[rel="stylesheet"]');
  styles.forEach(style => {
    if (!style.href.includes('critical')) {
      style.remove();
    }
  });
});
```

## Automating PDF Generation in CI/CD Pipelines

### GitHub Actions Example

```yaml
name: Generate PDFs

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  generate-pdfs:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'

    - name: Install dependencies
      run: npm ci

    - name: Install Puppeteer dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y ca-certificates fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 lsb-release wget xdg-utils

    - name: Generate PDFs
      run: npm run generate-pdfs

    - name: Upload PDFs
      uses: actions/upload-artifact@v2
      with:
        name: generated-pdfs
        path: output/
```

### Docker-based CI/CD

```yaml
# .github/workflows/pdf-generation.yml
name: PDF Generation

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest

    container:
      image: node:16

    steps:
    - uses: actions/checkout@v2

    - name: Install system dependencies
      run: |
        apt-get update
        apt-get install -y wget gnupg ca-certificates
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
        sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
        apt-get update
        apt-get install -y google-chrome-stable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1

    - name: Install Node dependencies
      run: npm ci

    - name: Generate PDFs
      run: npm run pdf:generate

    - name: Archive PDFs
      uses: actions/upload-artifact@v2
      with:
        name: pdfs
        path: dist/pdfs/
```

### Jenkins Pipeline

```groovy
pipeline {
    agent {
        docker {
            image 'node:16'
            args '-u root'
        }
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'npm ci'
                sh '''
                    apt-get update
                    apt-get install -y wget gnupg ca-certificates
                    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
                    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
                    apt-get update
                    apt-get install -y google-chrome-stable
                '''
            }
        }

        stage('Generate PDFs') {
            steps {
                sh 'npm run generate-pdfs'
            }
        }

        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'output/*.pdf', fingerprint: true
            }
        }
    }
}
```

## Conclusion

Puppeteer provides a robust and flexible solution for generating pixel-perfect PDF documents by leveraging the power of modern web browsers. By following the techniques and best practices outlined in this guide, you can create high-quality PDFs that accurately represent your web content across various use cases.

Key takeaways:

- Always configure browser launch options for production environments
- Use CSS for precise layout control and page breaks
- Handle dynamic content with proper waiting strategies
- Optimize performance through resource management and caching
- Implement comprehensive error handling and troubleshooting
- Automate PDF generation in CI/CD pipelines for consistent results

For more advanced use cases, consider exploring Puppeteer's extensive API documentation and community resources.