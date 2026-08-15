import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import openapiTS, { astToString } from 'openapi-typescript';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT = path.resolve(__dirname, '..');
const CONTRACT_PATH = path.resolve(ROOT, '../contracts/openapi.yaml');
const TARGET_PATH = path.resolve(ROOT, 'src/api/generated/schema.d.ts');

export async function generateSchema() {
  if (!fs.existsSync(CONTRACT_PATH)) {
    throw new Error(`OpenAPI contract not found at: ${CONTRACT_PATH}`);
  }

  const ast = await openapiTS(new URL(`file://${CONTRACT_PATH}`));
  const output = astToString(ast);
  
  const targetDir = path.dirname(TARGET_PATH);
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }

  fs.writeFileSync(TARGET_PATH, output, 'utf-8');
  console.log(`Generated TypeScript types from OpenAPI contract -> ${TARGET_PATH}`);
  return output;
}

if (process.argv[1] === __filename) {
  generateSchema().catch((err) => {
    console.error('Failed to generate schema:', err);
    process.exit(1);
  });
}
