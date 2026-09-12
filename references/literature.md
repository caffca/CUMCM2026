# 文献登记（2analysis-modeling；供论文 \cite 与 verify_refs 核验）

| id | 文献 | 用途（claim） | provenance | 状态 |
|---|---|---|---|---|
| L1 | W. K. Hale, "Frequency assignment: Theory and applications," *Proc. IEEE*, 68(12):1497–1514, 1980. DOI 10.1109/PROC.1980.11897 | 频指配问题（FAP）经典框架：干扰约束下的信道/频率指派模型 | 发现层 fap.zib.de/biblio（[bib](https://fap.zib.de/biblio/bibs/ha80.bib.txt)）+ Crossref DOI | 待 verify_refs |
| L2 | K. I. Aardal, S. P. M. van Hoesel, A. M. C. A. Koster, C. Mannino, A. Sassano, "Models and solution techniques for frequency assignment problems," *4OR-QRAL*, 5(2):79–108, 2007. DOI 10.1007/s10288-006-0024-2 | FAP 模型族与解法综述（整数规划/图论/局部搜索），支撑 Q2/Q4 的 CSP/整数规划路线选择 | [Zbl 1157.90005 区](https://zbmath.org/?q=ra%3Azytnicki.matthias+ai%3Amannino.carlo) + [FAP survey 站](https://fap.zib.de/survey/index.php) | 待 verify_refs |
| L3 | D. Brélaz, "New methods to color the vertices of a graph," *Comm. ACM*, 22(4):251–256, 1979. DOI 10.1145/359094.359101 | DSATUR 图着色：冲突图顶点操作/列表着色重表达（Q2 部分列表着色路线的算法学根基） | Crossref DOI | 待 verify_refs |
| L4 | L. Epstein, A. Levin, "Bin packing with conflicts," *Algorithmica*, 2011（及同作者 Two-dimensional packing with conflicts, Zbl 1144.68051, 2008） | 带冲突装箱：Q3 空闲可达集上加装 C 计划的装箱重表达与界技术 | [Zbl](https://zbmath.org/?q=an%3A1175.68200) + [Zbl 2D](https://zbmath.org/?q=ra%3Aullman.joseph-l+cc%3A68+py%3A2008) | 待 verify_refs |
| L5 | F. Rossi, P. van Beek, T. Walsh (eds.), *Handbook of Constraint Programming*, Elsevier, 2006. ISBN 978-0-444-52726-6 | 约束规划（CSP/CP-SAT 分支定界、no-overlap/表格约束）理论基础：Q2/Q4 精确差分 CSP | publisher/WorldCat | 待 verify_refs |
| L6 | GL.2 官方手册 CJCSM 3320.01D, "Joint Restricted Frequency Process/Deconfliction," jtcs.mil | 领域背景：用频冲突消解（deconfliction）在联合频谱行动中的规程化流程（支撑"撤销/平移/间隔调整"三类消解动作的现实性假设） | [官方 PDF](https://www.jcs.mil/Portals/36/Documents/Library/Manuals/CJCSM%203320.01D.pdf) | 官方文档（无需 DOI） |
| L7 | D. S. Johnson, "Near-optimal colorings of graphs and the size of maximal independent sets," *SIAM J. Comput.*, 3(2):100–113, 1974. DOI 10.1137/0203022 | 贪心/近似着色与独立集界：Q2 baseline 贪心+局部搜索与 Q3 set-packing 的近似分析传统 | Crossref DOI | 待 verify_refs |
| L8 | G. L. Nemhauser / L. A. Wolsey, *Integer Programming*, Wiley, 1999. ISBN 978-0-471-50621-0 | 集合覆盖/包装整数规划与 LP 对偶界：Q2 撤销下界与 Q3 LP 上界证明技术 | publisher/图书馆目录 | 待 verify_refs |

停止理由（evidence saturation）：Q1-Q4 每个关键方法主张（FAP 建模 L1/L2、图着色重表达 L3、带冲突装箱 L4、CP 精确求解 L5、IP 界技术 L8、启发式对照传统 L7、领域规程 L6）均已有≥1 条真实文献锚定；最后两轮查询（图着色 survey、CP-SAT 文档）仅返回上述集合的子集/弱版本（冗余率高），无新增未支撑主张 ⇒ 停止检索，转建模展开。

红线声明：全部检索词为方法学关键词；未检索、未阅读任何本届赛题题解/参赛方案/讨论（竞赛合规）。
