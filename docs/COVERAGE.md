# 覆盖率台账（本研究口径，非市场规模）

更新：2026-10-28（Phase 8 收官终局对账，见文末「终局对账」段；前次更新为同日 Phase 6/7 整合与 Round 6 回填，products.csv v0.5）
计数定义：候选=已发现未深核（仅存在性/二手线索，confidence C/U，notes 标「Round1新增候选,待深核」）/ 已核实=官网+仓库/文档至少一项一手核对 / 深研=完成案例 17 问或源码级 / 待验证=已核实但行 confidence 仍非 A（是已核实的子集，不另加总数）
**深研 = 3**：OpenSandbox（主仓 Round 2 深研 files/04 + Fast 外仓 Round 3 深研 files/06，主仓+外仓双深研完成，计 1 个产品）；E2B（Round 3 runtime 仓源码级深研，报告 files/07-E2B-RUNTIME-DEEP-DIVE.md，HEAD 92b83da）；Firecracker（Round 5 源码级深研，报告 files/12-FIRECRACKER-DEEP-DIVE.md，HEAD f0f48ff，计 Infra 类）。

| 类别（按 01-TAXONOMY 主类，每行只计一次主类） | 候选 | 已核实 | 深研 | 待验证（已核实子集） | 该类行数小计 | 备注 |
|---|---|---|---|---|---|---|
| P1 专用 Agent Sandbox SaaS | 3 | 7 | 1 | 3 | 10 | 已核实：E2B、Daytona(SaaS)、Runloop、Microsandbox、Blaxel、AWS Lambda MicroVMs、GCP Agent Compute Engine。Round 2：Lambda MicroVMs 与 ACE 升 A（ACE 定价为「已确认未公布」不降级），待验证由 5 降至 3 = Daytona、Runloop、Microsandbox。Round 3：**深研 1 = E2B（runtime 仓源码级，files/07）**，行 confidence 本为 A 不变。Round 5：Runloop 隔离子项升 A-（VM+容器双层官方明示），但 VMM 未点名、egress 默认口径/元数据/驻留仍 U，行 confidence 维持 B、仍计待验证（口径见 13 报告）。候选：Freestyle、Morph Cloud、Upstash Box |
| P2 Secure Code Runner / Judge | 2 | 3 | 0 | 0 | 5 | 已核实：nsjail、isolate、Judge0；候选：Piston、llm-sandbox |
| P3 Browser Sandbox | 1 | 4 | 0 | 3 | 5 | 已核实：Browserbase、Browserless、Steel.dev、Hyperbrowser；候选：Kernel。Round 2：Browserbase 6h 上限维持 B 并降权（见 Q21）。Round 5 攻坚后分化：**Browserbase 隔离升 A**（1 browser per VM/独立 subnet/销毁不复用，企业安全页明示）退出待验证；Browserless SaaS B+/开源版 A 分开写、Steel SaaS 维持 U（开源版 A）、Hyperbrowser 六渠道穷尽维持 U——三家行 confidence 仍 B，待验证=3。五家（含 P1 的 Runloop）元数据专项默认策略仍全 U（Q6） |
| P4 Computer Use / Desktop | 1 | 0 | 0 | 0 | 1 | 仅候选 E2B Desktop。本类仍是全表最薄弱处（见 02-ROUND1-REPORT） |
| P5 Cloud Dev Environment | 0 | 2 | 0 | 1 | 2 | 已核实：CodeSandbox SDK、Hugging Face Spaces。**HF Spaces 是邻域排除项（非 Agent Sandbox 反例）：计入行数对账，不计入 Sandbox 供给侧/竞品比较**，故 P5 实际 Sandbox 相关已核实只有 CodeSandbox SDK 1 条。待验证 1 = CodeSandbox SDK（隔离仅 B、定价时效风险高） |
| P6 通用云执行平台 | 0 | 9 | 0 | 5 | 9 | 已核实：Modal、Fly.io、Cloudflare Sandbox、Vercel Sandbox、Beam、Northflank、AWS Lambda、Azure Functions、GCP Cloud Run。Round 2：AWS Lambda 按官方 FAQ 升 A，待验证由 6 降至 5 = Fly.io、Beam、Northflank、Azure Functions、GCP Cloud Run。Modal 已按双运行时口径改写（Q18 已清），其行 confidence 本为 A 不在待验证内 |
| P7 Agent 平台内执行组件 | 0 | 2 | 0 | 1 | 2 | 已核实：OpenHands Runtime、AWS Bedrock AgentCore Code Interpreter。Round 2：AgentCore 定价/生命周期/microVM 隔离升 A（行 confidence 升 A；唯一保留 B 子项为 Firecracker 字样出处差异，见 Q10），待验证由 2 降至 1 = OpenHands Runtime（当前默认后端隔离为 C，待源码） |
| P8 开源自托管平台/控制面 | 3 | 2 | 1 | 0 | 5 | 已核实：OpenSandbox、GCP GKE Agent Sandbox。**深研 1 = OpenSandbox（Round 2 主仓源码级 + Round 3 Fast 外仓源码级，双深研完成）**。Round 2：GKE 按官方原文升 A（删除归纳价），待验证由 1 降至 0。候选：Kubernetes agent-sandbox (SIG)、AIO Sandbox (agent-infra)、CubeSandbox。注：Daytona OSS、E2B 开源组件、Microsandbox 开源部分虽带 P8 属性，主类已分别计入 P1，本表不双计（其 P8 属性写在 CSV category/notes 中） |
| 基础设施组件 (MicroVM/Wasm/安全容器/OS级) | 8 | 6 | 1 | 0 | 14 | 已核实：Firecracker、gVisor、Kata Containers、Cloud Hypervisor、Wasmtime、WasmEdge；候选：Google sandboxed-api、Dagger、Sysbox、Firejail、Bubblewrap、Hyperlight、Anthropic sandbox-runtime、firecracker-containerd。Round 2：Wasmtime license 逐字核结案升 A 口径（Q22）；Cloud Hypervisor 文档 CC-BY-4.0 已证、BSD-3-Clause 适用范围子项待核——按既有口径（待验证只计产品级关键字段），该子项缺口计入 OPEN-QUESTIONS Q22，不计入此处待验证。Round 5：**深研 1 = Firecracker（源码级，files/12，HEAD f0f48ff）**，行 confidence 本为 A 不变；gVisor 经线 C 选读补记（Gofer 协议修正 LISAFS、Systrap 默认依据、兼容清单口径入 limitations），不计深研（选读非全量深研） |
| **合计** | **18** | **35** | **3** | **13** | **53** | 与 products.csv v0.4 数据行数对账一致（见对账说明） |

## 实验计数（Round 4 新增，独立于产品计数）

计数定义：实验批 = 一次预注册 + 一份实验报告的完整批次；判定口径以 09 冻结 v1.0 为准；[SELF] 数据点 = 本项目自测产出的判定结论（区别于 [OFFICIAL]/[THIRD-PARTY]/[ESTIMATE]，Round 3 及以前 [SELF] = 0）。

- **已执行实验批：1**（Round 4 实验室第一批，LAB-MINI 载体，报告 files/10-LAB-BATCH1-REPORT.md；预注册 hidden_files/lab/PREREG-batch1.md；原始数据 16 文件、脚本 12 个，已同步公开仓 lab/batch1/，含全部无效批次）
- [SELF] 判定登记（按 10 报告 §7 口径）：
  - EXP-01a namespace 视图隔离：**通过**
  - EXP-01b cgroup 配额（C1/C2/C3）：**未判定——环境不具备（控制器未委派），顺延 LAB-REF**（RLIMIT 替代探针仅作机制参考，不计 C1/C2/C3 判定）
  - EXP-01c seccomp：**通过**
  - EXP-02 超时清零（C4+C7）：**通过**
  - EXP-03 网络矩阵（C8 子集 + ST-5，兼 Q29 配方验证）：**载体内部分通过**（U1–U8 全过、U9 N/A；拓扑级未判定，顺延 LAB-REF）
  - EXP-04 ST-1/ST-2/ST-4 冒烟：**通过**（冒烟级，非性能基线）
  - C6 快照一致性（含 Q32）：**未执行**，冻结判据已立，待 LAB-REF
  - Q34（62s 分段拆账）：**未执行**，冻结探针方案已登记，待 LAB-REF
- 产品侧计数本轮不变：**深研仍 2、产品仍 53 行**（见下对账说明），实验计数与产品计数不合并。

## 对账说明

### Round 5（2026-10-27，与 products.csv v0.4 逐项核对）

- products.csv 共 **54 行 = 1 表头 + 53 数据行**，行数不变（本轮只做攻坚/深研回填，无新增/删除行）。本表合计行数 53 = 候选 18 + 已核实 35，一致。
- confidence 分布（脚本统计，与 CSV 逐行一致）：**A 22 / B 13 / C 17 / U 1（Kernel）**，合计 53。较 Round 4（A 21 / B 14 / C 17 / U 1）唯一变化：**Browserbase B → A**（隔离升 A），B −1、A +1。
- 待验证 **14 → 13** = 已核实 35 中行 confidence 非 A 者（全部 13 个 B 行），减少的 1 行即 Browserbase，与升 A 一一对应。Runloop 隔离子项升 A- 但行 confidence 维持 B（VMM 未点名、egress 默认口径/元数据/驻留仍 U），仍计待验证——子项升格不等于整行升格，与 Round 2 的子项保留口径一致。
- 深研 **2 → 3**：新增 Firecracker（Infra 类，源码级 + 17 问组件子集，files/12）。gVisor 本轮为选读（三线定位 + Q12 结案），未做全量源码深研，**不计深研**。
- 实验计数本轮不变：已执行实验批仍 1，[SELF] 判定登记不变（Firecracker/gVisor 深研均为纯静态分析，未产生新 SELF 数据）。

### Round 4（2026-10-27，实验计数与 products.csv 对账）

- products.csv 未改动：共 54 行 = 1 表头 + 53 数据行，confidence 分布 **A 21 / B 14 / C 17 / U 1（Kernel）**，与 Round 3 一致；本表产品合计 53 = 候选 18 + 已核实 35、深研 2、待验证 14，全部不变，对账一致。
- 本轮新增的只有实验维度：已执行实验批 0 → 1，[SELF] 判定 6 条登记（通过 4：EXP-01a、EXP-01c、EXP-02、EXP-04；载体内部分通过 1：EXP-03；未判定/顺延 1 组：C1/C2/C3）+ C6/Q34 未执行登记。
- LAB-MINI 的全部绝对性能数字仅对本载体成立，禁止外推（09 §0 既定）。

### Round 3（2026-10-27，与 products.csv v0.3 逐项核对）

- products.csv 共 **54 行 = 1 表头 + 53 数据行**，行数与 Round 2 一致（本轮只做深研回填，无新增/删除行）。本表合计行数 53，一致；候选 18 + 已核实 35 = 53，一致。
- confidence 分布（脚本统计，与 CSV 逐行一致）：**A 21 / B 14 / C 17 / U 1（Kernel）**，合计 53，与 Round 2 完全相同——本轮两条深研行（E2B、OpenSandbox）原本即为 A，深研回填不改变等级分布，如实统计。
- 待验证 14 不变 = 已核实 35 中全部 14 个 B 行。
- 深研 **1 → 2**：OpenSandbox（P8，主仓+Fast 外仓双深研，仍计 1 个产品）与 E2B（P1，runtime 仓）。深研口径不变：须源码级 + 案例 17 问；文档/价表级核实不计。
- 两家深研均为纯静态源码分析：**均未部署、未运行、未实测，全项目 SELF 数据仍为 0**（新登记见 OPEN-QUESTIONS Q35）。

### Round 2（2026-10-27，与 products.csv v0.2 逐项核对）

- products.csv 共 **54 行 = 1 表头 + 53 数据行**，行数与 Round 1 一致（本轮只升证据等级与深研计数，无新增/删除行）。本表合计行数 53，一致；候选 18 + 已核实 35 = 53，一致。
- confidence 分布（脚本统计，与 CSV 逐行一致）：**A 21 / B 14 / C 17 / U 1（Kernel）**，合计 53。较 Round 1（A 16 / B 18 / C 18 / U 1）变化：A +5（AWS Lambda、AWS Lambda MicroVMs、AgentCore Code Interpreter、GKE Agent Sandbox 由 B 升 A；Agent Compute Engine 由 C 升 A），B −4，C −1。
- 待验证 14 = 已核实 35 中行 confidence 非 A 者（恰为全部 14 个 B 行，均属已核实；候选行的 C/U 不重复计入待验证）。较 Round 1 的 19 减少 5，与升 A 的 5 行一一对应。
- 深研 1 = OpenSandbox（P8）。其余 52 行深研仍为 0：证据等级升 A ≠ 深研，README/文档/价表级核实不计深研。
- 子项级保留（不影响行 confidence 与本表计数，逐项登记在 OPEN-QUESTIONS）：AgentCore 的 Firecracker 字样 B（Q10）、Cloud Hypervisor 的 BSD-3-Clause 范围待核（Q22）、Lambda MicroVMs 区域数 B（CSV status 内注明）、Browserbase 6h 维持 B（Q21，属 P3 已在待验证内）。

### Round 1（2026-10-27，与 products.csv v0.1 逐项核对，原文存档）

- products.csv 共 **54 行 = 1 表头 + 53 数据行**。本表合计行数 53，一致。
- 53 = 种子 23 条（已全部回填核实，不再计候选）+ Round 1 新增 30 条。
- 新增 30 = A 线新候选 14 + B 线新发现 9 + B 线云厂商拆分 7。
  - A 线候选 14：Piston、Google sandboxed-api、Kubernetes agent-sandbox (SIG)、Dagger、Sysbox、Firejail、Bubblewrap、Hyperlight、AIO Sandbox、Anthropic sandbox-runtime、firecracker-containerd、llm-sandbox、E2B Desktop、CubeSandbox。
  - B 线新发现 9：Blaxel、Beam、Northflank、CodeSandbox SDK、Hugging Face Spaces、Freestyle、Morph Cloud、Kernel、Upstash Box。其中前 5 个已核实，后 4 个为候选。
  - 云厂商拆分 7：AWS Lambda、AWS Lambda MicroVMs、AWS Bedrock AgentCore Code Interpreter、Azure Functions、GCP Cloud Run、GCP GKE Agent Sandbox、GCP Agent Compute Engine。拆分原因：三家云厂商的 Serverless 本体、MicroVM 原语、Agent 平台组件形态完全不同，禁止混为一个「云厂商 Sandbox」。
- 候选/已核实划分按 notes/status 口径，不按 confidence 单独划分（一处例外说明）：候选 18 = A 线 14 + B 线候选 4（Freestyle、Morph Cloud、Kernel、Upstash Box），均在 notes 标「Round1新增候选,待深核」；已核实 35 = 种子 23 + B 线已核实新发现 5 + 云厂商拆分 7。其中 GCP Agent Compute Engine 在 Round 1 的 confidence 为 C（仅宣布+博客转述的预览项），但因 B 线已做形态/设计半核实，计入已核实（半核实）而非候选；Round 2 已升 A，此例外说明自 Round 2 起不再适用（其行内仍明确标「未 GA」）。
- Round 1 时 confidence 分布为 A 16 / B 18 / C 18 / U 1，待验证 19；该组数字已被 Round 2 组替代，保留此处仅作历史对照。
- 不双计规则：一个产品只按主类计一次。Fly.io（Machines=P6 / Sprites=P1）、Vercel（P1 性质 / P6 主类）、E2B/Daytona/Microsandbox 的 P8 属性、GKE Agent Sandbox 的 P1/P8 双性，均只计主类，副属性在 CSV 中注明。
- 上一版（Round 0）台账为种子池 23 条全 U、各类计数为 0；Round 1 版替代之，种子池口径已关闭。
- 这些数字只说明本研究覆盖，不代表市场真实规模；禁止宣称"覆盖 100% 市场"。未覆盖清单见 02-ROUND1-REPORT.md、05-ROUND2-REPORT.md、08-ROUND3-REPORT.md 与 OPEN-QUESTIONS.md（Prized/Tensorlake/Deno Sandbox/LangSmith Sandboxes 等 20+ 仅登记未入表项不在本表计数内）。

## 设计类交付计数（Phase 6/7 新增，独立于产品/实验计数）

计数定义：参考架构 = files/14 中按统一 17 项模板（组件/控制面/数据面/调度/创建/执行代理/文件/网络/凭证/观测/快照/回收/故障/HA/边界/瓶颈/成本）+ 关键决策出处 + 最先被打穿路径 + 不适用场景完整成文的架构；选型场景 = files/15 中权重声明（门槛/一阶/二阶）+ 主推荐 + 替代 + 前提 + 风险 + 明确不推荐完整成文的场景；全局图 = 两份交付中的 Mermaid 图（结构级检查完成，渲染级未验证，见 16 报告 §4）。

- **参考架构：5**（A 容器型 / B MicroVM 型 / C 安全容器型（含 C1 gVisor、C2 Kata 两变体）/ D Wasm 型 / E 混合型），files/14-REFERENCE-ARCHITECTURES.md（546 行）
- **选型场景：9**（个人 Agent / AI Coding Agent / 企业内部运维 Agent / 公众 Agent SaaS / 不可信代码执行平台 / Browser Agent / Computer Use Agent / 高安全金融 / 大规模多租户），files/15-SELECTION-FRAMEWORK.md（264 行）；另含 17 维度定义与 9 组路线两两对照、C 级判断登记 18 条（C-1…C-18）
- **全局图：12 = 14 号 11 张 + 15 号 1 张**（14：技术分类、总体架构、控制/数据平面、生命周期状态、网络安全边界、多租户执行 + 五架构各自组件图 5 张；15：选型决策流程图）
- 整合与自检报告：files/16-PHASE67-REPORT.md（四项自检：(a) 架构引用对齐问题 0；(b) 9 场景抽查 9/9 一致、价格口径小错 1 已修；(c) 性能数字清单 6 个全合格、日期标注小错 1 已修；(d) C 级判断 18 条比对矛盾 0、无对照 3）

## 对账说明（Phase 6/7）

- 本轮为设计类交付，**未改动 products.csv**：产品计数不变（54 行 = 1 表头 + 53 数据行，候选 18 + 已核实 35，confidence A 22 / B 13 / C 17 / U 1），深研仍 3，待验证仍 13，实验计数仍 1 批——与 Round 5 对账段一致，两套计数不合并。
- 对 14/15 的两处小错修正（15 §3.6 代理价格区间、14 §5.2 兼容数字日期）不影响任何产品行与计数，已分别在被改文件与 16 报告 §2 登记。
- 附带发现（不计入本轮计数）：13-ROUND5-REPORT.md 本地与公开仓版本均在 §3 中途截断（§4–§6 缺失），已在 16 报告 §2 附记登记，待主线裁定，未静默修复。

## 终局对账（Phase 8 收官，2026-10-28，与实际文件逐项核对）

- **文档总数**：`files/` 共 22 个文件 = 编号交付 19 份（00、01、02、04–19；编号 03 从未使用）+ 台账 3 件（COVERAGE.md、OPEN-QUESTIONS.md、products.csv）。本轮新增：18-LAB-MANUAL.md（72 行）、19-FINAL-REPORT.md（295 行，24 章）。
- **products.csv（v0.5）**：54 行 = 1 表头 + 53 数据行，confidence 分布 **A 22 / B 13 / C 17 / U 1**（脚本统计）。Round 6 唯一改动为 OpenHands 行（core_scenario/official_evidence/notes 按 round6-gaps.md §3 回填：主仓现定位 Agent Canvas、SDK 已拆 software-agent-sdk、默认后端与隔离仍未核实），confidence B 不变，**分布与 Round 5 一致**。回填前备份：hidden_files/research/products.csv.bak-round6。
- **深研**：报告 **4 份**（OpenSandbox 主仓 04、OpenSandbox Fast 外仓 06、E2B runtime 07、Firecracker 12），按产品计 **3 个深研对象**（OpenSandbox 主仓+外仓计 1 个产品，与本台账既有口径一致）；另 gVisor **选读 1**（round5-C，三线定位 + Q12 结案，非全量深研，不计深研数）。
- **实验**：已执行 **1 批**（LAB-MINI，10 号报告）；原始数据 16 文件、脚本 12 个（ls 实测）；[SELF] 判定登记不变（通过 4 项 + 载体内部分通过 1 项 + 环境不具备 1 组）。
- **未解决问题 36 问终局分布**：已结案 **10**（Q1、Q8、Q11、Q12、Q13、Q14、Q18、Q25、Q28、Q31）/ 部分结案 **11**（Q2、Q3、Q4、Q6、Q7、Q9、Q10、Q16、Q19、Q21、Q22）/ 顺延 LAB-REF **6**（Q5、Q29、Q32、Q34、Q35、Q36）/ 冻结现状 **9**（Q15、Q17、Q20、Q23、Q24、Q26、Q27、Q30、Q33）；10+11+6+9=36，与 OPEN-QUESTIONS 编号总数一致。本轮变化：Q14 未开始→已结案（Round 6）、Q16 未开始→部分结案（Round 6，剩余子项拆分登记）。
- **设计类交付**：参考架构 5、选型场景 9、Mermaid 全局图 12（14 号 11 + 15 号 1，结构级检查完成、渲染级未验证）、90 天专家路线 1 份（17 号）。
- **待验证**：仍 13（已核实 35 中全部 B 行），与 Round 5 对账一致。
- 各计数互不合并：产品计数、实验计数、设计类计数、问题处置计数为四套独立口径，本段仅并列对账。
