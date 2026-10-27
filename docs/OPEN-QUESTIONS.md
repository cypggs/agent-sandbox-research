# 未解决问题清单（持续更新）

格式：问题 / 为什么重要 / 验证方法（源码/实验/官方文档/产品实测）/ 状态
Round 1 更新：2026-10-27。原 8 问保留并更新状态；第 9 问起为 A/B/C/D 四线 Round 1 移交的新缺口。

1. E2B 当前自托管形态（Embed/开源组件边界）与云服务隔离实现是否一致？/ 选型与私有化判断 / 查官方 repo+docs 当日版本 / **部分解答（Round 1）**：A 线已证运行时仓（infra→更名 runtime）README 明示 Embed 是全栈、含真实 Firecracker、需 Linux+KVM，且链路为 SDK/CLI→API→orchestrator→Firecracker→envd（A）；但"自托管与云服务的隔离实现/版本是否完全一致"仍未证，待 Round 2 读 runtime 源码与云文档逐项对照
2. Daytona 2025-2026 定位变化（dev environment → agent infra?）与隔离技术到底是什么？/ 易被营销误导 / 官方 docs+架构博客+repo / **部分解答（Round 1）**：定位已确认转 P1（现官网"Secure Infrastructure for Running AI-Generated Code"，B 线 A-）；OSS 已归档、2026-06 起核心转私有代码库（A 线 A）；隔离只确认"Container 类+Linux VM 类+Windows VM 类并存"（官方快照表 A），容器类底层 runtime（Docker/Kata/Sysbox 何者）官方未明示，仍为 U，待官方架构文档或实测
3. OpenSandbox（AAIF）规范 vs 实现的成熟度、与 E2B API 的关系？/ 与 Cassia 最对口 / 读 spec+源码 / **进行中（Round 1 有进展）**：仓库已迁 opensandbox-group（alibaba 旧址重定向）、版本 release-1.1.1（2026-10-09）、当日仍活跃、Apache-2.0（A）；README 确认 Docker/K8s + Firecracker 双运行时与 egress/Credential Vault（A）。spec 与实现的差距、与 E2B API 的兼容/映射关系未答，待 Round 2 源码深研（优先级第 1，见 02-ROUND1-REPORT）
4. Modal / Fly Sprites / Vercel Sandbox / Cloudflare Sandbox 的隔离技术一手证据分别是什么？/ P6 普遍只有二手转述 / 官方架构文档逐项核 / **大部分解答（Round 1）**：Modal=gVisor（官方 LP，A）；Vercel=Firecracker microVM+专用内核（官方 FAQ+安全文，A）；Cloudflare=VM-based isolation（官方架构页，A，形态为 VM 内容器，不是 V8 isolate）。**仅 Fly 仍未达 A**：官方只称 hardware-isolated / hardware-isolated VM，Firecracker 实现名仍为 B 级共识，待 Fly 官方 Machines/Sprites 架构页原文
5. 各 SaaS 的快照恢复"毫秒级"宣称的口径（VM resume / 进程就绪 / 首次命令可执行）？/ 数字不可直接比 / 统一定义后实测或找第三方复测 / **未开始（口径已备）**：Round 1 只记录官方公布值并标注未实测——OpenSandbox Firecracker 64ms P50、Microsandbox <100ms、Blaxel standby resume 约 25ms、Firecracker 冷启动 <125ms，四者语义各不相同禁止横比；D 线已给出 A1-A8 统一定义（t_submit/t_ack/t_ready 三段+就绪探针），待实验室实测
6. Browser SaaS 的内网/元数据访问默认策略与 SSRF 防护证据？/ Browser Agent 最大风险面 / 官方安全文档+自建实验 / **进行中（Round 1 证据为负）**：Browserbase/Browserless/Steel/Hyperbrowser 四家官方 pricing/docs 均未述底层隔离与默认 egress/元数据策略（B 线确认为未公开）；Microsandbox 是唯一给出 metadata 阻断一手表述的（非浏览器类）产品。待 Round 2 查各家安全文档/信任中心，并以 D 线 C8 网络策略矩阵+哨兵实验自测
7. MCP Server 隔离目前有无成型开源方案？/ 生态空白点判断 / GitHub+论文扫描 / **部分进展（Round 1）**：新增候选 Anthropic sandbox-runtime（OS 级、无容器文件/网络限制）、agent-infra AIO Sandbox（Browser/Shell/File/MCP/VSCode 合一单容器）说明厂商与社区已在填补，但尚无证据表明已有"成型、被广泛采用"的 MCP 专用隔离方案，判断维持"生态早期"，待 Round 2 深核两候选+MCP 规范安全部分
8. 哪些种子项目已归档/停更？/ 防误判活跃 / 逐仓查 archived/最后 commit/release / **Round 1 已完成（持续监测）**：种子 23 条已逐项核——仅 Daytona OSS 已归档（1 个）；其余种子仓均未归档且 2026-10 仍有 commit。附带发现的口径陷阱：Judge0 release 停滞（v1.13.1, 2024-04-18）但 commit 活跃、isolate 无 GitHub Release 只有 tag v2.7、Steel latest release 为 beta，已分别写回 CSV，引用时必须带口径

## Round 1 四线移交的新缺口（第 9 问起）

9. Runloop、Browserbase、Browserless、Steel.dev、Hyperbrowser 五家的底层隔离实现为何全部未公开？各自真实边界是什么？/ P1/P3 选型时隔离是第一变量，未公开即不可比，且浏览器类还叠加 SSRF/会话风险 / 查各家安全文档/信任中心/架构博客原文；无官方表述则以自建实验（会话间探测、元数据可达性）验证并标 SELF / 状态：未开始（B 线移交，Round 2 优先）
10. 云厂商 Sandbox 原语的隔离与定价 A 级原文普遍缺失（AWS Lambda/MicroVMs/AgentCore、GKE Agent Sandbox、Agent Compute Engine、Azure/GCP 本体）/ 云厂商是最可能的规模化供给方，B 级归纳不足以支撑选型 / 逐项打开 AWS Developer Guide/AgentCore 官方 docs/AWS 官方价表、Google 官方博客原文与 GKE 文档、Azure 零售价 API 直引 / 状态：未开始（B 线移交）
11. D 线引用的 OWASP LLM Top 10（2025 版编号）与 5 个 CVE 编号（runc CVE-2019-5736/CVE-2024-21626/CVE-2022-0492、内核 CVE-2016-5195/CVE-2022-0847）回原文升 A，并核 OWASP 是否已发新版改编号 / 威胁模型是后续所有安全结论的锚，B 级锚点会污染下游 / 打开 genai.owasp.org 与 nvd.nist.gov 逐条核对条目名、编号、年份 / 状态：未开始（D 线移交，成本低、应最先清）
12. gVisor 现行 syscall 兼容清单与 Systrap 平台的现行性能数字在哪里？/ 兼容性决定工作负载可用性；官方 Performance Guide 数字是旧 ptrace 平台口径，引用即误导 / 查 gVisor 官方兼容性文档现行版本；在目标版本/Systrap 上按 D 线 B7 自测 / 状态：未开始（C 线移交）
13. Firecracker 官方 snapshot 文档原文（快照组成/懒加载/校验）与恢复后熵、机器身份处理（VMGenID 类机制）的官方口径？/ 快照克隆的密钥/随机数重复是 MicroVM 路线的经典事故模型，无官方口径就无法写安全结论 / 读 firecracker 官方 docs/snapshotting 原文与相关实现；辅以 D 线 T23/C6 无害实验设计（待执行） / 状态：未开始（C 线移交；当前底稿中该段仅 C 级线索）
14. WasmEdge 的官方安全/架构文档在哪里？其 WASI 覆盖、socket 等扩展与宿主函数面的安全边界？/ 无此文档就无法与 Wasmtime 做有证据的对比，Wasm 路线结论会缺一半 / 查 WasmEdge 官方 docs 安全章节与扩展清单原文 / 状态：未开始（C 线移交）
15. Microsandbox 的底层 VMM 到底是自研还是基于 libkrun/Firecracker 等？/ 决定其隔离可信度与可审计性，README 只说 microVM / 读 superradcompany/microsandbox 源码的 VMM 依赖与实现 / 状态：未开始（A 线移交）
16. OpenHands 拆分后的新 SDK/runtime 仓在哪里、当前默认执行后端与隔离是什么？/ "OpenHands Runtime=Docker" 是历史结论，现版本（Agent Canvas, v1.33.0）是否成立决定 P7 全部引用 / 追踪 OpenHands 组织新仓与 runtime 调用链源码 / 状态：未开始（A 线移交）
17. Sandbox Fusion 类项目的正确组织/仓名是什么？（以 modelscope/sandbox-fusion 试查为 404）/ 该类多后端融合执行项目在国内生态有代表性，缺位会漏一条技术路线 / 以官方公告/论文反查正确仓名，禁止猜测 URL / 状态：未开始（A 线移交）
18. Modal VM Sandboxes（2026-06）的官方更新原文与默认隔离是否变化？/ 若 VM 类转默认，Modal 的 P6 结论与 gVisor 定价口径都要改 / 查 Modal 官方 changelog/更新页原文 / 状态：未开始（B 线移交；当前 CSV 默认仍按 gVisor A 级，VM Beta 仅 C）
19. Azure 的真正对位产品（Container Apps / Foundry Hosted Agents / Agent Sandbox 类）与 GCP Agent Compute Engine 的 GA 时间与定价？/ 用 Functions/Cloud Run 充数会系统性低估云厂商供给 / 查 Azure 官方产品页与 Google 官方博客/GA 公告原文 / 状态：未开始（B 线移交；ACE 现为预览未定价，不得比价）
20. B 线三处价格/事实冲突待澄清：Blaxel 收购公告原文与 scale-to-zero 5s vs 15s 双数字、Northflank BYOC $0.02083（pricing 页）vs $0.01389（博客）、CodeSandbox 现行套餐层与 credit 口径 / 冲突不澄清则比价表自相矛盾 / 回各家官方公告/pricing 现页逐项复核并记录版本日期 / 状态：未开始（B 线移交；CSV 已按 pricing 页优先并注明冲突）
21. Browserbase 付费 session 6h 上限、Daytona 默认 auto-stop 15min 的官方直引在哪里？/ 两者现在是 B 级多源一致但无官方原文，写进生命周期对比前必须升 A / 查 Browserbase compare 表与 Daytona sandbox 配置文档原文 / 状态：未开始（B 线移交）
22. 两个 license 细节：Wasmtime 完整 SPDX（Apache-2.0 WITH LLVM-exception）逐字核、Cloud Hypervisor LICENSES/ 各文件（Apache-2.0/BSD-3-Clause/CC-BY-4.0）的适用范围 / 影响合规引用准确性，属低成本可清项 / 打开两仓 LICENSE 原文逐字核 / 状态：未开始（A 线移交）
23. isolate tag v2.7 的日期、Judge0 的现行发布渠道（是否转 Docker 镜像/EE 版）？/ 两者决定 P2 的版本引用口径，并影响下游（Judge0/Piston 依赖 isolate） / 查 tag 指向 commit 日期、Judge0 官方发布说明/Docker Hub 与 EE 文档 / 状态：未开始（A 线移交）
24. 各主流发行版对 unprivileged user namespace 的默认策略（开启/受限/关闭）分别是什么？/ rootless 路线在生产宿主上是否可用取决于此，"本地能跑"不可推广 / 按目标发行版官方文档逐个核 / 状态：未开始（C 线移交）
25. D 线评测体系的待冻结项：C 组通过线阈值、D5 用户画像参数、标准任务套件 v0.1（ST-1~ST-6）细节 / 阈值后改即失去可复现性，必须在任何实测前冻结 / 主线评审 D 线底稿后冻结并写入复现包规范 / 状态：未开始（D 线移交；全部 25 条威胁验证方法与 32 条指标现均为"待执行"，无任何 SELF 数据）
26. 同域未核实的知名基础设施：crosvm、QEMU/microvm、Wasmer、Spin、wasmCloud、KubeVirt 等是否应入表？/ 影响 Infra 与 Wasm 路线的完整性判断 / 按 A 线候选流程逐仓核实（存在性→README→版本/license） / 状态：未开始（A 线移交，优先级低于第 3/13/15/16 问的源码深研）
27. B 线仅登记未入表的 20+ 候选（Prized、Tensorlake、Deno Sandbox、LangSmith Sandboxes、Prime Intellect Sandboxes、exe.dev、OpenComputer、Namespace、Superserve、Hopx、Islo、Sandboxs.ai、Mainbrella、Together Code Sandbox 独立定价、DigitalOcean Managed Agents、Anchor Browser、Browser Use Cloud 等）的取舍？/ 决定 Round 2 发现面的宽度与 P1/P3 覆盖可信度 / 逐个以官网一手做形态判定，能判定的入表、判定为邻域的学 HF Spaces 例单列排除 / 状态：未开始（B 线移交）
