# Round 2 线 B 过程日志：OpenSandbox 源码深研

日期：2026-10-27（Asia/Shanghai）

## 克隆
- 命令：`git clone --depth 50 https://github.com/opensandbox-group/OpenSandbox opensandbox-src`（位于 hidden_files/research/，3221 文件，约 59s）
- HEAD：`dbcc6d7f1d30ffd7c45f587ec86d57d565e83738`（短 `dbcc6d7`），commit 时间 2026-10-27 15:28:09 +0800，`chore(manifests): bump fast-sandbox pin to 0e20b90 (master) (#2438)`
- 本地 tag：仅 release-1.2.0-rc.1/rc.2（浅克隆）；`git describe` = release-1.2.0-rc.2-253-gdbcc6d7
- gh API 复核：releases 前五 = 1.2.0-rc.2(2026-10-21, prerelease)、1.2.0-rc.1(2026-10-15)、1.1.1(2026-10-09, 最新正式)、1.1.1-rc.1、1.1.0；repo created_at=2025-12-17（迁移后新仓口径）、archived=false、Apache-2.0、stars 16201、forks 1509、open_issues 145、pushed_at 2026-10-27T07:30:45Z；alibaba/OpenSandbox 经 API 返回同一仓库（重定向确认）

## 分析方法
1. 先读 GOAL.md、01-TAXONOMY、OPEN-QUESTIONS 第 3 问、round1-A 的 OpenSandbox 行。
2. 结构测绘：根 AGENTS.md 仓库地图 + find 两层目录。
3. 文档层：docs/architecture/index.md 全文、fast-sandbox/{index,checkpoints,firecracker,performance}.md、network/egress.md、guides/{credential-vault,secure-container,network-isolation,pause-resume}.md。performance.md 的 ACK 原始数据（含并发 20 失败、resume 62s）是关键口径证据。
4. 源码层逐项 grep/sed 核对：
   - server：main.py、middleware/auth.py（dispatch 全文）、api/lifecycle.py 路由表、services/sandbox_service.py ABC、factory.py（create_sandbox_service 全文）、composite_service.py（templateId/fsb- 分发）、runtime_resolver.py 类表、docker/docker_service.py（create/_provision/_prepare_resource_limits/NET_ADMIN drop/SYS_ADMIN 放宽段）、docker/container_ops.py（host_config 硬化）、docker/runtime.py（execd/bwrap 注入）、k8s/egress_helper.py（sidecar NET_ADMIN add + 主容器 drop）、k8s/security_context.py、fast_sandbox/service.py + fastpath_client.py（类/方法表）、snapshot_runtime_factory.py（Composite 按来源选 runtime）
   - execd：pkg/web/router.go（NewRouter 全文、路由分组）、controller/command.go（TimeoutMs/background）、pkg/isolation/bwrap.go、pkg/resources（cgroup v2 读取）
   - egress：main.go（Fatalf 点位）、pkg/constants/mode.go（ParseEgressMode、空回退 dns）、pkg/policy/always_rules.go（MergeAlwaysOverlay 顺序）、pkg/credentialvault/vault.go（Store 结构）、fastsandbox_vault_persist.go / fastsandbox_policy_persist.go（encryption-at-rest TODO 原文）
   - kubernetes：apis/sandbox/v1alpha1/{batchsandbox,pool,sandboxsnapshot}_types.go 关键字段
5. 定量项：find 统计测试文件（server 93 py / components 298 go / kubernetes 79 go / tests 108）、grep 统计 TODO/FIXME（排除 test 与生成代码：server 3 / components 6 / kubernetes 14 / 其余 0）、grep "e2b" 全仓（仅 2 处文档命中语境）、grep 169.254 于 egress Go 代码+docs（无命中，即无硬编码元数据阻断）。
6. 未做：未部署运行、未跑测试、未读外仓 fast-sandbox、未做 specs↔实现全量 diff。

## 假设复核结论（详见 04 报告 §10）
12 条：证实 9（Kata、gVisor、Fast=Firecracker 集成层、内容寻址 artifact、两套 checkpoint、L1/L2 实质、L7 experimental 定性、fail-closed、BatchSandbox）/ 修正 2（per-sandbox sidecar 仅容器路径；Vault 只活内存仅容器路径）/ 未证实 1（Fast 运行时内部实现，外仓未读）/ 完全证伪 0。

## 产出校验
- 正式交付：files/04-OPENSANDBOX-DEEP-DIVE.md（行数在回报中以 wc -l 实测为准）
- 本日志：hidden_files/research/round2-B-opensandbox-log.md
- products.csv 未改动。
