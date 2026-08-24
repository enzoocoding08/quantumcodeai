// Rendert eine ausgefuellte Story-.dc.html (1080x1920) zu PNG.
// Usage: node render.mjs <input.dc.html> <output.png>
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import path from 'path';
import fs from 'fs';

const [, , inputPath, outputPath] = process.argv;
if (!inputPath || !outputPath) {
  console.error('Usage: node render.mjs <input.dc.html> <output.png>');
  process.exit(1);
}

let html = fs.readFileSync(inputPath, 'utf-8');
html = html.replace('<script src="./support.js"></script>', '');
html = html.replace(/<x-dc>/, '').replace(/<\/x-dc>/, '');
html = html.replace(/<helmet>/, '<head>').replace(/<\/helmet>/, '</head>');

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const page = await browser.newPage();
await page.setViewportSize({ width: 1080, height: 1920 });
await page.setContent(html, { waitUntil: 'networkidle' });
await page.waitForTimeout(300);

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
await page.screenshot({ path: outputPath, clip: { x: 0, y: 0, width: 1080, height: 1920 } });
console.log('rendered', outputPath);

await browser.close();
