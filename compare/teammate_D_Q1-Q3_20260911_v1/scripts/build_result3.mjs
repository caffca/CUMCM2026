import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const repoRoot = "C:/Users/ysw/Desktop/CUMCM2026";
const templatePath = `${repoRoot}/data/raw/D题/附件/附件2/result3.xlsx`;
const resultsPath = `${repoRoot}/outputs/q3/results.json`;
const outputDir = `${repoRoot}/outputs/q3`;
const outputPath = `${outputDir}/result3.xlsx`;
const previewPath = `${repoRoot}/tmp/artifact-q3/result3_preview.png`;

const results = JSON.parse(await fs.readFile(resultsPath, "utf8"));
if (results.status !== "OPTIMAL" || results.optimality !== "PROVED") {
  throw new Error(`Q3 result is not a proved optimum: ${results.status}/${results.optimality}`);
}

const input = await FileBlob.load(templatePath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItem("Sheet1");
const expectedHeaders = ["新增用频装备序号", "调整后频段区间", "调整后时间区间"];
const actualHeaders = sheet.getRange("A1:C1").values[0];
if (JSON.stringify(actualHeaders) !== JSON.stringify(expectedHeaders)) {
  throw new Error(`Unexpected result3 template headers: ${JSON.stringify(actualHeaders)}`);
}

const rows = results.selected_plans.map((row) => [
  row["新增用频装备序号"],
  row["频段区间"],
  row["时间区间"],
]);
const lastRow = rows.length + 1;
if (rows.length !== results.solver.selected_count) {
  throw new Error(`Selected plan count mismatch: rows=${rows.length}, solver=${results.solver.selected_count}`);
}

if (rows.length > 0) {
  sheet.getRange(`A2:C${lastRow}`).values = rows;
  sheet.getRange(`A2:C${lastRow}`).format.font = { name: "宋体", size: 10 };
  sheet.getRange(`A2:C${lastRow}`).format.horizontalAlignment = "center";
  sheet.getRange(`A2:C${lastRow}`).format.verticalAlignment = "center";
  sheet.getRange(`A2:A${lastRow}`).format.numberFormat = "0";
}

workbook.recalculate();
const tableAudit = await workbook.inspect({
  kind: "table",
  sheetId: "Sheet1",
  range: `A1:C${Math.min(lastRow, 25)}`,
  maxChars: 5000,
  tableMaxRows: 25,
  tableMaxCols: 3,
});
const formulaAudit = await workbook.inspect({
  kind: "formula",
  sheetId: "Sheet1",
  range: `A1:C${lastRow}`,
  maxChars: 3000,
  options: { maxResults: 20 },
});

await fs.mkdir(`${repoRoot}/tmp/artifact-q3`, { recursive: true });
const preview = await workbook.render({
  sheetName: "Sheet1",
  range: `A1:C${Math.min(lastRow, 30)}`,
  scale: 2,
  format: "png",
});
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const exported = await SpreadsheetFile.importXlsx(await FileBlob.load(outputPath));
const exportedSheet = exported.worksheets.getItem("Sheet1");
const verification = {
  sheetNames: [exportedSheet.name],
  rowCount: exportedSheet.getUsedRange(true).rowCount,
  headers: exportedSheet.getRange("A1:C1").values[0],
  firstRows: exportedSheet.getRange("A2:C4").values,
  lastRows: exportedSheet.getRange(`A${lastRow - 2}:C${lastRow}`).values,
  expectedRows: rows.length,
  tableAudit: tableAudit.ndjson,
  formulaAudit: formulaAudit.ndjson,
};
process.stdout.write(`${JSON.stringify(verification, null, 2)}\n`);
