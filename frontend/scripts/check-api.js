import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import openapiTS, { astToString } from 'openapi-typescript';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT = path.resolve(__dirname, '..');
const CONTRACT_PATH = path.resolve(ROOT, '../contracts/openapi.yaml');
const TARGET_PATH = path.resolve(ROOT, 'src/api/generated/schema.d.ts');

async function checkSchema() {
  if (!fs.existsSync(CONTRACT_PATH)) {
    console.error(`OpenAPI contract not found at: ${CONTRACT_PATH}`);
    process.exit(1);
  }

  if (!fs.existsSync(TARGET_PATH)) {
    console.error(`Generated schema does not exist at: ${TARGET_PATH}. Run 'npm run generate:api'`);
    process.exit(1);
  }

  const existing = fs.readFileSync(TARGET_PATH, 'utf-8');
  const ast = await openapiTS(new URL(`file://${CONTRACT_PATH}`));
  const fresh = astToString(ast);

  if (existing !== fresh) {
    console.error(`Generated schema at ${TARGET_PATH} is out of date with ${CONTRACT_PATH}. Run 'npm run generate:api'`);
    process.exit(1);
  }

  console.log(`[OK] Schema freshness verified (${TARGET_PATH})`);
}

checkSchema().catch((err) => {
  console.error('Failed to check schema freshness:', err);
  process.exit(1);
});
