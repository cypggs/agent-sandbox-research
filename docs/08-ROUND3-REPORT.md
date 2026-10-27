# 08 · Round 3 阶段报告：Fast 外仓补完 + E2B runtime 源码深研

> 项目：Agent Sandbox 全领域技术研究（goal_a756da9ace9a）
> 阶段：Phase 2 产品数据库 v0.3；Phase 3 源码深研 2/53（OpenSandbox 双仓、E2B runtime）
> 日期：2026-10-27（Asia/Shanghai）｜ 证据等级：A 官方/源码/论文 · B 可靠独立 · C 推断待验证 · U 未知
> 输入底稿：files/06-FAST-SANDBOX-DEEP-DIVE.md（fast-sandbox HEAD `e0cd543`）、files/07-E2B-RUNTIME-DEEP-DIVE.md（runtime HEAD `92b83da`）、hidden_files/research/round3-A-fast-log.md
> 两轮深研均为纯静态源码分析：未部署、未运行、未调用任何云 API。本轮仍无任何自测数据（SELF=0），所有性能数字均为官方公布值并已标注。

## 1. 执行摘要

### 1.1 Fast 外仓（深研第 2 号的补完部分）：一个年轻平台、两层协议、一个双口径

1. **Fast 不是主仓的一个库，而是一个独立的 K8s 原生平台。** [A] 本仓自带 FastPath 控制面、CRD reconciler、Fastlet 节点代理、Firecracker 驱动、制品运行时 agent、Janitor 与模板构建器（660 文件、502 个 Go 文件、217 个测试文件，与主仓同级）；主仓只是它的一个客户端。成熟度口径必须带上：**无任何 release/tag、主仓以 commit pin 集成、CRD 仍是 v1alpha2 alpha、2026-01 才建仓**——引用其能力时不得与主仓 1.1.x 的发布面貌类比。
2. **协议是两层，不要混。** [A] 对外是 FastPath gRPC v2（:9090，15 个 RPC，proto 单一源头在本仓）；平台内控制面→Fastlet 这一跳是 **HTTP/JSON :5758**（`/api/v2/fastlet/*`），不是 gRPC；第三面是 Fastlet↔egress Handler 的 Sandbox Actions 通道（SET_BINDING 与 VAULT_/POLICY_ 转移）。Round 2 所说的"主仓有 FastPath gRPC 客户端"只对了一半。
3. **Firecracker 集成定案**：每沙箱一个 microVM、**快照恢复是唯一启动路径**（Create 与 Resume 共用同一恢复机器，无冷启动直启）；**jailer 可选**——仅配置 `JailerPath` 时才进 jailer-chroot 模式，未配置则直接子进程启动。禁止再写"Fast 路径必经 jailer"。[A]
4. **状态搬运定案**：checkpoint 时 StateMover **只搬文件路径、不搬状态字节**（原文 "no state bytes ever cross this process"）；egress 的策略执行（DNS/nft/L7）与 vault 的 v1 明文文件格式都在**主仓** `components/egress` 定义，外仓是编排者。Fast 路径的安全审计对象因此仍是主仓 egress。[A]
5. **create p50 出现两个官方口径，并存且不可互换**：外仓 README 的 77.9ms（暖池串行 SDK，2026-10-08 ACK）与主仓文档的 64.0ms 是不同样本集/完成口径。加上 Create 本身有 Ready 与 RuntimeReady 两种完成口径，任何 Fast 创建延迟引用必须注明口径与出处。[A：官方公布，未实测]
6. **62s 仍然未解，且边界已划清**：代码层已可证主因不在 VM 恢复本身（恢复机器与 create 共用、本地缓存命中为 ms 级；跨节点拉取 ~16s/3.5GiB、route 代际重解析、CR 状态投影与 SDK 轮询、vault/policy import 前置均为构成线索），但**没有任何分段计量能把 62s 拆账**，归因维持未证实，只能实验室实测（Q34）。[A 构成 / U 归因]
7. **新发现 F9**：外仓注释断言模板 vault 记录 "rides encrypted at rest"，双仓却 grep 不到任何加密实现（主仓只有 TODO 与 "v1 is plaintext"）。该断言标 U、已升格进 Q30 双件跟踪（落地实现 / 修正注释）。[A：grep 事实；断言本身 U]

### 1.2 E2B runtime（深研第 2 号）：不用 jailer、默认拒绝是硬编码、运营层在仓外

1. **链路证实并补全**：`SDK/CLI ─REST→ API ─gRPC→ orchestrator ─▶ Firecracker microVM ─▶ envd` 逐环对应源码；且"创建 sandbox"本质是"恢复快照"——模板即预启动 VM 的内存+磁盘+机器状态快照，创建/暂停/恢复/fork 同路同 artifact（diff 链）。流量路径（client-proxy→节点 proxy→envd）永不经过 API。[A]
2. **最重要边界修正：E2B 不用 Firecracker jailer。** FC 进程由以 **root** 运行的 orchestrator 直接拉起，宿主侧收敛靠每沙箱 cgroup + 独立 netns + nftables，而非 jailer 的 chroot+降权。写 E2B 隔离结论时必须带这一条——它的 hypervisor 边界很硬，但宿主侧信任边界比教科书 Firecracker 部署更依赖 orchestrator 自身代码质量。[A]
3. **元数据处理与 OpenSandbox 形成干净对照（本轮最有选型价值的对照结论）**：E2B 的 `DeniedSandboxCIDRs` 是**硬编码默认拒绝表**——RFC1918/CGNAT/loopback/169.254.0.0/16（含云元数据，代码注释明写）排在一切放行规则之前，豁免需要运维显式动作；而 OpenSandbox 双仓复核后的口径是**非默认、配方制**（无硬编码、文档明文归责部署方）。同一风险面，一个默认安全、一个默认开放待配方——这正是"机制强≠默认强"的双向实证。[A × 双仓]
4. **运营层仓外三件套**：① 计费与套餐档位由仓外 owning management service 拥有，本仓只消费 `project_limits` 投影与一行 `default_limits`；② secrets 的值存储与出口解析在仓外 secrets-store 后端与 `orchestrator-ee`（本仓 `/secrets` 只做元数据 CRUD 与转发，未配置答 403）；③ webhooks 后端是外部 gRPC 服务（未配置答 503）。即"开源全栈"在计费/secrets/webhooks 三面不完整，Embed 单机部署里这些面要么不存在、要么用部署级默认值。[A：以代码中的外部接缝为据]
5. **Q1 结案（见 §2.2 与 OPEN-QUESTIONS Q1）**：**同源同线已证、此刻同版本无法证**。同一代码库、同一隔离栈、同一 OpenAPI/SDK（A）；但 Cloud 的真相源是内部 monorepo，公开仓是 copybara 只读镜像，Embed 在平台 tag 之后以平台版本跟进发布，Cloud 线上版本无公开对照（U 尾巴保留）。

### 1.3 数据库净效果

products.csv 仍 53 行、无新增/删除；confidence 分布与 Round 2 **完全相同（A 21 / B 14 / C 17 / U 1）**——两条深研行原本即为 A，本轮是把 A 的成色从"文档级"换成"源码级"，不是升格。深研计数 1 → **2**（OpenSandbox 计 1 个产品、含其 Fast 组件；E2B 计 1）。待验证仍 14。详见 COVERAGE.md Round 3 对账。

## 2. Round 2 遗留裁定总表

### 2.1 Fast 8 项（基数 = 04 报告 §10/§3/§14 中涉及 Fast 内部实现的遗留项；逐项见 06 报告 §9）

| # | 遗留项 | 裁定 |
|---|---|---|
| F1 | Fast = Firecracker microVM（Round 2 仅证到集成层） | **证实**（升级为源码级：driver 包自述 + EnsureSandbox/launchVM 实现） |
| F2 | egress 是每 Fastlet 一个共享进程、per-subject 策略 | **证实**（细化：共享的是 Pool 声明的 Action Handler 进程即主仓 egress 二进制，Fastlet 经 Actions 通道发 SET_BINDING 区分 subject） |
| F3 | Vault Fast 路径有明文 v1 文件、"只活内存"不成立 | **证实**（外仓只搬路径；格式与明文事实在主仓 persist 原文，TODO 未落地） |
| F4 | 两套 checkpoint 互不共享（Fast 内容寻址 artifact） | **证实**（manifest/SHA256SUMS/`checkpoint:sha256:<digest>` 全实现，与 operator 的 OCI commit 无代码共享） |
| F5 | 元数据阻断不是默认 | **证实**（证据升级：双仓 grep 无命中 + 外仓文档明文归责部署方 + 默认策略允许 CIDR 外出口） |
| F6 | Fast Janitor 扫孤儿 | **证实**（`cmd/janitor` + 多后端扫描 + nodecleanup 残留进程契约） |
| F7 | 64ms 创建 / 35ms 恢复的运行时数字 | **修正（口径再收紧）**：create p50 双口径并存（77.9ms vs 64.0ms 不可互换）；35ms 级恢复仅本地缓存命中成立，跨节点为秒–分钟 |
| F8 | SDK resume ≈62s 的差距归因 | **仍未证实**（构成线索齐、拆账计量无；转 Q34 实验室） |
| F9 | （新增）模板 vault 记录 "rides encrypted at rest"（外仓注释断言） | **仍未证实（与代码现状冲突）**：双仓无加密实现；按设计意图处理，已升格进 Q30 |

> 计数说明（防误引）：按 06 报告 §9 逐项枚举，F1–F8 为证实 6 / 修正 1 / 未证实 1；F9 为新增未证实，单列。06 报告正文的汇总句写作"证实 5"，与其自身逐项表枚举差 1——本报告以逐项表为准并在此登记该出入，06 原文不改、待其勘误时一并处理。引用本轮裁定请引逐项表，不要引汇总句。

### 2.2 E2B 旧结论裁定（对象 = 2026-10-01 E2B Embed 笔记 (a) 与 Round 1 A 线结论 (b)，逐项见 07 报告 §8.1）

| 旧结论 | 裁定 |
|---|---|
| (a) Embed 是 Apache-2.0 单机自托管完整栈 | **证实**（"runs the whole E2B stack, every feature included, on a single machine"；单节点持有控制面/数据面/模板与快照存储/日志指标/Dashboard 逐项对应） |
| (a) 与 Cloud 相同 SDK/API，迁移主要是改 endpoint | **证实（官方自述级）**（"Same SDK, same API as E2B Cloud"；同一 OpenAPI spec 即本仓 API 生成源头） |
| (a) 部署形态（旧笔记语境 = 单机手动装） | **修正/扩展**：现行 Embed 官方分发为 Docker Compose / Terraform（GCP/AWS/Azure）/ Kubernetes 四种，镜像全部 pin 版本；且官方明示单机是设计上限，多节点走 BYOC/私有云/Cloud |
| (b) 运行时仓 infra→runtime 更名 | **证实**（gh 现名 e2b-dev/runtime；但 Go module 路径仍是 `github.com/e2b-dev/infra`，引用代码路径时须用旧路径） |
| (b) 链路 SDK/CLI→API→orchestrator→Firecracker→envd | **证实并补全**（补：流量路径不经 API；模板构建是同二进制的 template-manager 角色） |

汇总：证实 4、修正/扩展 1、证伪 0。Q1 由此结案到可证边界（同源同线 A；此刻同版本 U，见 OPEN-QUESTIONS Q1）。

## 3. CSV 变更清单（products.csv v0.2 → v0.3，行数不变 53）

| 产品行 | 变更字段 | 变更内容 | 依据 |
|---|---|---|---|
| E2B | isolation_tech、network_control、credential_security、deployment、latest_version、limitations、official_evidence、notes | isolation 改为"快照恢复为唯一/主启动路径 + 不用 jailer + orchestrator root 拉起 FC + 每沙箱 cgroup/netns"；network 写入硬编码 `DeniedSandboxCIDRs` 默认拒绝（含 169.254.0.0/16）与豁免开关；credential 写入 secrets 值解析在仓外 secrets-store/orchestrator-ee 的接缝事实；deployment 改为 Embed 四种分发（Compose/Terraform/K8s/BYOC）；latest_version 改为 GitHub Release 2026.30（2026-09-10）+ envd 0.10.2（另注 copybara 镜像与组件 SemVer）；limitations 改写为运营层仓外/不用 jailer/flag 密度/熵区分 U；official_evidence 补源码路径与 HEAD 92b83da；notes 标 Round 3 深研完成与 Q1 结论。confidence 保持 A | runtime 仓源码 HEAD 92b83da（A） |
| OpenSandbox | lifecycle、network_control、credential_security、startup_latency、limitations、notes | 在 Round 2 回填上补 Fast 外仓定案：lifecycle 补"snapshot 恢复唯一启动路径、jailer 可选、StateMover 只搬路径"；network 补"Fastlet HTTP/JSON :5758 内层协议、egress 执行与 vault 格式在主仓、SET_BINDING per-subject、元数据非默认双仓结论"；credential 补"vault v1 明文格式在主仓 egress 定义、外仓只传路径与 fence"；startup_latency 补 77.9ms 第二口径并存警告与 35ms 的缓存命中限定；limitations 补"fast-sandbox 无 release/tag 以 commit pin 集成、CRD v1alpha2 alpha、F9 加密注释-代码冲突标 U、62s 归因未证实"；notes 改为"主仓+Fast 外仓双深研完成" | fast-sandbox 源码 HEAD e0cd543 + 主仓 HEAD dbcc6d7（A） |

## 4. 未验证项（明确未清，不许当已清引用）

- **Fast 62s resume 的精确分段归因**：双仓无计量拆分，U（Q34，待实验室）。
- **F9 vault "encrypted at rest" 断言**：与双仓代码现状冲突，U（Q30 升格跟踪上游落地或改注释）。
- **E2B 此刻同版本性**：Cloud 线上版本未公开、公开仓是 copybara 镜像，U（Q1 尾巴，随结案保留）。
- **E2B 快照克隆的 guest 熵区分**：仓内有 virtio-rng 熵补充，但 grep 无 VMGenID/克隆通知处理，同快照 guest 的随机状态区分机制未找到，U（Q32，实验室议题）。
- **E2B RELEASING 与实际 GitHub Releases 的张力**：RELEASING 称无 GitHub Releases、实测有 2026.03–2026.30，官方未澄清，B 待澄清（Q33）；引用版本以 gh 实测为准。
- **E2B tcpfirewall 的 DNS rebinding 防护口径**：域名放行以解析结果落规则，完整防护未专项追踪，C。
- **仓外后端实现细节**（orchestrator-ee 的 secrets 出口注入粒度、secrets-store/webhooks 后端）：不在公开仓，只能以 API 侧元数据契约推断，C。
- **两家均未部署实测**：OpenSandbox 双仓与 E2B runtime（含 Embed "单机可跑通"官方自述，B）都只读了源码；全项目 SELF 数据仍为 0（Q35 状态登记）。其余 Round 2 遗留未动项（Q9 五家隔离、Q12 gVisor、Q13 Firecracker 官方原文、Q14 WasmEdge、Q15 Microsandbox、Q16 OpenHands、Q25 阈值冻结等）状态不变，见 OPEN-QUESTIONS。

## 5. Round 4 建议（按 05 报告既定序推进：深研已连做两轮，轮到实验室）

1. **实验室第一批（本轮建议的第 1 位）**。理由：05 报告既定序中两个深研位（Fast、E2B）已清完，下一位就是实验室；且本轮新登记的三个问题（Q32 熵、Q34 62s 拆账、Q29 配方实效）全部只能靠实测关闭，SELF=0 已成为全项目最大的系统性限定（Q35）。第一批顺序：
   - **先冻结 Q25**：C 组通过线阈值、D5 用户画像参数、标准任务套件 v0.1（ST-1~ST-6）——阈值后改即失去可复现性，必须在任何实测之前落字冻结。
   - **Q29 并入 C8 网络策略矩阵**：在自建集群按官方指南部署 OpenSandbox 并配 deny.always 配方，用 C8 矩阵 + 元数据哨兵地址验证配方实效与 04 报告所列软点（DNS 学习放行内网域名、L1-only 降级、模式字符串非法降级 dns-only）。
   - **E2B 熵议题（Q32）入实验清单**：自建 Embed 节点同模板恢复两个 sandbox，对比 boot_id 与熵池行为——这是 Q13（Firecracker 官方快照口径）在产品实现层的可测化身，成本低、结论硬。
   - **Q34 顺带拆账**：若 OpenSandbox 部署已为 Q29 立起来，Fast 路径按 t_submit/t_ack/t_ready + 分段探针测 resume，边际成本只剩探针与计时。
   - 基础三项不丢：namespace/seccomp 探针、超时后进程清零（C4）仍是实验室的立身项，与上面四项同批设计、分批执行。
2. **五家隔离未公开攻坚（Runloop + 四家 Browser SaaS，Q9，联动 Q6）**。理由：顺序天然在实验室之后——先穷尽安全文档/信任中心（低成本文档轮），仍无表述者转 C8 矩阵自测会话隔离与元数据可达性，而 C8 能力正是第 1 项的产出；先建能力再攻坚，避免每个目标重复造轮子。
3. **Firecracker 深研（含 Q13 官方 snapshot 原文与恢复后熵/VMGenID 口径）**。理由：两个平台深研都收敛到同一底座，且 Q32 的实验结论需要 Firecracker 官方口径做对照才能定性；排在实验室之后是因为实验会先把"现象"钉住，深研再回答"机制是否本来如此"。
4. **gVisor 选读（Sentry/Gofer/Systrap 三线 + Q12 兼容清单）**。理由不变（05 报告）：四个底座候选里代码量与概念密度最高、与本项目自建问题的对应度最低，只选读不通读；且 Modal/GKE 的默认运行时身份使它在选型框架成稿前必须补齐。

Round 4 之后的既有队列不变：P4 Computer Use 发现轮、候选池消化（Q26/Q27）、Microsandbox VMM（Q15）、OpenHands 新仓（Q16）、WasmEdge 安全文档（Q14）、选型框架与 90 天路线。

## 6. 本轮纪律自检

- 两份深研报告（06/07）本轮只读不改；全部回填结论可回溯到其章节与源码路径/HEAD（Fast `e0cd543`、E2B `92b83da`、OpenSandbox 主仓 `dbcc6d7`）。
- 未把"同源"写成"同版本"：Q1 结案措辞为"回答到可证边界"，U 尾巴在 CSV notes、OPEN-QUESTIONS 与本报告 §4 三处同写，没有被结案动作吞掉。
- 未把官方数字写成实测：64.0/77.9ms 双口径并存警告已同时写入 CSV 的 startup_latency 与 limitations；SELF 仍为 0 并新登记为 Q35 状态项，不再只散落在各轮报告里。
- 发现底稿内部计数出入（06 汇总句 vs 逐项表）时未静默改数、未改原文：在 §2.1 登记出入并声明以逐项表为准。
- 未宣称覆盖完整：深研 2/53、实验 0 次；未清项逐项登记（OPEN-QUESTIONS 现 35 问，Round 3 新增 Q32–Q35）。
