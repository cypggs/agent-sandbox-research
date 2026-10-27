# 覆盖率台账（本研究口径，非市场规模）

更新：2026-10-27（Round 4 整合，products.csv v0.3 不变；新增实验计数段）
计数定义：候选=已发现未深核（仅存在性/二手线索，confidence C/U，notes 标「Round1新增候选,待深核」）/ 已核实=官网+仓库/文档至少一项一手核对 / 深研=完成案例 17 问或源码级 / 待验证=已核实但行 confidence 仍非 A（是已核实的子集，不另加总数）
**深研 = 2**：OpenSandbox（主仓 Round 2 深研 files/04 + Fast 外仓 Round 3 深研 files/06，主仓+外仓双深研完成，计 1 个产品）；E2B（Round 3 runtime 仓源码级深研，报告 files/07-E2B-RUNTIME-DEEP-DIVE.md，HEAD 92b83da）。

| 类别（按 01-TAXONOMY 主类，每行只计一次主类） | 候选 | 已核实 | 深研 | 待验证（已核实子集） | 该类行数小计 | 备注 |
|---|---|---|---|---|---|---|
| P1 专用 Agent Sandbox SaaS | 3 | 7 | 1 | 3 | 10 | 已核实：E2B、Daytona(SaaS)、Runloop、Microsandbox、Blaxel、AWS Lambda MicroVMs、GCP Agent Compute Engine。Round 2：Lambda MicroVMs 与 ACE 升 A（ACE 定价为「已确认未公布」不降级），待验证由 5 降至 3 = Daytona、Runloop、Microsandbox。Round 3：**深研 1 = E2B（runtime 仓源码级，files/07）**，行 confidence 本为 A 不变。候选：Freestyle、Morph Cloud、Upstash Box |
| P2 Secure Code Runner / Judge | 2 | 3 | 0 | 0 | 5 | 已核实：nsjail、isolate、Judge0；候选：Piston、llm-sandbox |
| P3 Browser Sandbox | 1 | 4 | 0 | 4 | 5 | 已核实：Browserbase、Browserless、Steel.dev、Hyperbrowser；候选：Kernel。四家已核实的隔离全部未公开，故待验证=4。Round 2：Browserbase 6h 上限维持 B 并降权（见 Q21），不改变本类计数 |
| P4 Computer Use / Desktop | 1 | 0 | 0 | 0 | 1 | 仅候选 E2B Desktop。本类仍是全表最薄弱处（见 02-ROUND1-REPORT） |
| P5 Cloud Dev Environment | 0 | 2 | 0 | 1 | 2 | 已核实：CodeSandbox SDK、Hugging Face Spaces。**HF Spaces 是邻域排除项（非 Agent Sandbox 反例）：计入行数对账，不计入 Sandbox 供给侧/竞品比较**，故 P5 实际 Sandbox 相关已核实只有 CodeSandbox SDK 1 条。待验证 1 = CodeSandbox SDK（隔离仅 B、定价时效风险高） |
| P6 通用云执行平台 | 0 | 9 | 0 | 5 | 9 | 已核实：Modal、Fly.io、Cloudflare Sandbox、Vercel Sandbox、Beam、Northflank、AWS Lambda、Azure Functions、GCP Cloud Run。Round 2：AWS Lambda 按官方 FAQ 升 A，待验证由 6 降至 5 = Fly.io、Beam、Northflank、Azure Functions、GCP Cloud Run。Modal 已按双运行时口径改写（Q18 已清），其行 confidence 本为 A 不在待验证内 |
| P7 Agent 平台内执行组件 | 0 | 2 | 0 | 1 | 2 | 已核实：OpenHands Runtime、AWS Bedrock AgentCore Code Interpreter。Round 2：AgentCore 定价/生命周期/microVM 隔离升 A（行 confidence 升 A；唯一保留 B 子项为 Firecracker 字样出处差异，见 Q10），待验证由 2 降至 1 = OpenHands Runtime（当前默认后端隔离为 C，待源码） |
| P8 开源自托管平台/控制面 | 3 | 2 | 1 | 0 | 5 | 已核实：OpenSandbox、GCP GKE Agent Sandbox。**深研 1 = OpenSandbox（Round 2 主仓源码级 + Round 3 Fast 外仓源码级，双深研完成）**。Round 2：GKE 按官方原文升 A（删除归纳价），待验证由 1 降至 0。候选：Kubernetes agent-sandbox (SIG)、AIO Sandbox (agent-infra)、CubeSandbox。注：Daytona OSS、E2B 开源组件、Microsandbox 开源部分虽带 P8 属性，主类已分别计入 P1，本表不双计（其 P8 属性写在 CSV category/notes 中） |
| 基础设施组件 (MicroVM/Wasm/安全容器/OS级) | 8 | 6 | 0 | 0 | 14 | 已核实：Firecracker、gVisor、Kata Containers、Cloud Hypervisor、Wasmtime、WasmEdge；候选：Google sandboxed-api、Dagger、Sysbox、Firejail、Bubblewrap、Hyperlight、Anthropic sandbox-runtime、firecracker-containerd。Round 2：Wasmtime license 逐字核结案升 A 口径（Q22）；Cloud Hypervisor 文档 CC-BY-4.0 已证、BSD-3-Clause 适用范围子项待核——按既有口径（待验证只计产品级关键字段），该子项缺口计入 OPEN-QUESTIONS Q22，不计入此处待验证 |
| **合计** | **18** | **35** | **2** | **14** | **53** | 与 products.csv v0.3 数据行数对账一致（见对账说明） |

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
