# 01 · 分类体系 v0.1（2026-10-27，待第一轮扫描后修订）

分类原则：按 **隔离对象 / 威胁模型 / 运行方式** 分，不按营销名词分。
一个产品可有主类 + 多个技术标签；强行归为直接竞品是禁止的。

## 1. 按产品形态（主类）

| # | 主类 | 核心问题 | 典型对象（种子，待核实） |
|---|---|---|---|
| P1 | 专用 Agent Sandbox SaaS | 为 Agent 按需提供受控执行环境 API | E2B, Daytona, Runloop, Microsandbox |
| P2 | Secure Code Runner / Judge | 不可信代码判题式执行 | Judge0, Piston, isolate, nsjail |
| P3 | Browser Sandbox / 云浏览器 | 网页交互、浏览器指纹/会话隔离 | Browserbase, Browserless, Steel.dev, Hyperbrowser |
| P4 | Computer Use / Desktop Sandbox | GUI/远程桌面操作 | E2B Desktop, Anthropic Computer Use 参考实现, OSWorld 类环境 |
| P5 | Cloud Dev Environment / 云工作空间 | 持久化远程开发环境 | Gitpod, Coder, Codespaces, Daytona(兼) |
| P6 | 通用云执行平台（被 Agent 复用） | 通用计算，非专用 Sandbox | Modal, Fly.io, Cloudflare, AWS Lambda, Vercel Sandbox |
| P7 | Agent 平台内执行组件 | 某 Agent 框架自带 runtime | OpenHands Runtime, Claude Code 执行环境, SWE-agent 环境 |
| P8 | 开源自托管 Sandbox 平台/控制面 | 私有化部署的 Sandbox 系统 | OpenSandbox, E2B 开源组件, Daytona OSS, Sandbox Fusion 类 |

## 2. 按隔离技术（标签，可多选）

| # | 技术 | 隔离边界一句话 | 主要剩余风险（待深挖验证） |
|---|---|---|---|
| T1 | 进程/OS 级 | namespace+cgroups+seccomp+cap drop，同宿主内核 | 共享内核攻击面、配置错误 |
| T2 | 安全容器（用户态内核） | gVisor Sentry 拦截 syscall | 兼容性/性能、Sentry 本身漏洞 |
| T3 | MicroVM | KVM 独立 guest 内核，极小设备模型 | VMM 漏洞、快照状态泄露 |
| T4 | 安全容器（VM 型） | Kata：每 Pod/容器一个轻量 VM | 启动/密度开销 |
| T5 | Wasm | 线性内存+能力安全，宿主函数授权 | 生态/语言兼容、宿主函数即攻击面 |
| T6 | 完整 VM / 云实例 | 传统虚拟化 | 成本/启动慢、密度低 |
| T7 | 浏览器进程沙盒 | Chromium 多进程+站点隔离 | 浏览器 0day、SSRF/内网、会话窃取 |
| T8 | 语言级/解释器级 | 语言 VM 限制（如 RestrictedPython） | 绕过历史多，一般不单独作边界 |

## 3. 按执行模型（标签）

按请求（stateless run）/ 按任务（job 沙盒）/ 按会话（session 持久）/ 按用户常驻（workspace）/
环境池预热 / 快照恢复型。每种模型单独讨论生命周期、计费与状态污染风险。

## 4. 判定规则

- 只有 marketing 自称 sandbox、无隔离/生命周期证据 → 标 C 级，进候选清单，不进已核实清单。
- 已归档/停止维护（GitHub archived、官方 EOL 公告）→ 状态字段如实标，禁止当活跃产品推荐。
- 论文/原型 → 单独标 `paper-only`，不与可用产品混排比价比性能。
