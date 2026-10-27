# 02 · Round 1 阶段报告：产业扫描与数据库 v0.1

> 项目：Agent Sandbox 全领域技术研究（goal_a756da9ace9a）
> 阶段：Phase 1 第一轮产业扫描完成；Phase 2 产品数据库 v0.1 已产出、持续进行中
> 日期：2026-10-27（Asia/Shanghai）｜ 证据等级：A 官方/源码/论文 · B 可靠独立 · C 推断待验证 · U 未知
> 输入底稿：hidden_files/research/round1-A-opensource.md、round1-B-saas.md、round1-C-principles.md、round1-D-threat-bench.md
> 本报告只做整合与判断，所有事实均可回溯到底稿；本轮无任何自测数据（SELF=0），所有性能数字均为官方公布值并已标注。

## 1. 执行摘要（领域阶段判断，均带证据等级）

1. **专用 Agent Sandbox 已从"容器包一层 API"分化为以 MicroVM/硬件隔离为默认卖点的独立品类，但证据透明度两极分化。** E2B（Firecracker/每 session 独立内核）、Vercel Sandbox（Firecracker+专用内核）、Microsandbox（microVM+独立内核）、Blaxel（hardware-isolated microVM）的隔离均有官方一手表述（A）；而同属 P1 的 Runloop 隔离完全未公开（U），Daytona 只公开"容器+VM 并存"的分类、runtime 细节未公开（U）。判断：品类已成型（A 级产品证据），但"用 MicroVM"正在变成营销标配词，只有给出 VMM 名、每会话边界与网络/凭证机制的一手表述才可采信。[A/U 对照，见 products.csv]
2. **云厂商在 2025-2026 集中下场推出专用原语，供给格局正在重写，但多数还没到可比价阶段。** AWS Lambda MicroVMs、Bedrock AgentCore Code Interpreter、GKE Agent Sandbox、GCP Agent Compute Engine（2026-10-22 宣布、预览未定价）均为本轮新拆分入表项，其隔离/定价目前主要是 B 级归纳，A 级原文普遍缺失。[B] 与之对照，Cloudflare Sandbox（VM-based isolation）与 Vercel 的隔离证据已达 A。判断：云厂商原语是 Round 2 证据补强的最大缺口，也是潜在的格局变量。[B/C]
3. **Browser SaaS 是全领域透明度最差的类别。** Browserbase、Browserless、Steel、Hyperbrowser 四家的定价/并发均可 A 级核实，但四家底层租户隔离全部未公开（U），内网/元数据默认策略无一家给出证据。定价可比、隔离不可比——该类别当前无法做有证据的安全选型。[A（定价）/ U（隔离）]
4. **开源侧出现控制面收敛信号。** OpenSandbox 迁入 Agentic AI Foundation（AAIF）、v1.1.1 且当日活跃，提供 Docker/K8s+Firecracker 双运行时与统一 API（A）；Kubernetes SIG 的 agent-sandbox CRD 以候选入表（C）。判断：K8s 原生 Sandbox 编排可能成为自托管路线的标准层，值得源码级跟踪。[A/C]
5. **计费模型碎片化到了"不可直接排序"的程度。** 已核实的计费单位至少有：按 vCPU·秒（E2B）、按 GB RAM·秒（Blaxel）、按 core·秒且 1 core=2 vCPU（Modal）、browser hour（Browserbase）、30 秒 Unit（Browserless）、credit（Hyperbrowser/CodeSandbox）、实际用量 CPU·h（Fly Sprites）。B 线已证明各家 vCPU 定义互不一致。任何跨家比价必须先声明换算假设，否则即是错误结论。[A，源自各家官方 pricing 原文]
6. **原理与威胁侧的底稿已可支撑后续选型，但全部实验未执行。** C 线以 24 条 A 级证据（官方文档/论文）钉死了 Linux 隔离、MicroVM、gVisor、Wasm、Chromium 五个专题的机制边界；D 线给出 25 条威胁（九字段齐全）与 32 条可复现评测指标。两线的共同结论（底稿级，C）：隔离路线主要决定逃逸/内核类威胁（T04-T08、T21、T22）的上限，网络类（T09-T12）与 Agent 类（T19、T20）取决于平台策略与 Harness 授权层，换隔离技术不自动改善。[C，待跨线验证与实测]

## 2. 四线成果与关键发现

### 线 A · 开源项目发现
- 种子 16/16 全部一手核实（gh API：archived/license/release/最近 commit + README 原文）。状态异常 1 个：**Daytona OSS 已归档**。仓库更名/重定向 4 处（见 §3）。
- 新候选 14 个全部入表（C 级）：优先序建议 kubernetes-sigs/agent-sandbox、CubeSandbox、anthropics/sandbox-runtime、agent-infra/sandbox、Hyperlight。
- 关键发现：Judge0"版本停滞与开发活跃并存"、isolate 无 Release、Browserless 双许可非 OSI 开源、OpenHands 定位转 Agent Canvas 且 runtime 疑似拆仓——四者都会让按旧资料引用的人写出错误结论。

### 线 B · 商业 SaaS
- 24 个产品/服务核实（种子 12 + 云厂商 3 组拆 7 项 + 新发现 9 家），其中 HF Spaces 判定为非 Agent Sandbox 反例并按此入表（P5 邻域排除）。
- 隔离达 A 的：E2B、Modal（gVisor 默认）、Cloudflare、Vercel、Microsandbox、Blaxel、Sprites（定性 A-）、Northflank（厂商自述 A-）。隔离未公开的 5 家：Runloop + 四家浏览器 SaaS。
- 旧价污染实证：Fly Sprites 旧价、Steel legacy 套餐、CodeSandbox 旧 credit 价均已被官网现页覆盖，引用二手对比文必错（详见 §3）。

### 线 C · 底层原理
- 5 个专题、24 条 A 级证据、0 条编造数字。确立的机制结论包括：namespace 是视图隔离非安全边界、seccomp 官方原文"isn't a sandbox"、CAP_SYS_ADMIN 的 overloaded 陷阱、gVisor Sentry 不透传 syscall 与 Gofer 纵深、WASI 无环境权威与能力模型、Chromium 站点隔离与 `--no-sandbox` 一票否决项。
- 明确缺口（已移交 OPEN-QUESTIONS 第 12-14、24 问）：Firecracker snapshot 官方原文、gVisor 现行兼容清单、WasmEdge 安全文档、发行版 user-ns 默认策略。

### 线 D · 威胁模型与评测设计
- 威胁 25 条（spec 23 类全覆盖 + 快照/复用拆分 + 浏览器/GUI 补充），每条九字段；来源锚点为 OWASP LLM Top 10 (2025)、MITRE ATT&CK T1611、CWE-78/22/918、AWS IMDS 与 Firecracker/gVisor/Wasmtime/Chromium 官方文档。其中 OWASP 与 5 个 CVE 编号尚为 B（未逐条回 NVD/OWASP 原文），已列为 Round 2 最先清的低成本项（OPEN-QUESTIONS 第 11 问）。
- 评测 32 条指标（启动/运行/隔离可靠性/成本各 8）全部只有定义与方法，无数字；对照组 G0-G6、统计口径（nearest-rank、n≥300 才报 P99、四标签 [OFFICIAL]/[THIRD-PARTY]/[SELF]/[ESTIMATE]）已设计完毕，阈值待主线冻结（第 25 问）。

## 3. 冲突与纠错清单（Round 1 已裁决，CSV 已按裁决写入）

| # | 冲突/错误 | 裁决 | 依据 |
|---|---|---|---|
| 1 | 仓库更名 4 处：E2B infra→runtime、OpenSandbox alibaba→opensandbox-group、Microsandbox microsandbox/zerocore-ai→superradcompany、OpenHands All-Hands-AI→OpenHands | CSV 一律写新址并注明旧名 | A 线 gh API 重定向确认（A） |
| 2 | Daytona 状态：B 线底稿称"未直接核 GitHub、标 C 待 A 线复核" vs A 线已用 gh API 证实 archived | 以 A 线为准：OSS 已归档（A）；B 线的保留意见已过时 | A 线 gh API + README 置顶声明（A） |
| 3 | Daytona license：主分支 license API 404 vs v0.190.0 标签 LICENSE 全文 | 写 AGPL-3.0 并注明版本标签口径 | A 线标签下 LICENSE 原文（A） |
| 4 | Fly Sprites 旧价 $0.07/CPU·h + $0.04375/GB·h（多处旧资料）vs 现官网页 $0.0385 + $0.021875 | 用现页价并注明旧价作废 | B 线官网现页（A） |
| 5 | Steel 旧套餐（$29/$99 等按 hours 捆绑）vs 现定价页（Launch $0+usage / Scale $250） | 用现价；官方 FAQ 已称旧套餐 legacy | B 线官方 docs（A） |
| 6 | CodeSandbox credit 旧价 $0.018 vs 现 $0.01486 | 用现价并标注时效风险最高 | B 线官方博客（A-） |
| 7 | Northflank BYOC 平台费 $0.02083（pricing 页）vs $0.01389（其博客） | 以 pricing 页为准，冲突记入 CSV 与第 20 问 | B 线官网 pricing（A） |
| 8 | Blaxel scale-to-zero：同页 FAQ 5s vs 15s（网络无活动）两数字并存 | CSV 两写并注明段落口径，不擅自取一 | B 线官网 pricing 页内冲突（A 级页面、C 级结论） |
| 9 | Modal 定价：主 pricing 页 sandbox 单价抓取为空 vs 官方 LP 页明示 $0.00003942/core·s 等 | 两页互证后标 A- 写入 | B 线双页互证 |
| 10 | Modal 隔离：二手称 2026-06 推出 VM Sandboxes vs 官方 LP 的 gVisor 默认 | 默认结论维持 gVisor（A）；VM Beta 记 C 待官方原文，不覆盖默认 | B 线（见第 18 问） |
| 11 | Firecracker license：种子表记 Apache-2.0/MIT | 纠正为仅 Apache-2.0 | A 线 gh API（A） |
| 12 | Cloud Hypervisor license：API 返回 null 易误判"无许可" | 写 Apache-2.0/BSD-3-Clause 双许可（LICENSES/ 目录） | A 线目录原文（A） |
| 13 | Browserless"开源"定性：实为 SSPL-1.0 OR 商业双许可，SSPL 非 OSI 开源 | CSV 标注 source-available/双许可；分类修订建议已记 | A 线 LICENSE 原文（A） |
| 14 | Judge0 版本：写"最新 v1.13.1"会被读成停更，写"活跃"又掩盖 release 停滞 | CSV 同时写 release 日期（2024-04-18）与最近 commit（2026-10-26），双口径并列 | A 线 gh API（A） |
| 15 | OpenSandbox 仓库 created_at=2025-12-17 与"阿里开源"时间线表面冲突 | 判定为仓库迁移/重建口径（两路径同一仓），早期历史待官方公告交叉验证（B），不据此否定项目 | A 线 gh API |
| 16 | 候选发现中的 404 纠错：microsoft/hyperlight、anthropic/sandbox-runtime(单数)、modelscope/sandbox-fusion | 前两者正确仓为 hyperlight-dev/hyperlight、anthropics/sandbox-runtime（已入表）；Sandbox Fusion 正确仓名未定位（U，第 17 问） | A 线 gh 查询 |
| 17 | Cloudflare Sandbox 易被误写为"V8 isolate/普通容器" | 写 VM-based isolation（VM 边界内 Ubuntu 容器形态）；V8 isolate 是 Workers 本体、不同产品 | B 线官方架构页（A） |
| 18 | Wasmtime SPDX：API 简化显示 Apache-2.0 vs 通行完整写法 Apache-2.0 WITH LLVM-exception | CSV 注明待逐字复核，不影响分类 | A 线存疑项（第 22 问） |

未裁决而保留双口径的：Blaxel 5s/15s（#8）、Modal VM Beta（#10）——均已在 CSV 注明并挂 OPEN-QUESTIONS，不假装已解决。

## 4. 已覆盖 / 未覆盖清单

**已覆盖（核实层）**
- 产品数据库 v0.1：53 行（种子 23 全回填 + 新增 30），计数与 COVERAGE 逐类对账一致；深研 0。
- 搜索域：A 线覆盖 MicroVM/Container/Wasm/Untrusted/Secure Code Execution/Cloud Agent Runtime（开源部分）；B 线覆盖商业 SaaS 与云厂商。14 个搜索域中，Browser Sandbox、Computer Use、Serverless、AI Coding Agent Runtime、Cloud Dev Environment、多租户执行基础设施均已有入表项，但深度不均（见下）。
- 原理专题 5/5（Linux、MicroVM、gVisor、Wasm、浏览器/GUI）；威胁 25 条；评测指标 32 条设计。

**未覆盖 / 薄弱（Round 2 输入）**
- P4 Computer Use/Desktop：仅 1 个候选（E2B Desktop），OSWorld 类环境、云桌面厂商、Anthropic Computer Use 参考实现均未入表——全表最薄弱类。
- 源码深研：0/53。所有"隔离技术"目前最高只到 README/文档自述（A 级自述 ≠ 实现证据）。
- 实验：0 次执行。C/D 两线共约 15 个实验设想全部待执行；无任何 [SELF] 数据。
- B 线仅登记未入表的 20+ 候选（Prized、Tensorlake、Deno Sandbox、LangSmith Sandboxes、Prime Intellect、exe.dev、OpenComputer 等，见第 27 问）与浏览器邻域（Anchor Browser、Browser Use Cloud 等）。
- 基础设施同域未核：crosvm、QEMU/microvm、Wasmer、Spin、wasmCloud、KubeVirt（第 26 问）。
- 云厂商对位未核：Azure Container Apps/Foundry Hosted Agents、DigitalOcean Managed Agents、AgentCore 的 Browser/Runtime 其他组件（第 19 问）。
- 论文/原型类未系统检索（OSWorld 等评测环境、学术 MicroVM/Wasm 原型）。
- 深挖维度未做：各 SaaS 的 egress 粒度、快照一致性、GPU 矩阵、合规证书（SOC2/HIPAA）原文、区域/数据驻留、BYOC 真实运维成本。

## 5. Round 2 最高价值任务建议（按序）

1. **低成本升 A 清债（先做，1 轮内可清）**：OPEN-QUESTIONS 第 11 问（OWASP/NVD 回原文）、第 22 问（两个 license 逐字核）、第 21 问（Browserbase 6h、Daytona auto-stop 官方直引）、第 18 问（Modal VM Beta 官方原文）、第 10 问（云厂商隔离/价表 A 级原文，至少 AWS 三项与 GKE）。理由：这些是已入表结论的证据等级问题，不清债则 Round 2 的对比与选型会建在 B 级地基上。
2. **源码深研第一梯队（本项目的 L3 核心）**，优先序与理由：
   - **第 1：OpenSandbox**。唯一同时具备"统一 Sandbox API 控制面 + Docker/K8s 与 Firecracker 双运行时 + egress/Credential Vault"的开源实现，与自建平台（及 Cassia 选型）的架构问题一一对应；仓库当日活跃、规模可控（v1.1.1），创建→执行→回收调用链可完整追踪；同时回答第 3 问（spec vs 实现、与 E2B API 关系）。
   - **第 2：E2B runtime（e2b-dev/runtime）**。生产级 Firecracker 编排的一手样本（orchestrator/envd/API 链路已由 README 证实），且直接回答第 1 问（Embed 自托管与云服务是否一致）。排在 OpenSandbox 之后是因为其 infra 仓规模与部署耦合更大，先用 OpenSandbox 建立控制面参照系再读它，成本更低。
   - **第 3：Firecracker**。前两者共同的底座：设备模型、jailer、snapshot 三个专题决定所有 MicroVM 结论的下限；代码聚焦（Rust、单 VMM），且可一并清第 13 问（snapshot 官方原文+恢复后熵处理）。若 Round 2 目标改为"先钉隔离原语再看平台"，本项可与第 2 互换，但不建议越过 OpenSandbox——控制面问题（调度、生命周期、凭证）才是本项目最终要自建的部分。
   - **第 4：gVisor（选读）**。Sentry/Gofer 的完整实现是四个候选中代码量与概念密度最高的，且其价值主要是理解"第二内核"路线与 Modal/GKE 的默认运行时；建议只追 Sentry 的 syscall 拦截链、Gofer 协议与 Systrap 平台三条线，并顺带清第 12 问（兼容清单），不做全仓通读。
3. **P4 发现轮**：Computer Use/Desktop 专项扫描（E2B Desktop 核实 + OSWorld 类评测环境 + Anthropic 参考实现 + 云桌面厂商的形态判定），把 P4 从 1 个候选提升到可分类状态。
4. **五家隔离未公开厂商的证据攻坚**（第 9 问）：Runloop 与四家浏览器 SaaS——先穷尽安全文档/信任中心，仍无表述的转入实验室以 C8 矩阵自测其会话隔离与元数据可达性，结果标 [SELF]。
5. **实验室启动与阈值冻结**：先冻结第 25 问（C 组通过线、任务套件 v0.1），再执行 C 线/D 线最小实验的第一批（namespace/seccomp 探针、超时后进程清零 C4、网络矩阵 C8）——这是全项目从"文献研究"转入"可复现证据"的关口，应在源码深研之后、选型框架之前完成第一批。
6. **候选池消化**：A 线候选优先序（k8s agent-sandbox、CubeSandbox、sandbox-runtime、AIO Sandbox、Hyperlight）逐个从 C 升核实；B 线 20+ 登记候选做形态判定入表或排除（第 26、27 问）。

## 6. 本轮纪律自检

- 未用推测补全任何字段：CSV 中底稿没有的字段一律"未验证/未公开"，共识性说法（Fly/Lambda 的 Firecracker、Cloud Run 的 gVisor）均降格标注为 B 并注明官方未述。
- 未把官方公布值写成实测：4 处启动/恢复数字全部带 [OFFICIAL 官方公布未实测] 前缀。
- 未宣称市场覆盖完整：53 行只是本研究台账，缺口已逐项登记（OPEN-QUESTIONS 共 27 问，其中 Round 1 新增 19 问）。
- 底稿间冲突未被掩盖：共 18 项列入 §3，其中 16 项已裁决、2 项保留双口径。
