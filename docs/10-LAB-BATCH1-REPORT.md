# 10 · LAB 第一批实验报告（Round 4，LAB-MINI 载体）

> 执行日期：2026-10-27。评测线：`files/09-BENCHMARK-FREEZE-v1.md`（v1.0 冻结，未改动）。
> 预注册：`hidden_files/lab/PREREG-batch1.md`（含载体变更附录 #1–#3，全部先于或同步于对应实验登记）。
> 原始数据：`hidden_files/lab/raw/`；脚本：`hidden_files/lab/scripts/`（均可重跑，命令见各节末）。
> 本报告全部数字为 [SELF]（本机自测），无一来自文档或第三方。
>
> ⚠️ **全局限制（冻结文件 09 §2 既定）**：宿主本身是一台云端沙盒 VM（2 vCPU / ~7.9 GiB / 内核 7.0.0-39-generic / x86_64，无 /dev/kvm、无 Docker）。一切绝对性能数字**仅对本载体成立，禁止外推**至裸机/生产环境；本批的价值是机制验证与相对结论，不是性能基线。

## 0. 环境实测与载体裁定汇总（先于实验的探针结论）

任务简报的三个环境假设经实测**不成立**，证据链完整保存在各 raw 文件中，裁定如下（冻结判据本身未动，动的是载体）：

| # | 简报假设 | 实测 [SELF] | 裁定 |
|---|---|---|---|
| 1 | cgroup v2 可用（可建子组设配额） | 可见 cgroup 根 `cgroup.controllers` 为空；新建子组无 `cpu.max`/`memory.max`/`pids.max`；向任何 `cgroup.subtree_control` 写 `+cpu` 返回 ENOENT | 控制器未委派。C1/C2/C3 的 cgroup 形式在本载体**环境不具备** |
| 2 | systemd 瞬态单元可作配额执行体 | 行为探针：`CPUQuota=50%` 与 `20%` 下 3 s 忙循环实耗 CPU 3.02 s / 3.03 s；`TasksMax=16` 下成功派生 80 个子进程；`MemoryMax=64M` 下 Python 增长至约 3.1 GiB 未被杀（探针由人工终止，宿主无恙） | 瞬态单元只记录属性、**不执行**。禁用为配额载体 |
| 3 | `ip netns`/setns 可用 | `ip netns add`、`nsenter -t <pid> -n` 均 Operation not permitted；但 `unshare -n` 可用、按 PID 移交 veth 端点可用 | netns 单元改用 unshare 进程承载（EXP-02/04 已验证可行） |

另有 EXP-03 专项探针发现的宿主 runtime 网络干预（详见 §3.1）：connect()/sendto() 系统调用层拦截、子 netns 数据面限制、UDP 全面 EPERM、nft `ct state` 不可用。四项均为实测，非推测。

## 1. EXP-01 隔离探针

**假设**：在本载体上，namespace 视图隔离（a）与 seccomp 系统调用过滤（c）可证；cgroup v2 配额（b）可按 C1/C2/C3 判据证——其中 (b) 的载体前提已在 §0 被证伪。

**原始数据**：`raw/exp01.json`（有效批）；`raw/exp01-attempt1-invalid.json`（无效批，见失败原因）。

### 1(a) namespace 视图隔离 —— 判定：**通过** [SELF]

`unshare -Urmpfni`（user/mount/pid/net/ipc/uts）内侧 vs 宿主侧逐项核验，11 项检查全过：

| 检查 | 证据 [SELF] |
|---|---|
| 内部 PID = 1（宿主侧同进程为 4915） | `pid_self: 1 vs 4915` |
| UTS：内侧改 hostname 为 `exp01a-canary-host`，宿主仍为 `htch-runtime` | 双侧读数 |
| NET：内侧接口仅 `lo`（宿主为 host0+lo） | ifaces 列表 |
| MNT：内侧挂载 tmpfs 成功且宿主挂载表不可见 | mount rc=0；`tmpfs_target_in_host_mounts: false` |
| IPC：内侧新建 SysV 信号量成功（私有 IPC ns） | `semget_id` 有效 |
| 六个被 unshare 的 ns inode 全部与宿主不同 | pid [4026532439] vs [4026532325] 等逐项比对 |
| cgroup/time ns 相同——按设计未被 unshare，不计失败 | `shared_by_design_ns_same: {cgroup: true, time: true}` |

### 1(b) cgroup v2 配额（C1/C2/C3）—— 判定：**环境不具备**（非通过、非失败）

证据见 §0 表 #1/#2：控制器集合为空、配额文件不存在、subtree_control 写入 ENOENT；systemd 瞬态单元三探针（CPU/Tasks/Memory）全部不执行。在此环境下任何"C1 误差 x%"数字都将是伪造，故按预注册登记**环境不具备**，C1/C2/C3 的 cgroup 判定整体顺延 LAB-REF。

替代载体补充探针（RLIMIT；**只作机制参考，不是 C1/C2/C3 判定**）[SELF]：

| 探针 | 结果 [SELF] |
|---|---|
| RLIMIT_CPU = 2 s，忙循环子进程 | 被 SIGXCPU（信号 24）终止于 CPU 1.999 s，相对误差 0.04%（无效批 attempt-1 为 1.936 s / 3.21%） |
| RLIMIT_AS = 256 MiB，受控内存增长 | 增长停止于 232 MiB 分配、VmSize 254,976 kB（≈249 MiB，贴限）；进程存活退出（AS 语义为分配失败而非击杀，与 C2 的 cgroup 语义不同，不可互换） |
| 邻居哨兵（噪声参考） | 独占时 6 s 窗口 CPU 6.008 s；与忙循环并发时 5.338 s，退化 11.15%（attempt-1 批为 10.34%）。n=1、共享宿主噪声大，**不构成任何隔离判定** |

### 1(c) seccomp —— 判定：**通过** [SELF]

C 探针（`scripts/exp01c_seccomp.c`，prctl+seccomp 过滤 mount 等）：

| 组 | mount 结果 | 其余功能 |
|---|---|---|
| 过滤组 | `rc=-1 errno=1 (EPERM)`，未挂载 | getpid/文件 IO/socket 全部正常 |
| 对照组（私有 mount ns 无过滤） | `rc=0`，挂载成功 | 正常 |

### 失败与无效记录

attempt-1 无效：驱动漏传 unshare `-i` 标志导致 IPC 从未隔离，且一个 SysV 信号量泄漏到宿主 IPC ns（semid 1，已由本人 `ipcrm` 移除；宿主原有 semid 0 未动，实验后复核仍在）。同批 python/ctypes 装 seccomp 失败，已换 C 探针。无效批数据保留并标注，未混入结论。

**复现**：`python3 hidden_files/lab/scripts/exp01_run.py`

## 2. EXP-02 超时清零（C4 + C7）

**假设**：以"单元整体销毁"终止失控工作负载，T+2 s / T+10 s 时宿主侧残留（进程/端口/文件）为 0（C4 唯一通过线）；"只杀主进程"将留下可测残留（对照）。

**载体**（预注册附录 #1）：实验组终止手段由 `cgroup.kill` 改为 **PID namespace 整体拆除**（SIGKILL ns init，内核回收全 ns 进程）——与 cgroup.kill 同为"单元级全量终止"语义；对照组为只杀主进程。工作负载：双 fork 脱缰 + setsid 后台守护 + 心跳写文件 + 监听本地端口（233xx 段），三种终止模式（超时 kill / 主动取消 / 正常结束）× 两组 × 10 轮 = 60 轮。

**原始数据**：`raw/exp02_results.jsonl`（有效批，60/60 轮完整、0 失败轮）；无效批 `raw/exp02-batch1-invalid.jsonl`、`raw/exp02-batch2-invalid.jsonl`、`raw/exp02-batch3-crash.log`（见失败记录）。

### 结果 [SELF]

| 组 × 模式 | n | T+2s 残留（每轮） | T+10s 残留（每轮） |
|---|---|---|---|
| 实验组 × 超时 | 10 | 0 ×10 | 0 ×10 |
| 实验组 × 取消 | 10 | 0 ×10 | 0 ×10 |
| 实验组 × 正常结束 | 10 | 0 ×10 | 0 ×10 |
| 对照组 × 超时 | 10 | 6 ×10 | 6 ×10 |
| 对照组 × 取消 | 10 | 6 ×10 | 6 ×10 |
| 对照组 × 正常结束 | 10 | 6 ×10 | 6 ×10 |

- 实验组 30/30 轮 `destroy_confirmed_init_dead = true`，残留恒 0。
- 对照组残留恒为 6 = 守护进程 + setsid 子进程存活（2）+ 端口仍开（1）+ 三个临时文件（3）；T+10s 不自愈。**"只杀主进程"在三种模式下全部留下完整脱缰负载**——这是本批对运行时设计最直接的一条 [SELF] 证据：终止必须是单元语义，进程语义无效。

### 判定：**通过**

### 失败与近失记录（完整披露）

- **batch-1 无效**：驱动从 ns 内 `/proc/self/status` 读 init 宿主 PID，读到的是 grep 工具自身的 PID；另有负载 pid 文件竞态（12/60 轮未就绪）与驱动误删数据目录伪影。残留约 60 进程已按精确命令行清理。
- **batch-2 无效 + 近失事件**：ns 内对 `/proc/$$/status` 的 awk 解析落到宿主运行时 systemd，驱动记录 `init_hostpid = 1` 并据此发送了单 PID 的 SIGKILL。**宿主 systemd 未受影响**——内核对 PID namespace init 的信号保护在此起了作用，且全部 kill 均为单 PID 定向、无其他进程被误号。此事按近失（near-miss）登记：机制是侥幸而非设计，修复后不再可能复现（见下）。
- **batch-3 崩溃**：新安全断言在"正常结束"模式下误杀已自然退出的主进程检查（把"主进程已死"判为不安全），驱动在第 0 轮断言退出，无数据产出（日志保留）。
- **修复（batch-4 即有效批）**：init 宿主 PID 改由驱动在宿主侧以"负载主进程的 ppid"推导；pid 文件原子写（tmp+rename）+ 解析重试；守护心跳异常吞没；**任何 kill 前强制断言**：拒绝 pid ≤ 10、init 命令行必须含 `sleep infinity`、对照组主进程命令行必须含 `exp02_workload.py`、主进程已死则登记跳过。修复后先以单轮冒烟验证全路径，再跑满 60 轮。

**复现**：`python3 hidden_files/lab/scripts/exp02_run.py`

## 3. EXP-03 网络矩阵 + Q29 配方验证（C8 子集 + ST-5）

**假设**：OpenSandbox 式 deny 配方（默认拒绝出站 + 显式 deny 元数据/内网 + 仅放行白名单与受控 DNS）在本载体上能让全部 deny 用例被 DROP、allow 用例连通。

### 3.1 载体探针：宿主 runtime 的四层网络干预 [SELF]

原设计（双 netns + veth）经三批实测不可行（`raw/exp03-batch1/2/3-invalid.json`），探明干预层级：

1. **系统调用层拦截**：目标为 RFC1918/链路本地地址的 connect()/sendto() **立即返回 EPERM**（宿主 shell、新建 user+net ns 内、单 ns 内均复现），先于一切 nft 规则——该环境自带 SSRF 式出口过滤，本实验的 deny 结果若用真实私网/元数据地址将不可归因于配方。
2. **子 netns 数据面限制**：veth 双端 LOWER_UP、路由完整、`ip route get` 正常，跨 ns 流量仍 ENETUNREACH 且邻居表为空；lo 上非 127 地址、veth 本地地址同样 ENETUNREACH。子 ns 内实际可达的只有 **TCP → 127/8**。
3. **UDP 全面封锁**：sendto 对任何目标（含 127.0.0.1 任意端口）EPERM。DNS-over-UDP 在本载体不可用。
4. **nft conntrack 不可用**：任何 `ct state` 规则返回 ENOENT（独立复现）；配方须以无状态回复规则替代（见偏离 3）。

### 3.2 最终载体与明示偏离（预注册附录 #2/#3，判据未动）

单个子 netns 内以 lo 的 127/8 别名作全部端点，逐目标 allow/deny 与默认拒绝结构与冻结配方 1:1：`127.0.0.10` 白名单目标 / `.11` 非白名单公网 / `.254` 模拟元数据 / `.2` 模拟内网服务 / `.53` 受控解析器 / `.54` 非指定解析器。偏离清单：

| # | 偏离 | 原因 |
|---|---|---|
| 1 | 端点地址为 127/8 替身，非真实 169.254/私网/公网地址 | §3.1 第 1、2 条；字面生产 deny 行仍保留在规则集中，但**未被流量检验**，不 claimed |
| 2 | DNS 走 TCP/53（配方 tcp 行），udp 行未测 | §3.1 第 3 条 |
| 3 | 回复流量以 (saddr, sport) 无状态规则放行替代 `ct state established` | §3.1 第 4 条；全部 (saddr,sport) 对已被哨兵绑定占用，工作负载进程在本载体内无法冒充源 |
| 4 | 配方去掉 `oif lo accept` 豁免行 | 本载体中 lo 是唯一"线路"，保留该行将使任何目标规则都无法被检验 |

deny 判定签名：连接须以**超时**失败（dt ≥ 2.0 s，DROP 特征）；若为瞬时错误（EPERM 等），说明有更前置的干预层先行触发，该用例不计配方证据。

**原始数据**：`raw/exp03.json`（有效批）；失败迭代 `raw/exp03-batch4-nftfail.json`（ct 规则加载失败的完整记录）、`raw/exp03-batch5-nftsyntax.json`（nft 语法修正前的记录）。

### 3.3 结果 [SELF]

对照组（无配方）先证哨兵可达，否则 deny 无效——**4/4 全通**：非白名单 `CANARY-NONWL`、模拟元数据 `CANARY-METADATA`、模拟内网 `CANARY-INTERNAL`、非指定解析器 DNS 应答，均实际取得。

实验组（加载配方）9 用例：

| 用例 | 期望 | 实测 [SELF] | 判定 |
|---|---|---|---|
| U1 白名单 allow | 连通 `CANARY-PUBLIC` | 200，内容一致 | ✅ |
| U2 非白名单 deny | DROP | TimeoutError，dt=2.5 s | ✅ |
| U3 模拟元数据 deny | DROP | TimeoutError，dt=2.5 s | ✅ |
| U4 模拟内网 deny | DROP | TimeoutError，dt=2.5 s | ✅ |
| U5 DNS 直出非指定解析器 deny | DROP | TimeoutError，dt=2.5 s | ✅ |
| U6 指定 DNS allow | 解析得 127.0.0.10 | 应答一致 | ✅ |
| U7 白名单 302 跳转模拟元数据 deny | 第二跳 DROP | 第二跳 TimeoutError，未取得 CANARY-METADATA | ✅ |
| U8 DNS 重绑定（首答白名单、再答元数据） | 首访通、再访 DROP | get1=`CANARY-PUBLIC`；get2 TimeoutError dt=2.5 s | ✅ |
| U9 IPv6 元数据（fd00:ec2::254） | deny 或 N/A | connect 瞬时 PermissionError（dt=0.0）——宿主 runtime 干预先行触发，非配方证据 | **N/A**（原因：v6 非回环目标在本载体不可达，§3.1 第 1/2 条） |

U8 的机制读数：配方的防线在**连接目标**而非解析结果——同一域名第二次解析返回元数据替身地址后，连接仍被默认拒绝+Deny 行拦下；仅靠"解析时校验"挡不住重绑定，靠目标侧 deny 可以（限本载体策略逻辑范围）。

### 判定：**载体内通过（部分）**

C8 冻结线"deny 全过才算轨合格"——在本载体可检验的 8 个用例（U1–U8）中 deny 类 6/6、allow 类 2/2 全过，网络轨在**策略逻辑层**合格；但拓扑层（真实地址段、UDP DNS、conntrack 状态防火墙、lo 豁免）全部未被本载体检验，U9 为 N/A。整体按"部分"登记，拓扑级 C8 结论顺延 LAB-REF。

**复现**：`python3 hidden_files/lab/scripts/exp03_run.py`（规则集 `scripts/exp03_rules.nft`）

## 4. EXP-04 ST-1/ST-2/ST-4 冒烟（LAB-MINI）

**假设**：namespace 单元载体能以冻结成功判据完成三套冒烟：ST-1 创建→探针→销毁；ST-2 固定计算脚本输出哈希与宿主基线一致；ST-4 文件集打包哈希可复算校验。n=30，按 09 统计口径只报 P50/max。

**原始数据**：`raw/exp04.json`（含每轮耗时数组与证据）。

### 结果 [SELF]

| 套件 | n | P50 | max | 失败 | 残留单元 | 成功判据证据 |
|---|---|---|---|---|---|---|
| ST-1 探针 | 30 | 60.8 ms | 106.7 ms | 0 | 0 | 探针串 `LABMINI-PROBE-OK`、单元内 PID=1 |
| ST-2 计算 | 30 | 748.3 ms | 802.2 ms | 0 | 0 | 输出哈希 `4924359c…62f2` 与宿主基线**逐字一致**（fib(25)=75025） |
| ST-4 文件 | 30 | 456.6 ms | 621.7 ms | 0 | 0 | 打包清单哈希由 tar 内容复算一致 |

耗时为"单元启动→工作负载退出"全程（含 bash+python 进程树启动），ST-2 的 ~0.75 s 主要是解释器启动与 30 轮迭代纯 Python fib 的实算时间，**不是**沙盒创建开销的纯净读数；且按全局限制不可外推。ST-3/ST-6 按 09 冻结决定本批不测（Windows/大镜像），未动。

### 判定：**通过**（冒烟级；非性能基线）

**复现**：`python3 hidden_files/lab/scripts/exp04_run.py`

## 5. Q32 / Q34 登记

按 09 §5 冻结处置执行：Q32、Q34 仅限 LAB-REF（真实 KVM 宿主）验证，本批**只登记不取数**——未跑、未估算、无结论，待 LAB-REF 批次处理。OPEN-QUESTIONS 中两问的状态以本登记为准，不另行改写结论。

## 6. 实验后宿主清理验证 [SELF]

全部实验结束后逐项复核（2026-10-27 执行）：

| 检查项 | 结果 |
|---|---|
| 实验进程（workload/sentinel/suites，按精确路径匹配） | 0 |
| `sleep infinity` 单元 init 残留 | 0 |
| 宿主侧 veth 设备 | 0 |
| `ip netns list` | 空 |
| systemd 瞬态 lab 单元 | 0 |
| 实验端口（233xx、18080）监听 | 0 |
| 宿主 IPC | 仅原有 semid 0（实验泄漏的 semid 1 已在 EXP-01 后移除） |
| 可见 cgroup 根 | 无自建子目录残留（探针目录已删） |
| /tmp 实验目录（lab-exp02/03/04、调试脚本） | 已删除 |

## 7. 本批结论汇总

| 实验 | 判定 | 一句话 |
|---|---|---|
| EXP-01(a) namespace | 通过 | 六类 ns 视图隔离 11 项检查全过 [SELF] |
| EXP-01(b) cgroup 配额 C1/C2/C3 | 环境不具备 | 控制器未委派 + 瞬态单元不执行，判定顺延 LAB-REF；RLIMIT 替代探针仅作机制参考 |
| EXP-01(c) seccomp | 通过 | mount 被 EPERM 拦截、其余功能完好、对照组可挂载 |
| EXP-02 C4+C7 | 通过 | 单元级终止 30/30 零残留；只杀主进程 30/30 留全套脱缰残留（恒 6） |
| EXP-03 C8 子集/ST-5 | 载体内通过（部分） | 策略逻辑层 U1–U8 全过、对照 4/4；U9 N/A；拓扑级结论顺延 LAB-REF |
| EXP-04 ST-1/2/4 | 通过（冒烟） | n=30 零失败零残留，哈希判据全合；耗时不可外推 |

过程完整性说明：本批共产生 9 份无效/失败批次记录（EXP-01 ×1、EXP-02 ×3、EXP-03 ×5，其中 EXP-03 为三批拓扑无效 + 两批规则加载失败），全部保留在 `raw/` 并在上文逐批登记原因；有效批均为修复后的完整重跑，无挑数。
