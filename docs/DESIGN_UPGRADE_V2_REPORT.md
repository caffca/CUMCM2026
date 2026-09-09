# 设计先验库与绘图升级 v2 — 实施记录

日期：2026-09-09；实际仓库：`E:\CUMCM2026`。

结论：Phase A 的冻结绘图与中文页面链路已在本机 Windows 验证通过，使用已验证的
PDF替代链路及只读设计回退。**不是全部运行能力均已验证**：CTeX缺组件，按项目
名称启动custom agent的探测超时。Phase B 第一批为PARTIAL，完整合格抽取1/50，
6–10篇跨题pilot也未完成；不能把23个候选当作23篇国一或已读全文。

## Git 与增量边界

开工前/交付时均为main，HEAD=`db7f9c0062ce5607907824a2f7809474441e41e6`。
这是本次检查的快照，不是要求后续手工维护HEAD。主仓库没有新增commit、stage、
push、merge、rebase或cherry-pick。仅一个既有worktree；未创建正式Review Lane，
未虚构建模milestone。测试fixture的commit只存在于隔离scratch仓库。

开工前dirty（不是本轮新建的全部内容）：

```text
 M .agents/skills/handoff/SKILL.md
 M .agents/skills/modeling-workflow/SKILL.md
 M .agents/skills/paper-review/SKILL.md
 M AGENTS.md
?? .agents/skills/contest-orchestrator/
?? .agents/skills/shadow-review/
?? .codex/
?? docs/CODEX_MULTI_AGENT_ORCHESTRATION_DESIGN_V1.md
?? scripts/
```

对本次涉及的既有文件先保存了字节级副本于
`tmp/design-upgrade-v2-before/`。交付核对确认下列原有内容未动：handoff、
modeling-workflow、`.codex/config.toml`、原有七个agent TOML（包括visual-critic）、
`scripts/prepare-review-worktree.ps1`；另确认PAPER_WRITING_GUIDE与visualization/__init__未动。
重叠的旧dirty保持在工作区；不以一个新commit夹带之前的编排实施。
本轮增量审阅补丁：`tmp/design-upgrade-v2-incremental.patch`，以开工前副本为基线，
不是相对HEAD的混合diff。它是审阅产物，不自动应用。

本轮改动职责：

| 路径 | 实际增量 |
|---|---|
| AGENTS.md、README.md、contest-orchestrator/shadow-review/paper-review skills | 统一milestone后创建Review Lane、默认单helper且设计/审图串行；只读回退；先验按需路由与三层图表检查 |
| .codex/agents/figure-designer.toml | 新增Sol/xhigh、read-only规格/patch角色；没有改旧critic模型或放开主仓库writer |
| src/visualization/style.py、export.py、scripts/figures/render_figure.py | 无参兼容style、实际字体/颜色/尺寸、冻结身份/brief、四类纯绘图与PDF/PNG/figure note |
| tests/figures/ | 合成fixture、数值/状态smoke、中文页面、CTeX探测、限时agent探测、语料/打包契约测试 |
| references/design_priors/、.agents/skills/design-priors/、scripts/design_priors.py | 轻量CSV/JSONL/Markdown索引与卡片；显式小批次采集、独立状态、去重统计和schema检查 |
| .gitignore、scripts/check_delivery.py | 原文/页面图默认不进Git；显式交付allowlist检查，不打包整个仓库、不认证正式提交 |
| docs/FIGURE_STYLE_GUIDE.md、ENVIRONMENT.md、REFERENCE_PAPER_ANALYSIS.md、CURRENT_PROGRESS.md | 更新本轮已验证事实、只读回退、种子年份来源及真实建设进度 |
| docs/CODEX_MULTI_AGENT_ORCHESTRATION_DESIGN_V1.md | 仅增加historical/design-only提示；旧设计正文保留 |
| 本报告 | 实际证据、未通过项与下一批入口 |

保留Continuous Builder、异步Shadow Review、开局三scout、explore/milestone、outputs/qX、
风险导向验证及人工跨窗口裁决。不建数据库、daemon、run registry或execution journal。
没有检索/嵌入2026赛事AI规定，没有新建赛事AI审查或普通调用逐次审批；也没有删除真实记录。

## 模型、发现与权限：配置不等于调用成功

主集成会话为GPT-6 Astra，不冒称Sol Controller。本机Codex CLI为0.153.4。
项目角色目录及name/model/effort/sandbox字段与当前
[官方custom-agent文档](https://developers.openai.com/codex/subagents/)相符；
并发字段见[配置参考](https://developers.openai.com/codex/config-reference/)。
本轮未复制用户全局配置、登录信息或密钥。

| 检查/角色 | 实际运行与边界 |
|---|---|
| figure_designer目标 | gpt-5.6-sol / xhigh；输入必须带base_sha、question、figure_id、frozen来源/身份、brief和允许产物路径 |
| 原生显式设计调用 | `01a08453-c46f-7af0-92fd-84e1a8bf1ce9`；调用参数真实指定Sol/xhigh，返回4类设计规格；不调用文件工具、不写文件、不冒称看过像素 |
| 原生显式关键页审图 | `01a0845c-36d2-71e0-a5f2-7c801dda091d`；真实Sol/xhigh，输入实际页面图，返回KEEP，无P0/P1，仅表图顺序Polish；不写文件 |
| 项目命名角色探测 | `tests/figures/agent_runtime.py`在`tmp/figure-agent-v2-01/`限时150秒运行CLI；TIMEOUT，连接重试后只完成配置读取，未证实designer/critic被按名调用 |
| 配置状态 | CONFIGURED_NOT_RUNTIME_VERIFIED；9个TOML可解析不能代替上行运行证据 |
| 当前回退 | 原生spawn接口没有可指定的角色名/cwd参数；designer保持read-only，返回规格/文本patch，Review Root在明确的隔离目录执行 |
| workspace-write | NOT_RUN；未启用，未声称文件级allowlist由sandbox自动保证 |
| visual_critic常态配置 | 原有Terra/high/read-only不变；本轮独立关键页审阅显式使用Sol/xhigh，不混淆两者 |

触发时机是冻结milestone的重要框架/关键结果/复杂统计图，非每次EDA。
一幅图一个writer；共享style仍由集成者修改。只读角色不得写输入、模型、指标、
论文科学主张、共享进度或Git。正式Reviewer仍经原helper取得指定SHA；当前无真实
milestone，所有验证在独立scratch，不消费Builder dirty数据。脚本验证输入hash但
不替Review Root验证工作区是否真的检出该SHA，两项必须分别核对。

## 实际测试与产物

命令均从`E:\CUMCM2026`执行；无依赖安装/升级，无真实竞赛数据/训练/模型求解。

```powershell
.\.venv\Scripts\python.exe -X utf8 tests/figures/smoke.py --work E:\CUMCM2026\tmp\figure-v2-smoke-03
& 'C:\Users\zyy17\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tests/figures/chinese_page.py --work E:\CUMCM2026\tmp\figure-v2-smoke-03
.\.venv\Scripts\python.exe -X utf8 tests/figures/inventory_contract.py
.\.venv\Scripts\python.exe -X utf8 tests/figures/agent_runtime.py --work E:\CUMCM2026\tmp\figure-agent-v2-01
.\.venv\Scripts\python.exe -X utf8 scripts/design_priors.py validate
.\.venv\Scripts\python.exe -X utf8 scripts/design_priors.py stats
.\.venv\Scripts\python.exe -X utf8 C:\Users\zyy17\.codex\skills\.system\skill-creator\scripts\quick_validate.py .agents/skills/design-priors
git diff --check
git status --short
```

agent_runtime命令列为本轮已执行的限时失败探测，不是要求每次验收重跑；
scratch路径必须全新，已有路径会拒绝覆盖。

| 验收 | 实际结果 |
|---|---|
| 4类图各重跑2次；6项smoke | PASS；点/线/区间端点/残差与输入核对，颜色cycle与155mm实际检查，关闭figure对象 |
| 故意错误 | PASS：缺输入BLOCKED、身份过期STALE、单位/区间/聚合/反向结论错误BLOCKED、缺字BLOCKED |
| 冻结输入可用性 | PASS：fixture在独立scratch被显式跟踪并有本地synthetic SHA；前后输入身份一致；不依赖ignored的主线结果 |
| PNG与中文PDF像素 | PASS：集成者实际查看4张图及最终页面；最后代码只加强数值检查，4张PNG与上一轮逐字节一致；仍重新看了03版最终页面 |
| 中文页面链路 | PASS：项目Python/Matplotlib→矢量PDF→本机bundled ReportLab+pypdf→Poppler渲染；中文/English/真负号/μ/ε、表格、155mm MediaBox核对 |
| 5项语料与交付契约测试 | PASS：重复、未核验、缺全文、不完整卡片排除；允许源码与禁止环境/语料/路径越界检查 |
| 语料schema与新skill | PASS；GBK默认读取的初次skill校验失败，使用-X utf8后通过；不改环境全局编码 |
| TOML语法、CLI入口 | PASS：tomllib解析9文件；`codex --strict-config -C E:\CUMCM2026 exec --help`可用；不是命名角色运行证明 |
| 只读/ignored输入差异 | CLI探测的tracked、untracked及重要ignored输入前后未变；证据JSON的changed_paths为空。由于探测未完成，不视为writer隔离测试通过 |
| CTeX | FAIL：`xelatex --disable-installer -interaction=nonstopmode -halt-on-error E:/CUMCM2026/tests/figures/ctex-smoke.tex`在scratch02缺ctexart.cls；未安装，不再反复尝试 |
| 官方论文模板、正式提交匿名/篇幅/体积 | NOT_RUN / TBD：用户未给本轮适用模板，不阻塞此升级；测试页不是正式论文模板 |
| governance_check.py | NOT_RUN：当前治理瘦身仓库无此文件；未为旧bootstrap要求重建它 |

主要证据：

- `tmp/figure-v2-smoke-03/smoke-evidence.json`：真实source SHA、scratch base SHA、语义caption与数值断言。
- `tmp/figure-v2-smoke-03/figures/{comparison,sensitivity,prediction,framework}.{pdf,png,note.json}`。
- `tmp/figure-v2-smoke-03/chinese-page.pdf`及同名PNG：实际页面产物。
- `tmp/figure-agent-v2-01-evidence.json`：真实失败/超时日志与前后文件检查，不能包装成成功。
- `tmp/figure-v2-smoke-02/ctex-smoke.log`：CTeX失败定位。

机器note保留NOT_VISUALLY_VERIFIED/PENDING，因为机器脚本不能自行宣布像素审阅。
上表记录实际Agent像素检查；人工科学确认仍未发生。最初smoke01误将坐标范围外的
未绘制刻度文字当作裁切，已修正并重跑。中文页初版SimHei缺真负号，已增加本机
Segoe UI逐字符回退并复查。没有静默替换成英文，也没有打包字体。

## Phase B 第一批：真实数量与范围

官方展示入口：[2024](https://dxs.moe.gov.cn/zx/hd/sxjm/sxjmlw/2024qgdxssxjmjslwzs/)、
[2025](https://dxs.moe.gov.cn/zx/hd/sxjm/sxjmlw/2025qgdxssxjmjslwzs/)。
这里提供的是整套页面图，不能说已经下载PDF。完整原页集存于ignored的
`references/papers/`；不公开上传，不执行论文附录代码。

| 计数口径 | 数量 |
|---|---:|
| 找到候选 / 去重身份 | 23 / 23 |
| 取得唯一全文原页集 | 3（2024 B196：28页；2025 D037：37页；E030：36页） |
| 已入库user_confirmed国一 | 0（仅缺种子路径；已接受用户身份说明，种子真实篇数仍未知） |
| 新增independently_verified国一 | 1 |
| 去重国一总数 | 1 |
| 正文读完 | 1 |
| 做过任何视觉检查 | 5（1篇完整页读；2篇抽样；2篇仅摘要，不等于5篇视觉验收） |
| cards总数 | 3（1完整，2隔离的局部观察） |
| 完整合格抽取 | 1 / 50；pilot 6–10也未完成 |
| 模式 | 2个论证单例 + 1个视觉单例；达到3篇/2题门槛的0个 |

候选分布：2024本科A/B/C=5/3/4，高职高专D/E=1/3；2025本科A/B/C=1/2/2，
高职高专D/E=1/1。完整全文分布：2024本科B=1，2025高职高专D/E各1；
完整合格抽取仅2024本科B=1。没有用其他年份、其他赛事、省奖或重复转载凑数。

B196依据同篇标题与
[华南理工大学来源的2024-12-23报道](https://dxs.moe.gov.cn/zx/a/hd_sxjm_smtd/241223/1985118.shtml)
对应，报道明确2024全国一等奖及B题优秀论文。该证据只用于这一篇，不推导全部
官方展示均为国一。只读子agent实际阅读P1–28；集成者复核P1/9/12/19/23/26。
卡片区分原文、推断和未说明，记录了公式/摘要与表格的可定位冲突；未复算或认证原文结果。

D037/E030优先取得全文并查了6/5页，但奖项仍UNVERIFIED、正文仅部分阅读；两张
卡片scope_complete=false且隔离，不能给designer冒充已审核先验。B159/B195仅查摘要页。
公开展示的样本选择偏差很大；模式频率不能解释获奖因果。

`index`与`fetch`只做显式小批次资料处理，串行写同一CSV；不自动核验奖项或标已读。
每批运行validate/stats。统计的本地页面身份校验仅用于语料完整性，不建全库运行日志。

## 最多3个未解决项

1. **P1 / 语料**：用户确认种子路径未到位，新增D/E国一身份尚未核实，跨题pilot及50目标均未完成。只需种子文件夹或压缩包路径，不需要奖项证明。
2. **P1 / 命名角色运行**：CLI探测超时，未验证项目custom-agent自动发现/按名调用及独立writer cwd。继续安全只读规格/patch回退；不影响主线冻结绘图。
3. **P1 / CTeX**：缺ctexart.cls；替代中文页面链路已实测，但正式LaTeX论文编译仍未验证。后续按实际模板选择出版链路，当前不安装。

无已发现的Phase A绘图P0。表图对象顺序可统一，属于Polish，不继续无穷改版。

## 两条后续调用

赛前建设：

> 在E:\CUMCM2026继续设计先验库下一批。用户确认种子位于<明确路径>，按2025国一/user_confirmed接入，无需重复获奖证明。去重后优先完成6–10篇跨题pilot及D/E；读取INDEX，逐篇看正文与规定视觉样本，报告真实计数。网络新增仍独立核验，不执行2026赛事AI审查。

冻结图重画：

> 在真实milestone <完整SHA>的隔离Review Lane重画<figure_id>。使用<冻结plot-data路径及SHA256>、<brief>和<允许产物路径>，先查3–5张匹配且来源合格的卡（不足则如实说明）。显式Sol/xhigh只读设计/patch，Review Root执行纯绘图，visual_critic独立只读审图并检查最终中文页面。缺输入BLOCKED、过期STALE；不改科学结果，不自动采纳跨窗口补丁。

本轮使用openai-docs核对配置和运行证据，skill-creator保持先验skill按需加载，PDF skill
要求实际渲染/看像素并促成中文负号问题修复。没有用任何skill替代用户授权或赛事规定。
