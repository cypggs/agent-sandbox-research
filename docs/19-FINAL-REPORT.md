# 19 · 最终总报告：Agent Sandbox 全领域技术研究

> 项目：Agent Sandbox 全领域技术研究、产业图谱与专家知识体系（goal_a756da9ace9a）
> 收官日期：2026-10-28（Asia/Shanghai）｜ 执行跨度：2026-10-27 – 2026-10-28（Round 1–6 + Phase 6/7 + Phase 8）
> 结构：按用户 spec §24 的 24 章。每章为**综合结论 + 指针**，不复制原文；事实以各编号文件为准。
> 证据等级：A 官方/源码/论文/可复现实验 · B 可靠独立来源 · C 推断待验证 · U 未知。性能数字标签：[OFFICIAL]/[THIRD-PARTY]/[SELF]/[ESTIMATE]。
> 纪律声明：本报告不宣称覆盖 100% 市场；不使用无定义评分；C/U 不当事实陈述；缺数据处写「未验证/未公开」。

## 1. 执行摘要

1. **品类已成型，证据透明度两极分化。** 专用 Agent Sandbox 已从「容器包一层 API」分化为以 MicroVM/硬件隔离为默认卖点的独立品类；但同类产品间一手证据差距极大：E2B、Browserbase 的隔离有官方明文（A），Hyperbrowser 六渠道穷尽仍零技术表述（U）。「用 MicroVM」已成营销标配词，只有给出 VMM 名、每会话边界与网络/凭证机制的一手表述才可采信。（→ 第 4、6、7 章）
2. **控制面问题比隔离原语更决定自建平台的成败。** 三个平台级深研对象（OpenSandbox 双仓、E2B runtime）显示：调度、生命周期、egress 执行点、凭证注入与回收语义才是生产事故的来源；隔离原语（Firecracker/gVisor）本身的机制边界反而已被上游文档与源码钉得最死。（→ 第 6、19 章）
3. **默认姿态分野是本研究最重要的选型变量。** 同为 egress/元数据问题，E2B 是硬编码默认拒绝（169.254.0.0/16 写死在源码），OpenSandbox 是配方制（机制强、默认弱，非默认经双仓证实为产品口径而非疏漏）。选型先看默认姿态，再看机制清单。（→ 第 16、20 章）
4. **快照是 MicroVM 路线的安全枢纽，且上游校验比叙事弱。** Firecracker 快照 CRC64 仅覆盖 vmstate、内存/磁盘无内建校验加密、快照文件被官方列为可信输入；VMGenID 总是启用解决了克隆熵分化的机制层问题，但竞态窗口与 boot_id 不变是官方明示缺口。（→ 第 10、15 章）
5. **本项目产出了第一批可复现 [SELF] 证据，但范围如实有限。** LAB-MINI 载体上：namespace/seccomp 探针通过、单元级终止 30/30 零残留（vs 只杀主进程 30/30 恒残留 6）、网络配方策略逻辑层通过；cgroup 配额、快照一致性、拓扑级网络验证因环境不具备（无 KVM、cgroup 控制器未委派）整体顺延 LAB-REF。（→ 第 17、18 章）
6. **选型结论可辩护的前提是不打分。** 本项目选型框架用 17 维严格定义 + 场景公开加权（门槛/一阶/二阶）+ 逐产品 confidence 约束，9 个场景全部给出推荐/替代/前提/风险/明确不推荐；U 级隔离产品只出现在「明确不推荐」中。（→ 第 20 章）
7. **未决问题没有被掩盖。** 36 问终局：已结案 10、部分结案 11、顺延 LAB-REF 6、冻结现状 9（第 21 章逐问表）。研究局限五条如实登记，包括 13 号报告截断事件与 Mermaid 未做渲染级验证。

**交付物总览**：产品数据库 53 行（A22/B13/C17/U1）；深研报告 4 份（OpenSandbox 主仓 + Fast 外仓、E2B runtime、Firecracker）+ gVisor 选读；实验 1 批（LAB-MINI，raw 16 文件、脚本 12 个）；参考架构 5 种、选型场景 9 个、Mermaid 图 12 张；90 天专家路线 1 份。全部文件地图见第 23 章。

## 2. 领域定义与范围

**定义**：Agent Sandbox = 为 AI Agent（或其生成的不可信代码）提供受控执行环境的系统，其本质问题是：在敌对/不可信负载下，给出可验证的隔离边界、可控的网络与凭证面、可回收的生命周期。本研究按**隔离对象 / 威胁模型 / 运行方式**组织领域，不按营销名词组织。

**范围与边界**：纳入专用 Sandbox SaaS、安全代码执行、Browser/Desktop 沙盒、云厂商原语、Agent 平台内执行组件、开源自托管平台与隔离基础设施组件；HF Spaces 一类邻域对象以「非 Sandbox 反例」入表排除，防止用通用托管平台充数。研究方法四轨：产业扫描（官网/仓库一手核实）、源码深研（克隆定位到文件级）、威胁与评测设计（威胁 25 条 + 指标 32 条）、实验室（冻结线下自测）。研究计划与边界原文见 `00-RESEARCH-PLAN.md`。

**状态词纪律**：已发布 / 开发中 / 已归档被替代 / 论文原型 / 营销未证实五态分开登记——Daytona OSS 已 archived（2026-06 起核心转私有）而 SaaS 另论，是本纪律的典型案例（→ `02-ROUND1-REPORT.md` §3 裁决 #2/#3）。

## 3. 分类体系

分类体系 v0.1 在 Round 1 扫描后经受住了全表对账，未做结构性推翻：**8 个产品主类（P1–P8）× 8 个隔离技术标签（T1–T8）× 执行模型标签**，一产品只计一次主类、副属性写入 CSV 字段，防止双计与强行竞品化。

- 主类：P1 专用 Agent Sandbox SaaS / P2 Secure Code Runner·Judge / P3 Browser Sandbox / P4 Computer Use·Desktop / P5 Cloud Dev Environment / P6 通用云执行平台 / P7 Agent 平台内执行组件 / P8 开源自托管平台·控制面；另设「基础设施组件」行组承接 MicroVM/Wasm/安全容器/OS 级原语。
- 技术标签：T1 进程/OS 级 / T2 安全容器（用户态内核） / T3 MicroVM / T4 安全容器（VM 型 Kata） / T5 Wasm / T6 完整 VM / T7 浏览器进程沙盒 / T8 语言级。
- 判定规则三条：只有营销自称、无隔离/生命周期证据 → C 级候选；已归档如实标状态、禁止当活跃产品推荐；论文/原型单标 paper-only、不与可用产品混排比价。

原文与判定规则：`01-TAXONOMY.md`；全表按主类对账：`COVERAGE.md`。

## 4. 市场与生态全景

**阶段判断（带等级）**：

- **供给格局正被云厂商重写，但多数原语还没到可比价阶段。** AWS Lambda MicroVMs、Bedrock AgentCore、GKE Agent Sandbox、GCP Agent Compute Engine（2026-10-22 宣布、预览未定价）集中在 2025–2026 下场；经 Round 2 清债后 AWS 三项与 GKE 隔离/定价已升 A，ACE 定价经官方原文确认「尚未公布」（非缺证）。[A/B，→ 第 8 章]
- **开源侧出现控制面收敛信号。** OpenSandbox 迁入 Agentic AI Foundation、提供统一 API + 多运行时；Kubernetes SIG 的 agent-sandbox CRD 以候选入表。K8s 原生 Sandbox 编排可能成为自托管路线的标准层。[A/C]
- **Browser SaaS 是全领域透明度最差的类别**（Round 1 时点四家隔离全 U）；Round 5 攻坚后分化：Browserbase 升 A、Browserless 分版本记、Steel/Hyperbrowser SaaS 维持 U。定价可比、隔离不可比的格局只缓解了一半。[A/U]
- **计费碎片化到不可直接排序**：已核实计费单位至少 7 种（vCPU·秒、GB RAM·秒、core·秒且 1 core=2 vCPU、browser hour、30 秒 Unit、credit、CPU·h），且各家 vCPU 定义互不一致；任何跨家比价必须先声明换算假设。[A]
- **候选池如实冻结**：B 线登记未入表的 20+ 候选与 A 线同域未核基础设施（crosvm/Wasmer/Spin/KubeVirt 等）未在本研究周期内消化，终局处置为冻结现状（第 21 章 Q26/Q27），不以「没查」冒充「不存在」。

全景证据：`02-ROUND1-REPORT.md`（含 18 项冲突裁决）、`05-ROUND2-REPORT.md`、`COVERAGE.md`。

## 5. 产品数据库说明

`products.csv`：**53 数据行 × 31 字段**，字段覆盖身份（官网/仓库/许可/状态/版本）、场景、隔离技术、执行模型、生命周期、文件系统、网络控制、凭证安全、资源限制、浏览器/GUI、持久化、并发、启动延迟、定价、部署、优劣、适用场景、官方证据、confidence、检索日期、备注。

- **置信分布（终局，脚本统计）**：A 22 / B 13 / C 17 / U 1（U = Kernel，P3 候选）。已核实 35 行、候选 18 行；待验证 13 = 已核实中全部 B 行。
- **子项升格 ≠ 整行升格**：Runloop 隔离子项升 A−（官方双源明示）但 VMM 未点名、元数据/驻留仍 U，整行维持 B；Browserless、Steel 一律 SaaS 与开源版分开写。此口径贯穿 Round 2–6，是数据库可信度的核心机制。
- **版本口径陷阱已逐项登记**：Judge0 release 停在 v1.13.1（2024-04）但 commit 活跃、isolate 无 GitHub Release 只有 tag、仓库更名 4 处（E2B infra→runtime 等）——引用必须带口径（日期/来源面）。
- Round 6 终局回填：OpenHands 行按现行 README 更新（主仓 = Agent Canvas、SDK 已拆 `OpenHands/software-agent-sdk`、默认后端与隔离仍未核实、confidence B 不变），分布因此不变。

## 6. 开源项目分析

**深研对象与结论**（源码级，报告含克隆 HEAD 与文件级定位）：

- **OpenSandbox（主仓，Round 2）**：统一 Sandbox API 控制面 + Docker/K8s 与 Firecracker 多运行时 + egress/Credential Vault，是与自建平台架构问题一一对应的开源样本。实证差距：公开 snapshot 端点在 lifecycle 实现中保留 501、能力按后端分化；Fast 路径的 credentialProxy 与 volume mounts 被适配层直接拒绝；与 E2B **无关、非兼容**（无兼容层，迁移 = 按新 API 重写）。（`04-OPENSANDBOX-DEEP-DIVE.md`，HEAD dbcc6d7）
- **OpenSandbox Fast（外仓，Round 3）**：独立 K8s 原生平台（FastPath gRPC 控制面 + CRD reconciler + Fastlet 节点代理 + Firecracker 驱动 + Janitor），主仓只是其客户端；协议两层；**snapshot 恢复是唯一启动路径**、jailer 可选；运行时很年轻（无 release/tag、CRD v1alpha2）。创建 p50 双口径并存（本仓实测 77.9ms vs 主仓文档 64.0ms），35ms 恢复仅本地缓存命中。（`06-FAST-SANDBOX-DEEP-DIVE.md`，HEAD e0cd543）
- **E2B runtime（Round 3）**：见第 7 章（商业平台与开源组件同源，本章只记结论指针）。
- **状态异常与许可陷阱**：Daytona OSS archived（AGPL-3.0，SaaS 另论）；Browserless 为 SSPL-1.0 OR 商业双许可（非 OSI 开源）；Firecracker 仅 Apache-2.0（种子表 MIT 说法已纠正）；Cloud Hypervisor 为 Apache-2.0/BSD-3-Clause 双许可。
- **P4 与候选池是开源侧最薄弱处**：Computer Use 类仅 1 候选（E2B Desktop，C 级）；14 个 Round 1 新候选（CubeSandbox、AIO Sandbox、Hyperlight 等）只完成存在性登记、未逐个升核实，终局冻结现状。

## 7. 商业平台分析

- **E2B（深研）**：同源同线已证 A 级——同一套代码服务 Cloud/企业专属/Embed，隔离机制开源可审计；**此刻同版本无法证**（公开仓是内部 monorepo 的 copybara 只读镜像、Cloud 版本不公开）。实现要点：不用 jailer（orchestrator 以 root 直拉 Firecracker + 每沙箱 cgroup/netns）、169.254.0.0/16 硬编码默认拒绝、运营层（计费/secrets 解析/webhooks 后端）在仓外。（`07-E2B-RUNTIME-DEEP-DIVE.md`，HEAD 92b83da）
- **隔离证据达 A 的商业平台**：E2B、Browserbase（企业安全页明示 1 browser per VM/硬件虚拟化/独立 subnet/session 后销毁不复用）、Modal（双运行时口径：gVisor/VM，未指定由 Modal 选择——Round 2 已删除「默认 gVisor」旧结论）、Vercel Sandbox、Cloudflare Sandbox（VM-based isolation，非 V8 isolate）、Blaxel、Runloop（隔离子项 A−）。
- **维持 U 的**：Steel SaaS、Hyperbrowser SaaS（隔离技术零官方表述）；五家浏览器/Devbox 厂商 **VMM 点名率仍为 0**——选型文档 VMM 字段一律写「未点名」，不得以生态共识回填。
- **合规口径陷阱实证**：Hyperbrowser 的「aligned with SOC 2 TSC」≠ 已获 SOC 2 认证，CSV 已按其 security 页口径登记；引用厂商合规表述必须回原文区分 aligned / certified。
- **价格口径**：各家现行价已逐项回官网现页核实（旧价污染三处已作废登记：Fly Sprites、Steel legacy 套餐、CodeSandbox 旧 credit 价）；但计费单位不可比问题依旧（第 4 章），本报告不给跨家价格排名。

逐家证据：`products.csv`；攻坚过程：`hidden_files/research/round5-A-five-vendors.md`、`13-ROUND5-REPORT.md` §1.1。

## 8. 云厂商原语分析

- **AWS**：Lambda 本体（FAQ 原文，隔离+定价 A）；Lambda MicroVMs（开发者指南 Firecracker 原文 + 价表算例，A；「8h」口径已修正为含挂起总寿命，区域数子项维持 B）；Bedrock AgentCore Code Interpreter（定价/生命周期/microVM 隔离 A；其自身文档只到 microVM，Firecracker 字样仅见 AgentCore Runtime 的 harness 安全文档，出处差异已写入 CSV，子项维持 B）。
- **Google**：GKE Agent Sandbox 隔离升 A；网传「$0.0445」是错误归纳价、已删除（官方原文为 no extra charge, GKE pricing applies）——此为本研究删除错误数字的代表案例。Agent Compute Engine：2026-10-22 公告、内部已供 Gemini、客户 preview 未 GA、定价官方确认未公布。
- **Azure**：本研究周期内**未做对位核实**（Q19 部分结案：仅 ACE 侧完成；Azure 的 Container Apps/Foundry Hosted Agents 对位未查），如实登记为缺口，不以 Functions/Cloud Run 充数。
- **判断**：云厂商原语是潜在的格局变量（弹性、合规、既有云账单整合），但在本研究时点，除 AWS/GKE 外多数还处于「隔离可述、价格未定」阶段；选型中作为替代/溢出通道成立、作为唯一主干需逐项复核 GA 状态（→ 第 20 章场景 4/9）。

证据与保留子项：`OPEN-QUESTIONS.md` Q10/Q19、`05-ROUND2-REPORT.md`。

## 9. Linux 隔离原理

机制结论（原理底稿 24 条 A 级证据钉死，`hidden_files/research/round1-C-principles.md` 专题 1–2；本机实测补充见第 18 章）：

- **namespace 是视图隔离、不是安全边界**：它决定进程「看得见什么」，不决定「能做什么」；user namespace 是其余隔离得以 rootless 化的根，但 CAP_SYS_ADMIN 的 overloaded 语义是经典陷阱。
- **seccomp 官方原文定位为过滤机制而非沙盒本体**（"isn't a sandbox"）：它收窄 syscall 面，必须与 ns/cgroup/能力丢弃组装使用；本项目 EXP-01c 实测 mount 被 EPERM 拦截而其余功能完好，是该组装的最小实证 [SELF]。
- **cgroup 是配额与回收的执行面，不是隔离面**：配额语义（cpu.max/memory.max/pids.max）与回收语义（cgroup.kill 的单元级终止）是两件事；本项目最硬的一条 [SELF] 证据在此——单元级终止（以 PID-ns 整体拆除为同构载体）30/30 零残留，只杀主进程 30/30 恒残留全套脱缰负载。运行时设计的第一原则：**终止必须是单元语义，进程语义无效**。
- **发行版 user-ns 默认策略未系统核实**（Q24 冻结现状）：rootless 路线在目标宿主上是否可用不能由「本地能跑」推广，部署前须逐发行版核官方文档。

## 10. MicroVM 原理

以 Firecracker 源码级深研为锚（`12-FIRECRACKER-DEEP-DIVE.md`，HEAD f0f48ff，Q13 六子项全 A 结案）：

- **设备面**：「只有 5 个设备」口径已过期——NSDI'20 的最小设备集仍是核心，但现行代码含 virtio-balloon/rng/mem/pmem 与可选 PCI/热插拔（Developer Preview）。准确表述：**核心数据面极小、设备面持续受控扩张**。
- **双层防护**：VMM 内建 seccomp 是默认层，jailer 是外部可选围栏层；E2B 不用 jailer 丢的是外层围栏、不丢 seccomp，OpenSandbox Fast 的 jailer 可选与上游语义一致——评价任一 MicroVM 平台时两层须分开问。
- **快照**：组成为内存文件 + vmstate + 用户自管磁盘；Full 默认、Diff 仍 Developer Preview（须 rebase-snap 合并）；懒加载双后端 File mmap / UFFD（E2B 的 UFFD 用法是此后端的产品化）；**校验偏弱且官方不掩饰**：CRC64 仅覆盖 vmstate（防损坏不防篡改），内存/磁盘无内建校验与加密，快照文件在官方威胁模型中是可信输入——认证与加密是集成方责任。
- **克隆身份**：VMGenID **总是启用**（恢复写新随机 ID + 中断通知，guest 内核 ≥5.18 据此强制重播种 CSPRNG）；官方明示缺口：恢复竞态窗口、boot_id 不随克隆改变、userspace 自有熵池不在保证内。CPU template 官方明示**不是安全边界**；恢复环境须软硬件同构；最新 release 仍 v1.17.0。
- **性能口径**：冷启 <125ms [OFFICIAL] 的语义范围只到 microVM 运行、不含业务就绪；与 OpenSandbox 的 SDK resume ≈62s [OFFICIAL] 并置，正是「快照恢复 ≠ 毫秒可用」的完整证据链——中间隔着制品分发、路由、状态投影与轮询（Q34 拆账顺延 LAB-REF）。

## 11. 安全容器原理

**gVisor**（选读级深研，`hidden_files/research/round5-C-gvisor-owasp.md`，克隆 HEAD 4777ee7；Q12 两段口径结案）：

- **架构**：Sentry（用户态内核）零透传拦截 guest syscall，自身被最小宿主 syscall 面反向关住；文件面经 Gofer，现行协议是 **LISAFS**（9P 为前代遗留）——文件面信任边界 = Gofer 的挂载导出范围；**directfs 是必须当安全参数审查的旁路**，启用后不能沿用默认形态的隔离结论。
- **平台选择**：Systrap 凭无虚拟化依赖 + 低拦截开销于 2023 年中成为默认（ptrace 已停止支持）；KVM 平台只在裸金属占优，VM 内/嵌套环境官方指引即 Systrap。平台是按宿主形态选、不是按隔离强度选。
- **兼容性**：官方 compatibility 页由源码自动生成（2026-10-27 时点 352 条中 292 full-or-partial），引用必须带日期；未实现 ≠ 不可用，官方自列缺口（沙箱内 cgroup 只记账不限额、io_uring 默认禁用等）已回填 CSV。
- **性能数字官方未提供**：Systrap 性能只能由 D 线 B7 在目标版本自测（依赖 LAB-REF），任何引用旧 ptrace 口径 Performance Guide 图表的做法都是误导。

**Kata**：仅有运行时类映射级证据（每 Pod 一轻量 VM），其快照路径未深研（标 C）；在参考架构中作 C2 变体处理，选型中不得给 Kata 的密度/启动/快照强结论（→ 第 19、20 章）。

## 12. WebAssembly 沙盒

- **能力模型**：WASI 无环境权威（no ambient authority）——模块只能访问被显式授予的能力（预打开 FD、WIT imports 即权限清单），这是与进程级隔离根本不同的授权形态：权限面在编译/链接期即可枚举审查。
- **Wasmtime**：官方文档站设 security 专章，含「什么算安全漏洞」的逐项定义表，文档完备度为 Wasm 阵营最高。
- **WasmEdge（Q14 Round 6 结案）**：官方安全文档为**分散型**——SECURITY.md（报告邮箱、24h 确认/48h 响应、90 天披露时限、embargo 政策，A）+ CNCF TAG Security 自评（安全模型：模块隔离/线性内存/类型安全、无直接 syscall、一切 OS 资源经 WASI 接口、文件仅 `--dir guest:host[:readonly]` 一条授予路径、**侧信道明示 out of scope**，A）；文档站无 security 专章、无 host-function 权限专论。对照结论：**披露流程完备度与 Wasmtime 相当，差距在模型条文而不在流程**。
- **负载边界（架构 D 的硬约束）**：Wasm 路线跑不了 shell/完整工具链/fork-exec/浏览器/守护进程——其生态位是工具层/插件层与函数级负载的分层组件，不是通用沙盒替代（→ 第 19 章架构 D）。

证据：round1-C 专题 4、`hidden_files/research/round6-gaps.md` §1。

## 13. 浏览器与桌面沙盒

- **浏览器内层纪律**：Chromium 多进程 + 站点隔离是浏览器负载的第一道边界，`--no-sandbox` 是一票否决项（round1-C 专题 5）；但租户隔离的决定层在浏览器**之外**——每浏览器一台 VM / 一容器 / 一进程的部署形态差异，远大于浏览器自身版本差异。
- **厂商形态分化（Round 5 攻坚后）**：Browserbase = 每浏览器一台 VM + 独立 subnet + 销毁不复用（A）；Browserless 开源版与 Steel 开源版都是「单容器内多浏览器进程」的进程级分离（A），其 SaaS 表述明显不同于开源形态——**用开源版形态推断 SaaS 隔离强度是系统性错误**，本研究已逐家分开判定。
- **元数据/SSRF 默认策略是全类共同盲区**：五家（含 Runloop）无一家给出 169.254 专项默认策略原文（Q6 官方路线穷尽关闭），真实默认可达性只能靠 C8 矩阵 + 哨兵对真实产品做无害 [SELF] 实测（并入 LAB-REF 批次，未执行）。
- **桌面/Computer Use 是全研究最薄弱类**：P4 仅 1 个 C 级候选（E2B Desktop），OSWorld 类评测环境、云桌面厂商、Anthropic 参考实现均未入表做形态判定；本研究周期未做 P4 发现轮（终局登记，见第 21 章局限）。选型中 Computer Use 场景的结论是全场最弱、明示阶段性（→ 第 20 章场景 7）。

## 14. 威胁模型

威胁矩阵：**25 条威胁（T01–T25）**，每条九字段（资产/攻击者/入口/前置条件/影响/对应隔离层/缓解/残余风险/验证方法），锚点为 OWASP LLM Top 10、MITRE ATT&CK T1611、CWE-78/22/918、AWS IMDS 与 Firecracker/gVisor/Wasmtime/Chromium 官方文档（`hidden_files/research/round1-D-threat-bench.md`）。

- **编号纪律**：OWASP 五条编号与 5 个 CVE 已逐条回原文升 A（Q11）；2026 版已发布且大改编号（Excessive Agency LLM06:2025→LLM03:2026 等），本项目执行**双标注**决定——正文保留 2025 编号、§1.0.1 附 2026 映射，**引用必须带年份**（Q31 结案；2026 版 PDF 未逐字核，2026 侧为 A-/B+，如实登记）。
- **跨线结论（底稿级，已被深研与实验部分印证）**：隔离路线主要决定逃逸/内核类威胁（T04–T08、T21、T22）的上限；网络类（T09–T12）取决于平台策略与默认姿态、Agent 类（T19、T20）取决于 Harness 授权层——**换隔离技术不自动改善后两类**。
- **终止语义被实测升格为一等威胁面**：T21（残留/脱缰进程）在 EXP-02 中得到正反两面 [SELF] 证据（单元终止清零 vs 只杀主进程恒残留），是威胁矩阵与实验室互相印证的代表条目。

## 15. 隔离逃逸与供应链风险

- **逃逸面随路线分化**：共享内核路线（T1）的上限由内核 syscall 面与配置正确性决定（runc/内核 CVE 史见 D 线锚点）；MicroVM 路线的逃逸面收敛到 VMM + 设备模型，但**快照文件成为新的信任对象**——无内建认证/加密意味着快照供应链（制品分发、对象存储、模板导出）被攻破即等于 guest 内存被篡改，平台侧认证加密是必备补偿（架构 B 已写入，→ 第 19 章）；gVisor 路线的逃逸面在 Sentry 自身与 Gofer 导出范围，directfs 启用即改写结论。
- **克隆供应链**：同模板克隆的身份分化（VMGenID/boot_id/熵池）是快照路线的特有风险类，机制层已由上游证清（第 10 章），E2B 恢复路径是否实际吃到该机制未证（Q32 顺延 LAB-REF）——「上游有机制」不等于「产品已生效」。
- **模板/镜像供应链**：OpenSandbox Fast 的 vault 明文文件问题（Q30）是凭证供应链的实例：Fast 路径每沙箱明文 vault 文件落 Pod emptyDir、源码三处 TODO(encryption-at-rest)、外仓注释却断言「encrypted at rest」而双仓无加密实现（断言已标 U）——**注释与代码冲突时以代码为准**，是本研究的一条方法论结论。
- **厂商供应链**：Daytona OSS 归档转私有、仓库更名 4 处、Judge0 的 EE 渠道问题（Q23 未核）都提示：把开源组件写进生产依赖前，须核 archived 状态、许可（SSPL 双许可类）与发布渠道的当前形态。

## 16. 网络与凭证安全

**网络**：

- **执行点决定一切**：egress 策略在哪里执行（sidecar / 共享进程 / 宿主防火墙 / 云网络层）决定了它的绕过面与审计能力。OpenSandbox 双路径对照是现成教材：容器路径 sidecar 持 NET_ADMIN 做策略执行，Fast 路径是共享 egress 进程——同一产品、两种信任结构（`04`/`06` 深研报告）。
- **默认姿态两分**：E2B 硬编码默认拒绝（169.254.0.0/16 写死）vs OpenSandbox 配方制（deny.always 需部署方自填、双仓无 169.254 硬编码、外仓文档明文把元数据限制列为部署方责任）。LAB-MINI 实测证明配方在**策略逻辑层**成立（deny 6/6、含 302 跳转第二跳与 DNS 重绑定再访），但也证明配方的防线必须在**连接目标侧**而非解析侧（EXP-03 U8 读数 [SELF]）。
- **SaaS 侧整体未证**：浏览器类元数据默认策略全 U（第 13 章），是本领域公开证据的最大单点缺口。

**凭证**：

- **注入形态**：OpenSandbox Credential Vault 的结论必须分路径陈述——「Vault 只活 sidecar 内存」仅对容器路径成立；Fast 路径是明文 v1 vault 文件落 Pod emptyDir（Q30 跟踪中）。笼统引用「OpenSandbox 凭证不落盘」是错误结论。
- **解析位置**：E2B 的 secrets 值存储与出口解析在仓外服务（未配置时对应路由答 403）——自托管 E2B 时这部分要自建，不在开源仓内（→ 第 19 章架构 B 的运营层清单）。
- **设计规则（本研究结论）**：凭证不进入 guest 镜像与快照；注入点与 egress 执行点同侧；静态加密不能用上游 TODO 代替实现，选型时按「未实现」计价。

## 17. 性能成本与评测方法

**方法（先于一切数字）**：

- **阈值冻结**：C1–C8 通过线、D5 双画像（P-DEV 20 次/日、P-SAAS 200 次/日）、ST 套件 v1.0、统计口径（nearest-rank、五元组、n 门槛）在任何实测前冻结为 `09-BENCHMARK-FREEZE-v1.md` v1.0；测后改线 = 数据作废，改线须升版记原因、旧判定不回溯（Q25 结案）。
- **指标体系**：32 条指标（启动/运行/隔离可靠性/成本各 8）只有定义与方法，其中性能类至今**无一条产生跨产品可比数字**——这是方法的胜利而非失败：不可比的数字不生产。
- **启动数字四种语义不可混引**：创建 API 计时 / VM 恢复计时 / SDK 端到端 resume / 业务就绪，四者量级差三个数量级。现成对照组：OpenSandbox 创建 64.0ms（主仓文档）vs 77.9ms（外仓实测口径）vs SDK resume ≈62s（官方原文自标未解）——同源三数字，混引任何两个都是错误结论。
- **成本口径**：计费单位至少 7 种且 vCPU 定义互不一致（第 4 章）；成本比较只允许在声明换算假设 + D5 画像下做量级判断（15 号框架 §1 已逐维登记不可比陷阱）。

**已验证数字清单（全部带标签，此外无数字可用）**：Firecracker 冷启 <125ms [OFFICIAL·语义限定见第 10 章]；OpenSandbox 创建双口径与 62s [OFFICIAL]；LAB-MINI 的 EXP-04 冒烟耗时 [SELF·禁止外推]。B7（gVisor Systrap 性能自测）未执行：官方无数字、自测依赖 LAB-REF（→ 第 21 章）。

## 18. 实验室结果

第一批（2026-10-27，LAB-MINI，预注册先行，判定全按冻结 v1.0；完整规程与资产索引见 `18-LAB-MANUAL.md`，原始报告 `10-LAB-BATCH1-REPORT.md`）：

| 实验 | 判定 | 核心读数 [SELF] |
|---|---|---|
| EXP-01a namespace 视图隔离 | **通过** | 六类 ns 隔离 11 项检查全过 |
| EXP-01c seccomp | **通过** | mount 被 EPERM 拦截、进程其余功能完好、对照组可挂载 |
| EXP-01b cgroup 配额（C1/C2/C3） | **未判定·环境不具备** | 控制器未委派 + 瞬态单元不执行；RLIMIT 替代探针仅作机制参考 |
| EXP-02 超时清零（C4+C7） | **通过** | 单元级终止 30/30 轮残留 0；只杀主进程对照 30/30 轮残留恒 6 |
| EXP-03 网络矩阵（C8 子集/ST-5） | **载体内部分通过** | deny 6/6、allow 2/2、对照 4/4；U9（IPv6）N/A；拓扑级未判定 |
| EXP-04 ST-1/2/4 冒烟 | **通过（冒烟级）** | n=30 零失败零残留；耗时含解释器启动、禁止外推 |
| C6 / Q32 / Q34 / ST-3 / ST-6 / B7 | **未执行** | 判据/方案已冻结登记，顺延 LAB-REF |

过程完整性：全批 9 份无效批次（含 1 起近失事件：驱动误发 SIGKILL 至 PID 1，靠内核 ns-init 信号保护零损伤，修复护栏已冻结进手册 §2.2）全部留档并逐批登记原因；实验后宿主已逐项验证清理干净。**环境纠正**：本机无 /dev/kvm、无 Docker、cgroup 控制器未委派——主线先前「本机可跑 cgroup 实验」的判断错误已在 Round 4 认错并记入项目档案（`11-ROUND4-REPORT.md`）。

## 19. 五种参考架构

五种架构按统一 17 项模板（组件/控制面/数据面/调度/创建服务/执行代理/文件/网络/凭证/观测/快照/回收/故障/HA/安全边界/瓶颈/成本）成文于 `14-REFERENCE-ARCHITECTURES.md`（含跨架构决策矩阵 6 行 × 8 轴、全局图 6 张 + 各架构组件图 5 张）。每架构的每个关键决策标注**借鉴自哪个真实系统 + 证据等级**，不凭空设计；每架构另给「最先被打穿的三条路径」（回链 T01–T25）与不适用场景。

- **A 容器型**（ns+cgroup+seccomp）：密度与启动最优、隔离上限最低；借 OpenSandbox 容器路径的硬化组装，把元数据拒绝从其运维配方改成 E2B 式硬编码默认（设计判断，依据已在 14 号登记）。
- **B MicroVM 型**（KVM/Firecracker）：公众多租户主干；借 Firecracker 上游机制 + E2B 的创建即恢复/槽位网络 + Fast 的 warm pool/内容寻址；jailer 定为多租户默认开，快照须平台侧补认证加密（针对上游 CRC 弱项）。
- **C 安全容器型**：C1 gVisor（兼容为代价换共享内核之上的第二内核）/ C2 Kata（VM 型，证据深度较浅、结论强度受限）。
- **D Wasm 型**：能力模型最干净、负载子集最窄；定版为**分层组件而非替代**（工具/插件层）。
- **E 混合型**：分层路由（B 主干 + A/C 降档 + D 工具层 + 浏览器档），是企业运维与大规模多租户两场景的落点形态；复杂度即其主要风险。

## 20. 选型框架与场景结论

框架（`15-SELECTION-FRAMEWORK.md`）：17 个评价维度逐维给严格定义（测什么/证据从哪来/不可比陷阱）、9 组技术路线两两对照（每组给「分水岭问题」）、Mermaid 决策流程图；**不设综合评分**，判定方式为维度级定性（强/中/弱/U/不适用）+ 场景公开加权（门槛维一票否决 / 一阶维 / 二阶维）；C 级判断 18 条逐条登记（C-1…C-18）。点名纪律：主推荐须与 CSV confidence 一致，U 级隔离只进「明确不推荐」。

9 场景结论（一句版；完整版含替代/前提/风险/不推荐，见 15 号 §3）：

| # | 场景 | 主推荐 |
|---|---|---|
| 1 | 个人 Agent 项目 | B 型托管 SaaS：E2B（隔离 A、按 vCPU·秒计费）；替代本地 Microsandbox / Modal |
| 2 | AI Coding Agent | B 型二选一：云端 E2B / 自托管 OpenSandbox；替代 Runloop、Daytona SaaS、CodeSandbox SDK |
| 3 | 企业内部运维 Agent | E 型自托管：OpenSandbox on 自有 K8s 或 GKE Agent Sandbox（Default Deny 姿态）；替代 E2B Embed/BYOC（须自落实运营层三件套） |
| 4 | 面向公众的 Agent SaaS | B 型每会话 MicroVM：E2B 或 Blaxel（均隔离 A）；自托管轨 OpenSandbox；替代 Vercel Sandbox / Lambda MicroVMs |
| 5 | 不可信代码执行平台 | 分层组合：isolate/nsjail 原语 + Judge0 判题层；高不可信档整轨升 Firecracker 自建或 gVisor |
| 6 | Browser Agent | Browserbase（P3 中隔离唯一 A）；替代 Browserless SaaS / Steel 开源版（限低敏感自托管） |
| 7 | Computer Use Agent | E 型拼装：B 型 MicroVM 底座自建桌面镜像（E2B Desktop 仅 C 级候选）；结论明示阶段性 |
| 8 | 高安全金融 | 自托管 B/C 型最高档：OpenSandbox（Kata/gVisor 分档 + 配方实测验收）或 Firecracker 自建（快照自管认证加密）；云上必须时 GKE Agent Sandbox；未知即不得入选 |
| 9 | 大规模多租户平台 | 自建 E 型控制面：OpenSandbox 主干或 Firecracker 自建编排（须自建计费/secrets/webhooks）；Lambda MicroVMs 承接弹性溢出；替代 GKE Agent Sandbox |

注：涉及 Cassia 的场景（4/2）只给技术选型结论，不含实施计划（Cassia 本侧开发冻结在案）。

## 21. 未解决问题与研究局限

### 21.1 36 问终局处置表（2026-10-28，逐问归类；原文与状态全文见 `OPEN-QUESTIONS.md`）

**已结案（10）**：Q1 E2B 同源同线（保留「此刻同版本」U 尾巴）· Q8 归档监测（持续监测转为常规动作）· Q11 OWASP/CVE 回原文升 A · Q12 gVisor 兼容清单 + Systrap 数字缺位登记 · Q13 Firecracker 快照/VMGenID 六子项 · Q14 WasmEdge 安全文档（Round 6）· Q18 Modal 双运行时口径 · Q25 评测阈值冻结 v1.0 · Q28 Fast 外仓深研 · Q31 OWASP 双标注落地（2026 版 PDF 逐字核为不阻塞尾巴）。

**部分结案（11）**：Q2 Daytona（定位与容器自述已清，runtime 点名仍 U）· Q3 OpenSandbox（双仓深研完成，余 execd 全量 diff 与 provider 能力矩阵未逐项核）· Q4 四家隔离一手证据（仅 Fly 未达 A）· Q6 Browser 元数据（官方路线穷尽关闭，余真实产品 SELF 实测）· Q7 MCP 隔离（生态早期判断成立，候选未深核）· Q9 五家隔离攻坚（2A/1B+/2U，余 VMM 点名率 0 与 Q6 尾巴）· Q10 云厂商 A 级原文（AWS/GKE 已清，余 ACE 定价未公布、AgentCore 字样子项 B、Azure 转 Q19）· Q16 OpenHands（SDK 仓与 Agent Canvas 定位已证，余默认执行后端与隔离未核实）· Q19 云厂商对位（ACE 侧完成，Azure 未做、GA/定价待官方）· Q21 生命周期直引（Daytona 已清，Browserbase 6h 维持 B 且疑旧数字）· Q22 license 细节（Wasmtime 已清，余 Cloud Hypervisor BSD-3-Clause 适用范围待核）。

**顺延 LAB-REF（6）**：Q5 快照「毫秒级」口径实测（口径已备，待实测环境）· Q29 OpenSandbox 配方拓扑级实效（载体内已验证）· Q32 E2B 克隆熵分化实测（机制层已关闭）· Q34 OpenSandbox 62s 分段拆账（探针方案已冻结）· Q35 深研对象 SELF 数据（LAB-MINI 面已关闭，余 OpenSandbox/E2B 部署行为）· Q36 LAB-REF 环境获取（规格已登记，采购与否由用户决定）。

**冻结现状（9）**：Q15 Microsandbox VMM 实现未读 · Q17 Sandbox Fusion 正确仓名未定位 · Q20 B 线三处价格/事实冲突（CSV 已按 pricing 页优先并注冲突）· Q23 isolate tag 日期与 Judge0 发布渠道未核 · Q24 发行版 user-ns 默认策略未系统核 · Q26 同域基础设施候选（crosvm/Wasmer/Spin/KubeVirt 等）未入表判定 · Q27 B 线 20+ 登记候选未逐个判定 · Q30 OpenSandbox Fast Vault 明文（上游跟踪项：等 encryption-at-rest 落地或误导注释修正）· Q33 E2B RELEASING.md 与 GitHub Releases 张力（待官方澄清，引用以 gh API 实测为准）。

计数对账：10 + 11 + 6 + 9 = **36**，与 OPEN-QUESTIONS 编号总数一致，不删号。

### 21.2 研究局限（五条，如实登记）

1. **SELF 数据仅 LAB-MINI 可测面**：全部自测结论成立于单 netns + 127/8 替身 + PID-ns 单元载体；深研对象（OpenSandbox/E2B/Firecracker）均未部署实测，其官方性能数字（64.0/77.9ms、35ms、62s 等）始终是 [OFFICIAL] 而非本项目实测。LAB-REF 未获取是全项目最大的未闭合项。
2. **Mermaid 图未做渲染级验证**：14/15 号共 12 张图只通过结构级检查（节点 id、引号、冲突字符），本地 mermaid-cli 安装超时未产出渲染验证；建议在 GitHub 页面侧目视逐图核（公开仓 docs/14、docs/15），发现错误按小错流程回改。
3. **13 号报告截断事件**：`13-ROUND5-REPORT.md` 在 Round 5 落盘时即被截断（止于 §3 中途、带字面截断标记，§4–§6 从未写入），本地与公开仓同；2026-10-28 已公开勘误：文件头加标注、文末按整合记录补遗（可确证部分标〔补记〕、§4 明示原文缺失指向现行台账，不虚构重构），勘误提交 `8b2948b` 与原始提交并存可查。此事件前，引用 13 号只可引其现存 §1–§3 与补遗。
4. **P4 Computer Use 类未做发现轮**：全表仅 1 个 C 级候选，OSWorld 类环境与云桌面厂商未做形态判定；第 13/20 章涉及桌面与场景 7 的结论是全研究最弱的部分，后续若立项应先补发现轮再更新选型。
5. **云厂商原语多为 B 级且时效短**：除 AWS 三项与 GKE 隔离已升 A 外，云厂商侧证据以 B 级归纳为主、ACE 未 GA 未定价、Azure 对位未做；云厂商产品迭代快，本报告第 8 章结论的保鲜期以季度计，引用前须回官方现页复核。附带同类时效项：OWASP 2026 版 PDF 未逐字核（2026 侧映射 A-/B+）、gVisor 兼容计数为 2026-10-27 快照。

## 22. 90 天专家路线摘要

全文：`17-90DAY-EXPERT-PLAN.md`。要点：

- **定位**：把本项目的研究资产转成「人」的能力。L3 = 能独立对新对象产出可辩护结论（带等级、带出处、带口径，证不了的明说未验证）。五种可验收工作形态：核查 / 深研 / 实验 / 架构评审 / 选型，各有结业门槛与验收方式（如核查须 2 小时内对未入表新产品产出 CSV 规格一行 + 可辩护隔离结论）。
- **结构**：四阶段 × 12 周——阶段一 基础与威胁模型（W1 分类与证据方法 / W2 威胁 25 条与双标注 / W3 测量学与冻结纪律）；阶段二 隔离技术（W4 Linux 原语 + LAB-MINI 复现 / W5 MicroVM 与 Firecracker / W6 gVisor·Wasm·浏览器）；阶段三 平台架构（W7 OpenSandbox 双仓 / W8 E2B 与默认姿态对照 / W9 参考架构与选型演练）；阶段四 生产化与专家输出（W10 LAB-REF 进阶 / W11 新对象计时实战 / W12 评审答辩结业）。
- **教材原则**：不另起书单，必读只取本项目已验收材料与其中已核实的一手源；源码对象为本地五仓克隆（引用前核 HEAD 未漂移）。
- **LAB-REF 分叉**：需要 LAB-REF 的周次与实验全表登记；无 LAB-REF 时走纯源码/文档/设计替代路径，汇合点处按规则登记「未验证」，不许用替代路径产出冒充实测结论。
- **投入档位**：投入型 10–12 小时/周、维持型 4–5 小时/周（均为建议值）；门只看产出不看工时，未过周门不得进阶。

## 23. 附录索引（全部交付文件地图）

`files/` 正式交付（00–19 号 + 台账 3 件）：

| 文件 | 内容 |
|---|---|
| `00-RESEARCH-PLAN.md` | 研究计划、边界与执行顺序 |
| `01-TAXONOMY.md` | 分类体系 P1–P8 × T1–T8 与判定规则 |
| `02-ROUND1-REPORT.md` | Round 1 产业扫描报告（53 行 v0.1、18 项冲突裁决） |
| `04-OPENSANDBOX-DEEP-DIVE.md` | OpenSandbox 主仓源码深研（Round 2） |
| `05-ROUND2-REPORT.md` | Round 2 报告（证据债清理 + 深研 0→1） |
| `06-FAST-SANDBOX-DEEP-DIVE.md` | OpenSandbox Fast 外仓深研（Round 3） |
| `07-E2B-RUNTIME-DEEP-DIVE.md` | E2B runtime 深研（Round 3） |
| `08-ROUND3-REPORT.md` | Round 3 报告 |
| `09-BENCHMARK-FREEZE-v1.md` | 评测阈值冻结 v1.0（C1–C8/D5/ST v1.0） |
| `10-LAB-BATCH1-REPORT.md` | 实验室第一批实验报告（LAB-MINI） |
| `11-ROUND4-REPORT.md` | Round 4 报告（含环境纠正与近失事件披露） |
| `12-FIRECRACKER-DEEP-DIVE.md` | Firecracker 源码深研（Round 5） |
| `13-ROUND5-REPORT.md` | Round 5 报告（文件头含截断勘误标注、文末补遗） |
| `14-REFERENCE-ARCHITECTURES.md` | 参考架构 A–E + 决策矩阵 + 图组 |
| `15-SELECTION-FRAMEWORK.md` | 选型框架：17 维 + 9 组对照 + 9 场景 |
| `16-PHASE67-REPORT.md` | Phase 6/7 整合与四项自检报告 |
| `17-90DAY-EXPERT-PLAN.md` | 90 天（12 周）L3 专家路线 |
| `18-LAB-MANUAL.md` | 实验室手册（环境分级/护栏/规程/顺延清单/数据索引） |
| `19-FINAL-REPORT.md` | 本报告 |
| `products.csv` | 产品数据库 53 行 × 31 字段 |
| `OPEN-QUESTIONS.md` | 36 问台账（终局状态） |
| `COVERAGE.md` | 覆盖率与计数对账台账 |

底稿与资产（`hidden_files/research/`，公开仓镜像于 `research/`）：round1-A/B/C/D 四线底稿、round2-A/B、round3-A/B、round5-A/B/C、round6-gaps；五仓源码克隆只留本地不入仓（opensandbox-src / fast-sandbox-src / e2b-runtime-src / firecracker-src / gvisor-src，HEAD 见各深研报告头注）。实验资产（`hidden_files/lab/`，公开仓镜像于 `lab/batch1/`）：PREREG-batch1.md、scripts/ 12 个、raw/ 16 个。

## 24. 参考资料

本章只登记本项目**实际引用过**的一手源类别与仓内指针，不另行编造外部链接清单；逐条出处以各底稿/深研报告内的引用为准。

- **官方文档与价表**：各厂商官网 pricing/docs/企业安全页/Trust Center（Browserbase 企业安全页、Browserless Trust Center、Modal LP、AWS Developer Guide 与 FAQ、GKE 文档、Daytona docs 等）——指针：`products.csv` 的 official_evidence 字段逐行登记；攻坚路径见 `round5-A-five-vendors.md`。
- **官方源码仓**：OpenSandbox 主仓 + fast-sandbox 外仓、e2b-dev/runtime、firecracker-microvm/firecracker、google/gvisor、WasmEdge/WasmEdge（含 SECURITY.md 与 docs/embargo-policy.md）、OpenHands/OpenHands 与 OpenHands/software-agent-sdk——本地克隆与 HEAD 见第 23 章；深研报告内含文件级定位。
- **官方安全/标准文档**：OWASP LLM Top 10（2025 版正文 + 2026 版新闻稿/roundup，双标注见 round1-D §1.0.1）；MITRE ATT&CK T1611；CWE-78/22/918；NVD 条目（5 个 CVE 已逐条核）；CNCF TAG Security 的 WasmEdge Self Assessment；gvisor.dev compatibility 页（源码自动生成，2026-10-27 快照）；Chromium 官方文档（站点隔离）；Firecracker 官方 docs（snapshotting/威胁模型）与 NSDI'20 论文。
- **项目内一手证据**：实验室原始数据与脚本（第 23 章 lab 资产）；冻结文档 `09-BENCHMARK-FREEZE-v1.md`；各轮底稿的取证记录（gh api 输出、企业页原文摘录）。

---

**收官声明**：本报告为本研究周期的终局整合。Round 6 回填（Q14 结案、Q16 部分结案、OpenHands 行更新）已执行，CSV 分布不变（A22/B13/C17/U1）；36 问终局处置见第 21 章；顺延 LAB-REF 的 6 问与冻结现状的 9 问保留编号与原文，后续任何重启研究应从 `OPEN-QUESTIONS.md` 现行状态接续，不得以本报告摘要替代台账原文。
