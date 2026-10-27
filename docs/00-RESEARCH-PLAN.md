# 00 · 研究计划与执行状态

> 项目：Agent Sandbox 全领域技术研究、产业图谱构建与专家知识体系建设
> 启动：2026-10-27（Asia/Shanghai）｜ 研究截止口径：每轮以实际执行当天为准，逐条记录 `retrieved_at`
> 证据标准：A 官方/源码/论文/可复现实验 · B 可靠独立来源 · C 推断待验证 · U 未知。C/U 不得当事实。

## 1. 研究边界（先钉死定义）

**Agent Sandbox** = 为 AI Agent 提供受控执行环境的技术与基础设施，覆盖：代码执行、
Shell/工具链、独立文件系统、浏览器自动化、Computer Use/GUI、长短期云端工作空间、
不可信代码隔离、网络/凭证/资源治理、多租户、生命周期（创建/快照/休眠/恢复/销毁/复用）、
与 Agent Harness/工具调用/后台工作流的集成。

**必须区分的 14 个相邻概念**（分类体系见 `01-TAXONOMY.md`）：Code Execution Sandbox、
Agent Runtime Sandbox、Browser Sandbox、Computer Use/Desktop Sandbox、Secure Code Runner、
Cloud Dev Environment、MicroVM Isolation、Container Isolation、K8s Sandbox Orchestration、
Wasm Sandbox、OS-level Sandbox、Serverless Execution、LLM Agent Security Sandbox、
Harness 集成架构。不含 "Sandbox" 字样不等于无关；含该字样也不等于同类。

## 2. 执行顺序（用户 spec §16，不压缩成一轮搜索）

| 阶段 | 内容 | 产出 | 状态 |
|---|---|---|---|
| 0 | 计划、分类体系、种子清单、证据规范 | 本文件 + 01 + products.csv 骨架 | 进行中 2026-10-27 |
| 1 | 第一轮产业扫描：14 个搜索域 × 开源/商业/生态 | 每类候选/已核实清单 + COVERAGE | 待并行启动 |
| 2 | 产品数据库 v0.1→v1.0 | products.csv（约 30 字段/产品） | 未开始 |
| 3 | 核心技术深挖 + 代表产品源码级案例 | 原理专题 + 案例（17 问/产品） | 未开始 |
| 4 | 威胁模型、性能/成本评测体系 | 威胁矩阵 + benchmark 设计 | 未开始 |
| 5 | 实验室（4 阶段） | 实验手册（未执行标待执行） | 未开始 |
| 6 | 参考架构 A–E + 选型框架 | Mermaid 图 + 9 场景推荐 | 未开始 |
| 7 | 90 天专家路线 | 每周交付物 + 能力门 | 未开始 |
| 8 | 交叉核验、查漏、质审 | 最终报告 + 未解决问题清单 | 未开始 |

## 3. 第一轮扫描的 14 个搜索域（spec 市场覆盖率要求）

AI Agent Code Execution / Secure Code Execution / Cloud Agent Runtime / Remote Agent Execution /
Browser Sandbox / Computer Use Infrastructure / MicroVM Sandbox / Container Sandbox /
WebAssembly Sandbox / Serverless Code Execution / AI Coding Agent Runtime /
Cloud Development Environment / Untrusted Code Execution / Multi-tenant Execution Infrastructure

每域分别维护：已发现候选数 → 已核实数 → 已深研数 → 待验证数（见 COVERAGE.md）。
这些数字只说明本研究覆盖，不代表市场真实规模；禁止宣称"覆盖 100% 市场"。

## 4. 并行分工（主 Agent 统一术语、去重、交叉验证、整合）

- 线 A：开源项目发现（GitHub 组织/仓库、依赖、交叉引用、归档状态核实）
- 线 B：商业 SaaS（定位判定：专用 Sandbox / 通用云 / 浏览器服务 / 代码执行 / 云开发环境 / 平台内组件；定价与限制以官网当日为准）
- 线 C：底层原理（Linux 隔离、MicroVM/KVM、gVisor、Wasm——只用官方文档/源码/论文）
- 线 D：安全威胁模型 + 性能/成本评测设计
- 线 E（后续）：源码阅读地图、实验室、选型与 90 天路线

## 5. 每轮结束的强制自检

遗漏技术路线？遗漏重要开源/商业代表？名称/公司/项目混淆？归档项目误判活跃？
重复项？关键结论缺一手证据？不可直接比较的产品被强行对比？
未覆盖项与下一轮最高价值任务写入 `OPEN-QUESTIONS.md` 与 COVERAGE.md。
