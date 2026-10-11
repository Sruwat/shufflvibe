import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(process.argv[2] || "venue_pipeline_backend/data_market_ready");
const payload = JSON.parse(await fs.readFile(path.join(root, "auto_review_queue.json"), "utf8"));
const rows = payload.auto_review_queue || payload.rows || [];
const columns = ["venue_id", "google_place_id", "discovered_area", "discovered_city", "discovered_type", "google_lookup_url", "official_name", "official_address", "official_website", "social_links", "hours_json", "time_slots", "auto_status", "auto_confidence", "human_status", "human_notes"];
const workbook = Workbook.create();
const header = { fill: "#17324D", font: { name: "Arial", bold: true, color: "#FFFFFF" } };

const instructions = workbook.worksheets.add("Instructions");
instructions.showGridLines = false;
instructions.getRange("A1").values = [["SHUFFL Client Venue Verification"]];
instructions.getRange("A1").format = { font: { name: "Arial", size: 16, bold: true, color: "#17324D" } };
instructions.getRange("A3:B9").values = [
  ["What to edit", "Only human_status and human_notes in the Auto_Review_Queue sheet"],
  ["Allowed status 1", "verified"],
  ["Allowed status 2", "rejected"],
  ["Allowed status 3", "in_process"],
  ["Allowed status 4", "update_required"],
  ["Google data", "Use the live lookup link only to identify the venue; do not copy Google ratings/reviews/photos into this file"],
  ["Final step", "Save this same XLSX and send it back to SHUFFL"],
];
instructions.getRange("A3:B3").format = header;
instructions.getRange("A3:B9").format.wrapText = true;
instructions.getRange("A3:B9").format.borders = { preset: "all", style: "thin", color: "#D9E2EC" };
instructions.getRange("A3:B9").format.autofitColumns();

const queue = workbook.worksheets.add("Auto_Review_Queue");
queue.showGridLines = false;
queue.getRange("A1").values = [["SHUFFL Auto-Enriched Venue Review Queue"]];
queue.getRange("A1").format = { font: { name: "Arial", size: 14, bold: true, color: "#17324D" } };
queue.getRangeByIndexes(2, 0, 1, columns.length).values = [columns];
queue.getRangeByIndexes(2, 0, 1, columns.length).format = header;
queue.getRangeByIndexes(3, 0, rows.length, columns.length).values = rows.map(row => columns.map(column => row[column] ?? ""));
queue.freezePanes.freezeRows(3);
queue.getRangeByIndexes(2, 0, 1, columns.length).format.autofitColumns();

workbook.recalculate();
const output = path.join(root, "SHUFFL_Delhi_NCR_Client_Verification_Final.xlsx");
const blob = await SpreadsheetFile.exportXlsx(workbook);
await blob.save(output);
console.log(`Wrote ${output}`);
