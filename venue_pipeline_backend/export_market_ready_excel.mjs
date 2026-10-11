import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(process.argv[2] || "venue_pipeline_backend/data_market_ready");
const workbook = Workbook.create();
const font = "Arial";
const header = { fill: "#17324D", font: { name: font, bold: true, color: "#FFFFFF" } };

async function rowsFor(name) {
  try { const payload = JSON.parse(await fs.readFile(path.join(root, `${name}.json`), "utf8")); return payload[name] || (name === "auto_review_queue" ? payload.rows : []) || []; }
  catch { return []; }
}

function sheetFromRows(name, title, rows) {
  const sheet = workbook.worksheets.add(name.slice(0, 31));
  sheet.showGridLines = false;
  sheet.getRange("A1").values = [[title]];
  sheet.getRange("A1").format = { font: { name: font, size: 14, bold: true, color: "#17324D" } };
  const columns = rows.length ? [...new Set(rows.flatMap(row => Object.keys(row)))].sort() : ["status"];
  sheet.getRangeByIndexes(2, 0, 1, columns.length).values = [columns];
  sheet.getRangeByIndexes(2, 0, 1, columns.length).format = header;
  if (rows.length) sheet.getRangeByIndexes(3, 0, rows.length, columns.length).values = rows.map(row => columns.map(column => row[column] ?? null));
  const size = Math.max(1, rows.length + 1);
  // Large evidence/provenance sheets are intentionally left unstyled below the
  // header; styling every cell multiplies workbook memory without adding data.
  if (rows.length <= 500) {
    sheet.getRangeByIndexes(2, 0, size, columns.length).format.borders = { preset: "all", style: "thin", color: "#D9E2EC" };
    sheet.getRangeByIndexes(2, 0, size, columns.length).format.autofitColumns();
  }
  sheet.freezePanes.freezeRows(3);
}

const names = ["venues", "candidates", "auto_review_queue", "venue_hours", "venue_time_slots", "venue_scores", "score_evidence", "venue_tags", "venue_sources", "human_pass", "admission_log", "areas"];
const loaded = {};
for (const name of names) loaded[name] = await rowsFor(name);

const summary = workbook.worksheets.add("Summary");
summary.showGridLines = false;
summary.getRange("A1").values = [["SHUFFL Market-Ready Venue Database"]];
summary.getRange("A1").format = { font: { name: font, size: 16, bold: true, color: "#17324D" } };
summary.getRange("A3:B11").values = [
  ["Metric", "Value"],
  ["Search areas", loaded.areas.length],
  ["Candidates (place_id only)", loaded.candidates.length],
  ["Officially verified active venues", loaded.venues.length],
  ["Human-pass queue", loaded.human_pass.length],
  ["Auto-review rows", loaded.auto_review_queue.length],
  ["Score rows", loaded.venue_scores.length],
  ["Time-slot rows", loaded.venue_time_slots.length],
  ["Provenance rows", loaded.venue_sources.length],
];
summary.getRange("A3:B3").format = header;
summary.getRange("A3:B11").format.borders = { preset: "all", style: "thin", color: "#D9E2EC" };
summary.getRange("A3:B11").format.autofitColumns();

sheetFromRows("Venues", "Officially Verified Venues", loaded.venues);
sheetFromRows("Candidates", "Candidate Index (Google place_id only)", loaded.candidates);
sheetFromRows("auto_review_queue", "Client Auto Review Queue", loaded.auto_review_queue);
sheetFromRows("Venue_Hours", "Officially Verified Opening Hours", loaded.venue_hours);
sheetFromRows("Venue_Time_Slots", "Evidence-backed Time Slots", loaded.venue_time_slots);
sheetFromRows("Venue_Scores", "SHUFFL Venue Scores", loaded.venue_scores);
sheetFromRows("Score_Evidence", "Score Evidence", loaded.score_evidence);
sheetFromRows("Venue_Tags", "Approved SHUFFL Tags", loaded.venue_tags);
sheetFromRows("Venue_Sources", "Field-Level Provenance", loaded.venue_sources);
sheetFromRows("Human_Pass", "Admitted-Venue Human Pass", loaded.human_pass);
sheetFromRows("Admission_Log", "Admission Log", loaded.admission_log);
sheetFromRows("Areas", "Delhi-NCR Search Areas", loaded.areas);

workbook.recalculate();
const output = path.join(root, "SHUFFL_Delhi_NCR_Client_Verification_v2.xlsx");
const blob = await SpreadsheetFile.exportXlsx(workbook);
await blob.save(output);
console.log(`Wrote ${output}`);
