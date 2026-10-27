# 覆盖率台账（本研究口径，非市场规模）

更新：2026-10-27（Round 1 整合，products.csv v0.1）
计数定义：候选=已发现未深核（仅存在性/二手线索，confidence C/U，notes 标「Round1新增候选,待深核」）/ 已核实=官网+仓库/文档至少一项一手核对 / 深研=完成案例 17 问或源码级 / 待验证=已核实但关键字段仍 B/C/U（是已核实的子集，不另加总数）
**深研一律计 0**：Round 1 只做到核实层，未做任何源码级/17 问深研。

| 类别（按 01-TAXONOMY 主类，每行只计一次主类） | 候选 | 已核实 | 深研 | 待验证（已核实子集） | 该类行数小计 | 备注 |
|---|---|---|---|---|---|---|
| P1 专用 Agent Sandbox SaaS | 3 | 7 | 0 | 5 | 10 | 已核实：E2B、Daytona(SaaS)、Runloop、Microsandbox、Blaxel、AWS Lambda MicroVMs、GCP Agent Compute Engine(预览,半核实)；候选：Freestyle、Morph Cloud、Upstash Box。待验证 5 = Daytona、Runloop、Microsandbox、Lambda MicroVMs、ACE（隔离/定价/GA 状态未达 A） |
| P2 Secure Code Runner / Judge | 2 | 3 | 0 | 0 | 5 | 已核实：nsjail、isolate、Judge0；候选：Piston、llm-sandbox |
| P3 Browser Sandbox | 1 | 4 | 0 | 4 | 5 | 已核实：Browserbase、Browserless、Steel.dev、Hyperbrowser；候选：Kernel。四家已核实的隔离全部未公开，故待验证=4 |
| P4 Computer Use / Desktop | 1 | 0 | 0 | 0 | 1 | 仅候选 E2B Desktop。本类是全表最薄弱处，Round 2 优先补发现（见 02-ROUND1-REPORT） |
| P5 Cloud Dev Environment | 0 | 2 | 0 | 1 | 2 | 已核实：CodeSandbox SDK、Hugging Face Spaces。**HF Spaces 是邻域排除项（非 Agent Sandbox 反例）：计入行数对账，不计入 Sandbox 供给侧/竞品比较**，故 P5 实际 Sandbox 相关已核实只有 CodeSandbox SDK 1 条。待验证 1 = CodeSandbox SDK（隔离仅 B、定价时效风险高） |
| P6 通用云执行平台 | 0 | 9 | 0 | 6 | 9 | 已核实：Modal、Fly.io、Cloudflare Sandbox、Vercel Sandbox、Beam、Northflank、AWS Lambda、Azure Functions、GCP Cloud Run。待验证 6 = Fly.io、Beam、Northflank、AWS Lambda、Azure Functions、GCP Cloud Run（隔离无 A 级原文或定价未直核） |
| P7 Agent 平台内执行组件 | 0 | 2 | 0 | 2 | 2 | 已核实：OpenHands Runtime、AWS Bedrock AgentCore Code Interpreter。两者待验证：OpenHands 当前默认后端隔离为 C（待源码）、AgentCore 全部关键项为 B（待官方 docs 直引） |
| P8 开源自托管平台/控制面 | 3 | 2 | 0 | 1 | 5 | 已核实：OpenSandbox、GCP GKE Agent Sandbox(半核实 B)；候选：Kubernetes agent-sandbox (SIG)、AIO Sandbox (agent-infra)、CubeSandbox。待验证 1 = GKE Agent Sandbox。注：Daytona OSS、E2B 开源组件、Microsandbox 开源部分虽带 P8 属性，主类已分别计入 P1，本表不双计（其 P8 属性写在 CSV category/notes 中） |
| 基础设施组件 (MicroVM/Wasm/安全容器/OS级) | 8 | 6 | 0 | 0 | 14 | 已核实：Firecracker、gVisor、Kata Containers、Cloud Hypervisor、Wasmtime、WasmEdge；候选：Google sandboxed-api、Dagger、Sysbox、Firejail、Bubblewrap、Hyperlight、Anthropic sandbox-runtime、firecracker-containerd。六个已核实项的仓库/版本/license/自述隔离均为 A；其深层实现（快照原文、兼容清单、WasmEdge 安全文档等）缺口计入 OPEN-QUESTIONS，不计入此处待验证（口径：待验证只计产品级关键字段 B/C/U） |
| **合计** | **18** | **35** | **0** | **19** | **53** | 与 products.csv v0.1 数据行数对账一致（见对账说明） |

## 对账说明（2026-10-27，与 products.csv v0.1 逐项核对）

- products.csv 共 **54 行 = 1 表头 + 53 数据行**。本表合计行数 53，一致。
- 53 = 种子 23 条（已全部回填核实，不再计候选）+ Round 1 新增 30 条。
- 新增 30 = A 线新候选 14 + B 线新发现 9 + B 线云厂商拆分 7。
  - A 线候选 14：Piston、Google sandboxed-api、Kubernetes agent-sandbox (SIG)、Dagger、Sysbox、Firejail、Bubblewrap、Hyperlight、AIO Sandbox、Anthropic sandbox-runtime、firecracker-containerd、llm-sandbox、E2B Desktop、CubeSandbox。
  - B 线新发现 9：Blaxel、Beam、Northflank、CodeSandbox SDK、Hugging Face Spaces、Freestyle、Morph Cloud、Kernel、Upstash Box。其中前 5 个已核实，后 4 个为候选。
  - 云厂商拆分 7：AWS Lambda、AWS Lambda MicroVMs、AWS Bedrock AgentCore Code Interpreter、Azure Functions、GCP Cloud Run、GCP GKE Agent Sandbox、GCP Agent Compute Engine。拆分原因：三家云厂商的 Serverless 本体、MicroVM 原语、Agent 平台组件形态完全不同，禁止混为一个「云厂商 Sandbox」。
- 候选/已核实划分按 notes/status 口径，不按 confidence 单独划分（一处例外说明）：候选 18 = A 线 14 + B 线候选 4（Freestyle、Morph Cloud、Kernel、Upstash Box），均在 notes 标「Round1新增候选,待深核」；已核实 35 = 种子 23 + B 线已核实新发现 5 + 云厂商拆分 7。其中 GCP Agent Compute Engine 的 confidence 为 C（仅宣布+博客转述的预览项），但因 B 线已做形态/设计半核实，计入已核实（半核实）而非候选，并在其行内明确标「预览,未 GA,未定价」。
- confidence 分布（与 CSV 逐行一致）：A 16 / B 18 / C 18 / U 1（Kernel），合计 53。待验证 19 = 已核实 35 中 confidence 非 A 的行（B 18 中属已核实者 + ACE 的 C 1）；候选行的 C/U 不重复计入待验证。
- 不双计规则：一个产品只按主类计一次。Fly.io（Machines=P6 / Sprites=P1）、Vercel（P1 性质 / P6 主类）、E2B/Daytona/Microsandbox 的 P8 属性、GKE Agent Sandbox 的 P1/P8 双性，均只计主类，副属性在 CSV 中注明。
- 上一版（Round 0）台账为种子池 23 条全 U、各类计数为 0；本版替代之。种子池口径已关闭。
- 这些数字只说明本研究覆盖，不代表市场真实规模；禁止宣称"覆盖 100% 市场"。未覆盖清单见 02-ROUND1-REPORT.md 与 OPEN-QUESTIONS.md（Prized/Tensorlake/Deno Sandbox/LangSmith Sandboxes 等 20+ 仅登记未入表项不在本表计数内）。
