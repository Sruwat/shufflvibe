import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const input = process.argv[2];
const outputDir = process.argv[3];
if (!input || !outputDir) {
  console.error("Usage: node export_workbook_csv.mjs <workbook.xlsx> <csv-output-dir>");
  process.exit(2);
}
await fs.mkdir(outputDir, { recursive: true });
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(input));
function csvEscape(value) {
  if (value === null || value === undefined) return "";
  const text = String(value);
  return /[",\n\r]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}
for (const sheet of workbook.worksheets.items) {
  const used = sheet.getUsedRange();
  if (!used) continue;
  const csv = used.values.map(row => row.map(csvEscape).join(",")).join("\r\n") + "\r\n";
  await fs.writeFile(`${outputDir}/${sheet.name}.csv`, csv, "utf8");
}
console.log(`Exported ${workbook.worksheets.items.length} sheets to ${outputDir}`);
