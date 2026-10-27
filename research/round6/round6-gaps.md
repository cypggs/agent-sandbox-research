# Round 6 收官缺口处置底稿：Q14 WasmEdge 安全文档补核 + Q16 OpenHands 拆仓轻核实

> 日期：2026-10-28（Asia/Shanghai）｜ 方法：gh api + 官方站点/官方仓原文取证，无二手补位
> 范围：仅两问的定向核实；本稿不直接改 OPEN-QUESTIONS.md 与 products.csv，回填建议在 §3。

## 1. Q14 · WasmEdge 官方安全文档：找到（分散型，非文档站专章）

### 1.1 渠道穷尽清单（2026-10-28 实查）

| 渠道 | 结果 |
|---|---|
| GitHub 主仓 WasmEdge/WasmEdge 根目录 | **有 SECURITY.md**（gh api 实查存在）+ docs/SECURITY_CONTACTS.md、docs/embargo-policy.md |
| 官方文档站 wasmedge.org/docs | 首页三大类仅 Develop / Embed / Extend，**无 security 专章入口**（2026-10-28 实查首页） |
| CNCF TAG Security 评估站（tag-security.cncf.io） | **有 WasmEdge Self Assessment**（项目自评、CNCF 托管，源文件经 PR 合入 WasmEdge 主仓）——这是其最成体系的安全模型文档 |
| 官方博客（second-state / wasmedge 博客） | 未做逐篇穷尽；以上三处官方一手已足以定论，本稿不以博客补位 |

### 1.2 官方口径摘要（均 A 级：官方仓原文 / 项目官方自评）

- **漏洞披露体系完整**：SECURITY.md 规定报告邮箱 wasmedge-security@lists.cncf.io（24h 确认、48h 详细响应）、GitHub Security Advisory 私密通道、**90 天披露时限** + embargo 政策、受支持版本表。这一维与 Wasmtime 同级完备。
- **安全模型表述集中在 Self Assessment**：模块隔离（modular isolation）、线性内存模型、类型安全、**无直接系统调用**——一切 OS 资源（文件/硬件/网络）只能经 WasmEdge 提供的 WASI 接口访问；文件系统仅 `--dir guest:host[:readonly]` 一条授予路径，按 WASI-filesystem 实现；**侧信道攻击明示不在其关注范围（out of scope）**。
- **host function / 插件面**：自评与 README 的口径是「资源访问只能经运行时提供的接口（WASI 及插件 API）」——即宿主函数面 = 显式授予面，但**没有一份官方文档把 host function 的权限边界单独成章论述**（与下条 Wasmtime 对照项相关）。
- **已知逃逸/CVE 响应**：走 GitHub Advisory Database 公开（SECURITY.md 披露流程明示修复合并至全部受支持版本后公开），本轮未逐条枚举其历史 CVE（超出定向核实范围，不补）。

### 1.3 与 Wasmtime 的一句对照

Wasmtime 在官方文档站设有 security 专章、含「什么算安全漏洞」的逐项定义表（docs.wasmtime.dev，2026-10-28 检索实见）；WasmEdge 的披露**流程**完备度与之相当，但安全**模型**文档分散在 CNCF 自评里、文档站无专章、且无「安全漏洞定义」类条文——**文档完备度 Wasmtime > WasmEdge，差距在模型条文而不在披露流程**。

### 1.4 Q14 结论

**找到，可结案**：WasmEdge 官方提供成文的漏洞披露政策（SECURITY.md + embargo + 90 天时限）与一份 CNCF TAG Security 自评形式的安全模型文档（隔离性质、WASI 能力授予、侧信道不在范围）；不存在文档站形式的 security 专章与 host-function 权限专论。原问「无此文档就无法对比」的前提修正为：**可对比，但须以自评文档为据并注明其非文档站专章**。

## 2. Q16 · OpenHands 拆仓：SDK 独立仓已证实，无独立 runtime 仓

### 2.1 实查（gh api，2026-10-28）

- **主仓 OpenHands/OpenHands 未归档、2026-10-27 仍有推送**；README 已改版为 **「Agent Canvas — The self-hosted developer control center for coding agents and automations」**（可运行 OpenHands/Claude Code/Codex/Gemini/Pi/OpenCode 等 ACP 兼容 agent）——Round 1「定位转 Agent Canvas」得到现行 README 原文证实（A）。
- **独立 SDK 仓存在：OpenHands/software-agent-sdk**，组织描述「A clean, modular SDK for building AI agents with OpenHands V1」；README 原话「The OpenHands Software Agent SDK provides Python, TypeScript, and REST APIs for **building agents that work with code**.」（A）。配套仓：OpenHands/benchmarks（V1 评测）、OpenHands/docs（聚合文档，描述明示含 agent-sdk）。
- **无独立 runtime 仓**：gh api 分页拉全组织仓名并按 runtime/sdk/agent 过滤，命中仅 openhands-agent-monitor、agent-analysis、software-agent-sdk、rbren-sdk-experiments、agent-canvas、oss-agent-canvas——**没有名为或定位为 runtime 的独立仓**（2026-10-28 时点）。原问的「runtime 疑似拆仓」修正为：**拆出去的是 SDK（software-agent-sdk），主仓本体转为 Agent Canvas 控制面**；执行后端/默认隔离本轮按任务书不深挖，仍未核实。
- 附带：组织内另有 OpenHands/agent-canvas 与 oss-agent-canvas 两仓（与主仓 README 的 Agent Canvas 定位关系未深核，不在本轮范围）。

### 2.2 Q16 结论

**部分结案**：新仓定位已清（SDK 独立仓 = software-agent-sdk，主仓 = Agent Canvas）；「当前默认执行后端与隔离」子项仍未核实（需追 SDK/主仓调用链，属深研级工作量），建议在问题状态中拆分登记。

## 3. 回填建议（逐行，供主线执行，本稿未改台账）

- **OPEN-QUESTIONS 第 14 问**：状态改为「**已结案（Round 6 定向补核，2026-10-28）**：官方安全文档为分散型——SECURITY.md（披露流程/90 天时限，A）+ CNCF TAG Security 自评（安全模型：WASI 唯一资源面、--dir 授予、侧信道 out of scope，A）；文档站无 security 专章、无 host-function 权限专论；与 Wasmtime 对照结论见 round6-gaps.md §1.3。Wasm 路线结论的文档缺口就此关闭。」
- **OPEN-QUESTIONS 第 16 问**：状态改为「**部分结案（Round 6 轻核实，2026-10-28）**：独立 SDK 仓 OpenHands/software-agent-sdk 已证实（V1，Python/TS/REST，A）；主仓已转为 Agent Canvas 控制面（README 原文，A）；组织内无独立 runtime 仓。**剩余子项：现版本默认执行后端与隔离未核实**（需调用链深研），P7 引用暂按此边界。」
- **products.csv OpenHands 行回填建议（一行）**：product_name 维持「OpenHands (Runtime)」或改「OpenHands」并在 notes 注明现定位——core_scenario/notes 更新为「主仓现定位 Agent Canvas（自托管 coding agent 控制中心，README 原文 2026-10-28，A）；SDK 已拆为独立仓 OpenHands/software-agent-sdk（V1）；默认执行后端与隔离仍未核实（原 confidence B 与『核心隔离 C』的定性不变）」，official_evidence 补 software-agent-sdk 仓与主仓 README 两条。
