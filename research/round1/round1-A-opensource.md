# Round 1 · 线 A：开源项目发现 — 第一轮扫描核实表

> 线别：A（开源项目发现）｜ 执行日期：2026-10-27（Asia/Shanghai）｜ `retrieved_at=2026-10-27`
> 覆盖搜索域：MicroVM Sandbox / Container Sandbox / WebAssembly Sandbox / Untrusted Code Execution / Secure Code Execution / Cloud Agent Runtime（开源部分）
> 核实方法（优先级）：① `gh api repos/<owner>/<repo>`（archived / license / pushed_at）+ `releases/latest` + `commits?per_page=1`；② GitHub 官方仓库 README 原文（经 `gh api .../readme` 解码及 github.com 仓库页）；③ web 搜索仅用于发现种子外候选，不作版本/日期依据。
> 证据等级：A=官方文档/源码/仓库一手直接支持；B=可靠独立来源、无完整一手验证；C=公开信息推断待验证；U=无法确认。时间均为 UTC（GitHub API 原始值）。「最近维护」= 默认分支最近一次 commit 的 committer date（与 `pushed_at` 基本一致时互相印证）。
> 注意：本表只核实「仓库存在性 / 归档状态 / 版本 / 维护 / license / README 自述隔离技术」，不等于源码级验证；隔离技术的实际实现深度留待阶段 3 深挖。

## 1. 种子开源项目核实表（16 个项目）

| 项目 | 仓库 | 状态 | 最新版本 + 日期 | 最近维护 (最近 commit) | License | 隔离技术 (证据等级) | 一手证据 URL |
|---|---|---|---|---|---|---|---|
| E2B 开源组件（SDK 主仓 + 运行时仓） | https://github.com/e2b-dev/E2B ；运行时仓 https://github.com/e2b-dev/infra（API 返回现名 `e2b-dev/runtime`，已重定向/更名） | 活跃（两仓均 archived=false） | 主仓 `e2b@2.61.0`，2026-10-26；运行时仓 `2026.30`，2026-09-10 | 主仓 2026-10-26；运行时仓 2026-10-27 | Apache-2.0（两仓 API 均确认，A） | 主仓 README 仅自述 "secure isolated sandboxes in the cloud"，未写具体隔离技术 (A：自述原文)；运行时仓 README 明示架构链 `SDK/CLI ─REST→ API ─gRPC→ orchestrator ─▶ Firecracker microVM ─▶ envd`，且自述 "E2B Embed is the whole stack, real Firecracker sandboxes included … needs Linux with KVM" → **Firecracker MicroVM (A)** | https://github.com/e2b-dev/E2B ; https://github.com/e2b-dev/runtime |
| Daytona OSS | https://github.com/daytonaio/daytona | **已归档 + 停止维护**（archived=true；README 置顶声明 "This repository is no longer maintained. As of June 2026, Daytona's core development has moved to a private codebase."，A） | `v0.190.0`，2026-06-23（归档前最后 release） | 2026-06-25（最后 commit "Fix license link in README"；`pushed_at` 2026-07-24 为归档期杂项推送，未改变代码状态判断） | AGPL-3.0（GitHub license API 对主分支返回 404；按 README 链接查 `v0.190.0` 标签下 LICENSE 原文为 GNU Affero GPL v3 全文，A）。种子表此前记「未验证」，本轮已核实 | README 自述 sandboxes 为 "full composable computers with complete isolation, a dedicated kernel, filesystem, network stack"，且 "Built on OCI/Docker compatibility" (A：自述原文)；**底层究竟是 VM 还是容器、hypervisor 为何，README 未披露 → 具体实现 U**，不得仅凭 "dedicated kernel" 推断为 MicroVM | https://github.com/daytonaio/daytona |
| OpenSandbox | https://github.com/opensandbox-group/OpenSandbox （旧址 https://github.com/alibaba/OpenSandbox 经 API 确认重定向至此，为同一仓库） | 活跃（archived=false；README 标注为 Agentic AI Foundation / AAIF 项目） | `release-1.1.1`（OpenSandbox 1.1.1），2026-10-09 | 2026-10-27（当日仍有 commit） | Apache-2.0（API 确认，A） | README 自述："Start locally with Docker and deploy on Kubernetes through a unified sandbox API"；另有 **Fast Sandbox runtime：Firecracker**（README 原文含 "Firecracker creation: 64 ms P50 (serial) / 125.4 ms P99 (10 concurrent)"，此为官方公布数据、未经本轮实测），并自述 per-sandbox egress 策略与 Credential Vault → **Docker/K8s 容器 + Firecracker MicroVM 双运行时 (A：README 自述；性能数字为官方公布、未实测)** | https://github.com/opensandbox-group/OpenSandbox |
| Firecracker | https://github.com/firecracker-microvm/firecracker | 活跃（archived=false） | `v1.17.0`（Firecracker v1.17.0），2026-09-10 | 2026-10-26 | Apache-2.0（API + 仓库页双确认，A）。种子表记「Apache-2.0/MIT」不准确，本轮以 API 为准：仅 Apache-2.0 | README 自述：VMM 使用 Linux KVM 创建 microVM，"combine the security and isolation properties provided by hardware virtualization … with the speed and flexibility of containers"，极小设备模型以缩小攻击面；自带 Jailer（cgroup/namespace 隔离后降权）与线程级 seccomp (A) | https://github.com/firecracker-microvm/firecracker |
| gVisor | https://github.com/google/gvisor | 活跃（archived=false） | `release-20261019.0`（gVisor 20261019.0），2026-10-22（日期型版本号，周发布节奏） | 2026-10-27 | Apache-2.0（API + 仓库页双确认，A） | README 自述：用户态应用内核（application kernel，Go 实现、运行于用户空间）实现 Linux 接口，含 OCI runtime `runsc`，与 Docker/Kubernetes 集成；明确声明「不是 seccomp 过滤器、不是 VM」(A) → **用户态内核 / 安全容器 (T2)** | https://github.com/google/gvisor |
| Kata Containers | https://github.com/kata-containers/kata-containers | 活跃（archived=false） | `4.3.1`（Kata Containers 4.3.1），2026-10-21 | 2026-10-27 | Apache-2.0（API 确认，A） | 仓库描述 + README 自述：轻量级 VM，"feel and perform like containers, but provide the workload isolation and security advantages of VMs" (A) → **VM 型安全容器 (T4)**；具体 VMM（Cloud Hypervisor / QEMU / Firecracker 等多后端）细节本轮未逐项核实，待深挖 | https://github.com/kata-containers/kata-containers |
| Cloud Hypervisor | https://github.com/cloud-hypervisor/cloud-hypervisor | 活跃（archived=false） | `v54.0`，2026-10-14 | 2026-10-27（commit 2026-10-27T00:40Z） | GitHub license API 返回 null（无单一 LICENSE 文件）；查仓库 `LICENSES/` 目录含 `Apache-2.0.txt` 与 `BSD-3-Clause.txt` → **Apache-2.0 / BSD-3-Clause 双许可 (A：LICENSES 目录原文)**，另有 CC-BY-4.0 应为文档许可，未细核 | README 自述：运行于 KVM 与 Microsoft Hypervisor (MSHV) 之上的 VMM，Rust 实现、基于 rust-vmm，目标含 "Minimal emulation / Small attack surface" (A) → **KVM/MSHV MicroVM 级 VMM (T3)** | https://github.com/cloud-hypervisor/cloud-hypervisor |
| Wasmtime | https://github.com/bytecodealliance/wasmtime | 活跃（archived=false） | `v50.0.0`，2026-10-20 | 2026-10-27 | Apache-2.0（API 确认，A；准确 SPDX 为 Apache-2.0 WITH LLVM-exception，API 简化显示为 Apache-2.0，此细节待复核） | 仓库描述自述 "A lightweight WebAssembly runtime that is fast, secure, and standards-compliant"，README 自述 "A standalone runtime for WebAssembly" (A) → **Wasm 运行时 (T5)**；WASI / Capability-based Security 的具体能力模型本轮未查官方 Book，待线 C 深挖 | https://github.com/bytecodealliance/wasmtime |
| WasmEdge | https://github.com/WasmEdge/WasmEdge | 活跃（archived=false） | `0.18.1`，2026-10-22 | 2026-10-27 | Apache-2.0（API 确认，A） | 仓库描述 + README 自述：轻量、高性能、可扩展 WebAssembly runtime，CNCF sandbox 项目 (A) → **Wasm 运行时 (T5)**；其网络/文件能力插件（如 socket 扩展）的安全边界本轮未核，待深挖 | https://github.com/WasmEdge/WasmEdge |
| nsjail | https://github.com/google/nsjail | 活跃（archived=false） | `3.6`，2026-03-18 | 2026-10-02 | Apache-2.0（API 确认，A） | 仓库描述一手原文："utilizes Linux namespaces, cgroups, rlimits and seccomp-bpf syscall filters, leveraging the Kafel BPF language"；README 细列 namespace 类型（UTS/MOUNT/PID/IPC/NET/USER/CGROUP/TIME）、chroot/pivot_root、只读挂载 (A) → **OS 级进程隔离 (T1)** | https://github.com/google/nsjail |
| isolate | https://github.com/ioi/isolate | 活跃（archived=false；维护节奏慢但 2026-10-26 仍有 commit） | **无 GitHub Release**（`releases/latest` 返回 404，A：已查）；最新 tag `v2.7`（tag 日期未验证：tags API 不含日期，本轮未追 tag commit 日期） | 2026-10-26 | GPL-2.0-or-later（license API 为 NOASSERTION/"Other"；读 LICENSE 原文首行 "under the terms of the GNU General Public License … either version 2 … or any later version"，A） | README 自述："sandbox built to safely run untrusted executables … takes advantage of features specific to the Linux kernel, like namespaces and control groups"，构建依赖含 libseccomp (A) → **namespace + cgroups (+seccomp 依赖) OS 级隔离 (T1)** | https://github.com/ioi/isolate |
| Judge0 | https://github.com/judge0/judge0 | 活跃（archived=false；代码仍在更新）但 **release 严重滞后**（见存疑项） | `v1.13.1`，**2024-04-18**（`releases/latest`，A）；此后至 2026-10-27 无新 GitHub Release | 2026-10-26 | GPL-3.0（API 确认，A） | README 自述 "sandboxed open-source online code execution system"、"Sandboxed compilation and execution of untrusted code"，并在致谢中明示依赖 **Isolate** 与 Docker (A：README 原文) → **执行层隔离 = isolate (T1)，部署层 Docker**；Judge0 自身不是隔离原语 | https://github.com/judge0/judge0 |
| Browserless | https://github.com/browserless/browserless | 活跃（archived=false） | `v2.57.3`，2026-10-22 | 2026-10-23（commit；`pushed_at` 2026-10-27） | **SSPL-1.0 OR Browserless Commercial License（双许可）**（license API 为 NOASSERTION；读 LICENSE 原文首行即明示 dual-licensed，SPDX 行 `SSPL-1.0 OR Browserless Commercial License`，A）。注意：SSPL 不属 OSI 认可的开源许可，「开源」定性存争议，分类时应标注 | README 自述 "Deploy headless browsers in Docker"，以 Docker 镜像分发 Chromium/Chrome/Firefox 等，Puppeteer/Playwright 连接 (A) → **浏览器自动化基础设施，隔离主要来自 Docker 容器 + Chromium 自身进程沙盒 (A 为部署形态自述；浏览器隔离强度本身未在 README 量化，U)** | https://github.com/browserless/browserless |
| Steel (Steel Browser) | https://github.com/steel-dev/steel-browser | 活跃（archived=false） | `v0.5.4-beta`，2026-08-25（注意：latest release 仍带 beta 后缀，A） | 2026-10-23（commit；`pushed_at` 2026-10-25） | Apache-2.0（API 确认，A） | 仓库描述自述 "browser sandbox"；README 自述：以 Puppeteer + CDP 完整控制 Chrome 实例，管理 sessions/pages/browser processes、会话状态（cookies/local storage），提供预制 Docker 镜像 (A) → **浏览器进程会话隔离 (T7) + Docker 部署**；未见 MicroVM/容器强隔离自述，逐租户隔离实现 U，待深挖 | https://github.com/steel-dev/steel-browser |
| Microsandbox | https://github.com/microsandbox/microsandbox （API 确认现重定向至 https://github.com/superradcompany/microsandbox ；`zerocore-ai/microsandbox` 亦重定向至同一仓，见存疑项） | 活跃（archived=false） | `v0.7.11`，2026-10-24 | 2026-10-27 | Apache-2.0（API 确认，A） | README 自述："runs untrusted workloads inside fast, local microVMs"、"Hardware-level isolation with tiny virtual machines"、OCI 兼容、fork & snapshot、平均启动 <100ms（官方公布、未实测）(A：README 自述) → **本地优先 MicroVM 运行时 (T3)**；底层 VMM 是自研还是基于 libkrun/Firecracker 等，本轮未查源码，U | https://github.com/superradcompany/microsandbox |
| OpenHands Runtime | https://github.com/All-Hands-AI/OpenHands （API 确认现重定向至 https://github.com/OpenHands/OpenHands） | 活跃（archived=false）。注意：当前 README 已改为 "Agent Canvas" 定位（自托管 coding agent 控制中心），与种子录入时的 OpenHands 经典形态不同，见存疑项 | `v1.33.0`，2026-10-23 | 2026-10-27 | MIT（API 确认，A）。注意：历史上 OpenHands 部分目录曾有附加条款，本轮仅核实仓库级 license API 结果，企业版/云端条款未核 | 当前 README 自述可连接多种 "agent backends, e.g. running agents in Docker containers, on VMs, or within your company infrastructure" (A：自述原文)；种子所记「Docker 容器」为其历史默认 Runtime 形态，**当前版本默认执行后端与隔离细节本轮未在源码中定位（`openhands/` 旧 runtime 路径已 404，疑似拆分至独立 SDK 仓）→ 具体隔离实现 C，待源码线深挖** | https://github.com/OpenHands/OpenHands |

### 计数（本线口径，仅说明本轮覆盖，不代表市场规模）

- 种子指定核实：**16/16 个项目已完成一手核实**（仓库存在性、archived、license、最新 release、最近 commit 均有 gh API 记录；隔离技术均回溯到 README/仓库描述原文，个别实现细节如实标 U/C）。
- 其中状态异常：**Daytona OSS 已归档停更（1 个）**；仓库更名/重定向：**E2B infra→runtime、OpenSandbox alibaba→opensandbox-group、Microsandbox microsandbox→superradcompany、OpenHands All-Hands-AI→OpenHands（4 处）**。
- 无 GitHub Release 的项目：**isolate（1 个，仅 tag）**。

## 2. 新发现候选清单（种子外，仅候选 + 一句话依据，未深挖）

> 核实程度：以下候选均已用 `gh api repos/<repo>` 确认仓库存在、未归档、license 与最近推送时间（2026-10-27 当日查），但未读 README 全文、未核版本，故整体定级 **B（存在性 A、价值判断待深挖）**。`microsoft/hyperlight` 与 `anthropic/sandbox-runtime`（单数 anthropic）经查为 404，正确仓见下表，已纠正。

| # | 候选 | 仓库 | 一句话依据 |
|---|---|---|---|
| 1 | Piston | https://github.com/engineer-man/piston | 高性能通用代码执行引擎（MIT，gh 已确认），执行层基于 isolate 思路，是 Secure Code Runner 类除 Judge0 外最有代表性的开源实现，值得与 Judge0 对照。 |
| 2 | Google sandboxed-api | https://github.com/google/sandboxed-api | Google 官方为 C/C++ 库自动生成沙盒的框架（Apache-2.0，gh 已确认），代表「库级/进程级沙盒化」路线，与 nsjail 同源但抽象层不同。 |
| 3 | Kubernetes agent-sandbox (SIG) | https://github.com/kubernetes-sigs/agent-sandbox | K8s SIG 官方 Sandbox CRD/控制器（Apache-2.0，仓库描述明示 isolated/stateful/singleton agent runtime），是 K8s Sandbox 编排类的标准制定者，支持 gVisor/Kata 后端（Google 官方博客，B）。 |
| 4 | Dagger | https://github.com/dagger/dagger | 以容器为执行单元的可编程自动化引擎（Apache-2.0，gh 已确认），常被用作 Agent 的可复现工具执行层，属执行基础设施相邻候选。 |
| 5 | Sysbox | https://github.com/nestybox/sysbox | Nestybox 的增强型 runc（Apache-2.0，gh 已确认），让 rootless 容器像 VM 一样跑 systemd/Docker/K8s，是容器与 VM 之间的代表性中间路线。 |
| 6 | Firejail | https://github.com/netblue30/firejail | 老牌 Linux namespace + seccomp-bpf SUID 沙盒（GPL-2.0，gh 已确认），桌面/本地进程沙盒的基线对照，与 nsjail/bubblewrap 同类比较价值高。 |
| 7 | Bubblewrap | https://github.com/containers/bubblewrap | Flatpak 底层使用的非特权沙盒工具（gh 已确认；license API 为 NOASSERTION 待细核），Anthropic sandbox-runtime 等 OS 级方案的实际依赖之一。 |
| 8 | Hyperlight | https://github.com/hyperlight-dev/hyperlight | 微软系轻量 VMM 库（Apache-2.0，gh 已确认），仓库描述明示在 microVM 内安全执行不可信代码、低延迟，是 MicroVM 函数级沙盒的新路线（另有 Hyperlight Wasm 方向，待核）。 |
| 9 | AIO Sandbox (agent-infra) | https://github.com/agent-infra/sandbox | 仓库描述明示将 Browser/Shell/File/MCP/VSCode Server 合一的单 Docker 容器 Agent 沙盒（Apache-2.0，gh 已确认），是「全合一 Agent 工作空间」路线的代表。 |
| 10 | Anthropic sandbox-runtime | https://github.com/anthropics/sandbox-runtime | Anthropic 官方 OS 级沙盒工具（Apache-2.0，gh 已确认），仓库描述明示在无容器条件下对任意进程施加文件系统与网络限制，是 LLM 厂商自研本地沙盒的一手样本。 |
| 11 | firecracker-containerd | https://github.com/firecracker-microvm/firecracker-containerd | 官方让 containerd 以 Firecracker microVM 管理容器的组件（Apache-2.0，gh 已确认），是理解 MicroVM 与容器编排衔接的关键胶水层。 |
| 12 | llm-sandbox | https://github.com/vndee/llm-sandbox | 轻量可移植的 LLM 代码解释器沙盒 Python 库（MIT，gh 已确认），代表「库级嵌入、容器后端可插拔」的轻量路线。 |
| 13 | E2B Desktop | https://github.com/e2b-dev/desktop | E2B 官方桌面沙盒仓（Apache-2.0，gh 已确认），仓库描述明示为 LLM 提供可连接的图形桌面环境，是 Computer Use 类开源样本，应从 E2B 主仓拆出单独跟踪。 |
| 14 | CubeSandbox (TencentCloud) | https://github.com/TencentCloud/CubeSandbox | 腾讯云开源的 Agent 沙盒（gh 已确认存在且 2026-10-27 当日仍有推送；license API 为 NOASSERTION 待细核），仓库描述自称 Instant/Concurrent/Secure & Lightweight，国内厂商路线代表，值得下一轮优先核实其隔离实现。 |

## 3. 存疑 / 冲突项

1. **Daytona：OSS 归档 vs SaaS 存续**。OSS 仓已 archived 且 README 明示核心开发转入私有代码库（2026-06 起）；这不等于 Daytona SaaS 停运。SaaS 现状、定价与当前隔离实现须由线 B 以官网当日资料核实，两者不得混写。
2. **Daytona license API 异常**：主分支 license API 404，但 `v0.190.0` 标签下 LICENSE 为 AGPL-3.0 全文。推测归档/改版过程中主分支 LICENSE 路径变化（C），引用时应注明版本标签。
3. **Microsandbox 组织三度变迁**：种子写作 `microsandbox/microsandbox`，搜索结果曾出现 `zerocore-ai/microsandbox`，gh API 现均重定向至 `superradcompany/microsandbox`。引用一律用现名并注明旧名，避免后续检索断链。
4. **OpenHands 形态与 Runtime 拆分**：org 由 All-Hands-AI 更名为 OpenHands；当前 README 定位为 Agent Canvas，旧 `openhands/` runtime 路径 404。「OpenHands Runtime = Docker 容器」是历史结论（种子口径），在当前版本是否仍成立须源码线追踪其新 SDK/runtime 仓后才能升级为 A。
5. **OpenSandbox 仓库 `created_at` 为 2025-12-17**：与「阿里开源」叙事的时间线表面冲突，实为仓库迁移/重建后 API 以新仓创建时间记（gh 返回 opensandbox-group 与 alibaba 两路径为同一仓）。其早期历史与 AAIF 捐赠过程待线 B/生态线用官方公告交叉验证（当前定性 B）。
6. **Judge0 版本停滞与活跃开发并存**：最新 GitHub Release 停在 v1.13.1（2024-04-18），但默认分支 2026-10-26 仍有 commit。是否存在 Release 渠道变更（如仅 Docker 镜像/EE 版本）本轮未核，引用版本时必须同时注明 release 日期与 commit 活跃度，不得单写「最新版 1.13.1」误导为停更、也不得反之。
7. **isolate 无 Release 只有 tag**：最新 tag `v2.7` 的发布日期未验证（本轮未追 tag 指向 commit 的日期）；且其被 Judge0、Piston 共同依赖，版本口径会影响下游项目描述。
8. **Browserless 的「开源」定性**：SSPL-1.0 非 OSI 开源许可且商用需商业许可。products.csv 现将其归 P3/P8 开源自托管类，后续分类修订时建议标注「source-available / 双许可」以免与 Apache/MIT 类混同。
9. **Steel latest release 为 beta**：`v0.5.4-beta`（2026-08-25）为 GitHub `releases/latest` 返回值（预发布是否计入 latest 的口径由 GitHub 决定），成熟度判断应结合其 SaaS 线（线 B）而非单看版本号。
10. **Cloud Hypervisor license API 为 null**：因其采用 `LICENSES/` 多文件目录而非单 LICENSE，自动化抓取易误判为「无许可」；实际为 Apache-2.0 + BSD-3-Clause（文档另含 CC-BY-4.0，各文件适用范围待深挖时细核）。
11. **Wasmtime SPDX 细节**：API 报 Apache-2.0，其完整 SPDX 通行写法为 Apache-2.0 WITH LLVM-exception，本轮未开 LICENSE 原文逐字核对，暂记差异待复核（不影响分类）。

## 4. 本线未覆盖项（下一轮候选任务）

- **同域未核实的知名项目**：crosvm（ChromeOS VMM）、QEMU/microvm machine type、Wasmer、Spin（Fermyon）、wasmCloud、KubeVirt、virtlet、Runsc 之外的 Kata 具体 VMM 后端矩阵、Firecracker 的 jailer/snapshot 源码级核实 — 本轮仅完成种子 16 项 + 候选发现，未展开。
- **Sandbox Fusion 类项目仓名未定位**：以 `modelscope/sandbox-fusion` 试查返回 404，正确组织/仓名未确认（U），下一轮需以官方公告/论文反查，禁止猜测 URL。
- **源码级核实全部未做**：各项目「创建→执行→销毁」调用链、seccomp profile、网络策略实现均属阶段 3，本轮 README 自述不等于实现证据，表中 A 级仅限「官方自述」层面。
- **性能数字未验证**：OpenSandbox 的 Firecracker 64ms P50、Microsandbox <100ms 启动、Daytona <90ms 等均为官方公布数据，本轮只记录出处，未实测、未找第三方复现（待线 D）。
- **商业 SaaS 与云厂商**（Modal、Fly.io、Runloop、Browserbase、Hyperbrowser、Cloudflare/Vercel Sandbox 等）按分工属线 B，本线未核。
- **候选清单 14 项未深挖**：仅确认存在性；下一轮建议优先序：kubernetes-sigs/agent-sandbox、CubeSandbox、anthropic/sandbox-runtime、agent-infra/sandbox、Hyperlight（与 Agent 场景相关性最高）。
- **论文/原型类**（如 OSWorld 等评测环境、学术 MicroVM/Wasm 原型）本轮未系统检索，属线 C/生态线范围。

---
*文件：hidden_files/research/round1-A-opensource.md ｜ 下一步：主 Agent 将本表 A 级字段回填 products.csv（本线未改动 products.csv 与 files/ 下任何文件）。*
