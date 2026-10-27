# 18 · 实验室手册（独立成册）

> 项目：Agent Sandbox 全领域技术研究（goal_a756da9ace9a）
> 成册日期：2026-10-28（Asia/Shanghai）｜ 性质：实验规程与资产索引的单一入口
> 判据源头：`09-BENCHMARK-FREEZE-v1.md`（冻结 v1.0，未改动；本手册不改任何冻结值，只引用）
> 已执行证据：`10-LAB-BATCH1-REPORT.md`（第一批，LAB-MINI）；预注册：`hidden_files/lab/PREREG-batch1.md`
> 脚本与原始数据：`hidden_files/lab/scripts/`（12 个）、`hidden_files/lab/raw/`（16 个，含全部无效批次）
> 纪律：本项目全部 [SELF] 数据只来自本手册登记的环境与批次；测后改线 = 数据作废；无效批次与有效批次同等留档，不挑数。

## 1. 环境分级

### 1.1 LAB-MINI（已实测，现役载体）

实测指纹（[SELF]，2026-10-27 探查，见 10 报告 §0 与 PREREG §0）：

| 项 | 实测值 |
|---|---|
| 形态 | 云端沙盒 VM 内的 root 会话（userns 内，CapEff 含 SYS_ADMIN/NET_ADMIN） |
| CPU / 内存 | 2 vCPU / 7.9 GiB |
| 内核 / 架构 | Linux 7.0.0-39-generic / x86_64 |
| /dev/kvm | **无**（MicroVM 类实验对象在本载体不存在） |
| Docker | 无 |
| cgroup v2 | **控制器未委派**：根 `cgroup.controllers` 为空、新建子组无 cpu.max/memory.max/pids.max、`subtree_control` 写入 ENOENT；systemd 瞬态单元只记属性不执行（三探针实测） |
| namespace | unshare 全类可用（user/mount/pid/net/ipc/uts）；`ip netns add` / setns 路径被拒 |
| 网络干预（宿主 runtime） | connect()/sendto() 对 RFC1918/链路本地目标先行 EPERM；子 netns 数据面仅 TCP→127/8 可靠；UDP 全面 EPERM；nft `ct state` 规则 ENOENT |

**可用面**：namespace/seccomp 隔离探针、PID-ns 单元级终止清零、单 netns + 127/8 替身端点的网络策略逻辑验证、namespace 单元 ST 冒烟。
**禁用面**：一切绝对性能数字禁止外推、禁止产品排名（09 §0 既定）；cgroup 配额判定（C1/C2/C3）环境不具备。

### 1.2 LAB-REF（未获取，规格已登记 = OPEN-QUESTIONS Q36）

建议规格（研究侧建议，非采购决定）：x86_64、VT-x/AMD-V 且 /dev/kvm 对来宾可见（裸金属或开启嵌套虚拟化的实例）、≥4 vCPU（跑 K8s+Fast+Firecracker 建议 8 vCPU）、≥16 GiB RAM（建议 32 GiB）、≥100 GiB 磁盘、主流发行版（内核 ≥5.10、cgroup v2 且 subtree_control 可委派、root 可用）、可加载 nft/veth、无宿主侧 connect 拦截。

获取条件与边界（Q36 原文要点）：是否采购、何时采购由用户决定，本项目不替用户拍板；用户既有 AWS t3.small（无嵌套虚拟化、规格不足）与 MacBook Pro M5 Max（ARM+macOS、无 Linux KVM）均**不能**充当 LAB-REF。LAB-REF 是 C1/C2/C3、C6（含 Q32）、C8 拓扑级（含 Q29 真实地址段）、Q34 的共同前置。

## 2. 安全护栏（全部实验批次强制）

### 2.1 哨兵 / canary 原则

- 全部网络实验只对**自有哨兵**：端点为本机别名/替身地址（127/8 别名模拟白名单/非白名单/元数据/内网/DNS），哨兵返回可识别的 CANARY-* 内容串；**不访问任何真实外部地址、不触碰真实云元数据端点**。
- 对照组先行：无配方/无过滤时哨兵必须全部可达，否则 deny 结果不可归因、整批作废重跑。
- deny 判定签名：连接须以**超时**失败（DROP 特征，dt ≥ 2.0s）；瞬时错误（EPERM 等）说明有更前置的干预层先行触发，该用例不计为目标机制证据（记 N/A 并注明触发层）。
- 内存增长类探针：宿主 available < 400MiB 立即中止该项；增长步长按冻结值（8 MiB/100ms）。

### 2.2 kill 前断言规则（EXP-02 近失事件后冻结，见 10 报告 §2）

近失事件：EXP-02 batch-2 驱动因 ns 内外 PID 混用（从 ns 内 /proc 解析宿主 PID 落空），误向宿主 **PID 1** 发送单 PID SIGKILL；宿主 systemd 未受损——靠内核对 PID-namespace init 的信号保护，属侥幸而非设计。此后全项目 kill 类操作强制：

1. **宿主侧推导**：目标 PID 只能由宿主侧证据推导（如以负载主进程的 ppid 推导 ns init 的宿主 PID），禁止从 namespace 内 /proc 解析结果直接当宿主 PID 使用。
2. **拒绝低号**：任何 kill 前断言 pid > 10，pid ≤ 10 直接拒绝执行。
3. **命令行校验**：kill 前核对目标进程命令行与预期模式一致（本批口径：ns init 命令行须含 `sleep infinity`；对照组主进程命令行须含实验 workload 脚本名），不一致即中止并登记。
4. **已死跳过**：目标已自然退出则登记跳过，不对复用后的 PID 补发信号。
5. 每批实验设 trap 清理（杀全部子进程、删 netns/veth/临时目录），批后按 §6 清单逐项复核宿主。

### 2.3 云沙盒额度纪律（E2B 等云资源）

- 调试/测试脚本直接创建的云 sandbox **不受**平台 idle reaper 管理：任何脚本创建后必须在 finally 中 kill，能复用就复用、不每次新建（2026-10-07 实测教训：43 台历史调试 sandbox 空转被一键全杀）。
- 定期以 `Sandbox.list()` 核查 running 数，异常增长立即排查。
- 本项目现行状态：openmuse 已暂停且 `OPENMUSE_SANDBOX_DISABLED=1` 在案，**禁止新建任何 E2B sandbox**；E2B 深研全程为纯静态源码分析。本手册任何规程不构成创建云 sandbox 的授权。

### 2.4 冻结与预注册纪律

- 阈值先冻结后执行（09 文件）；预注册文件在任何正式运行前落盘，载体变更只能改载体、不能改判据，且须在运行前/同步登记（PREREG 附录 #1–#3 即此例）。
- 失败样本不进分位但必入失败率；异常值不删除；同条件 ≥3 批并报批间波动；差异小于批间波动时结论写「当前测量精度下不可区分」。

## 3. 已执行实验规程（第一批，2026-10-27，全部 [SELF]）

### 3.1 EXP-01 隔离探针

- **目的**：验证 LAB-MINI 载体上 namespace 视图隔离、cgroup 配额前提、seccomp 过滤三者的可证性。
- **环境**：LAB-MINI；脚本 `scripts/exp01_run.py`（+ `exp01a_namespaces.py`、`exp01bc_probes.py`、`exp01c_seccomp.c`）。
- **步骤**：(a) `unshare -Urmpfni` 内外逐项核验 11 项（内部 PID、UTS 改名、NET 接口集、MNT tmpfs 宿主不可见、IPC 私有信号量、六类 ns inode 全不同）；(b) cgroup 前提探针（controllers/subtree_control/配额文件存在性 + systemd 瞬态单元 CPU/Memory/Tasks 三行为探针）+ RLIMIT 替代探针（RLIMIT_CPU=2s、RLIMIT_AS=256MiB、邻居哨兵）；(
...[truncated 5641 chars]