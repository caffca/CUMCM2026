import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const templatePath = "data/raw/D题/附件/附件2/result1.xlsx";
const resultsPath = "outputs/q1/results.json";
const outputPath = "outputs/q1/result1.xlsx";
const previewPath = "tmp/result1_preview.png";

const results = JSON.parse(await fs.readFile(resultsPath, "utf8"));
const input = await FileBlob.load(templatePath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItem("Sheet1");
const expectedHeaders = ["序号", "冲突装备1", "冲突设备2"];
const actualHeaders = sheet.getRange("A1:C1").values[0];
if (JSON.stringify(actualHeaders) !== JSON.stringify(expectedHeaders)) {
  throw new Error(`Unexpected result1 template headers: ${JSON.stringify(actualHeaders)}`);
}

const rows = results.conflict_pairs.map((row) => [
  row["序号"],
  row["冲突装备1"],
  row["冲突装备2"],
]);
const lastRow = rows.length + 1;
sheet.getRange(`A2:C${lastRow}`).values = rows;
sheet.getRange(`A2:C${lastRow}`).format.font = { name: "宋体", size: 10 };
sheet.getRange(`A2:C${lastRow}`).format.horizontalAlignment = "center";
sheet.getRange(`A2:C${lastRow}`).format.verticalAlignment = "center";
sheet.getRange(`A2:A${lastRow}`).format.numberFormat = "0";

workbook.recalculate();
const formulaAudit = await workbook.inspect({
  kind: "formula",
  sheetId: "Sheet1",
  range: `A1:C${lastRow}`,
  maxChars: 3000,
  options: { maxResults: 20 },
});
const preview = await workbook.render({
  sheetName: "Sheet1",
  range: "A1:C20",
  scale: 2,
  format: "png",
});
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
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
  formulaAudit: formulaAudit.ndjson,
};
process.stdout.write(`${JSON.stringify(verification, null, 2)}\n`);
