# 05 · Round 2 阶段报告：清证据债 + OpenSandbox 源码深研第 1 号

> 项目：Agent Sandbox 全领域技术研究（goal_a756da9ace9a）
> 阶段：Phase 2 产品数据库 v0.2；Phase 3 源码深研启动（1/53）
> 日期：2026-10-27（Asia/Shanghai）｜ 证据等级：A 官方/源码/论文 · B 可靠独立 · C 推断待验证 · U 未知
> 输入底稿：hidden_files/research/round2-A-evidence-debt.md、files/04-OPENSANDBOX-DEEP-DIVE.md（HEAD `dbcc6d7`）、hidden_files/research/round2-B-opensandbox-log.md
> 本轮仍无任何自测数据（SELF=0）：所有性能数字均为官方公布值并已标注；OpenSandbox 未做部署实测。

## 1. 执行摘要

### 1.1 证据债：5 笔中 2 笔全清、3 笔部分清、0 笔原样维持（维持的是子项，不是整笔）

| 债项 | 结果 | 要点 |
|---|---|---|
| Q11 OWASP + 5 CVE | **全清** | 2025 版五条编号与 5 个 CVE 逐条回 genai.owasp.org / nvd.nist.gov 原文升 A。附带发现破坏性变更：**2026 版已发布且大改编号**，全项目新增规则「OWASP 引用必须带年份」（见 §3 与 Q31） |
| Q18 Modal VM Sandboxes | **全清（含改写旧结论）** | 官方原文证实双运行时（gVisor / VM-KVM），Round 1 的"默认 gVisor"写法已被官方现行 docs 取代，CSV 已整段改写（见 §3） |
| Q10 云厂商 A 级原文 | **部分清** | AWS 三项（Lambda 本体、Lambda MicroVMs、AgentCore）与 GKE 升 A；保留三处：ACE 定价为官方确认未公布（非缺证）、AgentCore 的 Firecracker 字样维持 B（出处差异）、Azure 本轮未做 |
| Q21 生命周期直引 | **部分清** | Daytona auto-stop 15min 找到官方原文升 A；Browserbase 6h 在现行官方渠道已不存在，维持 B 并降权（见 §3） |
| Q22 license 逐字核 | **部分清** | Wasmtime 完整 SPDX 结案升 A；Cloud Hypervisor 的 CC-BY-4.0 文档范围与 Apache 文件集已证，BSD-3-Clause 适用范围维持待核 |

数据库净效果：products.csv 仍 53 行，confidence 分布由 A16/B18/C18/U1 变为 **A 21 / B 14 / C 17 / U 1**（升 A 的 5 行：AWS Lambda、Lambda MicroVMs、AgentCore Code Interpreter、GKE Agent Sandbox、Agent Compute Engine）；待验证（已核实中非 A）由 19 降至 14。详见 COVERAGE.md Round 2 对账。

### 1.2 OpenSandbox 深研（深研第 1 号，主仓 HEAD `dbcc6d7`）：9 证实 / 2 修正 / 1 未证实

对 2026-10-23 旧笔记 12 条假设逐条回当前源码复核（04 报告 §10）：**证实 9、修正 2、未证实 1、证伪 0**。

核心结论：
1. **本仓 = 协议 + 控制面 + 容器数据面，不是完整 MicroVM 运行时**：生命周期服务、三后端分发、execd、egress、ingress、K8s operator 都在本仓；Fast Sandbox 的 Firecracker 运行时在外仓 `opensandbox-group/fast-sandbox`，本仓只有 gRPC 客户端/适配层/CR 读取。深研本仓回答得了控制面与容器路径，回答不了 Fastlet 内部（Q28）。[A]
2. **两处修正必须带路径引用**：① egress "per-sandbox sidecar 持 NET_ADMIN" 只对容器路径成立，Fast 路径是每 Fastlet 一个共享 egress 进程、per-subject 策略；② "Vault 只活内存" 只对容器路径成立，Fast 路径多一份每沙箱明文 v1 vault 文件落 Pod emptyDir（源码 `TODO(encryption-at-rest)`，Q30）。[A]
3. **64ms 与 62s 的口径警告**：Firecracker 创建 64.0ms P50 出自官方 2026-10-08 双节点 ACK 实测（暖池、模板已缓存、串行、终点 = guest `/ping` 200）；同一份官方实测里 SDK 口径 resume 约 62.66s（运行时恢复本身仅约 35ms，差距在端点/网关就绪，**官方自己标为未解**并警告不得混用）；且并发 20 时 100 次创建只成功 51 次（48 次 429 容量拒绝）。任何只引 64ms 的转述都是误导。[A：官方公布，未实测]
4. **元数据阻断非默认**：egress 机制本身是本项目最硬的部分（sidecar 独占 NET_ADMIN、L1 DNS + L2 dns+nft 默认拒绝、平台 overlay 压过用户策略、fail-closed），但全仓 egress 代码**没有硬编码的云元数据/内网 CIDR 阻断**——内网隔离靠运维按官方指南自写 `deny.always` 配方。机制强、默认弱，评测必须按实际部署测，不能按产品名下结论（Q29）。[A]
5. **与 E2B 无关**：全仓对 "e2b" 只有 2 处文档层对照提及，无兼容层、无 API 映射、无 SDK 互操作承诺；概念相似属同题 convergent design。从 E2B 迁移 = 按新 API 重写集成。[A]
6. 未证实 1 条即"Fast 运行时可在本仓审计"——不成立，本仓外实现一律按文档转述并标 U。

## 2. CSV 变更清单（products.csv v0.1 → v0.2，行数不变 53）

| 产品行 | 变更字段 | 变更内容 | 依据 |
|---|---|---|---|
| Modal | isolation_tech（整段改写）、network_control、strengths、limitations、notes | 双运行时口径：gVisor / VM（KVM 硬件虚拟化），runtime 参数选择、未设由 Modal 选择，GPU 仅 gVisor；删除"默认 gVisor"与"VM Beta 仅 C"；allowlist 升为正式能力 | 官方 docs Sandboxes/Networking + 2026-06-15 产品更新（A） |
| GCP GKE Agent Sandbox | pricing、isolation_tech、network_control、status、official_evidence、confidence B→A | **删除 $0.0445 归纳价**，改官方原文 "no extra charge, GKE pricing applies"；隔离升 A（gVisor 为主 + Kata + Default Deny） | 官方概念页 + how-to Costs 节（A） |
| AWS Lambda MicroVMs | isolation_tech、pricing、lifecycle、status、docs_url、official_evidence、confidence B→A | Firecracker 与 Graviton 单价升 A；**8h 修正为含挂起的总寿命**（非纯运行时长）；区域数子项注明 B | 开发者指南 + 官方价表算例 + FAQ（A） |
| AWS Bedrock AgentCore Code Interpreter | pricing、lifecycle、filesystem、status、official_evidence、confidence B→A | 定价（$0.0895/vCPU·h + $0.00945/GB·h）与生命周期（默认 900s、可配至 8h）升 A；microVM 隔离升 A；Firecracker 字样维持 B 并注明出处差异 | 官方价表 + Developer Guide/API（A） |
| AWS Lambda | isolation_tech、lifecycle、pricing、docs_url、official_evidence、confidence B→A | 隔离按 FAQ 原文升 A（原文在 FAQ 页不在 pricing 页，Round 1 缺口关闭）；单次 15min 升 A | 官方 FAQ + 价表（A） |
| GCP Agent Compute Engine | status、isolation_tech、network_control、credential_security、filesystem、pricing、official_evidence、confidence C→A | 状态/隔离升 A（单租户 microVM、Cloud Hypervisor boundary、Titanium、virtio-vsock、零秘密）；定价写"官方确认尚未公布"（两篇官方原文均无价格） | 官方公告 + deep dive（A） |
| Daytona | isolation_tech、lifecycle、notes | 补官方自述"默认 Linux containers"（runtime 名仍 U）；auto-stop 15min 由官方 docs 原文升 A | 官方 docs Sandboxes 页（A） |
| Browserbase | lifecycle、notes | 6h 上限改写为"现行官方未载明、仅第三方、疑旧版数字"，维持 B 并降权 | 现行 pricing/docs 复核（原文未找到，如实记录尝试路径） |
| Wasmtime | license、notes | license 改 `Apache-2.0 WITH LLVM-exception` 升 A，Q22 结案 | 仓库 LICENSE 原文 + 根 Cargo.toml（A） |
| Cloud Hypervisor | license、notes | 改写为 Apache 文件集 + CC-BY-4.0 文档（dep5 已证）；BSD-3-Clause 范围维持待核并写清 | LICENSES/ + .reuse/dep5（A，BSD 部分除外） |
| OpenSandbox | 除 name/category/site/github 外几乎全部字段 | 按 04 深研回填：双运行时 + secure_runtime 分档、lifecycle 三路、三套 checkpoint、network_control 按 sidecar/Fast 两路径分开写、credential_security 写 Vault 两路径差异（含 Fast 明文 v1 文件 + TODO）、limitations 写入元数据非默认 / resume 约 62s 官方未解 / snapshot 端点 501、official_evidence 写源码路径、notes 标"Round 2 源码深研完成（主仓），Fast 外仓未读" | 主仓源码 HEAD dbcc6d7（A） |

## 3. 冲突与旧结论改写清单（本轮最重要产出：防止旧结论继续流通）

| # | 旧结论（Round 1 及更早） | Round 2 裁决 | 依据 |
|---|---|---|---|
| 1 | Modal "默认 gVisor（A），VM 仅 Beta 转述（C）" | **改写**：双运行时并列，未设 runtime 时由 Modal 选择；官方已不声明 gVisor 为默认。硬说默认在原文层面不成立 | Modal 现行 docs（A） |
| 2 | GKE Agent Sandbox 定价 "$0.0445/vCPU·h（Autopilot 归纳，B）" | **删除**：该数字是把 GKE 通用资源价当产品价，口径错误。官方原文为无附加费、按 GKE 资源计价 | 官方 how-to Costs 节（A） |
| 3 | Browserbase "付费 session 6h 上限（B 多源一致）" | **降权**：现行官方 pricing/compare/docs 已无此数字，6h 仅存于第三方评测，疑为旧版页面数字；不得再当现行事实上限引用 | 现行官方页复核（原文未找到） |
| 4 | Lambda MicroVMs "最长 8h" | **口径修正**：8h 是含挂起的总寿命（running + suspended），不是纯运行时长 | 官方 FAQ（A） |
| 5 | AgentCore Code Interpreter "Firecracker microVM per-session（B）" | **部分改写**：microVM per-session 升 A；Firecracker 一词在 CI 自身文档无原文（仅 Runtime 的 harness 安全文档有），该词维持 B 并注明出处差异 | 官方价表/DevGuide vs harness-security 文档（A/B） |
| 6 | OpenSandbox "egress 是 per-sandbox sidecar"（2026-10-23 笔记全称表述） | **修正**：仅容器路径成立；Fast 路径为 per-Fastlet 共享进程 + per-subject 策略 | 主仓源码（A） |
| 7 | OpenSandbox "Vault 只活 sidecar 内存"（同上） | **修正**：仅容器路径成立；Fast 路径有明文 v1 文件落 emptyDir（TODO encryption-at-rest） | 主仓源码（A） |
| 8 | OWASP 编号不带年份的引用习惯（D 线底稿） | **立规**：2026 版已发布且大改号（Excessive Agency 06→03、Supply Chain 03→04、Unbounded Consumption 10→06、System Prompt Leakage→Hidden Context Exposure 08）；自本轮起不带年份的 OWASP 编号视为错误引用。威胁矩阵迁移方针见 Q31（双标注，不单方面改号） | genai.owasp.org 官网（A；2026 全表逐条为 A-/B+） |
| 9 | Lambda 隔离 "Firecracker 为业界共识（B）" | **关闭缺口**：官方 FAQ 有 dedicated Firecracker microVM 原文，升 A；教训是原文位置不在 pricing 页 | 官方 FAQ（A） |
| 10 | Fly 之外 P6 隔离证据的悲观判断（Round 1 报告 §1.2） | **收窄**：AWS/GCP 两家的新原语隔离原文已补齐；Fly 的 Firecracker 实现名仍为 B（不在本轮范围，未动） | 本轮 Q10 结果 |

## 4. 未验证项（明确未清，不许当已清引用）

- **Fast 运行时内部实现**：`opensandbox-group/fast-sandbox` 未克隆未读（Q28）。04 报告中所有 Fast 内部结论为 [A 文档 / U 源码]。
- **OpenSandbox 未部署实测**：本轮只读源码，未运行任何 OpenSandbox 部署；64ms/62s 等数字全部是官方公布未实测；元数据配方有效性未验（Q29）。
- **Browserbase session 上限**：官方原文路径已穷尽，再核只能实测/销售确认（Q21 保留）。
- **Cloud Hypervisor BSD-3-Clause 适用范围**：dep5 无条目，待 grep 源文件头（Q22 保留）。
- **AgentCore Code Interpreter 的 Firecracker 自证**：等 AWS 在 CI 文档点名或官方支持渠道确认（Q10 保留）。
- **Azure 对位产品**：本轮明确未做（Q19 保留）；ACE 的 GA 时间官方未给。
- **OWASP 2026 版 PDF 全文**：未逐字打开，全表逐条为 A-/B+；D 线底稿（round1-D）的来源等级回改与双标注执行（A 线建议第 11 条）尚未落到 D 线文件，登记在 Q31 待 Round 3 执行。
- 其余 Round 1 遗留未动：gVisor 兼容清单（Q12）、Firecracker snapshot 官方原文（Q13，仅有 OpenSandbox 旁证）、WasmEdge 安全文档（Q14）、Microsandbox VMM（Q15）、OpenHands 新仓（Q16）、五家隔离未公开（Q9）、P4 发现轮、候选池消化（Q26/Q27）。全项目实验仍为 0 次执行，SELF 数据仍为 0。

## 5. Round 3 建议（排序与理由）

1. **Fast 外仓深研（opensandbox-group/fast-sandbox）**。理由：OpenSandbox 深研只完成了主仓一半，Fast 是其最强隔离档与关键性能数字的产生处，且刚建立的主仓参照系（FastPath 客户端、CR、policy/vault relay）正好是读外仓的地图，边际成本全场最低；顺带可能直接推进 Q13（快照实现）与 Q30（vault 文件格式）。不先补这一号，"深研 1"的成色会被持续打折。
2. **E2B runtime 深研（e2b-dev/runtime）**。理由：Round 1 原定源码深研第 2 号，生产级 Firecracker 编排的一手样本（orchestrator/envd/API 链路），且直接回答 Q1（Embed 自托管与云服务隔离是否一致）——这是 Cassia 选型最相关的一个未答问题。排在 Fast 之后是因为两者同为 Firecracker 编排样本，先读完 OpenSandbox 全栈再读 E2B，对照框架更完整。
3. **实验室第一批（阈值冻结 → 最小实验）**。理由：全项目至今 SELF=0，文献与源码证据已足够支撑第一批无害实验：先冻结 Q25（C 组通过线、任务套件 v0.1），再执行 namespace/seccomp 探针、超时后进程清零（C4）、网络策略矩阵（C8）三项，并把 OpenSandbox 元数据配方验证（Q29）并入 C8 在自建集群执行。排在深研之后是因为实验设计需要参照实现细节（egress 软点、降级模式）才测得准。
4. **五家隔离未公开攻坚（Runloop + 四家 Browser SaaS，Q9）**。理由：顺序天然在后——先穷尽各家安全文档/信任中心（低成本），仍无表述的转实验室以 C8 矩阵自测会话隔离与元数据可达性，而 C8 能力正是第 3 项的产出；且 Browser 类还连带 Q6（SSRF/元数据默认策略），一次攻坚同时推进两问。

Round 3 之后的既有队列不变：Firecracker 深研（含 Q13 原文）、gVisor 选读（含 Q12）、P4 Computer Use 发现轮、候选池消化（Q26/Q27）、选型框架与 90 天路线。

## 6. 本轮纪律自检

- 证据债逐项回原文结案：OWASP/NVD/LICENSE/dep5/官方 docs 与价表均给 URL 与原文要点；抓不到的（Browserbase 6h、CH 的 BSD 范围、ACE 定价）如实写"未找到/未公布"及尝试路径，没有用二手转述结案。
- 旧结论改写不留暗坑：Modal 默认、GKE 归纳价、Browserbase 6h、Lambda 8h 口径四处均在 CSV 与本报告 §3 双写，引用旧版报告时能看到裁决。
- 深研结论锚定版本：OpenSandbox 全部结论锚定 HEAD `dbcc6d7`（2026-10-27），仓库日更，引用前须复核文件漂移（04 报告 §14）。
- 未宣称覆盖完整：深研 1/53、实验 0 次、SELF 数据 0；未清项逐项登记（OPEN-QUESTIONS 现 31 问，Round 2 新增 Q28–Q31）。
