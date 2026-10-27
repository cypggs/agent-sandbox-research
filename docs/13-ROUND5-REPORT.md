# 13 · Round 5 阶段报告（分支 B）：五家隔离攻坚、Firecracker 深研、gVisor 选读与 OWASP 双标注

> 项目：Agent Sandbox 全领域技术研究（goal_a756da9ace9a）
> 阶段：Round 5（用户拍板分支 B：暂不设 LAB-REF，先攻坚五家隔离未公开 + Firecracker 深研）完成
> 日期：2026-10-27（Asia/Shanghai）｜ 证据等级：A 官方/源码/论文 · B 可靠独立 · C 推断待验证 · U 未知
> 输入底稿：hidden_files/research/round5-A-five-vendors.md、files/12-FIRECRACKER-DEEP-DIVE.md、hidden_files/research/round5-C-gvisor-owasp.md、hidden_files/research/round1-D-threat-bench.md（§1.0.1 双标注已落地，531 行）
> 本轮纪律：纯静态分析（官网原文 + 源码定位），未部署、未运行、未产生新 [SELF] 数据；实验计数不变（仍 1 批）。

## 1. 执行摘要

### 1.1 五家攻坚战果：Round 1 的「全部未公开」解体

| 家 | Round 1 | Round 5 | 关键证据 |
|---|---|---|---|
| Browserbase | U | **A** | docs 企业安全页明示「1 browser per VM、硬件虚拟化层隔离」、每浏览器独立 subnet+严格防火墙、session 后 VM 销毁重建不复用、驻留四区域可选 |
| Runloop | U | **A-**（隔离子项） | docs 明示 VM 技术 + 官方 SDK README 明示「isolated at both the VM and container level」、每 Devbox 一台临时 VM；microVM 字样仅 PR 稿（B），VMM 未点名 |
| Browserless | U | **SaaS B+ / 开源版 A** | SaaS 官方 Trust Center 明示容器化环境+网络分段、官方 blog 明示每连接独立 browser instance；开源版为单 Docker 容器多浏览器进程（源码 A）——两版分开，不得等同 |
| Steel.dev | U | **SaaS U 维持 / 开源版 A** | SaaS 官方仅「Isolated sessions」营销语；Fly Machines 架构只是 2024 年合作方客户故事线索（B/C，须注日期）；开源版单 api 容器多浏览器进程（A） |
| Hyperbrowser | U | **U 维持** | security 页/Trust Center/docs/SDK/GitHub 组织/pricing 六渠道穷尽，仍零租户隔离技术表述——五家中最弱 |

**方法论教训（本轮最值钱的一条）**：Round 1 的负结论源于只查 pricing/docs 常规页——五家的隔离表述实际藏在**企业安全页（Browserbase）、Trust Center（Browserless）、官方 SDK README（Runloop）**里。此后查任何厂商的隔离，先查 trust/security 企业页与 SDK，再查常规 docs。另外两条横向结论：五家 **VMM 点名率仍为 0**（选型文档 VMM 字段一律写「未点名」，不得以生态共识回填）；**合规口径陷阱**已实证（Hyperbrowser 的「aligned with SOC 2 TSC」≠ 已获认证，已在 CSV 以 security 页口径登记）。

**开源版 ≠ SaaS 的系统性落差**：Browserless、Steel 的开源自托管版都是「单容器内多浏览器进程」的进程级分离，而其 SaaS 表述明显强于或至少不同于开源形态——任何用开源版形态推断 SaaS 隔离强度的写法都是错的，本轮已在 CSV 逐家分开判定。

### 1.2 Firecracker 深研：三个改写性发现（深研第 3 号，HEAD f0f48ff）

1. **「5 个设备」口径过期**：NSDI'20 的最小设备集仍是核心，但现行代码含 virtio-balloon、virtio-rng、virtio-mem、virtio-pmem 与可选 PCI 传输/热插拔（Developer Preview）。攻击面结论改写为「**核心数据面极小、设备面持续受控扩张**」，再引「只有 5 个设备所以安全」视为过期表述。
2. **快照校验比叙事弱、且官方不掩饰**：CRC64 **仅覆盖 vmstate 文件**（防意外损坏、非防篡改），内存/磁盘文件无内建校验与加密，快照文件在官方威胁模型里是**可信输入**——认证与加密是集成方责任。懒加载为 File mmap 与 UFFD 双后端；Diff 快照仍是 Developer Preview。
3. **VMGenID 总是启用**：恢复时写新 16 字节随机 ID 并注入中断，guest 内核（≥5.18）据此强制重播种 CSPRNG——克隆熵分化的上游机制存在且默认在。但官方明示**两个缺口不得省略**：vCPU 恢复到内核处理通知之间的**竞态窗口**、以及 **boot_id 不变**；外加 CPU template 官方明示**不是安全边界**、恢复环境须软硬件同构。
另：jailer 与内建 seccomp 是两层独立机制（E2B 不用 jailer 丢的是外层围栏、不丢 seccomp；OpenSandbox Fast 的 jailer 可选与上游语义一致）——Round 2/3 的对照结论就此有了上游锚点。

### 1.3 gVisor 选读：一条协议修正与平台选择逻辑

- **Gofer 协议已换代（对 Round 1 线 C 表述的修正）**：现行 Sentry↔Gofer 协议是 **LISAFS**（`pkg/lisafs`），9P 是前代、仅遗留保留。文件面信任边界 = Gofer 的挂载导出范围；**directfs 是必须当安全参数审查的旁路**，启用后不能沿用默认形态的隔离结论。
- **平台选择逻辑**：Systrap 凭无虚拟化依赖+低拦截开销于 2023 年中成为默认（ptrace 已停止支持）；KVM 平台只在裸金属占优，VM 内（含嵌套环境）官方指引就是 Systrap。Sentry 零透传、自身被最小宿主 syscall 面反向关住。

## 2. 结案清单（OPEN-QUESTIONS，本轮共关闭/推进 6 问，清单仍 36 问不删号）

| 问 | 结果 |
|---|---|
| Q13 Firecracker snapshot/VMGenID 官方口径 | **结案**：六子项全 A（组成/Full-Diff/CRC64 仅 vmstate/双后端懒加载/VMGenID 总是启用/网络时间与同构约束），含竞态窗口与 boot_id 不变两个官方明示缺口 |
| Q12 gVisor 兼容清单 + Systrap 性能数字 | **结案（两段口径）**：清单以 A 级解答（位置 gvisor.dev compatibility 页、源码自动生成、352 条中 292 full-or-partial @2026-10-27、引用带日期）；性能数字以「官方未提供」登记结案，转 D 线 B7 自测（依赖 LAB-REF） |
| Q31 OWASP 2026 双标注 | **结案（双标注已落地）**：D 线底稿新增 §1.0.1（规则+五条映射+LLM07→08 补注）；S1/S10 等级 B→A 回填完成。尾巴：2026 版 PDF 未逐字核（2026 侧 A-/B+），不阻塞结案 |
| Q9 五家隔离未公开 | **大部分结案**：2 升 A、1 家 B+/A 分开、2 维持 U（理由与穷尽记录齐全）；尾巴为 VMM 点名率 0 与元数据全 U，转 Q6 |
| Q6 Browser SaaS 元数据/SSRF 默认策略 | **官方路线穷尽关闭**：六渠道查尽、无一家给元数据专项原文；剩余只能对真实产品做 C8+哨兵 SELF 实测，并入 LAB-REF 批次（Q36） |
| Q32 E2B 克隆熵分化 | **机制层子问题关闭**：VMGenID 机制存在且总是启用已证（随 Q13）；E2B 恢复路径是否吃到该机制仍待 LAB-REF 实测，本问不结案 |
| Q14 WasmEdge | 未动仍开（本轮范围外，报告明示 Wasm 路线结论继续缺一半） |

## 3. CSV 变更清单（products.csv v0.3 → v0.4，53 行不变）

- **Browserbase**：isolation_tech 改写为 VM 口径（A）、lifecycle 补「不复用销毁重建」、network_control 改 subnet/防火墙口径、persistence 补驻留四区域与 zero-retention、limitations 改写、official_evidence 补企业安全页；**confidence B → A（本轮唯一整行升格）**。
- **Runloop**：isolation_tech 改写为 VM+容器双层（A/A-/B/C 分层标注）、network_control 补 Network Policies、lifecycle/deployment 补临时 VM 与 VPC、limitations 改写；**confidence 维持 B**——隔离子项升 A-，但 VMM 未点名、microVM 仅 PR 稿、egress 默认口径/元数据/驻留仍 U，按线 A 无「+」号口径不整行升 A（子项升格≠整行升格，与 Round 2 口径一致）。
- **Browserless**：isolation_tech 按 SaaS/开源版双写、network_control 补网络分段与 allowlist 非强制、persistence 补驻留细则、limitations/official_evidence/notes 更新；confidence 维持 B（SaaS 子项 B+、开源版 A 已注）。
- **Steel.dev**：isolation_tech 按 SaaS（U+2024 Fly 线索 B/C 注日期）/开源版（A）双写、credential_security 补 Credentials API（A 产品表述）、deployment 补 Outpost、limitations 改写（SOC 2 未明示）；confidence 维持 B。
- **Hyperbrowser**：isolation_tech 维持未公开并加六渠道穷尽注记、persistence 补驻留美国（A）、limitations 补 SOC 2 口径冲突（以 security 页「aligned」为准）；confidence 维持 B。
- **Firecracker**：isolation_tech 设备面口径更新（核心极小+受控扩张、seccomp/jailer 两层）、persistence 写入 snapshot 全套结论（CRC64 仅 vmstate、UFFD/File 双后端、Diff 为 Developer Preview）、network/resource_limit
...[truncated 3147 chars]