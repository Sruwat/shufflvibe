import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(process.argv[2] || "venue_pipeline_backend/data_market_ready_v2");
const payload = JSON.parse(await fs.readFile(path.join(root, "human_pass.json"), "utf8"));
const rows = payload.human_pass || [];
const columns = ["venue_id", "google_place_id", "google_lookup_url", "fit_out_age", "operator_class", "instagram_schedule", "human_status", "human_notes"];
const workbook = Workbook.create();
const instructions = workbook.worksheets.add("Instructions");
instructions.getRange("A1:B8").values = [
  ["SHUFFL Human Pass", "Only admitted venues are listed"],
  ["Edit", "fit_out_age, operator_class, instagram_schedule, human_status, human_notes"],
  ["Status 1", "verified"], ["Status 2", "rejected"], ["Status 3", "in_process"], ["Status 4", "update_required"],
  ["Google data", "Use google_lookup_url live; do not copy Google ratings/reviews/hours into this file"],
  ["Return", "Save this XLSX and send it back to SHUFFL"],
];
instructions.getRange("A1:B1").format = { fill: "#17324D", font: { name: "Arial", bold: true, color: "#FFFFFF" } };
instructions.getRange("A1:B8").format.wrapText = true;
const sheet = workbook.worksheets.add("human_pass");
sheet.getRange("A1").values = [["SHUFFL Human Pass — Admitted Venues"]];
sheet.getRange("A1").format = { font: { name: "Arial", size: 14, bold: true, color: "#17324D" } };
sheet.getRangeByIndexes(2, 0, 1, columns.length).values = [columns];
sheet.getRangeByIndexes(2, 0, 1, columns.length).format = { fill: "#17324D", font: { name: "Arial", bold: true, color: "#FFFFFF" } };
if (rows.length) sheet.getRangeByIndexes(3, 0, rows.length, columns.length).values = rows.map(row => columns.map(column => row[column] ?? ""));
sheet.freezePanes.freezeRows(3);
sheet.getRangeByIndexes(2, 0, 1, columns.length).format.autofitColumns();
workbook.recalculate();
const output = path.join(root, "SHUFFL_Human_Pass.xlsx");
const blob = await SpreadsheetFile.exportXlsx(workbook);
await blob.save(output);
console.log(`Wrote ${output}`);
