import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const repoRoot = "C:/Users/ysw/Desktop/CUMCM2026";
const templatePath = `${repoRoot}/data/raw/D题/附件/附件2/result4.xlsx`;
// The defaults reproduce the historical conditional chain.  The current
// formal workbook is built by supplying Q4_RESULTS_PATH and, when needed,
// Q4_OUTPUT_PATH/Q4_VALIDATION_PATH so the source witness is explicit.
const resultsPath = process.env.Q4_RESULTS_PATH ?? `${repoRoot}/outputs/q4/conditional_R3_RB1_chain.json`;
const outputPath = process.env.Q4_OUTPUT_PATH ?? `${repoRoot}/outputs/q4/result4.xlsx`;
const previewPath = process.env.Q4_PREVIEW_PATH ?? `${repoRoot}/tmp/artifact-q4/result4_preview.png`;
const validationPath = process.env.Q4_VALIDATION_PATH ?? `${repoRoot}/outputs/q4/result4_workbook_validation.json`;

const results = JSON.parse(await fs.readFile(resultsPath, "utf8"));
const input = await FileBlob.load(templatePath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItem("Sheet1");
const expectedHeaders = [
  "用频装备编号",
  "调整后频段范围",
  "调整后时间区间",
  "调整后间隔时长",
  "是否撤销用频计划",
];
const actualHeaders = sheet.getRange("A1:E1").values[0];
if (JSON.stringify(actualHeaders) !== JSON.stringify(expectedHeaders)) {
  throw new Error(`Unexpected result4 template headers: ${JSON.stringify(actualHeaders)}`);
}

const rows = results.summary.actions.map((row) => [
  row["装备编号"],
  row["动作"] === "freq" ? row["频段区间"] : null,
  row["动作"] === "time" ? row["时间区间"] : null,
  row["动作"] === "gap" ? row["调整后间隔"] : null,
  row["动作"] === "revoke" ? "是" : null,
]);
const lastRow = rows.length + 1;
if (rows.length > 0) {
  sheet.getRange(`A2:E${lastRow}`).values = rows;
  sheet.getRange(`A2:E${lastRow}`).format.font = { name: "宋体", size: 10 };
  sheet.getRange(`A2:E${lastRow}`).format.horizontalAlignment = "center";
  sheet.getRange(`A2:E${lastRow}`).format.verticalAlignment = "center";
}

workbook.recalculate();
const formulaAudit = await workbook.inspect({
  kind: "formula",
  sheetId: "Sheet1",
  range: `A1:E${lastRow}`,
  maxChars: 3000,
  options: { maxResults: 20 },
});
const preview = await workbook.render({
  sheetName: "Sheet1",
  range: `A1:E${Math.min(lastRow, 30)}`,
  scale: 2,
  format: "png",
});
await fs.mkdir(`${repoRoot}/tmp/artifact-q4`, { recursive: true });
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
await fs.mkdir(`${repoRoot}/outputs/q4`, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const exported = await SpreadsheetFile.importXlsx(await FileBlob.load(outputPath));
const exportedSheet = exported.worksheets.getItem("Sheet1");
const verification = {
  sheetNames: [exportedSheet.name],
  rowCount: exportedSheet.getUsedRange(true).rowCount,
  headers: exportedSheet.getRange("A1:E1").values[0],
  firstRows: exportedSheet.getRange("A2:E4").values,
  lastRows: exportedSheet.getRange(`A${Math.max(2, lastRow - 2)}:E${lastRow}`).values,
  expectedActionRows: rows.length,
  formulaAudit: formulaAudit.ndjson,
};
await fs.writeFile(validationPath, JSON.stringify(verification, null, 2), "utf8");
process.stdout.write(`${JSON.stringify(verification, null, 2)}\n`);
