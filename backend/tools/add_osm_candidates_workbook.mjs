import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const input = "data/SHUFFL_South_Delhi_Venue_Database_MVP.xlsx";
const osmPath = "staging/osm_candidates.json";
const websitePath = "staging/website_verification.json";
const outputPath = "data/SHUFFL_South_Delhi_Venue_Database_Discovery.xlsx";

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(input));
const osm = JSON.parse(await fs.readFile(osmPath, "utf8"));
let website = { venues: [] };
try { website = JSON.parse(await fs.readFile(websitePath, "utf8")); } catch {}
const siteByOsm = new Map((website.venues || []).map(row => [row.osm_id, row]));

const headers = [
  "candidate_id", "venue_name", "area", "amenity", "address", "latitude", "longitude",
  "osm_id", "osm_url", "official_website", "phone", "opening_hours_osm", "cuisine",
  "outdoor_seating_osm", "reservable_osm", "website_status", "website_title",
  "website_final_url", "discovery_status", "admission_decision", "source", "discovered_on", "notes",
];

const rows = (osm.venues || []).map((row, index) => {
  const site = siteByOsm.get(row.osm_id) || {};
  return [
    `SHUFFL-OSM-SD-${String(index + 1).padStart(4, "0")}`,
    row.venue_name || "", row.area || "", row.amenity || "", row.address || "",
    row.latitude ?? "", row.longitude ?? "", row.osm_id || "", row.osm_url || "",
    row.official_website || "", row.phone || "", row.opening_hours || "", row.cuisine || "",
    row.outdoor_seating || "", row.reservable || "", site.website_status || "not_checked",
    site.website_title || "", site.website_final_url || "", "OSM candidate", "Review",
    "OpenStreetMap Overpass", osm.retrieved_on || "", "Requires Foursquare enrichment and human admission review before app use.",
  ];
});

const existing = workbook.worksheets.getItemOrNullObject("Venue_Candidates");
if (existing && !existing.isNullObject) existing.delete();
const sheet = workbook.worksheets.add("Venue_Candidates");
sheet.showGridLines = false;
sheet.getRangeByIndexes(0, 0, rows.length + 1, headers.length).values = [headers, ...rows];
sheet.getRange(`A1:W${rows.length + 1}`).format.font = { name: "Arial", size: 10, color: "#222222" };
sheet.getRange("A1:W1").format = {
  fill: "#1F4E78",
  font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
};
sheet.getRange(`A1:W${rows.length + 1}`).format.verticalAlignment = "center";
sheet.getRange(`F2:G${rows.length + 1}`).format.numberFormat = "0.000000";
sheet.getRange(`A1:W${rows.length + 1}`).format.borders = { preset: "insideHorizontal", style: "thin", color: "#E5E7EB" };
sheet.getRange(`A1:W${rows.length + 1}`).format.autofitColumns();
sheet.getRange("A:A").format.columnWidth = 22;
sheet.getRange("B:B").format.columnWidth = 28;
sheet.getRange("E:E").format.columnWidth = 36;
sheet.getRange("I:I").format.columnWidth = 34;
sheet.getRange("J:J").format.columnWidth = 34;
sheet.getRange("W:W").format.columnWidth = 48;
sheet.freezePanes.freezeRows(1);
sheet.tables.add(`A1:W${rows.length + 1}`, true, "VenueCandidatesTable");

workbook.recalculate();
const preview = await workbook.render({ sheetName: "Venue_Candidates", range: "A1:W18", scale: 1, format: "png" });
await fs.writeFile("staging/venue_candidates_preview.png", new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`Wrote ${rows.length} OSM candidates to ${outputPath}`);
