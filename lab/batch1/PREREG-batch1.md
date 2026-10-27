# PREREG · Round 4 实验室第一批（预注册，跑实验前冻结）

> 注册时间：2026-10-27（Asia/Shanghai，环境探查后、任何正式实验运行前）
> 判据来源：files/09-BENCHMARK-FREEZE-v1.md（冻结 v1.0，不可改线）；指标定义：round1-D §2.4 C1–C8、§1 T09–T12/T21
> 数据标签：本批全部数字标 [SELF]；宿主为云端沙盒 VM（嵌套环境），**绝对性能数字禁止外推、禁止产品排名**（09 §0 LAB-MINI）

## 0. 环境指纹与载体偏差（探查实测，均为 [SELF] 探查证据）

实测环境：root（userns 内，CapEff 含 SYS_ADMIN/NET_ADMIN）、2 vCPU、RAM 7.9 GiB、内核 7.0.0-39-generic、x86_64、无 /dev/kvm、无 Docker。与任务简报一致的部分：unshare 全 namespace 可用、ip/nft/iptables 二进制可用。

**重大偏差（决定载体替换，逐项附证据）**：简报称"cgroup v2 可用"，实测为**控制器未委派**：
1. 本进程 cgroup namespace 视图根的 `cgroup.controllers` 为空文件；任意层级新建子 cgroup 均无 cpu.max/memory.max/pids.max 文件。
2. 向任意层级 `cgroup.subtree_control` 写 `+cpu/+memory/+pids` 均失败（write error: No such file or directory）。
3. systemd transient scope 的属性可被记录（`systemctl show` 显示 CPUQuotaPerSecUSec=500ms / MemoryMax=268435456 / TasksMax=64），但**行为上全部不生效**（三次决定性探查）：
   - CPUQuota=50% 与 20% 下 3s 忙循环各得 cpu=3.02s / 3.03s（应为 ≈1.5s / 0.6s）；
   - MemoryMax=64M 下 python 以 8MiB/100ms 增长至 chunks=396 ≈ 3.1 GiB 未被杀（探查进程由实验员手动终止，宿主无损）；
   - TasksMax=16 下成功派生 80 个 sleep 子进程（应 ≈15 处被拒）。
4. `ip netns add/exec` 的 setns 路径被拒（Operation not permitted）；但 `unshare -n` 进入新 netns、按 PID 把 veth 移入 netns、在 netns 内直接运行 nft/ip 均可用。

**载体替换决定（实验前登记，不改冻结判据本身）**：
- 配额类（C1/C2/C3 的 cgroup 口径）：LAB-MINI **不具备执行条件**，本批按"环境不具备"登记并给出全部证据；另以 RLIMIT（RLIMIT_CPU / RLIMIT_AS）做**替代载体补充探针**，数据明确标注 `[SELF·替代载体-RLIMIT]`，**不冒充 C1/C2/C3 的 cgroup 判定**。
- 终止/清零类（C4/C7）：实验组终止手段由 cgroup.kill 替换为 **PID namespace 整体销毁**（杀 ns init → 内核回收全 ns 进程；与 cgroup.kill 同为"以单元为回收粒度"，差异：不含资源配额语义、依赖 init 死亡触发）。判定线仍按 09 冻结（残留=0）。
- ST 冒烟载体：namespace 单元（unshare 多 ns），与 09 §4 对 LAB-MINI 的载体定义一致；cgroup 部分缺失如实声明。
- EXP-03 网络：netns 对以 unshare 进程对 + veth 按 PID 移入构建，nft 在 client ns 内直接加载（已探查可用）。

## EXP-01 隔离探针

### (a) namespace 视图隔离
- 假设：unshare 新建 pid/uts/ipc/mnt/net/user 后，内部视图（PID 编号、hostname、IPC 对象、挂载、网络接口、各 ns inode）与宿主互不可见/互不相同。
- 判据：逐项二值核验（内部 PID 为小号且 ≠ 宿主侧 PID；uts 改名只影响内部；内部 `ip link` 仅 lo 且 DOWN→UP 由内部完成；/proc/self/ns/* inode 与宿主同进程对比全不同；mnt 内挂 tmpfs 不出现在宿主挂载表）。全过 = 通过。
- 步骤：宿主记录基线（自身 pid、hostname、ns inode 集、ip link、mount 表摘要）→ unshare 内运行探针脚本输出同项 → 逐项 diff。

### (b) cgroup 配额（C1/C2/C3）+ RLIMIT 替代探针
- 假设（原）：cgroup cpu.max=50%/memory.max=256MiB/pids.max=64 可在本环境实例化并按冻结线生效。
- 预注册处置：因 §0 证据，该假设的**前提已证伪**，本实验登记为「不具备执行条件」，证据链完整入报告；不做任何数字补位。
- 替代探针（补充，不构成 C1/C2/C3 判定）：
  - RLIMIT_CPU：子进程设 RLIMIT_CPU=2s 忙循环，记录实际被杀时刻的 CPU 时间与墙钟，误差对 2s 计算。
  - RLIMIT_AS：子进程设 RLIMIT_AS=256MiB，以 8MiB/100ms 增长（冻结步长），记录触发 MemoryError 时的累计分配量，误差对 256MiB 计算（注：AS 是虚拟地址空间口径，含解释器基线，与 RSS 口径差异须在报告声明）。
- 邻居哨兵：替代探针运行同期跑一个无限制忙循环进程，记录其 CPU 时间与单独基线对比（劣化参考 C1 的 ≤10% 口径，仅作替代载体参考）。

### (c) seccomp
- 假设：子进程经 prctl(PR_SET_NO_NEW_PRIVS)+PR_SET_SECCOMP 安装 BPF 过滤（拦截 mount/umount2/init_module/finit_module/delete_module/reboot，返回 EPERM）后，被拦 syscall 返回 EPERM、进程其余功能（文件读写、getpid、socket）正常；无过滤对照组在私有 mount ns 内 mount tmpfs 成功。
- 判据：实验组 mount() 返回 -1/EPERM 且存活且完成其余探针；对照组 mount 成功。两者皆符 = 通过。
- 步骤：python ctypes 加载经典 seccomp BPF（x86_64 syscall 号：mount 165、umount2 166、reboot 169、init_module 175、delete_module 176、finit_module 313）；两组均在 unshare -Urmpf 私有 mount ns 内以 ctypes syscall(SYS_mount, "tmpfs", target, "tmpfs") 尝试。

## EXP-02 超时清零（C4+C7，PID-ns 单元载体）

- 假设：以单元（PID ns）为回收粒度销毁时，双 fork 脱缰 + setsid 后台进程 + 监听端口 + 临时文件四类残留在 T+2s/T+10s 均为 0（C4 冻结线）；只杀主进程（对照）将留下脱缰进程与端口（T21 的经典失效），如实记录不预设数字。
- 工作负载：主进程写 main.tmp、派生 (i) 双 fork+setsid 守护进程：绑 127.0.0.1 专属端口、每 0.5s 写 heartbeat.tmp；(ii) setsid 子进程：写 child.tmp 后长睡；主进程写 ready 文件（含各进程宿主 PID、端口、文件清单）。
- 终止方式（3 种 × 每组 10 轮）：超时 kill（启动后 2.0s 触发销毁）、主动取消（ready 后 0.5s 人为触发销毁）、正常结束（主进程 3s 后自退，随后触发单元销毁/对照组不做任何动作）。
- 实验组销毁 = 杀 ns init（SIGKILL）+ 删除该轮临时目录（平台 destroy 的文件面）；对照组 = 只 SIGKILL 主进程宿主 PID，不做其他任何动作。
- 检查：每轮销毁后 T+2s 宿主侧枚举（记录 PID 存活数、端口可连接/监听数、文件残留数）；全部轮次结束后按各轮销毁时间戳做 T+10s 复查扫掠。C7 清单在本载体下适用项：进程/端口/临时文件/netns（ns 随 init 死亡消失，以 init 与成员全灭为据）；cgroup/挂载/快照引用记 N/A-载体无此面。
- 判据（冻结）：实验组任一轮任一时点残留 >0 = C4 不通过；对照组不设通过线，只作对比证据。

## EXP-03 网络矩阵 + Q29 配方验证（C8 子集 + ST-5）

- 假设：OpenSandbox 式 deny 配方（默认拒绝出站 + 显式 deny 元数据/私网 + 仅放行白名单与受控 DNS）在 nft 层可完整实现 C8 子集矩阵：allow 用例通、全部 deny 用例被拒（C8 冻结：任一 deny 失败 = 该轨不合格）。
- 拓扑（全部本机地址模拟，禁止真实外网/真实元数据）：server ns 内哨兵监听于其 veth 接口的多个 /32 别名：10.99.0.2（内网哨兵 HTTP:8080 → CANARY-INTERNAL、受控 DNS:53）、169.254.169.254（模拟元数据 HTTP:80 → CANARY-METADATA）、203.0.113.10（模拟公网白名单 HTTP:8080 → CANARY-PUBLIC，/redir 返回 302 跳元数据）、203.0.113.11（模拟公网非白名单 HTTP:8080）、203.0.113.53（非指定解析器 DNS:53）；fd00:ec2::254（模拟元数据 v6 HTTP:80，若 v6 配置失败记 N/A 注明原因）。受控 DNS 行为：whitelist.test→203.0.113.10、internal.test→10.99.0.2、rebind.test 第 1 次答 203.0.113.10、第 2 次起答 169.254.169.254。
- client 配方（nft inet 表，output 链，policy drop）：lo 放行；established 放行；→受控 DNS(10.99.0.2:53 udp/tcp) 放行；→203.0.113.10:8080 放行（白名单）；169.254.0.0/16 显式 drop；10/8、172.16/12、192.168/16 显式 drop；其余默认 drop（含 v6）。
- 用例（≥8）：U1 白名单 allow；U2 非白名单公网 deny；U3 元数据 v4 deny；U4 内网哨兵 deny；U5 DNS 直出非指定解析器 deny；U6 指定 DNS allow；U7 白名单 /redir 跳元数据 deny（不得取得 CANARY-METADATA）；U8 rebinding（第二次解析得内网/元数据 IP 后连接 deny）；U9 元数据 v6 deny 或 N/A。
- 对照组：client 无 nft 规则重复 U2/U3/U4/U6，须全部可达，否则 deny 结果作废（哨兵可达性前提）。
- 判定：实验组 deny 用例全过且 allow 用例全过 = 通过；逐用例记录实际结果（HTTP 体/dig 结果/curl 退出码）。

## EXP-04 ST-1/ST-2/ST-4 冒烟（LAB-MINI 载体 = namespace 单元）

- 假设：namespace 单元可跑通三套件且成功判据（09 §4）可核验：ST-1 探针输出匹配；ST-2 输出哈希 = 宿主同脚本基准哈希；ST-4 打包内容重算哈希 = 生成清单哈希。
- 步骤：每套件 n=30 独立运行（unshare 新单元 → 执行 → 退出销毁），harness 计时全程墙钟（进程启动 → 退出且单元进程清零确认）；按冻结统计 n<100 只报 (n, P50, max) + 失败数/失败率。
- ST-2 脚本冻结：SHA-256 迭代 1,000,000 次（对计数器字节串）+ fib(25) 递归，输出二者组合的 SHA-256；脚本文件哈希随原始数据登记。
- ST-4 冻结：1,000 个 × 4KiB 文件（内容由序号种子确定性生成），写后全量读回算每文件 SHA-256 → 清单哈希 = 对排序后哈希串再 SHA-256；tar 打包后从包内重算清单哈希比对。

## 安全与中止条件

- 全部实验仅本机回环/自建 netns；模拟元数据地址为本机别名，**不访问任何真实外部地址**；内存增长类探针若宿主 available < 400MiB 立即中止该项；EXP-02/03/04 均设 trap 清理（杀全部子进程、删 netns/veth/临时目录）。
- 禁止：创建 E2B sandbox 或任何云资源；改动 09 冻结线；测后改判据。

## 清理验证（实验后）

`ip netns list` 为空、宿主无 veth-* 残留、无 lab 单元/哨兵进程（pgrep 模式核查）、/tmp 与工作区临时目录清除、systemd 无 lab* unit 残留、/sys/fs/cgroup 无自建目录。

## 预注册附录（2026-10-27，EXP-03 载体变更 #2/#3，判据不变）

EXP-03 原双 netns+veth 设计经三批实测不可行，证据（[SELF]，脚本 raw/ 同批保留 exp03-batch1/2/3-invalid.json）：
1. 宿主 runtime 出口过滤在 connect()/sendto() 系统调用层先行拦截：目标为 RFC1918/链路本地地址时**立即 EPERM**（宿主 shell、新 userns+netns 内均实测），先于本实验 nft 配方，deny 结果不可归因于配方；
2. 子 netns 内经 veth 的跨 ns 流量、甚至 lo 上非 127 地址、veth 本地地址均 ENETUNREACH（双端 LOWER_UP、路由与 route-get 正常、邻居表为空）——数据面不通；
3. UDP sendto 在本环境被无差别 EPERM（连 127.0.0.1 任意端口），DNS-over-UDP 不可用；TCP/127.x 可达（实测）。
载体变更 #3（最终）：单个子 netns 内以 lo 上 127/8 别名作全部端点（127.0.0.10 白名单 / .11 非白名单 / .254 模拟元数据 / .2 模拟内网 / .53 受控 DNS / .54 非指定 DNS），DNS 改走 TCP/53（配方 udp+tcp 双行中的 tcp 行受测，udp 行记为环境不可测）；配方去掉 `oif lo accept` 一行（本载体中 lo 即唯一"线路"，该豁免行不可测，属明示偏离）；配方逐目标 allow/deny 与默认拒绝结构与冻结配方 1:1 对应。字面生产规则（169.254/16、RFC1918、fd00:ec2::254）保留在规则集中但标注未被流量检验。U9（IPv6 元数据）预期 N/A：v6 非 127 目标在本载体不可达（原因实测记录）。C8 判定口径不变：deny 用例须全过（DROP 超时签名）才算轨合格，且结论范围明示为"配方策略逻辑"而非生产拓扑。
