import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(process.argv[2] || "venue_pipeline_backend/data");
const output = path.join(root, "SHUFFL_Delhi_NCR_Venue_Database.xlsx");
const venuesPayload = JSON.parse(await fs.readFile(path.join(root, "venues.json"), "utf8"));
const queuePayload = JSON.parse(await fs.readFile(path.join(root, "verification_queue.json"), "utf8"));
const areasPayload = JSON.parse(await fs.readFile(path.join(root, "areas_resolved.json"), "utf8"));

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Summary");
const venues = workbook.worksheets.add("Venues");
const queue = workbook.worksheets.add("Verification_Queue");
const areas = workbook.worksheets.add("Areas");
const font = "Arial";
const header = { fill: "#17324D", font: { name: font, bold: true, color: "#FFFFFF" } };

function writeTable(sheet, title, rows, columns) {
  sheet.showGridLines = false;
  sheet.getRange("A1").values = [[title]];
  sheet.getRange("A1").format = { font: { name: font, size: 14, bold: true, color: "#17324D" } };
  sheet.getRangeByIndexes(2, 0, 1, columns.length).values = [columns];
  sheet.getRangeByIndexes(2, 0, 1, columns.length).format = header;
  if (rows.length) sheet.getRangeByIndexes(3, 0, rows.length, columns.length).values = rows.map(row => columns.map(column => row[column] ?? null));
  const size = Math.max(1, rows.length + 1);
  sheet.getRangeByIndexes(2, 0, size, columns.length).format.borders = { preset: "all", style: "thin", color: "#D9E2EC" };
  sheet.getRangeByIndexes(2, 0, size, columns.length).format.wrapText = false;
  sheet.getRangeByIndexes(2, 0, size, columns.length).format.autofitColumns();
  sheet.freezePanes.freezeRows(3);
}

const venueColumns = ["venue_id", "name", "city", "area", "address", "venue_type", "rating", "review_count", "website", "phone", "price_level", "food", "alcohol", "live_music", "outdoor_seating", "reservable", "description", "tags", "time_slots", "energy_score", "crowd_score", "conversation_score", "movement_score", "focus_score", "food_score", "live_music_score", "politics_score", "scene_score", "heritage_score", "games_score", "admission_decision", "admission_reason", "verification_status", "score_confidence", "google_place_id", "google_maps_url"];
writeTable(venues, "SHUFFL Delhi-NCR Venue Database", venuesPayload.venues, venueColumns);
writeTable(queue, "Human Verification Queue", queuePayload.items, ["venue_id", "issue", "priority", "status", "notes"]);
writeTable(areas, "Delhi-NCR Search Areas", areasPayload.areas, ["area", "city", "state", "latitude", "longitude", "radius_meters", "priority", "geocode_source"]);

summary.showGridLines = false;
summary.getRange("A1").values = [["SHUFFL Delhi-NCR Venue Pipeline"]];
summary.getRange("A1").format = { font: { name: font, size: 16, bold: true, color: "#17324D" } };
summary.getRange("A3:B7").values = [
  ["Metric", "Value"],
  ["Areas", areasPayload.areas.length],
  ["Venues", venuesPayload.venues.length],
  ["Admitted", venuesPayload.venues.filter(row => row.admission_decision === "Admitted").length],
  ["Human verification items", queuePayload.items.length],
];
summary.getRange("A3:B3").format = header;
summary.getRange("A3:B7").format.borders = { preset: "all", style: "thin", color: "#D9E2EC" };
summary.getRange("A3:B7").format.autofitColumns();

workbook.recalculate();
await fs.mkdir(root, { recursive: true });
const blob = await SpreadsheetFile.exportXlsx(workbook);
await blob.save(output);
console.log(`Wrote ${output}`);
