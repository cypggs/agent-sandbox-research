# 18 · 实验室手册（LAB-MINI 规程 · LAB-REF 顺延规程 · 数据索引）

> 项目：Agent Sandbox 全领域技术研究（goal_a756da9ace9a）
> 手册版本：v1.1（2026-10-28 重写版，见文末勘误说明）
> 判据来源：`files/09-BENCHMARK-FREEZE-v1.md`（冻结 v1.0，未改动）
> 第一批执行报告：`files/10-LAB-BATCH1-REPORT.md`（207 行）
> 资产：脚本 `hidden_files/lab/scripts/`（12 个）、原始数据 `hidden_files/lab/raw/`（16 个）

## 1. 手册定位与证据纪律

本手册是本项目实验室部分的唯一操作规程：已执行实验的复现规程、
未执行实验的预置规程、环境分级、安全护栏与原始数据索引都在此登记。
它不是实验报告——判定结论只出现在实验报告（如 10 号）中，
手册只负责让任何一次实验可被原样重跑、可被逐项核对。

证据纪律（全项目通用，实验室部分尤其严格）：

- 本手册与实验报告中的自测数字一律标 **[SELF]**，
  口径为「本机、本载体、本批次实测」，与官方公布值
  [OFFICIAL]、第三方数据 [THIRD-PARTY]、估算 [ESTIMATE] 严格分开，
  不得混引、不得互相冒充。
- **冻结线先行**：所有通过/不通过判定只许引用
  `09-BENCHMARK-FREEZE-v1.md` 已冻结的判据编号（C1–C8、ST v1.0、
  统计口径、D5 画像）。冻结后改线必须升版并记录原因，
  已按旧版判定的结果不回溯改判；测后改线 = 该批数据作废。
- **预注册先行**：每批实验执行前先写预注册
  （如第一批的 `hidden_files/lab/PREREG-batch1.md`），
  载体变更以附录形式先于或同步于对应实验登记，不许事后补写。
- **原始数据全留档**：有效批、无效批、失败批、崩溃日志一律保留在
  `raw/` 并在报告中逐批登记原因；禁止挑数、禁止删除异常值、
  禁止用重试掩盖失败（统计口径见 09 §2）。
- **载体偏离明示**：实验载体与冻结规格不一致时（如 EXP-03 的
  127/8 替身端点），偏离必须逐条登记，且未被流量/实测检验的部分
  不得 claimed 为已验证。
- 宿主是云端沙盒 VM（嵌套环境）：一切绝对性能数字仅对本载体成立，
  **禁止外推**至裸机/生产环境，禁止用 LAB-MINI 数据做产品性能排名
  （09 §0 冻结）。

## 2. 环境分级

### 2.1 LAB-MINI（已实测指纹，逐项回指 10 号报告 §0/§3.1）

| 项 | 实测指纹 [SELF] | 出处 |
|---|---|---|
| 规格 | 2 vCPU / 约 7.9 GiB 内存 / x86_64 | 10 §0、09 §0 |
| 内核 | Linux 7.0.0-39-generic | 10 §0 |
| 身份 | root；宿主本身是云端沙盒 VM（嵌套环境） | 10 §0 |
| /dev/kvm | **无**——一切 MicroVM/快照类实验对象在此不存在 | 10 §0、§5 |
| Docker / 容器运行时 | **无** | 10 §0 |
| cgroup v2 | 根可见，但**控制器未委派**：根 `cgroup.controllers` 为空、新建子组无 `cpu.max`/`memory.max`/`pids.max`、向任何 `cgroup.subtree_control` 写 `+cpu` 返回 ENOENT | 10 §0 表 #1 |
| systemd 瞬态单元 | 只记录属性、**不执行**配额：`CPUQuota=50%/20%` 下 3 s 忙循环实耗 CPU 3.02/3.03 s；`TasksMax=16` 下成功派生 80 个子进程；`MemoryMax=64M` 下 Python 增长至约 3.1 GiB 未被杀 | 10 §0 表 #2 |
| netns 操作 | `ip netns add`、`nsenter -t <pid> -n` 均 Operation not permitted；`unshare -n` 可用、按 PID 移交 veth 端点可用 | 10 §0 表 #3 |
| 宿主 runtime 网络干预 ① | 系统调用层拦截：目标为 RFC1918/链路本地地址的 connect()/sendto() 立即返回 EPERM，先于一切 nft 规则 | 10 §3.1 第 1 条 |
| 宿主 runtime 网络干预 ② | 子 netns 数据面限制：veth/路由/邻居表均正常时跨 ns 仍 ENETUNREACH；子 ns 内实际可达的只有 **TCP → 127/8** | 10 §3.1 第 2 条 |
| 宿主 runtime 网络干预 ③ | UDP 全面封锁：sendto 对任何目标（含 127.0.0.1 任意端口）EPERM，DNS-over-UDP 不可用 | 10 §3.1 第 3 条 |
| 宿主 runtime 网络干预 ④ | nft conntrack 不可用：任何 `ct state` 规则返回 ENOENT，配方须以无状态回复规则替代 | 10 §3.1 第 4 条 |

**LAB-MINI 可用面**（已实测可跑）：

- namespace 视图隔离探针（`unshare -Urmpfni` 六类 ns）
- seccomp 系统调用过滤探针（C 探针，prctl+seccomp）
- PID namespace 单元级整体终止（超时清零类实验）
- RLIMIT 替代探针（仅作机制参考，不构成 cgroup 判据的判定）
- 单子 netns + lo 上 127/8 替身端点的网络**策略逻辑**矩阵
- ST-1/ST-2/ST-4 冒烟（namespace 单元载体）

**LAB-MINI 禁用面**（环境不具备，强行取数即伪造数据）：

- cgroup 配额判定（C1/C2/C3 的 cgroup 形式）——控制器未委派
- 以 systemd 瞬态单元充当配额执行体——只记属性不执行
- KVM/MicroVM 启动、快照与恢复（C6/Q32/Q34 的对象）——无 /dev/kvm
- 容器运行时类实验（ST-3 的一部分）——无 Docker
- 拓扑级网络验证：真实 169.254/RFC1918 地址段、跨 netns 数据面、
  UDP DNS、conntrack 状态防火墙——被宿主 runtime 干预封死
- 任何产品性能排名与绝对性能基线——冻结明令禁止

### 2.2 LAB-REF（规格建议与获取条件，Q36）

状态：**未获取**。LAB-REF 是 C1/C2/C3 配额判定、C6 快照一致性
（含 Q32 熵分化）、C8 拓扑级验证（含 Q29 真实地址段部分）与
Q34（62 s 分段拆账）的**共同前置**，是当前全项目唯一的硬环境瓶颈
（OPEN-QUESTIONS Q36）。

建议规格（研究侧建议，非采购决定）：

- x86_64，VT-x/AMD-V 且 /dev/kvm 对来宾可见
  （裸金属，或开启嵌套虚拟化的云实例）
- ≥4 vCPU（跑 K8s+Fast+Firecracker 建议 8 vCPU）
- ≥16 GiB RAM（建议 32 GiB）
- ≥100 GiB 磁盘
- 主流 Linux 发行版：内核 ≥5.10、cgroup v2 且可委派
  subtree_control、root 可用
- 可加载 nft/veth 等网络设施、无宿主侧 connect 拦截

可选来源（仅列选项与边界）：① 云厂商裸金属/嵌套虚拟化实例
（按需计费、用后释放）；② 用户自有/新购本地小主机常驻；
③ 既有测试集群等资源借用。

事实边界（防误选，Q36 已登记）：用户既有 AWS t3.small 无嵌套
虚拟化且规格不足，不能充当 LAB-REF；用户本地 MacBook Pro
（M5 Max，Apple Silicon + macOS）没有 Linux KVM，不能充当
LAB-REF。**是否采购、何时采购由用户决定，本项目不替用户拍板。**

## 3. 安全护栏

### 3.1 哨兵 / canary 原则

- 一切网络与隔离实验的对端只能是**自有哨兵**：自建的哨兵服务、
  canary 固定字符串（如 `CANARY-PUBLIC`、`CANARY-METADATA`）、
  自有地址段替身。禁止对任何第三方地址、真实云厂商元数据服务
  或他人系统发探测流量。
- 实验只在自建/授权环境执行，只用无害负载
  （固定字符串、固定哈希计算、心跳写文件）。
- 对照组先行：任何 deny 结论之前，必须先以对照组证明哨兵可达，
  否则 deny 无效（EXP-03 对照组 4/4 全通后才计实验组证据）。
- deny 判定签名须可归因：如 EXP-03 要求连接以**超时**失败
  （DROP 特征）；瞬时错误（EPERM 等）说明有更前置的干预层先行
  触发，该用例不计配方证据（U9 即按此判 N/A）。

### 3.2 kill 前强制断言（五条）与 EXP-02 近失事件

任何向进程发送终止信号的实验驱动，kill 前必须逐条断言
（源自 EXP-02 batch-4 修复，10 号报告 §2）：

1. **拒绝 pid ≤ 10**：目标 PID 小于等于 10 一律拒绝发送信号。
2. **PID 来源必须是宿主侧推导**：目标宿主 PID 只能由驱动在宿主侧
   以「负载主进程的 ppid」推导；禁止从 namespace 内部读
   `/proc/self/status`、`/proc/$$/status` 解析宿主 PID
   （ns 内外 PID 混用是近失事件的根因）。
3. **init 身份校验**：单元 init 的命令行必须含 `sleep infinity`，
   不符即拒绝。
4. **负载身份校验**：对照组主进程命令行必须含
   `exp02_workload.py`，不符即拒绝。
5. **已死则跳过**：主进程已自然退出时登记跳过并继续，
   不得把「主进程已死」判为不安全而误杀、也不得对已死 PID
   发送信号（batch-3 正是断言误判导致驱动崩溃，无数据产出）。

**近失事件（EXP-02 batch-2，完整披露于 10 号报告 §2）**：
驱动在 ns 内对 `/proc/$$/status` 的 awk 解析落到宿主运行时
systemd，记录 `init_hostpid = 1` 并据此向 **PID 1** 发送了单 PID
的 SIGKILL。宿主 systemd 未受影响——靠的是内核对 PID namespace
init 的信号保护；全部 kill 均为单 PID 定向、无其他进程被误杀。
定性：**机制是侥幸而非设计**。护栏（上列五条）落地后先以单轮
冒烟验证全路径，再跑满 60 轮，60/60 验证根除。此教训已同步
记入项目工作规范：杀进程类实验脚本必须带护栏，kill 前强制断言
（拒绝 pid≤10、校验目标命令行、宿主侧 ppid 推导）。

同批其他失败（均留档，见 §6 索引）：batch-1 驱动读到 grep 工具
自身 PID、负载 pid 文件竞态、误删数据目录伪影，残留约 60 进程
已按精确命令行清理；EXP-01 attempt-1 漏传 unshare `-i` 导致
IPC 未隔离、一个 SysV 信号量泄漏到宿主（semid 1，已 `ipcrm`
移除，宿主原有 semid 0 未动）。

### 3.3 云额度纪律（E2B 教训）

- 调试/测试脚本直接调云 SDK 创建的 sandbox **不受**平台 idle
  reaper 管理（reaper 只管平台登记在册的实例）：2026-10-07 曾
  发现 43 台历史调试脚本创建的 E2B sandbox 在跑空转，一键全杀。
- 规则：任何脚本创建云 sandbox 后必须
  `finally { await sbx.kill() }`；能复用就复用，不要每次新建；
  定期以 `Sandbox.list()` 检查 running 数量，异常增长立刻排查。
- **现行状态**：openmuse 项目已暂停，总开关
  `OPENMUSE_SANDBOX_DISABLED=1` 在案，**禁止新建任何 E2B
  sandbox**；E2B 深研全程为纯静态源码分析，不调云 API。
  本手册任何规程都不得被解读为授权创建云端 sandbox。

### 3.4 冻结 / 预注册纪律

- 阈值先冻结后执行（09 v1.0）；测后改线 = 数据作废；
  改线须升版记原因、旧判定不回溯改判。
- 每批实验先预注册（假设、载体、轮次、判定线指针），
  载体变更走预注册附录（如第一批附录 #1–#3），先于或同步于
  对应实验登记。
- 无效批次全留档并登记原因，不挑数、不删异常值、
  失败样本不进分位但必入失败率且不重试掩盖（09 §2）。
- 实验后必须做宿主清理验证并留记录（清单见 10 号报告 §6：
  实验进程/单元 init 残留/veth/netns/瞬态单元/监听端口/
  宿主 IPC/cgroup 自建目录//tmp 实验目录，逐项复核为零）。

## 4. 第一批实验规程（EXP-01 – EXP-04，已执行）

### 4.1 EXP-01 隔离探针（01a / 01b / 01c）

- **目的**：验证 LAB-MINI 载体上 namespace 视图隔离、cgroup 配额
  前提、seccomp 过滤三者的可证性（10 号报告 §1）。
- **环境**：LAB-MINI。
- **脚本**：`scripts/exp01_run.py`（驱动）、
  `scripts/exp01a_namespaces.py`、`scripts/exp01bc_probes.py`、
  `scripts/exp01c_seccomp.c`；数据 `raw/exp01.json`（有效批）、
  `raw/exp01-attempt1-invalid.json`（无效批）。
- **复现命令**：`python3 hidden_files/lab/scripts/exp01_run.py`

**EXP-01a namespace 视图隔离**

- 步骤要点：`unshare -Urmpfni`（user/mount/pid/net/ipc/uts）
  内侧与宿主侧逐项核验 11 项——内部 PID、UTS 改名、
  NET 接口集、MNT tmpfs 宿主不可见、IPC 私有信号量、
  六类 ns inode 与宿主全不同；cgroup/time ns 按设计未
  unshare、相同不计失败。
- 已得结果（10 §1(a)）：**通过** [SELF]。11 项检查全过：
  内部 PID=1（宿主侧同进程 4915）；内侧改 hostname 为
  `exp01a-canary-host`、宿主仍 `htch-runtime`；内侧接口仅 lo；
  内侧 tmpfs 挂载成功且宿主挂载表不可见；IPC 私有信号量
  创建成功；六个 ns inode 逐项与宿主不同。
- 判定线：本项为机制探针，无冻结 C 编号判据，
  以 11 项逐项核验全过为通过（预注册口径）。

**EXP-01b cgroup v2 配额（C1/C2/C3）**

- 步骤要点（原设计）：在可委派 cgroup v2 子组上设
  `cpu.max`/`memory.max`/`pids.max`，按 C1/C2/C3 判据取数。
- **判定形态：「环境不具备」**（非通过、非失败）：载体前提
  已被 §0 探针证伪——控制器集合为空、配额文件不存在、
  subtree_control 写入 ENOENT；systemd 瞬态单元三探针
  （CPU/Tasks/Memory）全部只记属性不执行。在此环境下任何
  「C1 误差 x%」数字都将是伪造，故按预注册登记
  **环境不具备**，C1/C2/C3 的 cgroup 判定整体顺延 LAB-REF
  （顺延规程见 §5.1）。
- 替代探针（RLIMIT，仅机制参考、**不是** C1/C2/C3 判定）
  [SELF]：RLIMIT_CPU=2 s 忙循环被 SIGXCPU 终止于 CPU
  1.999 s（相对误差 0.04%）；RLIMIT_AS=256 MiB 增长止于
  232 MiB 分配（AS 语义为分配失败而非击杀，与 C2 的
  cgroup 语义不可互换）；邻居哨兵退化 11.15%（n=1、噪声大，
  不构成任何隔离判定）。
- 判定线指针：09 §1 的 C1/C2/C3（LAB-REF 执行时原样适用）。

**EXP-01c seccomp 过滤**

- 步骤要点：C 探针以 prctl+seccomp 安装过滤（阻断
  mount/umount2/reboot/init_module/delete_module/
  finit_module 并返回 EPERM），过滤组尝试 mount 并核验
  其余功能（getpid/文件 IO/socket）；对照组在私有 mount
  ns 无过滤下尝试 mount。
- 已得结果（10 §1(c)）：**通过** [SELF]。过滤组 mount
  返回 `rc=-1 errno=1 (EPERM)` 未挂载、其余功能全部正常；
  对照组 `rc=0` 挂载成功。
- 失败记录：attempt-1 无效——驱动漏传 unshare `-i`、
  IPC 从未隔离且信号量泄漏宿主（已移除）；同批
  python/ctypes 装 seccomp 失败，已换 C 探针。无效批
  数据保留标注，未混入结论。

### 4.2 EXP-02 超时清零（C4 + C7）

- **目的**：验证「单元整体销毁」终止失控负载后残留为 0，
  并以「只杀主进程」作对照证明进程语义终止无效（10 §2）。
- **环境**：LAB-MINI。载体经预注册附录 #1 变更：实验组终止
  手段由 `cgroup.kill` 改为 **PID namespace 整体拆除**
  （SIGKILL ns init，内核回收全 ns 进程）——与 cgroup.kill
  同为「单元级全量终止」语义；对照组为只杀主进程。
- **负载**：双 fork 脱缰 + setsid 后台守护 + 心跳写文件 +
  监听本地端口（233xx 段），见 `scripts/exp02_workload.py`。
- **步骤要点**：三种终止模式（超时 kill / 主动取消 /
  正常结束）× 两组 × 10 轮 = 60 轮；每轮在 T+2 s 与
  T+10 s 两时点由宿主侧枚举进程、监听端口、临时文件残留；
  kill 前执行 §3.2 五条断言；init 宿主 PID 由宿主侧 ppid
  推导；pid 文件原子写（tmp+rename）+ 解析重试。
- **判定线**：09 §1 的 C4——残留 = 0 为唯一通过线，
  任一轮任一时点残留 >0 即不通过；C7 清单与 C4 共用
  检查脚本。
- **已得结果（10 §2）**：**通过** [SELF]。实验组 30/30 轮
  两时点残留恒 0（`destroy_confirmed_init_dead = true`）；
  对照组 30/30 轮残留恒 6（守护+setsid 子进程存活 2 +
  端口仍开 1 + 临时文件 3），T+10 s 不自愈。
- **脚本/数据**：`scripts/exp02_run.py`、`scripts/exp02_workload.py`；
  `raw/exp02_results.jsonl`（有效批 60/60 轮）、
  `raw/exp02_driver.log`（有效批驱动日志），无效批与
  近失记录见 §3.2 与 §6 索引。
- **复现命令**：`python3 hidden_files/lab/scripts/exp02_run.py`

### 4.3 EXP-03 网络矩阵 + Q29 配方验证（C8 子集 + ST-5）

- **目的**：验证 OpenSandbox 式 deny 配方（默认拒绝出站 +
  显式 deny 元数据/内网 + 仅放行白名单与受控 DNS）在
  本载体上能让全部 deny 用例被 DROP、allow 用例连通
  （10 §3）。
- **环境**：LAB-MINI。原设计（双 netns + veth）经三批实测
  不可行（§2.1 网络干预四层），最终载体经预注册附录
  #2/#3 变更为：单个子 netns 内以 lo 的 127/8 别名作全部
  端点，逐目标 allow/deny 与默认拒绝结构与冻结配方 1:1。
- **端点映射**：`127.0.0.10` 白名单目标 / `.11` 非白名单公网 /
  `.254` 模拟元数据 / `.2` 模拟内网服务 / `.53` 受控解析器 /
  `.54` 非指定解析器。
- **载体偏离四条（如实登记，判据未动）**：
  1. 端点地址为 127/8 替身，非真实 169.254/私网/公网地址
     （因干预 ①②）；字面生产 deny 行仍保留在规则集中，
     但**未被流量检验**，不 claimed。
  2. DNS 走 TCP/53（配方 tcp 行），udp 行未测（因干预 ③）。
  3. 回复流量以 (saddr, sport) 无状态规则放行替代
     `ct state established`（因干预 ④）；全部 (saddr,sport)
     对已被哨兵绑定占用，工作负载进程在本载体内无法冒充源。
  4. 配方去掉 `oif lo accept` 豁免行：本载体中 lo 是唯一
     「线路」，保留该行将使任何目标规则都无法被检验。
- **步骤要点**：先跑对照组（无配方）证明哨兵可达；
  再加载配方（`scripts/exp03_rules.nft`）跑 U1–U9 九用例；
  deny 判定签名为连接以超时失败（dt ≥ 2.0 s，DROP 特征），
  瞬时错误不计配方证据。
- **判定线**：09 §1 的 C8——任一 deny 用例失败 = 该系统
  网络轨不合格；allow 用例通过率 ≥95% 且失败逐个归因；
  矩阵 v1 九类用例（公网白名单/非白名单/内网哨兵/
  元数据 v4/元数据 v6/DNS 直出/DoH/重定向跳内网/重绑定）。
- **已得结果（10 §3.3）**：**载体内通过（部分）** [SELF]。
  对照组 4/4 全通；实验组可检验的 8 用例（U1–U8）中
  deny 类 6/6、allow 类 2/2 全过（含 302 跳转第二跳 DROP、
  DNS 重绑定再访 DROP——防线在连接目标而非解析结果）；
  U9（IPv6 元数据 fd00:ec2::254）为 **N/A**（宿主干预先行
  触发，非配方证据）。拓扑层（真实地址段、UDP DNS、
  conntrack 状态防火墙、lo 豁免）全部未被本载体检验，
  拓扑级 C8 结论顺延 LAB-REF（§5.4）。
- **脚本/数据**：`scripts/exp03_run.py`、`scripts/exp03_sentinel.py`、
  `scripts/exp03_client.py`、`scripts/exp03_rules.nft`；
  `raw/exp03.json`（有效批）+ 五份无效/失败批（见 §6）。
- **复现命令**：`python3 hidden_files/lab/scripts/exp03_run.py`

### 4.4 EXP-04 ST-1/ST-2/ST-4 冒烟

- **目的**：以冻结成功判据验证 namespace 单元载体能完成
  三套标准任务冒烟（10 §4）。
- **环境**：LAB-MINI，载体为 namespace 单元
  （unshare user/mount/pid/uts/ipc/net）；n=30，
  按 09 统计口径只报 P50/max。
- **步骤要点**：ST-1 创建单元 → 运行探针（固定字符串 +
  自身资源视图）→ 销毁；ST-2 跑固定 Python 脚本
  （SHA-256 迭代 1,000,000 次 + 斐波那契递归基准段，
  脚本哈希登记）；ST-4 生成 1,000 个 × 4 KiB 文件 →
  全量读回校验 → tar 打包。耗时为「单元启动 → 工作负载
  退出」全程（含 bash+python 进程树启动），非沙盒创建
  开销的纯净读数。
- **判定线**：09 §4 的 ST-1/ST-2/ST-4 成功判据——
  ST-1 探针输出匹配 + C7 清单全清；ST-2 输出哈希与
  基准值一致；ST-4 打包文件 SHA-256 与清单一致。
- **已得结果（10 §4）**：**通过（冒烟级；非性能基线）**
  [SELF]。三套件 n=30 零失败、零残留单元：
  ST-1 P50 60.8 ms / max 106.7 ms（探针串
  `LABMINI-PROBE-OK`、单元内 PID=1）；
  ST-2 P50 748.3 ms / max 802.2 ms（输出哈希
  `4924359c…62f2` 与宿主基线逐字一致，fib(25)=75025）；
  ST-4 P50 456.6 ms / max 621.7 ms（打包清单哈希由
  tar 内容复算一致）。耗时禁止外推。
- **脚本/数据**：`scripts/exp04_run.py`、`scripts/exp04_suites.py`；
  `raw/exp04.json`（每轮耗时数组与证据）。
- **复现命令**：`python3 hidden_files/lab/scripts/exp04_run.py`
- 注：ST-3/ST-6 按 09 冻结决定本批不测，顺延规程见 §5.5/§5.6。

## 5. 顺延实验清单（8 项，全部待 LAB-REF 或指定前置）

以下各项目前**未执行、无数据、无结论**；规程要点为预置设计，
执行时须先按 §3.4 写预注册，前置不具备时只登记不取数
（第一批对 Q32/Q34 即如此处置，10 号报告 §5）。

### 5.1 C1 / C2 / C3 cgroup 配额判定

- **前置条件**：LAB-REF（cgroup v2 控制器可委派：
  subtree_control 可写、子组有 cpu.max/memory.max/pids.max）。
- **规程要点**：在委派子组内分别执行——C1：10 s 忙循环
  按 cpu.max 口径测 CPU 占用，并测墙钟超时误差与邻居哨兵
  劣化；C2：内存按冻结步长 8 MiB/100 ms 增长，核验限制
  生效点、OOM 只杀超限方、终止后内存 100% 回收（出现
  宿主级 OOM 整例失败）；C3：fork 密集负载核验 pids 生效点
  误差，并以 cgroup.kill 在 5 s 内终止后核验清零。
- **判定线指针**：09 §1 的 C1（CPU 相对误差 ≤10%；
  墙钟超时误差 ≤ max(500 ms, 配额时长 5%)；邻居劣化
  ≤10%）、C2（三分项全过）、C3（生效点误差
  ≤ max(5%, 2 个进程)）。

### 5.2 C5 跨任务污染

- **前置条件**：一个存在「实例复用」的目标系统
  （自建平台部署于 LAB-REF，或经授权的真实产品环境）；
  LAB-MINI 无复用对象可测。
- **规程要点**：按 canary 清单 v1 五面逐项布设与回收检查——
  文件 / 进程 / 挂载 / 环境变量 / 缓存目录；任务 A 写入
  canary 后销毁/释放，任务 B 在复用到的同一实例上逐面
  探测残留。一次性不复用系统记「不适用-无复用」，不记满分。
- **判定线指针**：09 §1 的 C5——污染率 = 0 为通过线。

### 5.3 C6 快照一致性（含 Q32 熵分化）

- **前置条件**：LAB-REF（/dev/kvm 可见、Firecracker 类
  快照路径可跑）；Q32 子项另需自建 E2B 节点（Embed）。
- **规程要点**：自同一快照恢复两个实例，两个方向分项
  报告、禁止合并：①「应存活」校验集（文件/状态类）逐项
  核对；②「应分化」项（机器身份/密钥/随机性）核对同源
  两实例重复数。Q32 子项在自建 E2B 节点上同模板恢复
  两实例，对比 `/proc/sys/kernel/random/boot_id` 与
  熵池行为（无害自测，标 [SELF]）；机制层背景见
  12 号 Firecracker 深研（VMGenID 总是启用，但 E2B 恢复
  路径是否吃到该机制静态证据答不了，须实测）。
- **判定线指针**：09 §1 的 C6（「应存活」100% 通过、
  「应分化」同源两实例重复数 = 0）+ 09 §5 对 Q32 的
  冻结处置。

### 5.4 C8 拓扑级验证（含 Q29 配方实效）

- **前置条件**：LAB-REF（真实多 netns/veth 数据面、
  无宿主 connect 拦截、UDP 可用、nft conntrack 可用）；
  Q29 子项另需按官方 network-isolation 指南真实部署
  OpenSandbox（K8s）的自建测试集群。
- **规程要点**：以真实地址段重跑 C8 矩阵九类用例——
  169.254 元数据（v4 与 v6）、RFC1918 内网哨兵、
  UDP DNS 直出与 DoH、conntrack 状态防火墙、
  含 `oif lo accept` 豁免行的完整配方；Q29 子项把
  Pod/Service CIDR 写进 deny.always 并重打 sidecar 镜像
  后原样验证，并逐项核 04 号报告 §5 的软点（DNS 学习
  地址集对内网域名的放行、L1-only 降级、模式字符串
  非法降级 dns-only）。全部对端为自有哨兵，标 [SELF]。
- **判定线指针**：09 §1 的 C8（deny 任一失败 = 网络轨
  不合格；allow ≥95% 且失败逐个归因）。EXP-03 的载体内
  结论（§4.3）不替代本项拓扑级结论。

### 5.5 ST-3 工具链

- **前置条件**：LAB-REF 或镜像就绪（依赖源镜像化），
  且有容器运行时/等效执行载体；LAB-MINI 两者皆无。
- **规程要点**：固定小项目 pip 安装 + pytest（09 §4
  冻结规格），脚本与依赖版本哈希登记；成功判据为
  安装完成且测试套件按预期通过，耗时按 09 §2 统计
  口径报告。
- **判定线指针**：09 §4 的 ST-3（现状态：
  「冻结-待 LAB-REF/镜像就绪」）。

### 5.6 ST-6 浏览器

- **前置条件**：浏览器执行环境（LAB-REF 上的浏览器
  运行时，或后续 GUI 环境批次）；LAB-MINI 无浏览器环境。
- **规程要点**：按 09 §4 冻结的子轨定义执行浏览器
  任务冒烟（页面加载/脚本执行/截图类探针），与 C8
  网络矩阵共用自有哨兵页面，不访问第三方站点。
- **判定线指针**：09 §4 的 ST-6（子轨冻结定义，
  LAB-MINI 延后）。

### 5.7 B7 gVisor Systrap 性能自测

- **前置条件**：LAB-REF；在其上部署目标版本 gVisor，
  平台选 Systrap（官方现行材料未提供 Systrap 性能数字，
  ptrace 时代旧数字引用即误导——Q12 已以「官方未提供」
  结案，数字只能自测产生）。
- **规程要点**：按 Round 1 线 D 的 B7 指标设计，在
  目标版本/Systrap 上跑 syscall 密集与 IO 类负载，
  与同机原生容器基线同条件对照；按 09 §2 统计口径
  报五元组与批间波动，差异小于批间波动时写
  「当前测量精度下不可区分」。
- **判定线指针**：本项为数字生产型实验（无通过线），
  口径从 09 §2；背景与结案口径见 OPEN-QUESTIONS Q12。

### 5.8 Q34 OpenSandbox 62 s resume 分段拆账

- **前置条件**：LAB-REF，其上真实部署 OpenSandbox
  （K8s + Fast 路径）；LAB-MINI 无 /dev/kvm、无 Docker，
  部署前提不具备（10 号报告 §5）。
- **规程要点**：按 09 §5 已冻结的分段探针方案取数：
  t_submit / t_ack / t_ready 三点计时 + 缓存命中分层
  （本地缓存命中与跨节点全集拉取分开统计），对照双仓
  代码层候选环节（跨节点拉取、route generation 推进后
  客户端重解析、CR 状态投影与 SDK 轮询间隔、
  vault/policy import 前置）逐项归因。
- **判定线指针**：本项为归因型实验（无通过线）；
  冻结处置见 09 §5——本批只登记不取数、不许以本地
  实验冒充拆账。背景见 OPEN-QUESTIONS Q34。

## 6. 原始数据索引（raw/ 共 16 个，2026-10-28 以 ls 实点核对）

有效批 4 份、无/失败批与日志 12 份，全部保留，不挑数。

| # | 文件 | 内容说明 |
|---|---|---|
| 1 | `exp01.json` | EXP-01 有效批原始数据：01a 11 项核验、01b 探针与 RLIMIT 补充、01c 对照读数 |
| 2 | `exp01-attempt1-invalid.json` | EXP-01 attempt-1 无效批：漏传 unshare `-i`、IPC 未隔离批的原始读数 |
| 3 | `exp02_results.jsonl` | EXP-02 有效批（batch-4）：60/60 轮逐轮原始数据（两组 × 三模式 × 10 轮） |
| 4 | `exp02_driver.log` | EXP-02 有效批驱动日志：逐轮进度与分组汇总（残留 0） |
| 5 | `exp02-batch1-invalid.jsonl` | EXP-02 batch-1 无效批逐轮数据：驱动 PID 误读与 pid 文件竞态批 |
| 6 | `exp02-batch1-driver.log` | EXP-02 batch-1 驱动日志与汇总 |
| 7 | `exp02-batch2-invalid.jsonl` | EXP-02 batch-2 无效批逐轮数据：含 `init_hostpid = 1` 的近失批次记录 |
| 8 | `exp02-batch2-driver.log` | EXP-02 batch-2 驱动日志与汇总 |
| 9 | `exp02-batch3-crash.log` | EXP-02 batch-3 驱动断言误判崩溃的 traceback 日志（无数据产出） |
| 10 | `exp03.json` | EXP-03 有效批（v3 单 netns + 127/8 替身载体）：对照组与 U1–U9 全用例读数 |
| 11 | `exp03-batch1-invalid.json` | EXP-03 拓扑迭代批 1（无效）：双 netns/veth 原设计的失败读数 |
| 12 | `exp03-batch2-invalid.json` | EXP-03 拓扑迭代批 2（无效）：同上路线的第二批失败读数 |
| 13 | `exp03-batch3-invalid.json` | EXP-03 拓扑迭代批 3（无效）：同上路线的第三批失败读数 |
| 14 | `exp03-batch4-nftfail.json` | EXP-03 批 4：`ct state` 规则加载失败（ENOENT）的完整记录 |
| 15 | `exp03-batch5-nftsyntax.json` | EXP-03 批 5：nft 语法修正前的规则加载记录 |
| 16 | `exp04.json` | EXP-04 原始数据：ST-1/ST-2/ST-4 各 30 轮耗时数组、宿主基线与哈希证据 |

脚本索引（`scripts/` 共 12 个）：
`exp01_run.py`（EXP-01 驱动）、`exp01a_namespaces.py`、
`exp01bc_probes.py`、`exp01c_seccomp.c`、
`exp02_run.py`（EXP-02 驱动）、`exp02_workload.py`、
`exp03_run.py`（EXP-03 驱动）、`exp03_sentinel.py`、
`exp03_client.py`、`exp03_rules.nft`、
`exp04_run.py`（EXP-04 驱动）、`exp04_suites.py`。

## 7. 勘误说明（v1.1 重写缘由）

本手册 v1.0（2026-10-28 首版）落盘时被截断（72 行、
止于 EXP-01 步骤中途、文件内带字面截断标记），
顺延清单、数据索引与落款均未写入。本 v1.1 依据已验收
源材料（09 冻结文件、10 号报告全文、scripts/ 12 个、
raw/ 16 个，均已核尾部完整或 ls 实点）完整重写，
规程与数字与 10 号报告逐项对齐，未新增任何实验数据。
截断原件的处置与 13 号报告截断勘误同例：不静默覆盖，
在此明示。

---
手册版本 v1.1（2026-10-28 重写）· 尾部完整性已验：本行即全文最后一行。
