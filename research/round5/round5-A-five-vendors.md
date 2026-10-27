# Round 5 线 A · 五家隔离未公开攻坚（对应 OPEN-QUESTIONS Q9 / Q6）

- 轮次：Round 5 线 A（分支 B 第 1 项）
- 日期：2026-10-27
- 对象：Runloop、Browserbase、Browserless、Steel.dev、Hyperbrowser
- Round 1 基线：五家官方 pricing/docs 均未述底层隔离，CSV 中 isolation_tech 均为「未公开」，confidence 均为 B（定价 A、隔离 U）。
- 本轮方法：逐家穷尽官方渠道六类——①官网 security/trust 页与 trust center 子域 ②docs 的 architecture/security/isolation 页 ③官方 blog 工程文 ④官方 GitHub 组织 ⑤SOC 2/合规页的 tenant isolation 表述 ⑥changelog/状态页。每家均留下「搜索路径清单」证明穷尽。
- 证据等级：官方明示=A；官方材料可推断=B/C 并注明推断链；第三方=C 并注明来源性质。**开源/自托管版架构 ≠ SaaS 架构，全文分开判定，禁止等同。**
- 本文件只给结论与 CSV 回填建议，**不修改 products.csv 与 files/**。

---

## 1. Runloop（runloop.ai）

### 1.1 搜索路径清单（本轮实际走过）

| 渠道 | 路径 | 结果 |
|---|---|---|
| 官网 | runloop.ai 首页 / 平台页 | 平台定性表述，无隔离机制 |
| 官网 pricing | https://runloop.ai/pricing（已全文打开） | Enterprise 含「Deploy to VPC」；页脚有 AICPA SOC 徽标与 HIPAA Compliant 标识图；FAQ 含「Does the Enterprise plan include SOC2 and compliance certifications?」条目（正文未在抓取中展开） |
| docs | https://docs.runloop.ai/docs/devboxes/overview（Devbox Overview，已全文打开，页面更新 2026-05-19） | **命中隔离明示**（见发现表 R-1） |
| docs | Network Policies 相关页（经官方 blog 互链定位） | egress 策略能力（R-3） |
| 官方 blog | https://runloop.ai/blog/network-policies-release 《Safer Agents with Network Policies》 | hostname allowlist / deny-all 策略细节（R-3） |
| 官方 SDK | PyPI `runloop_api_client`（厂商发布）README | **命中「VM and container level」明示**（R-2） |
| 官方新闻稿 | GlobeNewswire 2026-06-10 《Trajectory Uses Runloop to Scale Continual Learning》（厂商发稿、第三方电讯社站点承载，已打开原文） | 「isolated microVM」表述（R-4，仅 B） |
| GitHub 组织 | github.com/runloopai 全仓清单（gh API 实测） | 主体为 SDK/示例；**forks 命中 kata-containers、cloud-hypervisor/rust-hypervisor-firmware、containerd/overlaybd**（R-5，C 级线索） |
| Trust center | trust.oneleet.com/runloop（第三方汇总 rl-list 所述，未能打开核实） | 登记为「存在但未核」路径，不作证据 |
| 安全/合规页 | runloop.ai 自述 SOC 2 Type II / HIPAA / GDPR（定价页与官网口径，R1 已记） | 组织合规口径，无隔离技术细节 |
| 同名异物排除 | docs.runloop.sh 的「Runloop OS」（WASM agent）与 runloop.ai **无关**，本轮明确排除、未引用 | — |

### 1.2 发现表

| # | 事实 | 原文要点 | 来源 | 等级 |
|---|---|---|---|---|
| R-1 | ①隔离机制=SaaS 用 VM 技术 | “We use virtual machine technology to provide isolation”；Devbox 为 “Isolated, ephemeral virtual machines…created on demand, and deleted when no longer needed” | docs.runloop.ai Devbox Overview | **A** |
| R-2 | ①隔离为 VM + 容器双层 | “Every devbox is isolated at both the VM and container level” | 官方 Python SDK（PyPI runloop_api_client）README | **A**（厂商发布物；与 R-1 互证） |
| R-3 | ③egress 可控：Network Policies | hostname allowlist（支持通配）、deny-all 策略、blueprint 级与运行时两级策略、即时传播；另有 Agent Gateways / MCP Hub 使真实凭证不进入 devbox | docs + 官方 blog network-policies-release | **A**（能力）；**默认策略是否 deny-all 未述 → 默认口径 U** |
| R-4 | ①「microVM」字样 | “Each Devbox is an isolated microVM that spins up in under 500ms… credentials never entering the training environment, customer-by-customer isolation” | GlobeNewswire 2026-06-10 厂商新闻稿（Trajectory 案例） | **B**（官方发稿但属 PR 渠道；docs 未用 microVM 一词，VMM 名未点名） |
| R-5 | ①技术栈强线索：Kata + Cloud Hypervisor + overlaybd | runloopai 组织 fork 了 kata-containers（pushed 2025-11-06）、cloud-hypervisor 的 rust-hypervisor-firmware（2025-10-29）、containerd/overlaybd（2026-08-25）、containerd | gh API 实测组织仓库清单 | **C**（fork 行为与「VM+容器双层」自述吻合，指向 Kata Containers + Cloud Hypervisor 栈；fork ≠ 生产使用，禁止写成事实） |
| R-6 | ②session 边界 = 每 Devbox 一台临时 VM | 随 R-1：devbox 按需创建、不再需要时删除 | docs Devbox Overview | **A** |
| R-7 | ④数据驻留区域 | 官方渠道未见区域/驻留表述；Enterprise 可 Deploy to VPC（AWS/GCP/Azure 为第三方汇总口径，未回官方 enterprise 页逐字核） | pricing 页（VPC 项） | VPC=**A**（pricing 明示）；区域驻留=**U** |
| R-8 | ③元数据（169.254）默认策略 | 全部官方渠道未见专项表述 | — | **U** |

### 1.3 结论等级

**Runloop：隔离由 U 升 A−。** 官方 docs 与官方 SDK 双源明示「VM 技术 + VM 与容器双层隔离、每 Devbox 一台临时 VM、用完删除」（A）；「microVM」仅见厂商 PR 稿（B）；具体 VMM 名未点名，Kata/Cloud Hypervisor 仅为组织 fork 的 C 级强线索。egress 有 allowlist/deny-all 策略能力（A），但**默认策略口径与元数据专项策略仍 U**；数据驻留区域未公开（U），Enterprise VPC 为 A。

---

## 2. Browserbase（browserbase.com）

### 2.1 搜索路径清单

| 渠道 | 路径 | 结果 |
|---|---|---|
| docs 企业安全页 | https://docs.browserbase.com/account/enterprise/security（已全文打开，页面更新 2026-10-08） | **本轮五家中最完整的隔离明示**（B-1~B-5） |
| Trust center | trust.browserbase.com（docs 内有官方链接存在性确认；本轮未打开核内容） | 登记为已知门户，内容未核，不作证据 |
| 官网 / pricing | browserbase.com、pricing 页（R1 + Round 2 Q21 已复核） | 定价 A；session 6h 上限官方原文不存在（Q21 已结，维持 B 疑旧版数字，本轮不重复） |
| docs 其他 | session/timeout/keepAlive、Contexts 相关页（R1 已查） | 产品能力层，无隔离实现新增 |
| 官方 blog / changelog | blog 与 changelog 检索「VM / Firecracker / isolation」 | 未见点名 VMM 的工程文；VMM 名维持未点名 |
| GitHub 组织 | browserbase 组织（Stagehand 等客户端/框架仓为主） | 无服务端架构仓（SaaS 闭源），无新增证据 |
| 合规 | SOC 2 Type II、HIPAA/BAA、第三方渗透测试——均见于上述 docs 企业安全页 | A（官方页明示） |

### 2.2 发现表

| # | 事实 | 原文要点 | 来源 | 等级 |
|---|---|---|---|---|
| B-1 | ①隔离机制 = 每浏览器一台专用 VM | Isolation = “1 browser per VM”；“Each browser runs in a dedicated VM, providing strong isolation at the hardware virtualization layer” | docs 企业安全页 | **A** |
| B-2 | ②session 边界与网络隔离 | 每浏览器独立 subnet + 严格防火墙规则防横向移动；无 GPU 访问 | 同上 | **A** |
| B-3 | ④会话销毁 = 不复用 | “No browser reuse”：session 结束后 VM 被 kill 并从零重建 | 同上 | **A** |
| B-4 | ④数据驻留可选区域 | US West / US East / EU (Germany) / Asia (Singapore) | 同上 | **A** |
| B-5 | ④零留存选项 | 可经 Create Session API 关闭日志与 session replay 实现 zero data retention | 同上 | **A** |
| B-6 | ①VMM 技术名（Firecracker 等） | 官方全渠道未点名，只到「VM / hardware virtualization layer」 | — | **U**（只能写「VM（官方未点名 VMM）」） |
| B-7 | ③元数据/169.254 默认策略 | 仅有 subnet + 防火墙的定性表述，无元数据专项默认策略原文 | — | **U** |

### 2.3 结论等级

**Browserbase：隔离升 A——五家中唯一把四问答全三问半的一家。** 「1 browser per VM、硬件虚拟化层隔离、独立 subnet + 严格防火墙、session 后 VM 销毁重建不复用、驻留四区域可选」均为官方 docs 明示（A）。缺口只剩：VMM 未点名（U）、元数据默认策略无专项表述（U）。

---

## 3. Browserless（browserless.io）

### 3.1 搜索路径清单

| 渠道 | 路径 | 结果 |
|---|---|---|
| Trust Center | https://www.browserless.io/trust（已全文打开） | **命中容器化与网络隔离表述 + 罕见的数据驻留细则**（L-1、L-4） |
| 官方 blog | https://www.browserless.io/blog/browser-infrastructure-for-computer-use-agents（已打开） | 每连接独立 browser instance 明示（L-2） |
| 官网 / pricing | browserless.io、pricing（R1 已核：Unit 计费、双许可等） | 定价 A |
| docs | BaaS / self-hosting 文档（R1 + 本轮） | 自托管形态；Enterprise 自托管镜像「与云端跑的是同一个 container」（官方 self-host 文自述，L-5） |
| GitHub 组织 | github.com/browserless/browserless（gh 实测：一手） | **开源版形态：单个 Docker 镜像内承载多个浏览器进程**，并发由 `src/config.ts` 的 MAX_CONCURRENT_SESSIONS/CONCURRENT 控制（L-3） |
| 合规 | SOC 2 Type II、GDPR、BAA、DPA——见 Trust Center | A（组织级；注：自托管部署在客户自身审计边界内） |
| 安全联系 | security@browserless.io（Trust Center 明示） | — |

### 3.2 发现表

| # | 事实 | 原文要点 | 来源 | 等级 |
|---|---|---|---|---|
| L-1 | ①SaaS 隔离 = 容器化浏览器环境 + 网络分段 | “Containerized browser environments”；“Network segmentation and isolation”；“Browser automation runs in isolated environments” | 官方 Trust Center | **A**（官方表述粒度只到「容器化环境」，未点名每 session 一容器） |
| L-2 | ②session 边界 = 每连接独立浏览器实例 | “Every Browserless connection gets its own browser instance, so one poisoned session can't read another's cookies or state”；文中另建议用户侧域名 allowlist（产品建议，非默认强制） | 官方 blog | **A**（边界语义）；allowlist 默认强制性 = 否（官方仅建议） |
| L-3 | ①**开源/自托管版**形态 = 单容器多浏览器进程 | 单个 Docker 镜像内以并发参数控制多个浏览器进程，会话分离在进程级 | browserless/browserless 仓 `src/config.ts` 等一手核实 | **A（仅开源版事实）**；与 SaaS 拓扑不得等同 |
| L-4 | ④数据驻留细则（诚实口径） | 存储主要在美国（AWS / DigitalOcean / Supabase）；区域端点（San Francisco / London / Amsterdam）只决定浏览器执行地，存储/转发数据仍可能出 EU，**仅 Amsterdam 在 EU 内**；终止服务后按内部政策删除 | 官方 Trust Center | **A** |
| L-5 | SaaS 与自托管关系 | Enterprise 自托管镜像「与云端跑的是同一个 container」 | 官方 self-host 文档自述 | **A**（镜像同一性）；但 SaaS 的部署拓扑（每租户/每 session 如何切分）官方未述，**不得由镜像同一性推出拓扑同一性** |
| L-6 | ③元数据默认策略 | 官方全渠道未述 | — | **U** |
| L-7 | ①SaaS 每 session 是否独立容器 | Trust Center 只到「容器化环境」粒度，未点名 | — | **U**（粒度未明） |

### 3.3 结论等级

**Browserless：SaaS 隔离 B+，开源版 A，分开记。** SaaS 侧官方明示「容器化环境 + 网络分段 + 每连接独立 browser instance」（A 级表述），但是否每 session 独立容器未点名、元数据策略未述，故 SaaS 综合 B+。开源/自托管版为 A 级事实：**单个 Docker 容器内多浏览器进程、进程级会话分离**——与 SaaS 不得等同。数据驻留细则是五家中最诚实的一家（A）。

---

## 4. Steel.dev（steel.dev）

### 4.1 搜索路径清单

| 渠道 | 路径 | 结果 |
|---|---|---|
| 官网 | steel.dev 现页（已打开） | 仅 “Isolated sessions” 营销语 + “Encrypted in transit”、HIPAA signed BAAs、Enterprise “Dedicated capacity”（S-1） |
| 自托管产品页 | Steel Outpost（官网，企业自托管） | “data stays in your network”、BYOK、your own region（S-2，驻留口径 A、隔离机制仍无） |
| docs | docs.steel.dev：Credentials API 等（已核） | 凭证加密存储、注入不暴露给 agent、防注入后提取（S-3，凭证子项 A 级产品表述） |
| docs | sessions / self-hosting 相关页检索 | 会话 API 语义层，无租户隔离机制表述 |
| GitHub 组织 | github.com/steel-dev/steel-browser（一手核实） | **开源版：docker-compose 为 api+ui 两服务，单个 api 容器内管理多个浏览器进程/session**（S-4） |
| 合作方材料 | Fly.io 官方客户故事（2024 年，距今约 762 天）引 Steel 联创原话 | Steel 跑在 Fly Machines API 上、主 orchestrator API 路由 session 到 browser instances、全部在 WireGuard 隧道后不对公网暴露（S-5） |
| 合规 | SOC 2：官方全渠道未见明示（仅 HIPAA BAA 口径） | SOC 2 = **U** |
| Trust center 子域 | trust.steel.dev 等未见官方链接 | 未发现门户 |

### 4.2 发现表

| # | 事实 | 原文要点 | 来源 | 等级 |
|---|---|---|---|---|
| S-1 | ①SaaS 隔离 | 官网仅 “Isolated sessions” 一语，无机制、无边界定义 | steel.dev | **C 级营销表述**（不足以定性） |
| S-2 | ④自托管驻留 | Outpost：data stays in your network、BYOK、your own region | 官网 Outpost 页 | **A**（自托管驻留口径）；隔离机制未述 |
| S-3 | 凭证安全 | Credentials API：凭证加密存储、注入时不暴露给 agent、防注入后提取 | docs.steel.dev | **A**（产品表述，凭证子项） |
| S-4 | ①**开源版**形态 = 单 api 容器多浏览器进程 | docker-compose 为 api+ui 两服务；README 自述 api “manages sessions, pages, and browser processes”——自托管会话分离在单容器内进程级 | steel-dev/steel-browser 一手 | **A（仅开源版事实）** |
| S-5 | ①SaaS 历史架构线索 | Steel 跑在 Fly Machines API 上，orchestrator 路由 session，WireGuard 隧道后不暴露公网（Fly Machines 本身为 Firecracker microVM 属 Fly 官方架构） | Fly.io 客户故事（2024）引联创原话 | **B/C**：来源为合作方、距今约 2 年；「Steel 现在仍全量跑 Fly」未证，**禁止写成现行事实**，引用必须带 2024 年日期 |
| S-6 | ③egress/元数据默认策略 | 官方全渠道未述 | — | **U** |
| S-7 | SOC 2 | 官方未见明示（仅 HIPAA BAA） | — | **U** |

### 4.3 结论等级

**Steel.dev：SaaS 隔离维持 U（仅营销语），开源版 A。** SaaS 侧官方只有 “Isolated sessions” 一语与 2024 年合作方客户故事（Fly Machines 线索，B/C 且须注日期），不足以定性现行隔离，维持 U。开源版为 A 级事实：**单个 api 容器内多浏览器进程、进程级会话分离**。凭证子项（Credentials API）与自托管驻留（Outpost）各有 A 级产品表述，但不改变隔离判定。

---

## 5. Hyperbrowser（hyperbrowser.ai）

### 5.1 搜索路径清单

| 渠道 | 路径 | 结果 |
|---|---|---|
| 官方安全页 | https://hyperbrowser.ai/security（已全文打开，页面更新 2026-05-07） | 通篇组织安全：加密 at rest/in transit、季度访问审查、年度渗透测试、数据托管美国；自称 “aligned with SOC 2 Trust Services Criteria”——**未声称取得 SOC 2 认证**（H-1、H-2） |
| Trust Center | https://trust.hyperbrowser.ai（已打开；主体名 S2 Labs） | 全是通用 SOC 2 控制条目（变更/可用性/保密/漏洞/事件/网络安全政策类），**零租户隔离/会话边界技术内容**（H-3） |
| docs | docs 站点 Sandbox 产品页（introduction/CLI 等，已核） | 只有 Sandbox 产品语义（image/cpu/memory/disk/volumes/snapshots、<50ms 启动口径），隔离机制未述（H-4） |
| SDK | PyPI hyperbrowser SDK 文档 | 同 docs，只有产品语义 |
| 官网 / pricing | hyperbrowser.ai、pricing（R1 已核） | Sandbox 按 VM 计费（官方称 VM 定性 A-、技术名未公开，R1 口径维持） |
| 官方 blog / 第三方 | blog 与第三方有「Enterprise 含 SOC 2」说法 | 与 security 页口径**冲突**，以 security 页为准（H-2） |
| GitHub 组织 | hyperbrowserai 组织（SDK/MCP 类仓为主） | 无服务端架构仓，无新增证据 |

### 5.2 发现表

| # | 事实 | 原文要点 | 来源 | 等级 |
|---|---|---|---|---|
| H-1 | ④数据驻留 | 生产数据托管美国 | 官方 security 页 | **A** |
| H-2 | 合规口径冲突 | security 页仅称 “aligned with SOC 2 Trust Services Criteria”（对齐 ≠ 认证）；blog/第三方称 Enterprise 含 SOC 2 | security 页 vs blog/第三方 | 以 security 页为准：SOC 2 认证状态 **B/C 且冲突登记**，不得写「已获 SOC 2」 |
| H-3 | ①租户隔离/②会话边界 | Trust Center 全量条目无任何隔离技术内容；security 页亦无 | trust.hyperbrowser.ai / security 页 | **U（穷尽后仍无）** |
| H-4 | ①Sandbox 隔离 | docs 只给产品语义与 “isolated cloud environments” 定性语，无机制 | docs | 定性语 **C**；机制 **U** |
| H-5 | ③egress/元数据默认策略、④会话销毁方式 | 官方全渠道未述 | — | **U** |

### 5.3 结论等级

**Hyperbrowser：维持 U——五家中最弱。** 官网 security 页、Trust Center、docs、SDK、GitHub 组织六类渠道已穷尽，仍无任何租户隔离/会话边界技术表述；仅数据驻留（美国，A）与 Sandbox「VM 计费」定性（R1 的 A-）可记。另登记一处口径冲突：SOC 2 只有「aligned」自述，blog/第三方的「含 SOC 2」说法不得采信为认证事实。

---

## 6. 对 products.csv 的逐行回填建议（只建议，不代改）

> 字段口径沿现 CSV 列：isolation_tech / network_control / credential_security / limitations / notes / confidence。

### 6.1 Runloop（现行：isolation_tech=「未公开…」，confidence=B）

- **isolation_tech** 建议改写：`VM+容器双层 (官方docs明示 "virtual machine technology" 且官方SDK明示 "isolated at both the VM and container level", A); 每Devbox一台临时VM、用完删除 (A); microVM字样仅见官方PR稿 (B); VMM未点名, Kata+Cloud Hypervisor仅组织fork线索 (C, 不作结论)`
- **network_control** 建议补：`Network Policies: hostname allowlist(通配)/deny-all/blueprint级+运行时策略 (A, 官方blog+docs); 默认策略口径未明示 (U); 元数据专项策略未公开 (U); Agent Gateways/MCP Hub使真实凭证不进devbox (A)`
- **deployment** 可补：`Enterprise含 Deploy to VPC (pricing明示, A); 数据驻留区域未公开`
- **limitations** 建议改写：`隔离已由未公开升A- (VM+容器双层官方明示); 残缺口: VMM名未点名、egress默认口径与元数据策略未公开、驻留区域未公开`
- **confidence**：建议 B → **B+**（若主线口径不用 + 号，则维持 B 并在 notes 注明「隔离子项已 A」）；notes 追加 Round 5 线 A 出处（本文件 §1）。

### 6.2 Browserbase（现行：isolation_tech=「未公开…」，confidence=B）

- **isolation_tech** 建议改写：`每浏览器一台专用VM, 硬件虚拟化层隔离 (官方docs企业安全页明示 "1 browser per VM", A); 每浏览器独立subnet+严格防火墙 (A); VMM未点名 (U)`
- **lifecycle** 可补：`No browser reuse: session后VM被kill并从零重建 (A)`
- **network_control** 建议改写：`独立subnet+严格防火墙防横向移动 (A); 元数据/169.254专项默认策略未述 (U)`（替换现「默认内网/元数据策略未公开」的全称口径）
- **persistence/驻留** 可补：`数据驻留可选 US West/US East/EU(Germany)/Asia(Singapore) (A); 可关日志与replay实现zero data retention (A)`
- **limitations** 建议改写：`隔离已升A; 残缺口: VMM未点名、元数据默认策略无专项表述; session 6h上限维持B疑旧版 (Q21不变)`
- **confidence**：建议 B → **A-**（定价 A + 隔离 A，扣分项为 VMM/元数据两 U 与 6h 的 B）。

### 6.3 Browserless（现行：isolation_tech=「未公开…」，confidence=B）

- **isolation_tech** 建议改写：`SaaS: 容器化浏览器环境+网络分段 (官方Trust Center, A表述), 每连接独立browser instance (官方blog, A); 每session是否独立容器未点名 (U). 开源/自托管版: 单Docker容器内多浏览器进程、进程级会话分离 (源码一手, A) —— 两版分开, 不得等同`
- **network_control** 可补：`网络分段与隔离 (Trust Center, A定性); allowlist为官方建议非默认强制; 元数据默认策略未述 (U)`
- **persistence/驻留** 可补：`存储主要在美国 (AWS/DigitalOcean/Supabase); 区域端点仅决定执行地, 仅Amsterdam在EU内; 终止后按内部政策删除 (Trust Center, A)`
- **limitations** 建议改写：`SaaS隔离粒度(每session容器?)未明、元数据策略未公开; 双许可定性标注不变`
- **confidence**：建议维持 **B**，notes 注明「SaaS 隔离子项 B+、开源版 A、驻留 A（本文件 §3）」。

### 6.4 Steel.dev（现行：isolation_tech=「未公开…」，confidence=B）

- **isolation_tech** 建议改写：`SaaS: 官方仅 "Isolated sessions" 营销语, 机制未公开 (U维持); 2024年Fly.io客户故事称跑于Fly Machines API+WireGuard (B/C, 须注日期, 不作现行结论). 开源版: 单api容器内多浏览器进程、进程级会话分离 (仓库一手, A) —— 两版分开`
- **credential_security** 可补：`Credentials API: 凭证加密存储、注入不暴露给agent (docs, A产品表述)`
- **deployment** 可补：`Enterprise自托管Steel Outpost: data stays in your network/BYOK/自选region (官网, A口径)`
- **limitations** 建议改写：`SaaS隔离维持U; SOC 2官方未见明示 (仅HIPAA BAA); OSS beta成熟度注记不变`
- **confidence**：维持 **B**，notes 追加 Round 5 线 A 出处（本文件 §4）。

### 6.5 Hyperbrowser（现行：isolation_tech=「未公开…」，confidence=B）

- **isolation_tech**：**维持「未公开」**，建议追加穷尽注记：`官方security页/Trust Center/docs/SDK/GitHub组织六渠道已穷尽 (Round5), 仍无租户隔离与会话边界技术表述; Sandbox仅 "isolated cloud environments" 定性语`
- **persistence/驻留** 可补：`生产数据托管美国 (security页, A)`
- **limitations** 建议追加：`SOC 2口径冲突: security页仅称 aligned with SOC 2 TSC (未声称认证), blog/第三方 "Enterprise含SOC 2" 说法与之冲突, 以security页为准`
- **confidence**：维持 **B**（定价 A、隔离 U 不变），notes 追加 Round 5 穷尽记录（本文件 §5）。

---

## 7. 五家横向小结

| 家 | ①隔离机制 | ②session 边界 | ③egress/元数据默认 | ④驻留/销毁 | 本轮判定 |
|---|---|---|---|---|---|
| Browserbase | VM（每浏览器一台，硬件虚拟化层）A | 独立 subnet+防火墙 A | 元数据专项 U | 驻留 4 区域可选 A；VM 销毁重建不复用 A | **U → A** |
| Runloop | VM+容器双层 A；microVM B；VMM 名 U（Kata/CH 线索 C） | 每 Devbox 一台临时 VM A | allowlist/deny-all 能力 A；**默认口径 U**；元数据 U | 临时 VM 用完删除 A；驻留区域 U；Enterprise VPC A | **U → A-** |
| Browserless | SaaS 容器化+网络分段 A 表述（粒度 U）；开源版单容器多进程 A | 每连接独立 instance A | allowlist 仅建议；元数据 U | 驻留细则 A（存储主要在美、仅 Amsterdam 在 EU 内） | **SaaS B+ / 开源 A** |
| Steel.dev | SaaS U（仅营销语；2024 Fly 线索 B/C）；开源版单 api 容器多进程 A | SaaS U；开源版进程级 A | U | Outpost 自托管驻留 A；SaaS 销毁 U | **SaaS U 维持 / 开源 A** |
| Hyperbrowser | U（穷尽仍无） | U | U | 驻留美国 A；销毁 U | **U 维持** |

横向结论（供主线整合 Q9/Q6 时引用）：

1. **Q9 的「五家全部未公开」在本轮解体为 2 升 A 级（Browserbase、Runloop）、1 家 SaaS 官方表述到位但粒度未明（Browserless B+）、2 家维持 U（Steel SaaS、Hyperbrowser）**。Round 1 的负结论主要源于只查 pricing/docs 常规页——隔离表述实际藏在企业安全页（Browserbase）、Trust Center（Browserless）与官方 SDK README（Runloop）里，这是本轮的方法论教训：**查隔离先查 trust/security 企业页与 SDK**。
2. **Q6（Browser SaaS 元数据/内网默认策略）五家全军覆没**：无一家给出 169.254/元数据专项默认策略原文；最接近的只有 Browserbase 的 subnet+防火墙定性表述与 Runloop/Browserless 的 allowlist 能力/建议。Q6 的关闭路径仍只能是 D 线哨兵实验自测（SELF），官方文档路线本轮已穷尽。
3. **开源版与 SaaS 的系统性落差**：Browserless、Steel 两家的开源自托管版均为「单容器内多浏览器进程」的进程级分离（A 级事实），而其 SaaS 官方表述（容器化环境/每连接独立实例）明显强于或至少不同于开源形态——**任何用开源版形态推断 SaaS 隔离强度的写法都是错的**，本轮已逐家分开判定。
4. **VMM 点名率仍为 0**：五家无一在官方渠道点名 Firecracker/Cloud Hypervisor/Kata 等具体实现；Runloop 的 Kata+Cloud Hypervisor 仅为组织 fork 的 C 级线索。选型文档中五家的 VMM 字段应写「未点名」，不得以生态共识回填。
5. **合规口径陷阱**：Hyperbrowser 的「aligned with SOC 2 TSC」不得转写为「已获 SOC 2 认证」；Steel 官方仅 HIPAA BAA、无 SOC 2 明示。此类口径已在各家回填建议中单列。

---

## 附：本轮未尽事项（如实登记）

- Runloop Trust Center（trust.oneleet.com/runloop）未能打开核实；Runloop 数据驻留区域、egress 默认口径仍 U，待后续或销售确认。
- Browserbase Trust Center（trust.browserbase.com）仅确认官方链接存在，未打开核内容（其隔离关键事实已由 docs 企业安全页 A 级覆盖，门户内容为增量非必需）。
- Steel Fly.io 客户故事为 2024 年材料，现行架构是否仍在 Fly 上未证；若主线需要，可在后续轮次以 Steel 官方 changelog/状态页再核。
- 五家 egress/元数据默认策略（Q6）官方路线已穷尽，后续只能走产品实测（SELF），不在本线范围。
