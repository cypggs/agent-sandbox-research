# Round 2 · 线 A：清证据债（Q11 / Q22 / Q21 / Q18 / Q10）

> 执行：2026-10-27（Asia/Shanghai），retrieved_at 统一 2026-10-27
> 纪律：每项必须回原文页面/仓库原文；抓不到如实写未找到与尝试路径，不用二手转述结案。
> 底稿间关系：本文件是对 round1-B-saas.md、round1-D-threat-bench.md 相关 B 级结论的原文复核，部分结论**推翻或修正** Round 1 写法（见各节"对 Round 1 的修正"）。

## 0. 总表

| 债项 | 子项 | 原等级 | 结论一句话 | 新等级 | 原文 URL |
|---|---|---|---|---|---|
| Q11 | OWASP 2025 版 5 条编号（LLM01/02/03/06/10） | B | 2025 版五条编号与条目名与 D 线引用完全一致 | **可升 A**（须带"2025 版"标注） | https://genai.owasp.org/llm-top-10/ |
| Q11 | OWASP 是否已发新版 | 待核 | **已发 2026 版（2026-08-03 发布、09-02 官宣），且大改编号**：Excessive Agency 06→03、Supply Chain 03→04、Unbounded Consumption 10→06 | **可升 A**（新版存在与关键改号）；2026 全表逐条为 A-/B+（官方 PDF 经多源一致转录，未逐字打开 PDF 全文） | https://genai.owasp.org/2026/09/01/owasp-genai-security-project-unveils-2026-top-10-for-llm-applications-new-agent-control-standard-and-sponsors-as-community-tops-30000-members/ ；https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ |
| Q11 | CVE-2019-5736 | B | runc ≤1.0-rc6（Docker <18.09.2），覆盖宿主 runc 二进制得宿主 root，CVSS 3.1 **8.6 HIGH** | **可升 A** | https://nvd.nist.gov/vuln/detail/CVE-2019-5736 |
| Q11 | CVE-2024-21626 | B | runc ≤1.1.11（1.1.12 修复），FD 泄漏致工作目录落入宿主文件系统命名空间、可完全逃逸，CVSS 3.1 **8.6 HIGH** | **可升 A** | https://nvd.nist.gov/vuln/detail/CVE-2024-21626 |
| Q11 | CVE-2022-0492 | B | Linux 内核 cgroups v1 `release_agent` 提权并绕过 namespace 隔离，CVSS 3.1 **7.8 HIGH**，且已入 CISA KEV | **可升 A** | https://nvd.nist.gov/vuln/detail/CVE-2022-0492 |
| Q11 | CVE-2016-5195 | B | Dirty COW：内核 2.x–4.x、4.8.3 之前，COW 竞态写只读映射提权，CVSS 3.1 **7.0 HIGH** | **可升 A** | https://nvd.nist.gov/vuln/detail/CVE-2016-5195 |
| Q11 | CVE-2022-0847 | B | Dirty Pipe：内核 5.8 / 5.15 / 5.16 三分支未初始化 pipe buffer flags，可写只读文件页缓存提权，CVSS 3.1 **7.8 HIGH** | **可升 A** | https://nvd.nist.gov/vuln/detail/CVE-2022-0847 |
| Q22 | Wasmtime SPDX | 待逐字核 | 仓库 LICENSE 原文 = Apache-2.0 正文 + 文末 LLVM Exceptions 专节；根 Cargo.toml 声明 `license = "Apache-2.0 WITH LLVM-exception"`，完整 SPDX 成立 | **可升 A（结案）** | https://github.com/bytecodealliance/wasmtime/blob/main/LICENSE ；https://github.com/bytecodealliance/wasmtime/blob/main/Cargo.toml |
| Q22 | Cloud Hypervisor LICENSES/ 适用范围 | 待细核 | LICENSES/ 含 Apache-2.0 / BSD-3-Clause / CC-BY-4.0 三文本；`.reuse/dep5` 明示：文档（docs/*.md、*.md）→ CC-BY-4.0，一批脚本/配置/清单文件 → Apache-2.0；**BSD-3-Clause 的文件适用范围在 dep5 中未见对应条目，未完全核清** | **部分升 A**（CC-BY 与 Apache 范围可升 A；BSD-3-Clause 范围 **维持待核**） | https://github.com/cloud-hypervisor/cloud-hypervisor/tree/main/LICENSES ；https://github.com/cloud-hypervisor/cloud-hypervisor/blob/main/.reuse/dep5 |
| Q21 | Browserbase 付费 session 6h 上限 | B | 现行官方 pricing 页与 docs 均未见 6h 表述（pricing 仅 Free 标 15 min/session，compare 表无 session 时长行；docs 只讲 timeout/keepAlive 机制），6h 仅见于第三方评测 | **维持 B**（官方原文未找到） | 尝试路径见 §3.1（https://www.browserbase.com/pricing ；https://browserbase.mintlify.app/platform/browser/long-sessions/overview ） |
| Q21 | Daytona 默认 auto-stop 15min | B | 官方 docs 原文："By default, Daytona sandboxes auto-stop after 15 minutes of inactivity." | **可升 A** | https://www.daytona.io/docs/en/sandboxes/ |
| Q18 | Modal VM Sandboxes | C（VM Beta 仅转述） | 官方 2026-06-15 产品更新以 **Alpha** 推出 VM Sandboxes（真实 Linux 内核）；现行官方 docs 为双运行时（gVisor / VM），VM 隔离原文为"KVM 硬件虚拟化"，未设 `runtime` 时"由 Modal 选择"，官方已不再把 gVisor 写成唯一默认 | **可升 A**（存在与隔离表述）；"默认仍为 gVisor"的旧写法 **应删除/改写** | https://modal.com/blog/product-updates-vm-sandboxes-domain ；https://modal.com/docs/guide/sandboxes ；https://modal.com/docs/guide/sandbox-networking |
| Q10 | AWS Lambda MicroVMs 隔离+定价 | B | 开发者指南原文"through Firecracker virtualization"；官方价表算例直引 Graviton 单价 $0.0000276944/vCPU·s + $0.0000036667/GB·s、快照读 $0.00155/GB、写 $0.0038/GB、存储 $0.08/GB·月 | **可升 A** | https://docs.aws.amazon.com/lambda/latest/dg/lambda-microvms-guide.html ；https://aws.amazon.com/lambda/pricing/ ；https://aws.amazon.com/lambda/faqs/ |
| Q10 | AWS Bedrock AgentCore Code Interpreter 隔离+定价 | B | 定价升 A：官方价表 Code Interpreter $0.0895/vCPU·h + $0.00945/GB·h、按秒按实际消耗、会话自 microVM 启动至关闭计费；生命周期升 A：默认 900s、可配至 8h。隔离："每会话 microVM"升 A；**"Firecracker"未在 Code Interpreter 自身文档中找到原文（仅 Runtime 的 harness 安全文档有此表述），该具体词维持 B** | **定价/生命周期可升 A；microVM 隔离可升 A；Firecracker 字样维持 B** | https://aws.amazon.com/bedrock/agentcore/pricing/ ；https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/bedrock-agentcore-dg.pdf（Session management 节）；https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-security.html（仅 Runtime） |
| Q10 | AWS Lambda 本体 隔离+定价 | B（隔离）/ A（价） | 官方 FAQ 原文：每个执行环境运行于"dedicated Firecracker microVM with its own kernel, memory, and file system"；Event 调用最长 15min；价表 $0.20/百万请求 + $0.0000166667/GB·s、免费层 100 万请求 + 400,000 GB·s/月 | **可升 A** | https://aws.amazon.com/lambda/faqs/ ；https://aws.amazon.com/lambda/pricing/ |
| Q10 | GKE Agent Sandbox 隔离 | B | 官方概念页原文：kernel-level isolation、主要用 gVisor、亦可配 Kata、Default Deny 网络；how-to 官方示例 `runtimeClassName: gvisor` | **可升 A** | https://docs.cloud.google.com/kubernetes-engine/docs/concepts/machine-learning/agent-sandbox ；https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox |
| Q10 | GKE Agent Sandbox 定价 | B（Autopilot 归纳价） | 官方原文："Agent Sandbox on GKE is offered at no extra charge. GKE pricing applies"——**无产品专属单价**，Round 1 的"$0.0445/vCPU·h 归纳价"应删除 | **可升 A（口径修正后）** | https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox （Costs 节） |
| Q10 | GCP Agent Compute Engine 状态/隔离/定价 | C | 官方公告（2026-10-22）：已推出、已在为 Gemini 供能、客户 preview"in the coming months"；隔离原文"hardware-isolated Cloud Hypervisor boundary with its own guest kernel"、Titanium IPU、凭证在 microVM 外的 egress 注入、每 VM 独立 Hyperdisk；两篇官方博客**均无任何定价** | **状态/隔离可升 A；定价维持"未公开/未定价"**（A 级确认未公布，非缺证） | https://cloud.google.com/blog/topics/ai-infrastructure/introducing-agent-compute-engine-and-expanded-agent-governance ；https://cloud.google.com/blog/topics/ai-infrastructure/agent-compute-engine-deep-dive |

---

## 1. Q11 · OWASP 编号 + 5 个 CVE 回原文

### 1.1 OWASP LLM Top 10（2025 版）——D 线引用无误，可升 A

打开 https://genai.owasp.org/llm-top-10/ （现标题为 "LLMRisks Archive"，页首自述含 "Read the OWASP Top 10 for LLMs 2023-24" 的归档结构，页面按序给出十条的定义段落）。与 D 线（round1-D §1.27 之 S1、及 T13/T17/T19/T20/T22 引用）逐条对位：

| 编号（2025） | 条目名 | 官网归档页对应段落要点 | 与 D 线引用 |
|---|---|---|---|
| LLM01:2025 | Prompt Injection | "A Prompt Injection Vulnerability occurs when user prompts alter the…" | 一致 |
| LLM02:2025 | Sensitive Information Disclosure | "Sensitive information can affect both the LLM and its application…" | 一致 |
| LLM03:2025 | Supply Chain | "LLM supply chains are susceptible to various vulnerabilities…" | 一致 |
| LLM06:2025 | Excessive Agency | "An LLM-based system is often granted a degree of agency…" | 一致 |
| LLM10:2025 | Unbounded Consumption | "Unbounded Consumption refers to the process where a Large Language…" | 一致 |

结论：**2025 版五条全部可升 A**，但引用时必须带版本标注（如 `LLM06:2025`），原因见 1.2。

### 1.2 新版已发布：2026 版且编号大改 —— 对下游是破坏性变更

- 存在性（A）：genai.owasp.org 官方新闻稿（2026-09-01 发布）标题即 "OWASP GenAI Security Project Unveils 2026 Top 10 for LLM Applications…"，称其为 "the latest edition of the project's flagship guidance"，下载页为 https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ （已打开，页文自述 "OWASP Top 10 for LLM Applications 2026 is the latest community-driven guide…"）。二手资料一致称 2026 版正文发布于 2026-08-03、文件为 `OWASP-GenAI-LLM-Top-10-2026-v1.0.pdf`；本轮未逐字打开该 PDF 全文，故"08-03 发布日"记为 B。
- 改号在 OWASP 官网自身亦有实证（A）：官网 Q3 2026 Exploit Roundup 已按 2026 编号写作 "LLM01:2026 Prompt Injection"、"LLM02:2026 Sensitive Information Disclosure"、"**LLM03:2026 Excessive Agency**"、"LLM05:2026 Data and Model Poisoning"（https://genai.owasp.org/2026/10/08/genai-and-agentic-ai-exploit-roundup-q3-2026/ ）。
- 2026 全表（多家独立转录与官网用法互证一致，标 A-/B+，正式引用前建议再逐字核 PDF）：LLM01 Prompt Injection / LLM02 Sensitive Information Disclosure / **LLM03 Excessive Agency** / **LLM04 Supply Chain** / LLM05 Data and Model Poisoning / **LLM06 Unbounded Consumption** / LLM07 Misinformation / LLM08 Hidden Context Exposure（由 2025 的 System Prompt Leakage 更名扩围）/ LLM09 Vector and Embedding Weaknesses / LLM10 Improper Output Handling。
- 对本项目的直接影响（D 线五条的 2025→2026 映射）：LLM01 不变；LLM02 不变；**LLM03:2025 Supply Chain → LLM04:2026**；**LLM06:2025 Excessive Agency → LLM03:2026**；**LLM10:2025 Unbounded Consumption → LLM06:2026**；另 D 线引用过的 LLM07:2025 System Prompt Leakage → LLM08:2026 Hidden Context Exposure。
- 裁决：D 线底稿按 2025 版引用本身正确且可升 A；但从本轮起，任何**不带年份**的 "LLM06" 等写法都会产生歧义（2026 版 LLM06 已是 Unbounded Consumption）。建议全项目统一改写为带年份编号，并决定威胁矩阵是否迁移到 2026 编号（迁移属主线决策，本线只报事实）。

### 1.3 五个 CVE —— 逐个打开 nvd.nist.gov（详情页 + NVD 官方 API 双通道互证），全部可升 A

| CVE | 原文结论（一句话） | 受影响产品/版本（NVD 原文） | CVSS（NVD） |
|---|---|---|---|
| CVE-2019-5736 | runc 的 /proc/self/exe 文件描述符处理缺陷使攻击者可覆盖宿主 runc 二进制并获得宿主 root | runc through 1.0-rc6；Docker before 18.09.2 等 | 3.1 **8.6 HIGH**，CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H |
| CVE-2024-21626 | runc 内部 FD 泄漏使新容器进程工作目录落入宿主文件系统命名空间，可访问宿主文件系统并可覆盖半任意宿主二进制实现完全逃逸 | runc 1.1.11 及更早（CPE：<1.1.12；GitHub 口径 ≥v1.0.0-rc93, <1.1.12），1.1.12 修复 | 3.1 **8.6 HIGH**，向量同上（NVD 详情页直接打开核对，NIST/CNA/ADP 三方同分） |
| CVE-2022-0492 | Linux 内核 `cgroup_release_agent_write`（kernel/cgroup/cgroup-v1.c）缺陷，特定条件下可用 cgroups v1 release_agent 提权并意外绕过 namespace 隔离 | Linux kernel 多分支（CPE：2.6.24 起至 <4.9.301 / <4.14.266 / <4.19.229 / <5.4.177 / <5.10.97 / <5.15.20 / <5.16.6，及 5.17 rc1/rc2） | 3.1 **7.8 HIGH**，CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H；NVD 页另载：已入 CISA KEV（Vulnerability Name "Linux Kernel Improper Authentication Vulnerability"，2026-06-02 收录） |
| CVE-2016-5195 | Dirty COW：mm/gup.c 的 COW 处理竞态使本地用户可写只读内存映射提权，2016-10 已在野利用 | Linux kernel 2.x through 4.x before 4.8.3 | 3.1 **7.0 HIGH**，CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H |
| CVE-2022-0847 | Dirty Pipe：pipe buffer `flags` 未正确初始化含残留值，非特权本地用户可写只读文件页缓存并提权 | Linux kernel 5.8–<5.10.102、5.15–<5.15.25、5.16–<5.16.11（NVD CPE 口径） | 3.1 **7.8 HIGH**，CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H |

注：CVE-2019-5736 / CVE-2016-5195 / CVE-2022-0847 的详情页抓取未完整呈现描述段，改由 NVD 官方 API（services.nvd.nist.gov/rest/json/cves/2.0）取原文描述与 NIST 口径 CVSS，并与详情页可读部分（2024-21626、2022-0492 两页为浏览器直开全页核对）互证；API 与详情页同属 nvd.nist.gov 官方源，按原文计 A。

---

## 2. Q22 · 两个 license 逐字核

### 2.1 Wasmtime —— 完整 SPDX 成立，可升 A 结案

- 仓库文件：`LICENSE`（仓库根目录唯一 license 文件，gh contents 已确认）。
- 原文关键行：正文为 Apache License Version 2.0 全文；文末（第 205 行起）有专节标题行：
  `--- LLVM Exceptions to the Apache 2.0 License ----`
  其下为 LLVM 例外正文（"As an exception, if, as a result of your compiling your source code, portions of this Software are embedded into an Object form…"，含 GPLv2 冲突时可整节豁免的条款）。
- 第二原文：仓库根 `Cargo.toml` 声明 `license = "Apache-2.0 WITH LLVM-exception"`。
- 结论：通行完整 SPDX 写法 **Apache-2.0 WITH LLVM-exception** 与仓库原文逐字相符，Round 1"待复核"可关闭。原文 URL：https://github.com/bytecodealliance/wasmtime/blob/main/LICENSE

### 2.2 Cloud Hypervisor —— 三文本的范围：两个已明、一个未明

- 仓库结构：根目录无单一 LICENSE 文件，有 `LICENSES/` 目录，含三文件：`Apache-2.0.txt`、`BSD-3-Clause.txt`、`CC-BY-4.0.txt`（gh contents 已确认）。
- 适用范围原文：`.reuse/dep5`（REUSE 规范文件）逐字为：
  - `Files: docs/*.md *.md` → `License: CC-BY-4.0`（即全部 Markdown 文档/根目录文档走 CC-BY-4.0）
  - `Files: scripts/* test_data/* *.toml .git* .editorconfig fuzz/Cargo.lock fuzz/.gitignore resources/linux-config-* vmm/src/api/openapi/cloud-hypervisor.yaml CODEOWNERS Cargo.lock` → `License: Apache-2.0`
- 未核清部分：本轮取到的 dep5 全文中**没有出现 BSD-3-Clause 的 Files 条目**；BSD-3-Clause.txt 存在于 LICENSES/ 但其对应文件范围未在 dep5 中定位（不排除个别源文件以文件头声明适用）。按纪律不猜测：**BSD-3-Clause 适用范围维持待核**，后续可逐仓 grep 源文件头确认。
- 结论：CSV 现行写法 "Apache-2.0 / BSD-3-Clause 双许可（另有文档 CC-BY-4.0 待细核）" 应改写为："代码以 Apache-2.0 为主（dep5 列明文件集），文档 CC-BY-4.0，LICENSES/ 另含 BSD-3-Clause 文本（适用范围待核）"。

---

## 3. Q21 · 两个生命周期数字找官方原文

### 3.1 Browserbase 付费 session 6h —— 官方原文未找到，维持 B

尝试路径（如实记录）：
1. 打开官方 pricing 页全文（https://www.browserbase.com/pricing ，本轮现行版本）：Free 档仅标 "15 minutes /session"；Developer/Startup/Scale 三档的 Infrastructure 清单**不再列 session 时长**；页下 Compare plans 对比表行项为 Concurrency / Browser hours / Agent runs / Search API / Fetch API / Data Retention 等，**无 session duration 行**。
2. 打开官方 docs 的 Long sessions 页（https://browserbase.mintlify.app/platform/browser/long-sessions/overview ，文档自带 Updated: 2026-10-08）：只讲 session timeout 机制（项目级设置、可自定义 timeout、示例为 3600s）与 keepAlive，**未给任何按套餐的时长上限数字，更未出现 6h**。
3. 站内/搜索引擎以 "session / 360 / 6 hours" 检索官方域：命中的 6h 说法全部来自第三方评测站（gologin、prospeo、browser-use 对比文等），无一来自 browserbase.com / docs 官方页。

结论：**官方原文未找到，维持 B**。补充判断（标推论）：Browserbase 现行 pricing 页已经改版（新增 Agent runs、Search/Fetch 计量），Round 1 的"6h"很可能是旧版 pricing/compare 表的数字、现已被官方撤下展示；是否仍为实际执行上限，官方无现行原文可证，不得升 A、亦不得当现行事实引用。

### 3.2 Daytona 默认 auto-stop 15min —— 找到官方原文，可升 A

官方 docs《Sandboxes》页（https://www.daytona.io/docs/en/sandboxes/ ）"Running indefinitely"节原文：

> "By default, Daytona sandboxes auto-stop after 15 minutes of inactivity. To keep a sandbox running without interruption from inactivity, set the auto-stop interval to `0`…"

同页 SDK 参考互证：`set_autostop_interval` 参数说明 "Defaults to 15"（Python SDK 页）、TypeScript SDK 页 "Default is 15 minutes"。结论：**可升 A**。附带新事实（同页原文，可一并回填）：Daytona 现行 docs 自述 "Sandboxes run as Linux containers by default"，另有 Linux VM / Windows / GPU / macOS 类——此为对 OPEN-QUESTIONS 第 2 问"容器类底层 runtime"的部分推进（仍未点名 Docker/Kata/Sysbox，runtime 名维持 U）。

---

## 4. Q18 · Modal VM Sandboxes 回官方原文

原文链（三处官方，互证）：

1. 官方产品更新博客（Published: 2026-06-15，https://modal.com/blog/product-updates-vm-sandboxes-domain ）：
   > "🔲 VM Sandboxes (Alpha) — We're building a new VM runtime for Sandboxes. VM Sandboxes run a real Linux kernel, so they can support workloads that run Docker containers within the Sandbox, or that require Linux features like eBPF, systemd, cgroups, or custom filesystem mounts."
   同文另载 Domain Allowlisting（`outbound_domain_allowlist`）为 Sandbox 正式能力。
2. 官方 docs《Sandboxes》"Runtimes"节（https://modal.com/docs/guide/sandboxes ，现行）：
   > "Sandboxes run on one of two runtimes: **gVisor**… provides strong isolation and is suitable for most workloads. **VMs** run the Sandbox in a virtual machine with its own Linux kernel… Switch runtimes via the `runtime` parameter, or leave unset to let Modal choose for you. GPU Sandboxes are only supported with `runtime="gvisor"`."
3. 官方 docs《Networking and security》"Security model"节（https://modal.com/docs/guide/sandbox-networking ）：
   > "VMs: the Sandbox runs in its own virtual machine with its own Linux kernel, **isolated by the CPU's hardware virtualization through the Linux KVM hypervisor**."（gVisor 侧表述为用户态实现 syscall 接口）

后续状态：官方 Runtime Roundup 博客已称 VM Sandboxes 在 Linear、Legora、Snorkel 等客户生产使用、"give your agent access to a full Linux computer"（https://modal.com/blog/runtime-product-update-sandbox-endpoints ）；官方 changelog 亦列 "Give agents a full computer with VM Sandboxes" 条目。

裁决：
- **是否已发布**：已发布——2026-06 以 Alpha 推出、现已进入客户使用与 docs 正式条目，不再是"仅 B 级转述"。**可升 A**。
- **VM 类的隔离表述**：官方原文只说到 **KVM 硬件虚拟化 + 独立 Linux 内核**，未点名任何 VMM 产品（不是 Firecracker 的官方表述，不得回填 Firecracker）。**可升 A（表述为 KVM）**。
- **默认隔离是否仍 gVisor**：现行 docs 的口径是"双运行时、用 `runtime` 参数切换、未设则由 Modal 选择"，**官方未再声明 gVisor 为默认**。Round 1/CSV 中"默认仍 gVisor（A）"的写法已被官方现行文档取代，应改写为双运行时口径；硬说"gVisor 默认"在原文层面不成立。
- 连带：Round 1 B 线"VM runtime 下 rootfs 固定 512 GiB（官方 sandbox-resources 文档，A）"本轮未复核，不在本项裁决范围内。

---

## 5. Q10 · 云厂商五项回原文（Azure 本轮不做，按任务书）

### 5.1 AWS Lambda MicroVMs —— 隔离与定价均可升 A

- 隔离（开发者指南原文，https://docs.aws.amazon.com/lambda/latest/dg/lambda-microvms-guide.html ）：
  > "AWS Lambda MicroVMs deliver these core capabilities through **Firecracker virtualization**, which powers Lambda Functions' 15 trillion+ monthly invocations."
  同页定位："serverless compute environments that provide **VM-level isolation** with full operating system capabilities"，由快照启动、可 suspend/resume 保内存与磁盘状态。
- 生命周期（官方 FAQ，https://aws.amazon.com/lambda/faqs/ ）："Each MicroVM has a total lifespan of **up to 8 hours, including both running and suspended time**"；"You pay per second of compute while a MicroVM runs, plus snapshot storage while it's suspended."
  ⚠️ 口径修正：Round 1 的"最长 8h"应注明是**含挂起的总寿命 8h**，不是纯运行时长 8h。
- 定价（官方价表 MicroVMs 专节，https://aws.amazon.com/lambda/pricing/ ）：按秒计费；价表两个官方算例直接使用 Graviton（ARM）单价——**$0.0000276944/vCPU-second、$0.0000036667/GB-second**；快照写 **$0.0038/GB**、快照读 **$0.00155/GB**、快照/镜像存储 **$0.08/GB-month**（镜像存储有 1 周最低保留期）；基线默认 2GB/1vCPU、内存:vCPU=2:1、可纵向扩至基线 4x、挂起不收 compute。Round 1 标 B 的这组数字与官方价表现行算例逐字一致，**可升 A**。

### 5.2 AWS Bedrock AgentCore Code Interpreter —— 定价/生命周期升 A；Firecracker 一词维持 B

- 定价（官方价表，https://aws.amazon.com/bedrock/agentcore/pricing/ ）：价表列 **Code Interpreter CPU $0.0895 per vCPU-hour、Memory $0.00945 per GB-hour**（与 Runtime microVMs v1、Browser Tool 同价）；计费口径原文："Billing is based on CPU and memory consumption across your session lifetime, calculated at per-second increments… spans from **microVM boot**, initialization, active processing, idle periods, until session termination (**microVM shutdown**)"，I/O 等待不计 CPU、1 秒最低计费、128MB 最低内存计费。同页另载新客户最高 $200 Free Tier credits（页级口径）。
- 生命周期（官方 Developer Guide，Session management 节）：**Session timeout Default: 900 seconds (15 minutes)，可配至 8 hours**；会话内文件/数据持续可用、会话终止即清理；会话数据 TTL 保留策略 30 天。API 参考互证：`sessionTimeoutSeconds` 默认 900、最大 28,800（https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_StartCodeInterpreterSession.html ）。
- 隔离：官方 Developer Guide 对 Code Interpreter 的定性原文是 "An isolated sandbox environment for agents to execute code"；结合价表"microVM boot/shutdown"的计费边界表述，**"每会话 microVM 隔离"可升 A**。但 **"Firecracker microVM per-session"（Round 1 B 线写法）在 Code Interpreter 自身的 docs/价表中未找到原文**——本轮找到的 Firecracker 原文出自 AgentCore 的 harness 安全文档（https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-security.html ）："Every session runs in its own **Firecracker microVM in AgentCore Runtime**"，其主语是 **Runtime** 会话而非 Code Interpreter。故：Code Interpreter 的 Firecracker 字样 **维持 B**（同平台 Runtime 已证、CI 未自证），回填时应把 isolation 写为 "microVM per-session（官方价表/文档，A）；Firecracker 未在 CI 文档自证（B）"。

### 5.3 AWS Lambda 本体 —— 隔离与定价均可升 A

- 隔离（官方 FAQ 原文，https://aws.amazon.com/lambda/faqs/ ，"How does AWS Lambda isolate my code?"）：
  > "Every Lambda execution environment runs inside a **dedicated Firecracker microVM with its own kernel, memory, and file system** — no two environments share a kernel or memory space. Event Functions isolates each request in its own environment… MicroVMs provides the same Firecracker-based isolation with customer-controlled lifecycle…"
  另一答："All execution environments run inside Firecracker microVMs with hardware-level isolation"。Round 1"Firecracker 为业界共识 B、官方 pricing 页未述"的缺口就此关闭——原文不在 pricing 页而在 FAQ 页。
- 生命周期（同 FAQ）：Event Functions "An invocation can run for **up to 15 minutes** by default"（Managed Instances 异步可至 90min、Durable Functions 另计，不属本体口径）。
- 定价（官方价表，https://aws.amazon.com/lambda/pricing/ ）：Event Functions $0.20/百万请求 + 时长 $0.0000166667/GB·s（x86 第一档；算例口径）；免费层 100 万请求 + 400,000 GB·s/月。与 Round 1 已填数字一致，维持 A 并补隔离升 A。

### 5.4 GKE Agent Sandbox —— 隔离升 A；定价口径修正后升 A（删除归纳单价）

- 隔离（官方概念页《About Agent Sandbox on GKE》，https://docs.cloud.google.com/kubernetes-engine/docs/concepts/machine-learning/agent-sandbox ）原文要点：
  - "**Kernel-level isolation**: Provides strong, kernel-level isolation for untrusted, LLM-generated code. Agent Sandbox on GKE also works with open source **Kata Containers**."
  - "AI agent runtimes: Safely execute untrusted code in an environment isolated by security-focused runtimes like **gVisor**."
  - Limitations 节："it is **primarily intended to be used with security-hardened runtimes like gVisor**"（即主推 gVisor、Kata 为可选项，无"gVisor 默认"的强制表述——回填措辞应作"以 gVisor 为主、支持 Kata"）。
  - 网络："implements a **Default Deny** network security posture for all sandboxed environments"；Warm Pool 预热 <1s 分配、Pod snapshots 暂停/恢复。
- 隔离（官方 how-to，https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox ）：官方示例 SandboxTemplate 直接写 `runtimeClassName: gvisor` 与 `sandbox.gke.io/runtime: gvisor` 节点选择，与概念页互证。
- 定价（同 how-to 的 Costs 节）原文：
  > "**Agent Sandbox on GKE is offered at no extra charge. GKE pricing applies** to the resources that you create."
  即**不存在产品专属价表**；Round 1 CSV 的"按 Autopilot 资源价归纳 $0.0445/vCPU·h（B）"是把 GKE 通用资源价当产品价，口径错误，**应删除该数字**、改写为"无附加费，按所用 GKE 资源计价（A）"。

### 5.5 GCP Agent Compute Engine —— 状态/隔离升 A；定价维持未定价

- 状态（官方公告，Google Cloud Blog，Published 2026-10-22，https://cloud.google.com/blog/topics/ai-infrastructure/introducing-agent-compute-engine-and-expanded-agent-governance ）原文：
  > "we are **launching Agent Compute Engine**, a purpose-built compute service that **already powers Gemini** as an agent for work tasks. **It will be available in preview in the coming months**, providing hardware-isolated runtime sandbox security."
  即：已对外发布（内部已供 Gemini 使用）、**客户侧仍是未来数月的 preview**，不是 GA、不可自助开通。Round 1 的"预览（未 GA）"判断方向正确，现可由 C 升 A。
- 隔离（同公告原文）：
  > "Agent Compute Engine delivers strong isolation via a **hardware-isolated Cloud Hypervisor boundary with its own guest kernel and root access**."
  另：运行于 **Titanium** IPU；"service credentials are **injected in egress outside the microVM**"、每 microVM 短时凭证与加密可验证 ID；CoW 内存共享多 agent 共模板、空闲 microVM 经 checkpoint/restore 暂停；每 microVM 独立 **Hyperdisk** 持久化工作区。
- 隔离补充（官方 deep dive，https://cloud.google.com/blog/topics/ai-infrastructure/agent-compute-engine-deep-dive ）："Each agentic session runs inside a dedicated, **single-tenant and memory-safe microVM**"；零秘密架构（guest 内无持久秘密、无云元数据服务器访问、仅会话级 SPIFFE 证书+短时 token）；网络无标准网卡/默认网关/直达 VPC，全部流量走 **virtio-vsock** 到本地代理再到外部网关；快照与卷静态加密。注：deep dive 全文未点名 Cloud Hypervisor（已全文检索），VMM 名的原文只在公告篇——引用 VMM 名时只引公告篇。
- 定价：公告与 deep dive 两篇官方原文**均未出现任何价格/计费字样**（已检索确认）；结合"preview in the coming months"，定价结论维持 **未公开/未定价**——此为本轮以 A 级原文确认的"尚未公布"，不是证据缺失型 U。

---

## 6. 对 products.csv 的具体回填建议（逐行：产品名 → 字段 → 新值 → 等级）

> 仅建议，不直接改表。retrieved_at 均为 2026-10-27。

1. **Wasmtime** → `license` → `Apache-2.0 WITH LLVM-exception (仓库LICENSE原文: Apache-2.0正文+文末LLVM Exceptions专节; 根Cargo.toml license字段同式)` → **A**；`notes` 删除"待复核"字样，改注"Q22已逐字核结案 2026-10-27"。
2. **Cloud Hypervisor** → `license` → `Apache-2.0 (代码, .reuse/dep5列明文件集) + CC-BY-4.0 (文档 docs/*.md与*.md); LICENSES/另含BSD-3-Clause文本, 其文件适用范围待核` → **A（BSD 范围部分除外）**。
3. **Daytona** → `lifecycle` → 在现值中把"默认15min空闲auto-stop为B级待官方直引"替换为`默认15min空闲auto-stop (官方docs原文, A); auto_stop_interval=0可禁用; 另有ttl_minutes墙钟销毁` → **A**；`isolation_tech` 追加`官方docs现自述: Sandboxes run as Linux containers by default, 另有Linux VM/Windows/GPU/macOS类 (A自述); 容器runtime名仍未公开(U)`。
4. **Browserbase** → `lifecycle` → 把"付费6h上限为多源B级待官网compare表复核"改写为`Free session 15min (pricing明示, A); 付费档session上限: 现行官方pricing/compare/docs均未载明 (2026-10-27复核未找到原文), 6h说法仅见第三方, 维持B且疑为旧版页面数字` → **维持 B**。
5. **Modal** → `isolation_tech` → 整段改写为`双运行时: gVisor (用户态syscall接口) / VM (独立Linux内核, KVM硬件虚拟化), 由runtime参数选择, 未设由Modal选择; GPU仅gVisor (官方docs, A)。VM Sandboxes 2026-06-15以Alpha推出 (官方博客, A), 现已客户生产使用` → **A**；删除原文中"VM Sandboxes Beta(2026-06, 仅B级转述, C待官方原文复核)"与"默认gVisor"的表述；`notes` 中"VM Beta单独为C待复核"删除。
6. **AWS Lambda MicroVMs** → `isolation_tech` → `Firecracker virtualization (开发者指南原文, A); VM级隔离+快照启动+suspend/resume` → **A**；`pricing` → 数字不变、等级升 **A**，来源改注`官方价表MicroVMs专节算例直引 (US East N. Virginia, Graviton)`；`lifecycle` → `总寿命最长8h (含挂起时间, 官方FAQ, A); 挂起不收compute、仅快照存储` → **A**；`status` 的"半核实"改`活跃 (已在14个区域可用)`口径可据官方 What's New（本轮检索见 2026-10 扩区公告）——此点未逐字打开公告正文，标 **B** 供主线取舍。
7. **AWS Bedrock AgentCore Code Interpreter** → `pricing` → `$0.0895/vCPU·h + $0.00945/GB·h (官方价表, A); 按秒按实际消耗计费, I/O等待不计CPU, 1s最低/128MB最低内存` → **A**；`lifecycle` → `默认timeout 900s(15min), 可配至28,800s(8h) (官方Developer Guide/API, A); 会话内文件持续, 终止即清理, 会话数据TTL 30天` → **A**；`isolation_tech` → `microVM per-session (官方价表以microVM boot/shutdown为计费边界, A); Firecracker字样未在CI自身文档出现, 仅AgentCore Runtime文档有 (B)` → **A/B 混合标注**；`official_evidence` 补 `https://aws.amazon.com/bedrock/agentcore/pricing/` 与 Developer Guide PDF。
8. **AWS Lambda** → `isolation_tech` → `每执行环境独占Firecracker microVM (独立kernel/memory/filesystem) (官方FAQ原文, A)` → **A**（由"未公开/B 共识"升）；`lifecycle` → `单次调用最长15min (官方FAQ, A; Managed Instances异步90min为另一形态)` ；`confidence` 本行可由 B 升 **A**（定价+隔离均已 A）。
9. **GCP GKE Agent Sandbox** → `isolation_tech` → `kernel级隔离, 以gVisor为主 (官方示例runtimeClassName: gvisor), 支持Kata Containers; Default Deny网络 (官方概念页/how-to, A)` → **A**；`pricing` → **删除** `$0.0445/vCPU·h 归纳价`，改`无附加费: "offered at no extra charge, GKE pricing applies" (官方how-to Costs节, A)` → **A**；`status` 的"半核实(B级归纳)"改`已可用 (GKE托管add-on, 基于开源Agent Sandbox controller)` → **A**。
10. **GCP Agent Compute Engine** → `status` → `已发布公告 (2026-10-22), 内部已供Gemini使用; 客户preview "in the coming months", 未GA (官方博客, A)` → **A**；`isolation_tech` → `单租户microVM, hardware-isolated Cloud Hypervisor boundary, 独立guest内核+root, Titanium IPU; 零秘密 (凭证在egress外注入), 无元数据访问, 网络仅virtio-vsock经代理 (官方公告+deep dive, A)` → **A**；`credential_security` 同步按上改 **A**；`pricing` 维持`未公开/未定价 (官方公告与deep dive均未载价格, 2026-10-27确认)`；本行 `confidence` 由 C 升 **A（定价字段除外，定价为已确认未公布）**。
11. （非 CSV、属 D 线底稿）**round1-D-threat-bench.md** → S1/S10 来源行等级 B 改 **A**，并在 S1 加注：`2025版编号已核; 2026版已发布且改号 (Excessive Agency=LLM03:2026, Supply Chain=LLM04:2026, Unbounded Consumption=LLM06:2026, System Prompt Leakage→Hidden Context Exposure=LLM08:2026), 后续引用须带年份`。

## 7. 本轮未清/新留缺口

- OWASP 2026 版 PDF 全文未逐字打开：全表逐条目前靠官网新闻稿+官网 roundup 用法+多家一致转录互证（A-/B+）；若主线决定威胁矩阵迁移 2026 编号，需先逐字核 PDF。
- Cloud Hypervisor 的 BSD-3-Clause 文件适用范围未定位（dep5 无条目），留待 grep 源文件头。
- Browserbase 6h：现行官方渠道已无此数字；若主线仍需该上限，只能走产品实测/销售确认，不再有原文路径。
- AgentCore Code Interpreter 的 Firecracker 自证：CI 文档只到 microVM；如需升 A，只能等 AWS 在 CI 文档中点名或以官方支持渠道确认。
- Lambda MicroVMs"14 个区域"仅见官方 What's New 检索摘要，未逐字打开正文，已在回填建议中降为 B 供取舍。
