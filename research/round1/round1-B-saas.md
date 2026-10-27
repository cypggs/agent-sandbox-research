# 线 B · 第一轮商业 SaaS 扫描

> 项目：Agent Sandbox 全领域技术研究（goal_a756da9ace9a）
> 线别：B — 商业 SaaS
> 检索日：**2026-10-27（Asia/Shanghai）**，下文所有价格/限制均为当日官网/官方文档口径，`retrieved_at=2026-10-27`
> 证据分级：**A** = 官方文档/官网 pricing 页/官方 API 参考直接支持；**B** = 可靠独立来源交叉、无完整一手；**C** = 推断待验证；**U** = 未公开/无法确认。定价与隔离**不以二手博客作 A 级**。
> 纪律：无官方表述写「未公开」；不推测内部架构；形态判定给出依据原文。
> 范围：种子 12 家 + 云厂商 3 组 + 主动发现 9 家 = **24 个产品/服务已核实**（含判定为「非 Agent Sandbox」的 Hugging Face Spaces）。

---

## 0. 总览表（仅 A 级可比项，空缺 = 未公开/U）

| # | 产品 | 形态判定（主类） | 隔离（官方表述，A 级优先） | 计费单位（官方） | 免费额度（官方） | 最大单次运行 | 并发（官方） | 证据 |
|---|---|---|---|---|---|---|---|---|
| 1 | E2B | P1 专用 Agent Sandbox | Firecracker microVM，每 session 独立内核 | 按秒：$0.000014/vCPU·s 起 | Hobby $100 一次性 | 1h Hobby / 24h Pro（连续） | 20 / 100→1,100 Pro | A |
| 2 | Daytona | P1 专用（原 P5 转型） | 容器类 + Linux/Windows VM 类并存（官方快照表） | $0.0504/vCPU·h + $0.0162/GiB·h，按秒 | $200 compute | 无固定上限；默认 15min 空闲 auto-stop（B） | 按 Tier 资源配额，非固定并发数 | A（价格/类） |
| 3 | Modal Sandboxes | P6 通用云的 Sandbox 原语 | gVisor（默认）；VM Sandbox Beta（2026-06，B 转述待一手复核） | 非抢占 3×：$0.00003942/core·s + $0.00000672/GiB·s（LP 页） | Starter $30/月 credit | 默认 5min，可配至 24h | Starter 100 containers / Team 5,000 | A |
| 4a | Fly.io Machines | P6 通用云 | 官方 pricing 页仅称 "hardware-isolated"；Firecracker 为 B 级共识 | 按秒，preset 计价，如 shared-cpu-1x 256MB $0.0030/h | 新 org 无持续免费层（B） | 未公开（Machines 通用） | 未公开 | A 价格 / U 隔离细节 |
| 4b | Fly.io Sprites | P1 专用（持久型） | 官方页称 "hardware-isolated VM"；Firecracker 为 B | 实际用量：$0.0385/CPU·h + $0.021875/GB·h | $30 trial credit（每 user/org 一次） | 无 session 上限表述；idle 分 running/warm/cold | 按 Plan：如 Hero 100 并发 running | A 价格/状态 / B 隔离名 |
| 5 | Runloop Devboxes | P1 专用（Coding Agent / 评测） | **未公开**（官网/pricing 未述隔离实现） | $0.108/CPU·h + $0.0252/GB·h | Basic 免费 + $50 credit，100GB 存储 | 未公开 | Trial 3 running Devboxes | A 价格 / U 隔离 |
| 6 | Microsandbox | P1/P8 开源 + 私有 Beta 云 | microVM，独立内核，硬件隔离（官网原文） | 本地开源免费；云 **未公开定价**（/pricing 需 owner 确认） | 本地免费 | 未公开 | 未公开 | A 隔离 / U 云价格 |
| 7 | Browserbase | P3 Browser SaaS | **未公开**（不述底层隔离实现） | browser hour：超额 $0.12 / $0.10 /h | Free：1 browser hour，3 并发 | 15min Free / 6h 付费（B 交叉，官网 pricing 未直接列时长） | 3 / 25 / 100 / 250+ | A 价格并发 / U 隔离 |
| 8 | Browserless | P3 Browser SaaS + 自托管 | **未公开** | Unit = 30s/连接；套餐含 units | Free 1k units/月，2 并发 | 2 / 15 / 30 / 60 min 按套餐 | 2 / 10 / 40 / 100 | A |
| 9 | Steel.dev | P3 Browser SaaS + 开源自托管 | **未公开**（仅 Chromium 会话） | $0.10/h Launch，$0.08/h Scale，按分钟向上取整 | Launch $30 一次性 credit（90 天） | 15min / 1h / 24h 按套餐 | 10 / 100 / 1,000+ | A 价格 / U 隔离 |
| 10 | Hyperbrowser | P3 Browser SaaS（兼 Sandbox） | Browser：**未公开**；Sandbox 仅称 VM 计费 | Browser $0.10/h；Sandbox $0.045/vCPU·h + $0.015/GiB·h；1 credit=$0.001 | Free 5,000 credits，1 并发 | 未公开 | 1 / 25 / 100 / 1,000+ | A 价格 / U 隔离 |
| 11 | Cloudflare Sandbox | P6 平台组件（Workers 生态） | 官方架构页："VM-based isolation — Each sandbox runs in its own VM"（容器形态） | Containers 计价：$0.000020/vCPU·s（active）+ $0.0000025/GiB·s | Workers Paid $5/月含 375 vCPU-min + 25 GiB-h 等 | 由 Durable Object / sleep 策略决定，未给统一上限 | 未给统一并发数；instance type 至 4 vCPU/12GiB | A |
| 12 | Vercel Sandbox | P1/P6 专用（Vercel 生态） | Firecracker microVM，独立 guest 内核（官方 FAQ + 安全文） | Active CPU $0.128/h + Provisioned Memory $0.0212/GB·h（iad1） | Hobby：5 CPU-h/月 + 420 GB-h 等 | 45min Hobby / 24h Pro·Ent（单 session） | 10 / 10,000 / 10,000 | A |
| 13a | AWS Lambda（Event） | P6 Serverless，非专用 Sandbox | Firecracker 为 B 级共识；官方 pricing 页未述隔离实现 | $0.20/百万请求 + $0.0000166667/GB·s（x86 一档） | 100 万请求 + 400,000 GB·s/月 | 15min（函数上限，B/常识需以开发者指南复核） | 账号配额制，未在本轮 pricing 页核 | A 价格 / U 隔离原文 |
| 13b | AWS Lambda MicroVMs | P1 性质的云厂商 Sandbox 原语 | Firecracker microVM（sandbox.watch 归纳为 B；AWS 定价页以 MicroVM 命名，隔离细节待开发者指南 A 级复核） | Graviton $0.0000276944/vCPU·s + $0.0000036667/GB·s（定价页算例引价单，B→待官方价表直引） | 未公开免费层 | 最长 8h（28,800s） | 未公开 | B |
| 13c | AWS AgentCore Code Interpreter | P7 平台组件（Bedrock AgentCore） | Firecracker microVM per-session（B） | $0.0895/vCPU·h + $0.00945/GB·h（B） | 未公开 | 默认 15min，最大 8h（B） | 未公开 | B |
| 14 | Azure Functions | P6 Serverless，非专用 Sandbox | **未公开**（官方 pricing 不述隔离） | Flex：按 GB·s + 执行次数；免费授信 250k 次 + 100k GB·s/月/订阅 | 同左 | Flex 最长时长未在本轮官方 pricing 页核实 | 未公开 | A 价格结构 / U 隔离 |
| 15a | GCP Cloud Run | P6 通用容器平台，非专用 Sandbox | **未公开**（官方 pricing 不述；gVisor 为业界共识 B） | 请求计费型 $0.000024/vCPU·s + $0.0000025/GiB·s；常驻型 $0.000018 + $0.000002 | 180k/240k vCPU·s 等按模式 | 服务/Job 语义，无 Sandbox session 上限概念 | 未公开 | A 价格 / U 隔离 |
| 15b | GCP GKE Agent Sandbox / Agent Compute Engine | P8/P1 云厂商新原语 | GKE：gVisor 默认、Kata 可选（B）；ACE：Cloud Hypervisor microVM、单租户（B，预览未定价） | GKE 按 Autopilot $0.0445/vCPU·h 归纳（B）；ACE **未公开/未定价，预览** | 未公开 | GKE 无固定上限（B）；ACE 未公开 | 未公开 | B / U |
| 16 | Blaxel（现 Baseten 旗下） | P1 专用（perpetual） | 官方 pricing FAQ："own hardware-isolated microVM" | $0.0000115/GB RAM·s（active，按内存计，CPU 自动伸缩） | 无订阅费；$200 credit 为 B 级转述，官网 pricing 页未直列金额 | "seconds to multiple days"；TTL 按 Tier（B 补充） | Tier 0:10 → Tier 9:100,000+ | A 价格隔离 / B 免费额 |
| 17 | Beam (beta9) | P6/P1 通用 + Sandbox | gVisor + runc（Beam 官方博客自述，A-：厂商博客） | 官网 docs 指向 pricing 页；博客率：CPU $0.190/core·h 等（B，待 pricing 页直核） | $30/月 credit（B） | Sandbox lifetime 默认 600s（官方 docs） | 未公开 | B |
| 18 | Northflank | P6 通用平台 + Sandbox/Harness | Kata + Cloud Hypervisor 为主，Firecracker/gVisor 可选（官方对比页自述） | Cloud：$0.01667/vCPU·h + $0.00833/GB·h，按秒 | Free Sandbox tier：2 services 等，$20/月资源内 | 无平台固定 session 上限（官方博客自述） | 未给 Sandbox 专用并发数 | A 价格 / A- 隔离自述 |
| 19 | CodeSandbox SDK | P5 云开发环境 → P1 SDK | Firecracker microVM（B；官方博客未在本轮直引隔离句） | credit $0.01486/个；≈$0.0446/vCPU·h + $0.0149/GB·h（官方博客） | Build 免费层 400 credits/月一说为 B，官方 FAQ 口径待对齐 | hibernate/resume 语义（B） | Build 10 并发 VM（官方博客称已升至 10） | A- 价格 / B 隔离 |
| 20 | Hugging Face Spaces | **非 Agent Sandbox**（P5 邻域：ML Demo 托管） | **未公开，且非隔离卖点** | CPU Basic 免费；CPU Upgrade $0.03/h；T4 small $0.40/h 等（官方 docs 表） | CPU Basic 免费 | Free CPU 48h 无活动 sleep（B） | 不适用 | A 价格 / 判定 A |
| 21 | Freestyle | P1 专用 VM | Full KVM VM（B，厂商对比页自述） | $0.04032/vCPU·h + $0.0129/GB·h（第三方计算器引官网，B，待官网直核） | 未核实 | 未公开 | 未公开 | B/C |
| 22 | Morph Cloud | P1 专用 | Full VM（B） | MCU $0.05/单位·h（B） | 未核实 | 未公开 | 未公开 | B/C |
| 23 | Kernel (onkernel) | P3 Browser（新发现） | **未公开** | 未在本轮核到官网 pricing A 级 | $5/月 free usage 转述（B） | 未公开 | 未公开 | U/B |
| 24 | Upstash Box | P1 专用（新发现） | **未公开** | $0.10/$0.20/$0.40 per active core·h 按规格（厂商博客 B） | 10 boxes + 5 CPU-h/月（B） | 未公开 | 未公开 | B |

> 读表警告：各家「vCPU」定义不一致（Modal 1 physical core = 2 vCPU；Vercel/Cloudflare 为 active CPU；Blaxel 按 GB RAM 计且 CPU 自动分配；Fly Sprites 按实际用量）。**横向比价必须注明计费基础，不可直接排序当结论。**

---

## 1. E2B

- **形态判定 — P1 专用 Agent Sandbox SaaS（+ P8 开源组件）｜A**
  依据：官网自述 “The AI Agent Cloud / Open-source sandbox platform that gives AI agents isolated machines”（pricing 页页脚描述）；产品即按需 Sandbox API + Code Interpreter，无通用云/IDE 混杂定位。开源运行时 Apache-2.0（Enterprise 页原文）。
- **隔离 — A**
  原文要点：Enterprise 页 “Every agent session runs in its own Firecracker microVM”；“A microVM with its own kernel per session. A kernel exploit inside the sandbox still needs a Firecracker escape to reach the host.”；网络 “Egress allow and deny per sandbox”；凭证 “Values resolve at egress. No API response, log, or sandbox holds them.”
  链接：https://e2b.dev/enterprise ； https://e2b.dev/pricing
- **定价 — A**
  计费：按运行秒，vCPU 档位价（pricing 页表）：1 vCPU $0.000014/s、2（默认）$0.000028/s、4 $0.000056/s、6 $0.000084/s、8 $0.000112/s。内存包含关系以 docs billing 页为准（本轮抓取显示与 vCPU 组合计价，明细需在写入 products.csv 时以 docs 原表逐格复核）。
  套餐：Hobby $0 + $100 一次性 credit；Pro $150/月 + usage，Enterprise custom（最低 $3,000/月，pricing 页 estimator 注记）；BYOC 为 Enterprise。
  链接：https://e2b.dev/pricing ； https://docs.e2b.dev/billing
- **生命周期 / 持久化 / 并发 — A**
  连续运行上限（不暂停）：1h Hobby / 24h Pro / Custom Enterprise；暂停后保留 **Unlimited**，暂停不计费，pause/resume 重置连续运行时钟（docs billing 原文）。磁盘：10 GiB Hobby / 20+ GiB Pro。并发：20 Hobby / 100 Pro（含，+500 槽位/$500·月，上限 1,100）/ 1,100+ Enterprise，Enterprise 称 “Tens of thousands”。创建速率 1/s Hobby、5/s Pro。Secrets/project：10 / 100 / 100。

## 2. Daytona

- **形态判定 — P1 专用 Agent Sandbox（由 P5 云开发环境转型）｜A-**
  依据：现官网标题 “Secure Infrastructure for Running AI-Generated Code”，pricing/billing/limits 全围绕 Sandbox 资源与生命周期；历史 CDE 定位为 B 级背景，不改变当前主类。
  状态注记（重要）：多家独立来源称其原开源仓于 2026-06 转闭源/归档（Northflank 对比文、B 级）——**本轮未直接打开 GitHub 仓库页核实 archived 状态，标 C，须线 A 复核后再写状态字段**。
- **隔离 — A（分类存在性）/ U（实现细节）**
  官方快照表明确并存三类：Container（daytona-small/medium/large）、Linux VM（daytona-vm-*）、Windows、GPU 类。原文：https://www.daytona.io/docs/en/snapshots/
  但官方文档未在本轮找到「容器类底层 runtime 为何（Docker/Kata/Sysbox）」的一手句；二手普遍称 Docker 默认 + Kata 可选（B）。**products.csv 隔离字段只能写「Container + VM 并存（官方）」，runtime 细节标未验证。**
- **定价 — A**
  Linux compute $0.0504/vCPU·h、memory $0.0162/GiB·h、storage $0.000108/GiB·h（前 5 GiB 免费）；Windows $0.0858/vCPU·h；GPU preemptible：B300 $4.08/h、B200 $3.59/h、MI355X $3.44/h、H200 $2.61/h、H100 $2.27/h、RTX PRO 6000 $1.74/h、5090 $0.74/h、4090 $0.57/h。全部按秒计费。$200 free compute included。
  链接：https://www.daytona.io/pricing
  计费状态机（官方 billing）：Started 全计；Stopped/Paused 仅 disk（Paused 仅 VM 类，内存状态不计费）；Archived 不计费（仅 container 类）；Ephemeral/GPU stopped 即自动删除。https://www.daytona.io/docs/en/billing/
- **生命周期 / 持久化 / 并发 — A**
  无套餐式并发数，改为 Tier 资源池：Tier1 10 vCPU/10GiB/30GiB（邮箱验证）→ Tier4 500/1000GiB/5000GiB（$2,000/30 天 top-up）→ Custom。速率：Sandbox Creation 300–600/min 按 Tier。持久化：stateful 设计，snapshots + volumes（volumes 免费、每 org 上限 100、不计 storage quota）。默认 auto-stop 15min 为 B 级（多源一致，官方 sandbox 配置文档待线 B 第二轮直引）。

## 3. Modal — Sandboxes

- **形态判定 — P6 通用 Serverless 云平台，Sandbox 为其一原语（非专用）｜A**
  依据：pricing 页主体为 Functions/GPU/批量，Sandbox 单列一节且按非抢占 3× 计价；官网 sandbox 页亦置于通用平台内。
- **隔离 — A（默认类）**
  官方 LP 原文：“gVisor-based runtime — Rely on strict security and isolation guarantees from our battle-tested containerization technology.” https://modal.com/lp/sandboxes
  新变化：2026-06-15 产品更新称推出 VM Sandboxes (Alpha/Beta)「run a real Linux kernel」+ 出站域名 allowlist——本轮仅见独立来源转述（B），**未取得 Modal 官方更新页原文，写 C 待复核**，不得据此改默认隔离结论。VM runtime 下 rootfs 固定 512 GiB（官方 sandbox-resources 文档，A）。
- **定价 — A**
  Starter $0/月 + $30/月 credit、3 seats、100 containers + 10 GPU 并发；Team $250/月 + $100 credit、5,000 containers + 50 GPU；Enterprise custom。Sandbox 按 max(request, actual) 按秒计，non-preemptible = 3× list：LP 页明示 CPU $0.00003942/core·s（1 core = 2 vCPU，min 0.125 core）、Memory $0.00000672/GiB·s。注：pricing 主页该两数字在抓取中被前端隐藏，仅 LP 页可见，两页互证后标 A-。区域 multiplier：broad 1.15×、narrow 1.75×（官方 region 文档）。
  链接：https://modal.com/pricing ； https://modal.com/docs/guide/sandbox-resources
- **生命周期 / 持久化 / 并发 — A**
  默认 max lifetime 5min，`timeout=` 可至 24h；超 24h 官方建议用 Filesystem Snapshot 恢复至新 Sandbox。`idle_timeout=` 可设空闲自动终止。持久化靠 Volumes / 网络文件系统，非 Sandbox 本体常驻。并发见套餐 containers 上限；厂商称可达 25,000 并发事件案例与 “100,000 concurrent per customer” 为营销案例页表述（B，不作配额承诺）。

## 4. Fly.io — Machines 与 Sprites（必须分开）

### 4a. Machines
- **形态 — P6 通用云平台原语｜A**。依据：fly.io/pricing 通用 compute 表，无 Sandbox 专用 API 语义；需自建编排（B 级共识）。
- **隔离 — U（细节）**。官方 pricing 页仅一句 “Customer workloads on Fly.io are hardware-isolated”。Firecracker 实现为业界共识（B），本轮未取得 Fly 官方 Machines 架构页原文，**不得写 A**。
- **定价 — A**。按秒：shared-cpu-1x·256MB $0.0030/h（$2.19/月）、performance-1x·2GB $0.0458/h（$33/月）为表头示例，preset 至 performance-16x，额外 RAM $6.00/GB·月（上限 128GB，2026-10-01 更新口径）；Stopped rootfs $0.15/GB·月；Volumes $0.15/GB·月；Snapshots $0.08/GB·月（前 10GB 免费）；egress NA/EU $0.02/GB、APAC 等 $0.04、Africa/India $0.12。https://fly.io/pricing/
- **生命周期**：auto-stop/start 为 Machines 通用能力（本轮未直引官方 docs 页，标待复核）；无 Sandbox session 概念。

### 4b. Sprites（sprites.dev / fly.io/sprites）
- **形态 — P1 专用持久型 Agent 计算机｜A**。官方页标题 “Linux computers for agents”，原文 “Sandboxes aren't enough — Sprites are full Linux computers designed for agents”，用例明列 coding agents / MCP servers / untrusted code / dev environments。
- **隔离 — A-（定性）/ B（实现名）**。官方页原文：“Real hardware-isolated Linux computers”、“Run it in a hardware-isolated VM”。Firecracker 名未出现在本轮抓到的官方 sprites 页原文中（第三方一致称 Firecracker，B）。
- **定价 — A（注意与旧价冲突）**。现官方页：CPU $0.0385/CPU·h（按 cpu.stat 累计实际用量）、Memory $0.021875/GB·h（实际用量）、Storage HOT $0.000683/GB·h、COLD $0.000027/GB·h；$30 trial credit（每 user 一次、每 org 最多一次）。**旧资料常引 $0.07 + $0.04375 为早期/standard 口径，已被现页覆盖，引用时必须用现页并注明日期。** Plan 捆绑额度例：Hero $100/月含 1,200 CPU-h、4,800 RAM GB-h、150GB storage（官方 FAQ）。https://fly.io/sprites/
- **生命周期 / 持久化 / 并发 — A**。100GB volume，按实际使用计 storage，POSIX 文件系统，checkpoint/restore。三态 running（计费）/ warm（不计）/ cold（不计）；idle 判定四信号（in-flight 请求、stdout 输出、TCP 连接、active task 最长 1h 可续）。并发与创建速率按 Plan 分级：pay-as-you-go 创建 10/min，Hero 100 并发 running + 100 warm、cold 无限，至 Mythic 240/min。

## 5. Runloop

- **形态判定 — P1 专用（AI 软件工程 Agent 的 Devbox + 评测）｜A-**
  依据：pricing 页全围绕 Devboxes/Blueprints/Snapshots/Axon（agent coordination），Pro 描述 “For teams running agents in production”，Enterprise 含 RFT 与 VPC 部署。
- **隔离 — 未公开（U）**
  本轮检索官网与 pricing 页均无隔离实现表述；第三方称 “dedicated microVMs”（B）。**按纪律写未公开，不得采信二手。**
- **定价 — A**
  Basic $0 + usage（100GB free storage，$50 credit）；Pro $250/月 + usage（1TB free storage，含 Suspend/Resume、Repo Connections）；Enterprise custom（VPC）。Usage：Devbox CPU $0.108/CPU·h（$0.00003/s）、Memory $0.0252/GB·h、Devbox Storage $0.00034236/GB·h、Blueprint Build $0.252/h、Blueprint/Snapshot/Object Storage $0.000072/GB·h、Active Axon $0.006/axon·h。https://runloop.ai/pricing
- **生命周期 / 并发 — A（部分）**
  Trial 限制：3 running Devboxes、5 blueprints、10 snapshots、3 objects，升级解除。Suspend/Resume 为 Pro 起；suspended 是否计费官网 FAQ 有该问但抓取未展开答案，标未验证。最大单次运行时长未公开。

## 6. Microsandbox

- **形态判定 — P1/P8：开源自托管优先，托管云为 Private Beta｜A**
  依据：官网 “open-source microVM sandboxes for AI agents and untrusted code… run locally on your own hardware, or request access to our managed cloud”，“private beta. access is by request”，YC F26，Apache 2.0。
- **隔离 — A**
  官网原文：“runs each sandbox in its own microVM”“hardware-isolated microVMs with their own kernel”“ordinary Docker Engine containers share a kernel（对比）”。网络默认：可达公网，private/host-local/link-local/metadata 目的地被阻断，可收紧至 allowlist 或全禁，云上该阻断不可解除。凭证：destination-bound，沙箱内为 placeholder，真值仅在 host 侧注入至 allowlist 目的地的受拦截出站请求（官网 FAQ 原文，要点已全）。https://microsandbox.dev/
- **定价 — 本地 A / 云 U**
  本地 Apache 2.0 runtime 免费（官网原文）。云定价官网自述 “private beta pricing is published at /pricing; rates need owner confirmation before promotion”——即**官方自己声明未定版，本轮标未公开，不得引用任何第三方价**。
- **生命周期 / 并发 — 未公开（U）**。官网未述 session 上限、暂停语义、云并发。

## 7. Browserbase

- **形态判定 — P3 Browser Sandbox SaaS（+ Stagehand / Search / Fetch / Runtime 平台组件）｜A**
  依据：pricing 页主体为 browser hours + concurrency，FAQ 自述 “complete platform to build and deploy agents that browse…”；明确 cloud-first、无 on-prem（仅 private cloud/VPC for enterprise）。
- **隔离 — 未公开（U）**。官网/pricing/docs 本轮未见底层隔离实现（容器/VM/Chromium 进程模型）表述。不得以「云浏览器」推断隔离边界。
- **定价 — A**
  Free $0：3 并发、1 browser hour、15min/session（pricing 页 infrastructure 列）、3 agent runs、1k Search + 1k Fetch、7 天 retention。Developer $20/月：25 并发、100 browser hours（超 $0.12/h）、1GB proxies（超 $12/GB）。Startup $99/月：100 并发、500h（超 $0.10/h）、5GB proxies（超 $10/GB）。Scale custom：250+ 并发、500+h usage-based。注：套餐月费数字在 pricing 页抓取中以标题 “Free, $20, $99, or Custom” 形式出现（A-）。https://www.browserbase.com/pricing
- **生命周期 / 持久化 — A（部分）**
  Session 时长：Free 15min 明示；付费 6h 上限为多源 B 级（官网 compare 表未直列），标待复核。Contexts/profiles 保存 cookies 与登录态为产品能力（官方用例页），保留期按 data retention 7/30/30+ 天计（此为数据保留，非浏览器状态保证）。

## 8. Browserless

- **形态判定 — P3 Browser SaaS + 可自托管（P8 属性）｜A**
  依据：pricing 页为 Browser as a Service（Chrome/WebKit/Firefox、Puppeteer/Playwright、BrowserQL），Enterprise 提供 private deployment / licensed self-hosting，OSS 与 Private Docker 版可自托管（FAQ 原文）。
- **隔离 — 未公开（U）**。官方 pricing/docs 本轮未述会话间隔离实现。
- **定价 — A**
  Unit 定义（官方原文）：“A Unit is a block of browser time of up to 30 seconds per browser connection”，reconnect 计新 Unit；住宅代理 6 units/MB、机房代理 2 units/MB、Captcha 成功 10 units。
  Free $0：1k units/月、2 并发、2min max session。Prototyping $25/月（年付）：20k units、10 并发（年付 +5）、15min、超额 $0.0020/unit。Starter $140/月（年付）：180k units、40 并发、30min、$0.0017/unit。Scale $350/月（年付）：500k units、100 并发、60min、$0.0015/unit。年付省 30% 并加并发。https://www.browserless.io/pricing
- **生命周期**：persisted sessions/replays 存储 1/7/30/90 天按套餐；此为回放保留，非浏览器进程存活。

## 9. Steel.dev

- **形态判定 — P3 Browser SaaS + 开源浏览器 API（可自托管）｜A**
  依据：官方 docs pricing 页 + 开源定位（Apache 2.0 为 B 级转述，仓库 license 待线 A 核）。
- **隔离 — 未公开（U）**。官方 docs 仅述 Chromium 会话（含 Enterprise 的 Stealth Browser = 自研 Chromium fork），未述租户隔离实现。
- **定价 — A（2026-10-23 更新页）**
  Launch $0 + usage：$30 一次性 credit（90 天）、browser $0.10/h、proxy $10/GB、Captcha $3/1k、Browser Tools $5/1k、10 并发、max session 15min、60 req/min。Scale $250 + usage：$100/月 credit、$0.08/h、proxy $6/GB、Captcha $1/1k、100 并发、max 1h、Dedicated IP $5/IP·月。Enterprise custom：1,000+ 并发、max 24h。Browser hours 按分钟向上取整。https://docs.steel.dev/overview/pricinglimits
  注意：旧套餐（Hobby/Starter $29/Developer $99/Startups $499 + 按 hours 捆绑）已被官方 FAQ 称为 legacy，**引用旧价即错误**。
- **生命周期**：session 上限见上；profiles/cookies 复用为产品能力（docs），云端保留细节未在本轮展开。

## 10. Hyperbrowser

- **形态判定 — P3 Browser SaaS 为主，2026 年已扩展为「Browsers + Sandboxes + Web Data + Agents」四产品共用 credit｜A**
  依据：现 pricing 页原文 “Each plan includes credits for browsers, sandboxes, web data, and agents”。
- **隔离 — 未公开（U）**。Browser 与其 Sandbox 的底层隔离均无官方实现表述；Sandbox 计费行仅称 “while the VM runs”，可记「官方称 VM（定性）」为 A-，技术名未公开。
- **定价 — A**
  1 credit = $0.001。Free：5,000 credits、1 并发、7 天 retention。Startup $30/月：30,000 credits、25 并发。Scale $100/月：100,000 credits、100 并发。Enterprise：1,000+ 并发、180+ 天。
  用量：Browser $0.10/h（100 credits/h）+ proxy $10/GB；**Sandbox：vCPU $0.045/vCPU·h + Memory $0.015/GiB·h**（按 allocated、VM 运行时计）；Fetch $0.001/page 起；HyperAgent/Browser Use $0.02/step 另加 browser 与 proxy。购入 credits 12 个月过期，套餐 credits 不结转。https://www.hyperbrowser.ai/pricing
- **生命周期**：session/ sandbox 最大时长未公开；profiles 复用登录态（B 级产品页转述）。

## 11. Cloudflare Sandbox（Sandbox SDK + Containers）

- **形态判定 — P6 云厂商平台组件（Workers + Durable Objects + Containers），非独立专用 SaaS｜A**
  依据：官方架构页三层模型（Worker 调用 SDK → Durable Object 管身份/生命周期 → Container 执行），计费并入 Containers + Workers Paid。
- **隔离 — A**
  官方架构页原文：“VM-based isolation — Each sandbox runs in its own VM”；container 层描述为 “Isolated Ubuntu container executes untrusted code safely”。即官方口径 = VM 边界内的容器形态，**不要简化为「普通容器」或「V8 isolate」**（后者是 Workers 本体，与 Sandbox 不同）。https://developers.cloudflare.com/sandbox/sdk/concepts/architecture/
- **定价 — A（Containers 口径，2026-10-05 更新）**
  前提：Workers Paid $5/月。含：375 vCPU-min/月、25 GiB-h/月、200 GB-h/月。超额：CPU $0.000020/vCPU·s（**仅 active**，2025-11 起改版，官方 changelog 互证）、Memory $0.0000025/GiB·s（按 provisioned）、Disk $0.00000007/GB·s。Egress NA/EU $0.025/GB（含 1TB）等分区域。Instance types：lite 1/16 vCPU/256MiB/2GB → standard-4 4 vCPU/12GiB/20GB。https://developers.cloudflare.com/containers/platform/pricing/
- **生命周期 / 持久化 — A**
  按请求/手动启动计费，sleep 后停计（可 scale-to-zero）；`destroy()` 立即终止并永久删除全部文件/进程/会话（官方 lifecycle API）。持久化靠外挂：S3 兼容挂载（R2/S3/GCS）与 Backups（目录快照存 R2）。默认 idle sleep 约 10min 为 B 级转述，官方可配 `keepAlive`，统一上限未公开。

## 12. Vercel Sandbox

- **形态判定 — P1 专用 Sandbox（深度绑定 Vercel 平台，但 SDK 可独立使用）｜A**
  依据：官方 FAQ “on-demand, isolated Linux microVM that runs arbitrary code safely through an SDK or CLI”“purpose-built to execute untrusted or AI-generated code”。
- **隔离 — A（本轮证据最完整之一）**
  官方 FAQ 原文：“Each sandbox runs in its own Firecracker microVM with a dedicated kernel… Code in one sandbox can't see the processes, filesystem, or network of any other.”
  官方安全文补充：bare-metal EC2 上 Firecracker + guest 内核，microVM 内再跑 Linux container，**microVM 而非 container 才是安全边界**；网络策略在 host 侧 VM 外强制，firewall 拦截出站 TCP/DNS 并可注入凭证（凭证不进 VM）。https://vercel.com/sandbox ； https://vercel.com/docs/sandbox/pricing
- **定价 — A（iad1，docs 更新 2026-09-10）**
  Hobby 含：Active CPU 5h/月、Provisioned Memory 420 GB-h/月、Creations 5,000/月、Data Transfer 20GB/月、Snapshot 15GB(lifetime)。Pro/Ent：Active CPU $0.128/h（仅活跃，I/O 等待不计）、Memory $0.0212/GB·h、Creations $0.60/1M、Snapshot $0.08/GB·月；Drive（beta）$0.05/GB·月 + reads $0.0015/GB + writes $0.004/GB。Pro 费用先抵 $20/月平台 credit。
- **生命周期 / 持久化 / 并发 — A**
  单 session：默认 timeout 5min，可 extend，最大 45min Hobby / 24h Pro·Ent；stop/resume 重置该限，persistent sandbox 总寿命 effectively unbounded。持久化默认开：stop 时文件系统自动快照、resume 恢复，可 `persistent:false` 关。资源：vCPU 上限 4/8/32，RAM 固定 2GB/vCPU，盘 64GB ephemeral NVMe（SDK 3.0+），最多 15 ports、4 drives/run。并发 10 / 10,000 / 10,000；vCPU 分配速率动态配额（Pro 起始 150/min → 上限 5,000/min）。

## 13. AWS — Lambda / Lambda MicroVMs / AgentCore（云厂商组）

- **形态判定**：Lambda Event Functions = **P6 通用 Serverless，非 Agent Sandbox**（按请求/GB·s，无交互式会话/文件系统语义）；**Lambda MicroVMs = 云厂商推出的专用 Sandbox 原语**（per-user/per-job 有状态隔离环境）；**AgentCore Code Interpreter = P7 平台内代码解释组件**。三者不可混为一个「AWS Sandbox」。
- **隔离**：Lambda 经典款 Firecracker 为业界共识但本轮官方 pricing 页未述，标 B/U；MicroVMs/AgentCore 的 Firecracker 表述本轮来自 sandbox.watch 等独立归纳（B），**须第二轮以 AWS Developer Guide / AgentCore 官方 docs 直引升级为 A**。
- **定价 — Event A / MicroVMs B+**
  Event（官方 pricing 页，A）：$0.20/百万请求 + duration $0.0000166667/GB·s（x86 tier1），免费层 1M 请求 + 400,000 GB·s/月；另有 tenant isolation 附加计费（每新建隔离环境计费，官方算例）。
  MicroVMs（官方 pricing 页已设专节，结构 A、单价 B）：按 instance-second，内存:vCPU = 2:1（如 8GB→4 vCPU）；单价本轮引价单转述：Graviton $0.0000276944/vCPU·s + $0.0000036667/GB·s，snapshot read $0.00155/GB、write $0.0038/GB、storage $0.08/GB·月；suspended 仅付快照存储类费用。https://aws.amazon.com/lambda/pricing/
  AgentCore Code Interpreter（B）：$0.0895/vCPU·h + $0.00945/GB·h（active 口径）。
- **生命周期**：MicroVMs 最长 8h，支持 suspend/resume 保全状态（进程+文件，官方算例原文）；AgentCore session 默认 timeout 15min、最大 8h（B）。Lambda Event 单次最长 15min 为常识口径，本轮未直引开发者指南，标待复核。

## 14. Azure — Functions（及邻域提示）

- **形态判定 — P6 通用 Serverless，非专用 Agent Sandbox｜A（定价页定位）**
  与 Agent code execution 的关系仅在于「可承载工具调用后端」，无 Sandbox 会话/快照/交互执行语义。Azure 真正对位产品应是 Container Apps / Foundry Hosted Agents / Agent Sandbox 类新服务——**本轮未核实，列入未覆盖（见文末），不得用 Functions 充数**。
- **隔离 — 未公开（U）**。官方 pricing 页不述隔离实现。
- **定价 — A（结构）/ 单价以区域计算器为准**
  Consumption：按执行次数 + GB·s，免费授信 1M 次 + 400,000 GB·s/月/订阅（中国区官方页明示单价示例，全球页数字因 JS 渲染未直读到，标 A-）。Flex Consumption（现推荐，Linux Consumption 将于 2028-09-30 退役为 B 级转述）：可选内存规格、On Demand / Always Ready 两模式，免费授信 250,000 次 + 100,000 GB·s/月/订阅（官方 pricing 页原文）。https://azure.microsoft.com/en-us/pricing/details/functions/
- **生命周期**：Flex 的 timeout/常驻语义未在本轮 pricing 页核实，标未验证。

## 15. Google Cloud — Cloud Run / GKE Agent Sandbox / Agent Compute Engine

- **形态判定**：Cloud Run = **P6 通用容器平台，非专用 Sandbox**；GKE Agent Sandbox = K8s 上的 Agent 专用原语（P8/P1）；Agent Compute Engine = 2026-10-22 宣布的托管 microVM 预览（**未 GA、未定价，不得当可用产品比价**）。
- **隔离**：Cloud Run 官方 pricing 不述（U；gVisor 为 B 级共识）。GKE Agent Sandbox：runtime 可配内核级隔离、通常 gVisor、亦支持 Kata（B，sandbox.watch 归纳）。ACE：单租户 microVM、Cloud Hypervisor、独立 guest 内核、无长期凭证入沙箱、virtio-vsock + 代理注入凭证（Google 技术博客要点，独立转述 B，官方原文待第二轮直引）。
- **定价 — Cloud Run A / 其余 B·U**
  Cloud Run（官方 pricing，A）：CPU always allocated $0.000018/vCPU·s + $0.000002/GiB·s（免费 240,000 vCPU·s + 450,000 GiB·s）；request-based $0.000024 + $0.0000025 + $0.40/百万请求（免费 180,000 vCPU·s + 360,000 GiB·s + 2M 请求）。Cloud Run instances 新形态：1 vCPU/1GiB 常驻 30 天 $5.70（官方博客，A-），最长 7 天连续运行、stop/resume、固定 HTTPS URL。https://cloud.google.com/run/pricing（经官方页搜索摘要核）
  GKE Agent Sandbox 按 Autopilot 资源价归纳 $0.0445/vCPU·h（B）。ACE 未定价（官方称 preview in coming months，B）。

---

## 16. 新发现供应商（种子外）

### 16.1 Blaxel — 现 Baseten 旗下（状态变化，重要）
- 形态：P1 专用 perpetual Sandbox（+ Batch Jobs / MCP Hosting / Agent Runtime 平台）。2026-09 被 Baseten 收购、平台继续运行（B：收购分析文 + Blaxel 博客互证；官方收购公告原文待补，状态字段写「已收购，运营中（B）」）。
- 隔离 A：pricing 页 FAQ “Every agent runs in its own hardware-isolated microVM”；同页称 “One microVM per agent, app, or job”。
- 定价 A：active $0.0000115/GB RAM·s（CPU 随内存自动伸缩，无 vCPU 单价）、snapshot storage $0.20/GB·月、images $0.045/GB·月、volumes $0.12/GB·月；Batch $0.000006/GB·s、MCP $0.000007/GB·s；无基础订阅费；HIPAA add-on $250/月、支持 add-on $800/$1,600 + 用量%。并发 Tier：0:10（免费）→1:50（$20/月 top-up）→2:200（$50）→9:100,000+。https://blaxel.ai/pricing
- 生命周期 A：约 5s 无活动 scale-to-zero（FAQ 另处称 15s 网络无活动，**官方页内两数字并存，引用须注明出处段落**）、standby resume 约 25ms、standby 仅付快照存储、内存快照保进程、Volumes/Agent Drive 保长期数据；运行时长 “a few seconds to multiple days”。

### 16.2 Beam（beta9）
- 形态：P6 通用 Serverless GPU/CPU 平台 + Sandbox 原语；核心 beta9 开源（AGPL-3.0，厂商博客自述）+ BYOC/自托管。
- 隔离：厂商官方博客自述 runc + gVisor（A-：厂商博客，非 docs）。其自述劣势即「gVisor, not Firecracker」。
- 定价：官方 docs 定价页仅述计费规则（运行时计费、不为拉镜像/排队计费、storage 1TB 内免费、超 $0.021/GB·月、Sandbox 用 lifetime 而非 idle timer、Python 默认 lifetime 600s）并指向 pricing 页；具体单价本轮仅得其博客对比数（CPU $0.190/core·h、RAM $0.020/GB·h、H100 $3.50/h，B），**pricing 页直核列为缺口**。https://docs.beam.cloud/v2/resources/pricing-and-billing

### 16.3 Northflank
- 形态：P6 通用应用平台（服务/数据库/任务同平面）+ Sandbox / Cloud Harness 产品线；自助 BYOC 至 AWS/GCP/Azure/Oracle/CoreWeave 等。
- 隔离 A-（厂商对比页自述）： “MicroVM isolation using Kata Containers with Cloud Hypervisor as the primary approach; Firecracker and gVisor where supported”，每 sandbox 独立 microVM。属厂商自述，未经第三方验证，写 A- 并注明自述。
- 定价 A：Northflank Cloud $0.01667/vCPU·h + $0.00833/GB·h 按秒；BYOC 平台费 $0.02083/node vCPU·h（pricing 页）——注：其部分博客写 BYOC $0.01389 口径不一，**以 pricing 页为准并记录冲突**。Free Sandbox tier：2 services/2 jobs/1 database、$20/月资源内、always-on 不睡。持久盘 $0.11657/GiB·月、egress $0.06/GB。https://northflank.com/pricing
- 生命周期：官方博客称 sessions 无平台固定上限、ephemeral 或 persistent 可选、暂停停 compute（B/A- 混合，docs 直引待补）。

### 16.4 CodeSandbox SDK（Together AI）
- 形态：P5 云开发环境出身，现以 SDK 提供 VM Sandbox（fork/hibernate/resume 语义），并以 Together Code Sandbox 形式并入 Together 平台。
- 隔离 B：多源称 Firecracker microVM、约 2s boot；本轮未取得 codesandbox.io 官方隔离原文，标 B。
- 定价 A-（官方博客）：Together 收购后 credit 单价 $0.018 → **$0.01486**，对应 $0.0446/h/vCPU + $0.0149/h/GB RAM；并发上限 Build 5→10、Scale 100→250（官方博客原文）。套餐层（Build 免费含 credits、Scale $170/月起）为第三方汇总（B），须以现 pricing 页复核——其定价体系 2025–2026 多次变动，**本项时效风险最高**。https://codesandbox.io/blog/codesandbox-sdk

### 16.5 Hugging Face Spaces — 判定：非 Agent Sandbox（反例，保留记录）
- 形态：ML Demo/应用托管（Gradio/Docker/Static），无不可信代码隔离卖点、无 Sandbox API/会话生命周期语义。与 Agent Sandbox 的关系仅为「可托管 agent demo 前端」。**建议 products.csv 中单列为邻域/排除项，不与 Sandbox 比价。**
- 定价 A（官方 docs 表）：CPU Basic 2 vCPU/16GB 免费、CPU Upgrade 8 vCPU/32GB $0.03/h；GPU T4 small $0.40/h 起至多卡 A100 $20/h 档（docs 表摘录，完整表以 https://huggingface.co/docs/hub/spaces-gpus 为准）。隔离未公开且非其承诺项（U）。

### 16.6 Freestyle
- 形态：P1 专用（Full Linux VM for agents，TS SDK、live fork、hibernate）。隔离 Full KVM VM（B）。定价第三方计算器引官网 $0.04032/vCPU·h + $0.0129/GB·h（B），官网 pricing 页直核未完成 → **C/B，列缺口**。

### 16.7 Morph Cloud
- 形态：P1 专用（snapshot/branch 的 VM）。定价 MCU 模型 $0.05/MCU·h（B）。隔离/生命周期官网直核未完成 → 列候选待核。

### 16.8 Kernel（Cloud Browsers for Agents）
- 形态：P3 新兴云浏览器（YC 系，logged-in sessions 复用卖点）。本轮仅得 B 级转述（$5/月 free usage），官网 pricing/隔离均未核 → **U，列候选**。

### 16.9 Upstash Box
- 形态：P1 专用（Upstash 的 agent 计算机）。定价 B（厂商对比文）：Small/Medium/Large $0.10/$0.20/$0.40 per active core·h，内存免费，keep-alive 月费 $8/$16/$32，paused 仅 $0.10/GB·月 storage。官网直核未完成 → 列候选待核。

### 16.10 其他仅登记候选（未核实，不进已核实计数）
Prized（Firecracker + Boxes，官方 docs 对比页自述 $0.04/vCPU·h）、Tensorlake、Superserve、Namespace、Hopx、exe.dev、OpenComputer、Islo、Boat/Boxd、Agent37、Deno Sandbox、Together Code Sandbox（与 16.4 同源）、LangSmith Sandboxes、Prime Intellect Sandboxes、DigitalOcean Managed Agents、Azure Container Apps / Foundry Hosted Agents、Sandboxs.ai、Mainbrella。

---

## 17. 价格 / 隔离信息缺口（本线已知缺口）

1. **Microsandbox 托管云定价未公开** — 官网自述 private beta 定价需 owner 确认后才发布；本地开源免费已确认。云并发、session 上限同样未公开。
2. **Runloop 隔离未公开** — 官网/pricing 全文未述隔离实现；microVM 说法仅二手（B），products.csv 须写未公开。
3. **四家浏览器 SaaS 隔离未公开** — Browserbase / Browserless / Steel.dev / Hyperbrowser 官方 pricing/docs 均未述底层租户隔离（容器/VM/Chromium 进程模型）；只能确认会话/浏览器实例分离的产品语义，不能写隔离等级。
4. **Modal 官方 pricing 主页数字渲染问题** — sandbox CPU/memory 的 $/s 在主页抓取中为空，靠官方 LP 页补齐（已互证，仍标 A-）；Modal VM Sandboxes（2026-06）官方原文未取得，默认隔离仍以 gVisor 为准。
5. **云厂商隔离 A 级原文普遍缺失** — AWS Lambda / Azure Functions / GCP Cloud Run 官方 pricing 页均不述隔离；Lambda MicroVMs、AgentCore、GKE Agent Sandbox、Agent Compute Engine 的隔离与价格细节本轮多为 B 级归纳，须第二轮以开发者指南/官方博客原文升级。
6. **Azure Functions 全球页单价未直读** — 受前端渲染，$ /GB·s 具体数仅中国区页示例与 Flex 结构可确认；须以 Azure 官方零售价 API 复核。
7. **AWS Lambda MicroVMs 单价未直引官方价表** — 定价页专节结构已确认，单位价引自 AWS Price List 转述（B）；须第二轮打开价表/Calculator 直引。
8. **GCP 定价经官方页搜索摘要核** — Cloud Run 数字与官方一致性高但未完整打开 pricing 全文页逐行核；ACE 未定价、预览状态，GKE Agent Sandbox 价格为 Autopilot 资源价推算，非产品专属价表。
9. **旧价污染严重** — Fly Sprites（$0.07 旧价）、Steel 旧套餐（$29/$99 按 hours）、CodeSandbox 旧 credit 价、Northflank BYOC 两口径并存；引用二手对比文时必须回官网现页。
10. **Daytona 状态与 runtime 细节待核** — 原开源仓 archived/闭源（2026-06）说法仅 B/C；容器类底层 runtime 官方未明示。
11. **Blaxel 收购后主体与条款** — Baseten 收购（2026-09）官方公告原文未取得；定价页内 scale-to-zero 5s 与 15s 两数字并存。
12. **Beam / Freestyle / Morph / Upstash Box / Kernel 官网 pricing 未直核** — 现有数字为厂商博客或第三方计算器（B/C），不得进 A 级比价表。
13. **免费额度口径不一** — 一次性 credit（E2B $100、Steel $30、Fly $30 trial）、月度 credit（Modal $30、Vercel $20 平台 credit）、资源授信（Azure/GCP）不可直接横比，表格已分列注明。
14. **并发定义不一** — E2B/Vercel 为 sandbox 数，Modal 为 containers 数，Daytona 为资源池而非并发数，浏览器系为 browser sessions 数；跨类比价须换算假设并声明。

## 18. 本线未覆盖项（交第二轮 / 其他线）

- **云厂商对位产品未核**：Azure Container Apps、Azure Foundry Hosted Agents / Agent Sandbox、DigitalOcean Managed Agents、AWS Bedrock AgentCore 其他组件（Browser/Runtime）、GCP Agent Compute Engine 官方原文与定价（待 GA）。
- **新发现候选未深核**：Kernel、Freestyle、Morph、Upstash Box、Prized、Tensorlake、Deno Sandbox、LangSmith Sandboxes、Prime Intellect Sandboxes、exe.dev、OpenComputer、Namespace、Superserve、Hopx、Islo、Sandboxs.ai、Mainbrella、Together Code Sandbox 独立定价页。
- **浏览器邻域未核**：Anchor Browser、Browser Use Cloud、Steel 自托管部署细节、Browserbase Stagehand/Runtime 独立计费、Hyperbrowser Sandbox 独立文档。
- **深挖维度未做（本轮仅四项核实）**：网络出口策略细节（allowlist 粒度、凭证注入实现）、快照/fork 语义与一致性、冷启动实测、GPU 可用性矩阵、SOC2/HIPAA 证书原文、区域与数据驻留、自托管/BYOC 操作成本——归线 B 第二轮 + 实验室线实测。
- **与开源线交叉待对齐**：Daytona 仓库状态、Microsandbox 自托管成本、CodeSandbox 开源部分、Steel 开源仓库 license/隔离实现——交线 A 以仓库一手核实。
- **products.csv 未更新**：按任务纪律，本文件仅为研究底稿；字段回填（含 confidence、retrieved_at=2026-10-27、source_url）待主线汇总时统一写入。

---

*线 B 第一轮完。核实口径：24 个产品/服务（种子 12 + 云厂商 3 组拆 7 项 + 新发现 9 家，其中 Hugging Face Spaces 判定为非 Agent Sandbox 反例）。所有未取得一手表述处均已标未公开/U，未以二手博客充当 A 级。*

