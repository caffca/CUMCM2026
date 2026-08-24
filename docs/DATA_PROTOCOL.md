# Data Protocol

Last updated: TBD
Status: draft
Freeze status: not frozen

## 1. Data Inventory

| Data ID | Source | Official / external | Version/date | Local path | Hash | Status |
|---|---|---|---|---|---|---|
| D-001 | TBD | official | TBD | TBD | TBD | not acquired |

## 2. Raw Data Integrity

- `data/raw/` 默认只读。
- 官方附件不得被手工覆盖。
- 重要原始文件记录 hash。
- 若允许外部数据，必须记录来源、访问时间、许可证/规则边界和用途。

## 3. Preprocessing

明确记录：

- 空值处理；
- 异常值处理；
- 去重；
- 单位换算；
- 坐标/时间系统；
- 编码和类别映射；
- 插值/平滑；
- 采样；
- 特征构造；
- 派生变量。

不得在论文中使用未被脚本或 manifest 记录的“手工修正”。

## 4. Data Versions

每个稳定处理版本应有：

```text
input hashes
processing script / commit
parameters
output path
output hash / manifest
```

## 5. Train / Validation / Test or Grouped Evaluation

若题目涉及机器学习、预测或统计泛化，记录：

- grouping key；
- split / CV strategy；
- leakage boundary；
- preprocessing fitting scope；
- test/final set access rule。

若题目不涉及此类评估，标记 `N/A`，不得机械套用。

## 6. Data Change Procedure

正式数据处理口径变化必须：

1. 创建 decision；
2. 更新本协议版本；
3. 重新生成 manifest/hash；
4. 标记受影响 run / figure / table；
5. 不覆盖旧版本。
