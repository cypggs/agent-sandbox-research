# Round1 线C · 底层隔离原理底稿

> 项目：Agent Sandbox 全领域研究 · 线C（底层隔离原理）
> retrieved_at：2026-10-27（Asia/Shanghai）
> 证据规则：本稿只用 A 级证据——官方文档 / 内核文档（kernel.org、man-pages）/ 官方架构文档 / 原始论文 / 官方博客。C/U 不当事实；无官方/论文数据处写「未验证」。
> 状态：原理底稿，非最终报告。实验部分只设计、不执行，统一标「待执行」。
> 对应 spec：§5.1 Linux、§5.2 MicroVM、§5.3 gVisor、§5.4 Wasm、§5.5 浏览器/GUI。

---

## 专题 1 · Linux 操作系统隔离

### 1.1 一句话边界

Namespace 决定「能看见什么」，cgroups 决定「能用多少」，seccomp/capabilities/LSM 决定「能做什么」。三者都运行在**同一个宿主内核**上执行——这是容器隔离与 VM 隔离最根本的分界，下文 1.9 详述。 [A]

### 1.2 Namespace：7+1 类，逐个能 / 不能

内核 man-pages 的 namespaces(7) 定义：namespace 把一个全局系统资源包装成抽象，使 namespace 内进程以为自己拥有该资源的独立实例；变更只对同 namespace 成员可见，对外不可见；其用途之一是实现容器。当前表列 8 类（含较新的 Time 与 Cgroup）。 [A · https://manpages.ubuntu.com/manpages/noble/man7/namespaces.7.html ]

| Namespace | Flag | 隔离什么（能） | 不能做什么（边界） |
|---|---|---|---|
| Mount | CLONE_NEWNS | 挂载点列表；容器内 mount/umount 不影响宿主视图；配合 pivot_root + 只读根可给出独立根文件系统视图 [A · 同上] | 不隔离文件内容本身：同一底层文件经 bind mount / 共享卷仍可被多方看到；不做访问控制，权限仍靠 UID/LSM/DAC |
| UTS | CLONE_NEWUTS | hostname 与 NIS domain name；sethostname 只影响本 ns [A · https://www.kernel.org/doc/man-pages/online/pages/man7/uts_namespaces.7.html ] | 纯标识隔离，无安全纵深；泄露 hostname 不是边界突破 |
| IPC | CLONE_NEWIPC | System V IPC、POSIX 消息队列 [A · namespaces(7) 同上] | 不隔离 Unix domain socket 的文件系统路径部分、网络、文件；抽象套接字由 network ns 隔离 |
| PID | CLONE_NEWPID | PID 编号空间；ns 内首进程为 PID 1，宿主上是普通 PID [A · namespaces(7) 同上] | 不隐藏宿主进程的存在性到「不可推断」程度：时序、资源消耗、/proc 若未配合 mount ns 重挂仍可泄露；PID ns 不隔离信号权限的全部语义，权限仍看 user ns |
| Network | CLONE_NEWNET | 网络设备、IPv4/IPv6 协议栈、路由表、防火墙规则、/proc/net、/sys/class/net、端口号、抽象 Unix socket [A · https://www.kernel.org/doc/man-pages/online/pages/man7/network_namespaces.7.html ] | 只给独立栈，不给策略：默认新 net ns 只有 loopback，出站是否可达公网/内网/元数据地址完全取决于 veth/bridge/NAT/防火墙如何接线；配错即等于无隔离 |
| User | CLONE_NEWUSER | UID/GID 映射（见 1.6）；ns 内 capability 只作用于该 user ns 拥有的资源 [A · namespaces(7) 同上] | 不是「免费的 root」：映射外的 UID 显示为 nobody/overflow；创建 user ns 本身在部分发行版受 sysctl/LSM 限制，且历史上 user ns 扩大了非特权用户可达的内核代码路径（攻击面争议的根源，需以具体内核版本核查，未验证具体 CVE 清单） |
| Cgroup | CLONE_NEWCGROUP | cgroup 根目录视图，使容器内看到的 cgroup 路径以自身为根 [A · namespaces(7) 同上] | 只改视图，不改限额；限额由 cgroup v2 控制器决定（1.3） |
| Time | CLONE_NEWTIME | boot / monotonic 时钟偏移（为子进程生效） [A · namespaces(7) 同上] | 不影响 wall-clock（CLOCK_REALTIME）；不提供时间可信度 |

**结论**：Namespace 是「视图隔离」，不是「资源限额」，也不是「系统调用权限收敛」。单独使用任何一类 namespace 都不构成安全沙箱。 [A · 由 namespaces(7) 定义推导，属定义层结论]

### 1.3 cgroups v2：资源治理，不是安全边界

内核官方文档定义：cgroup 是把进程分层组织、沿层级以受控可配置方式分配系统资源的机制，由 core + controllers 组成；v2 只有单一层级树，每个进程恰属一个 cgroup，控制器行为是层级的——上层限制不能被下层覆盖。 [A · https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html ]

- **能**：CPU（cpu.max / cpu.weight）、内存（memory.max / memory.low / memory.min + OOM 行为）、I/O（io.max）、PID 数（pids.max，防止 fork bomb 在宿主层面耗尽 PID）、以及 cgroup.freeze、cgroup.kill 等生命周期控制（具体文件以该文档为准）。 [A · 同上]
- **不能**：cgroups 不决定进程能调用什么 syscall、能打开什么文件、能连什么网络。它防的是「吵闹邻居 / 资源耗尽型 DoS」，不防「利用内核漏洞逃逸」。把 memory.max 设好就宣称沙箱安全，是典型的虚假安全感（见 1.9-Q6）。
- **v1→v2 的关键差异**：统一层级、no internal process 约束、压力信息（PSI 经 *.pressure 暴露）等，细节以官方 v2 文档为准；生产 Agent Sandbox 应只按 v2 设计。 [A · 同上]

### 1.4 seccomp：缩小内核暴露面，不是沙箱本身

内核文档原文立场（必须引用纠正误解）：「System call filtering isn't a sandbox. It provides a clearly defined mechanism for minimizing the exposed kernel surface.」过滤以 BPF 程序表达，只看 syscall 号与参数标量值，BPF 不解引用指针，因此避免了系统调用拦截框架常见的 TOCTOU 问题；返回值包括 KILL_PROCESS / KILL_THREAD / TRAP / ERRNO / USER_NOTIF / TRACE / LOG / ALLOW。 [A · https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html ]

- **能**：把进程可达的 syscall 集合从数百个收敛到工作负载实际需要的子集，从而让被禁 syscall 背后的内核代码路径对攻击者不可达；USER_NOTIF 还允许监督进程代为处理 mount 等敏感调用。 [A · 同上]
- **不能 / 坑**：
  1. 只能按号+寄存器参数过滤，不能安全地按指针指向的内容过滤（路径字符串等）——路径策略应交给 LSM/Landlock，而不是 seccomp。 [A · 同上，TOCTOU 段]
  2. 必须校验 arch 值：同一架构多种调用约定下 syscall 号重叠，不过滤 arch 可被绕过。内核文档把这列为最大 pitfall。 [A · 同上]
  3. 允许集里只要留有 ioctl、io_uring、bpf、perf_event_open、ptrace 等「宽接口」syscall，过滤收益会被大幅稀释；gVisor 官方亦指出：当应用依赖 ioctl/io_uring 这类宽 syscall 时，很难构造安全的通用过滤集。 [A · https://gvisor.dev/docs/architecture_guide/intro/ ]
  4. seccomp 过滤器一经安装只能收紧、子进程继承——这是优点（防降级），也意味着 launcher 必须在 exec 不可信代码前装好。 [A · seccomp 文档，子进程继承段]

### 1.5 Capabilities：把 root 拆开，但 CAP_SYS_ADMIN 仍然过大

man-pages 定义：capabilities 把传统 Unix 的「UID 0 特权」拆成一组可独立授予/丢弃的能力，线程有 permitted / effective / inheritable / bounding / ambient 集合；文件 capabilities 可附在可执行文件上。 [A · https://www.mankier.com/7/capabilities ]

- 对沙箱的用法：容器默认应丢弃全部 capability（`--cap-drop=ALL` 等价语义），再按需加回最小集（如 NET_BIND_SERVICE）；bounding set 决定 exec 后能力的上限，配合 `no_new_privs` 防 setuid 提权。 [A · 同上]
- **陷阱**：CAP_SYS_ADMIN 在 man page 中被明确标注为 overloaded，涵盖 mount、大量管理操作等——授予 CAP_SYS_ADMIN 在实践中接近授予大半个 root，不能把它当作「一个小权限」放进白名单。 [A · 同上，CAP_SYS_ADMIN 条]
- CAP_NET_RAW 允许 raw/packet socket（可用于伪造/嗅探），CAP_SYS_PTRACE 允许跟踪其他进程，CAP_DAC_READ_SEARCH / DAC_OVERRIDE 绕过文件读权限——这些都是 Agent Sandbox 默认必须去掉的高危项，理由直接来自各自的 man-page 定义。 [A · 同上]

### 1.6 User Namespace 与 UID/GID 映射

user_namespaces(7)：新建 user ns 的进程在该 ns 内可拥有完整 capability 集，但这些 capability 只对**该 user ns 所拥有的资源**生效；UID/GID 映射经 /proc/[pid]/uid_map、gid_map 写入（一次写入定义一段连续映射）。 [A · https://manpages.debian.org/bookworm/manpages/user_namespaces.7.en.gz ]

内核 idmappings 文档给出形式化：映射是 userspace-id ↔ kernel-id 的区间映射；初始 user ns 是恒等映射 u0:k0:r4294967295，其他 user ns 典型如 u0:k10000:r10000——即容器内 UID 0 映射到宿主 UID 10000。 [A · https://www.kernel.org/doc/html/v5.16/filesystems/idmappings.html ]

- **安全收益**：容器内 root ≠ 宿主 root。即使进程在容器内以 UID 0 写入文件，宿主侧看到的属主是映射后的非特权 UID，配合 subordinate UID 区间可实现 rootless 容器。 [A · 同上 + user_namespaces(7)]
- **代价/风险**：
  1. 映射没配对（identity mapping、或把宿主 0 映射进来）会让收益归零。
  2. 文件系统必须理解 idmapped mounts，否则共享卷上会出现属主错乱/权限意外放宽；idmappings 文档正是对这一层的形式化说明。 [A · 同上]
  3. 非特权 user ns 的可用性本身是发行版策略开关，不同宿主表现不一致——「在我的机器上 rootless 能跑」不能推广到所有生产宿主（具体发行版默认值：未验证，需按目标发行版官方文档逐个核）。

### 1.7 LSM / AppArmor / SELinux / Landlock

LSM 框架：内核文档说明 LSM 提供钩子框架，各安全模块在构建时选入、启动时经 `security=` 选择；主要用户是 MAC 扩展，例子包括 SELinux、Smack、TOMOYO、AppArmor；/sys/kernel/security/lsm 可读当前启用列表，capability 模块恒在第一位。 [A · https://www.kernel.org/doc/html/latest/admin-guide/LSM/index.html ]

| 机制 | 模型 | 在 Agent Sandbox 中的定位 |
|---|---|---|
| SELinux | 标签型 MAC，策略集中管理，类型强制 | 强，但策略编写/排障成本高；适合宿主层给 runtime、VMM、gofer 等进程打标分区 |
| AppArmor | 路径型 MAC，per-profile | 比 SELinux 易上手；适合给容器/launcher 做文件+能力收敛 |
| Landlock | 非特权、进程自限制的 stackable LSM | 见下 |

Landlock 内核文档：目标是让**包括非特权进程在内的任何进程**都能安全地限制自身 ambient rights（如全局文件系统/网络访问）；它是 stackable LSM，可作为既有系统级访问控制之上的新层叠加；规则集（ruleset）按文件层级授予文件访问权、按端口授予 TCP/UDP 网络权，经 landlock_restrict_self 强制后不可撤销、只能继续收紧，且要求先设 no_new_privs（有 CAP_SYS_ADMIN 的情形除外，文档亦警告风险）。 [A · https://www.kernel.org/doc/html/latest/userspace-api/landlock.html ]

**定位结论**：LSM/Landlock 解决的是 seccomp 解决不了的「语义策略」——哪个路径可读写、哪个端口可连。生产沙箱的合理组合是 seccomp 管 syscall 面、Landlock/LSM 管对象访问、namespace 管视图、cgroups 管配额，四者缺一不可替代。 [A · 由上述四份官方文档的职责定义归纳]

### 1.8 eBPF：在隔离中的真实角色

内核 BPF verifier 文档：eBPF 程序安全性分两步判定——先做 DAG/CFG 检查（禁环、禁不可达），再沿所有路径模拟执行、跟踪寄存器与栈的状态（指针类型如 PTR_TO_CTX / PTR_TO_MAP / PTR_TO_STACK，越界/未初始化读会被拒绝）。 [A · https://docs.kernel.org/bpf/verifier.html ]

BPF LSM 文档：eBPF 程序可挂到 LSM 钩子上（如 `SEC("lsm/file_mprotect")`），经 bpf(2) 的 BPF_PROG_LOAD 加载、用 libbpf 的 bpf_program__attach_lsm 挂载，实现可编程的 MAC/审计策略。 [A · https://www.kernel.org/doc/html/v6.6/bpf/prog_lsm.html ]

- **角色**：观测（syscall/网络/文件事件审计、异常行为检测）+ 动态策略（BPF LSM）+ 网络执行点（cgroup/socket 级 eBPF 做 egress 控制）。
- **边界**：eBPF 程序在内核里执行，verifier 是其安全根；verifier 或 JIT 的缺陷即内核级缺陷。给 Agent 本身加载任意 eBPF 的权限（CAP_BPF/CAP_SYS_ADMIN + bpf syscall）等于交出宿主——沙箱内必须经 seccomp 禁掉 bpf/perf_event_open。 [A · verifier 职责定义 + capabilities 定义归纳]

### 1.9 回答 spec §5.1 的 8 个重点问题

**Q1 Namespace 解决了什么、不能解决什么？**
解决：全局资源的视图隔离（进程、网络、挂载、主机名、IPC、身份、时间、cgroup 视图），使一组进程像在独立机器上一样命名资源。 [A · namespaces(7)]
不能：不限量（那是 cgroups）、不限 syscall（seccomp）、不限对象访问（LSM）、不换内核（所有 ns 共享同一内核）。

**Q2 cgroups 解决了什么、不能解决什么？**
解决：分层资源分配与限制、吵闹邻居抑制、OOM/PID 等耗尽型故障的围栏。 [A · cgroup-v2 文档]
不能：任何权限/机密性问题；被限住的进程依然可以利用内核漏洞、读它有权读的文件、连它能连的网络。

**Q3 seccomp 如何限制系统调用？**
在 syscall 入口执行 BPF 过滤程序，输入是 syscall 号、arch 与参数寄存器，输出 ALLOW/ERRNO/KILL/TRAP/USER_NOTIF 等动作；只能收紧、被子进程继承；不能解引用指针参数。 [A · seccomp 文档]

**Q4 为什么容器通常不等价于独立虚拟机？**
因为容器内进程的每一次系统调用都直接进入**同一个宿主内核**执行，隔离靠的是内核自觉地在每个检查点都正确应用 namespace/capability/seccomp/LSM 策略；而 VM 内进程的 syscall 进入的是 guest 内核，宿主侧只暴露 KVM 的 VM-exit 接口与极小的虚拟设备接口。gVisor 官方用最直白的话概括了前者：用 Linux 安全原语时，被沙箱的工作负载「only one system call away from host compromise」，且这些原语的执行者仍是那个单体内核。 [A · https://gvisor.dev/docs/architecture_guide/intro/ ] VM 的代价则是要预分配资源、启动一个完整 guest 内核（同源官方对比）。 [A · 同上]

**Q5 如何组合构建最小权限执行环境？**
user ns（UID 映射到非特权区间）+ mount ns/pivot_root（只读根 + 独立 tmpfs 工作区）+ net ns（默认无外联，只经受控 veth/代理）+ pid/ipc/uts ns + cgroup v2（cpu/memory/pids/io 上限）+ cap drop ALL + no_new_privs + seccomp 白名单 + Landlock/LSM 路径与端口策略 + 只读 /proc、/sys 掩码。每一层对应上文一份官方文档的职责，不重叠、不互相替代。

**Q6 哪些安全配置容易产生虚假的安全感？**
① 只开 namespace 不配 seccomp/cap（「容器默认配置 = 安全」）；② seccomp 用默认/过宽 profile 却留 ioctl/io_uring/bpf；③ 给了 CAP_SYS_ADMIN 还以为是最小权限 [A · capabilities man page 对其 overloaded 的标注]；④ cgroup 限额齐全就宣称防逃逸；⑤ --privileged、挂 docker.sock、挂宿主 / 到容器内——这些直接把边界送回给工作负载（属配置层结论，A 级依据为上述各机制的定义：边界由配置决定）；⑥ 网络 ns 接了 NAT 就以为有 egress 控制（net ns 本身不含策略，见 1.2）。

**Q7 不可信代码能否接触宿主机内核？**
能，且是直接接触：容器模型的定义即如此——不可信进程的 syscall 由宿主内核亲手执行，seccomp 只是缩小可达子集。 [A · gVisor intro 的对比论述 + seccomp 文档] 这正是 MicroVM/gVisor 路线存在的理由：把「不可信代码 ↔ 宿主内核」之间再插入一层（guest 内核或用户态 Sentry）。

**Q8 容器运行时和宿主机之间的信任边界在哪里？**
边界不在运行时二进制本身，而在三条线上：(1) 内核检查点线——runtime（runc/containerd 等）只负责在进程启动前把 namespace/cgroup/seccomp/LSM 装好，启动后执行期的强制者只有内核；runtime 本身不在每次 syscall 的路径上。(2) 特权线——runtime 以 root/高 cap 运行的那一小段 setup 代码、以及它接受的镜像/配置输入，是宿主侧 TCB 的一部分，setup 期的竞态与挂载处理缺陷会绕过全部执行期策略（具体 CVE：未验证，不在本稿列举）。(3) 逃生口线——宿主目录挂载、runtime socket、特权容器开关，一旦授予，工作负载与宿主之间就不再存在上述任何检查点。

### 1.10 本专题最小实验设想（只设计 · 待执行）

- **假设 H1**：仅 namespace+cgroups 的进程仍可直接触发宿主内核的宽 syscall 面；加入 seccomp 白名单后，被禁 syscall 返回 EPERM/SIGSYS 且进程其余功能不受影响。
  验证方法（待执行）：在一次性测试 VM 中用 unshare 创建 mount/pid/net/user ns，分别在无 seccomp 与有 seccomp（libseccomp 小程序）两种配置下跑同一组探针（尝试 ptrace、bpf、mount、连外网），记录 errno 与审计日志差异。
- **假设 H2**：user ns 内 UID 0 写出的文件，在宿主上属主为映射后的非特权 UID。
  验证方法（待执行）：写入 uid_map `0 100000 65536` 后 touch 文件，宿主侧 stat 对照。

**本专题证据条数：9 条 A 级**（namespaces(7)、network_namespaces(7)、uts_namespaces(7)、cgroup-v2、seccomp_filter、capabilities(7)、user_namespaces(7)/idmappings、LSM index、Landlock、eBPF verifier、BPF LSM、gVisor intro 对比段——按独立官方文档计 9 个来源文档族）。

---

## 专题 2 · MicroVM 与硬件虚拟化（KVM / Firecracker / Cloud Hypervisor）

### 2.1 核心差异：边界从 syscall 接口移到硬件虚拟化接口

Firecracker 官方定位：开源虚拟化技术，专为创建和管理安全的、多租户的容器与函数服务而建；microVM 提供强于传统 VM 的隔离叙事下同时追求容器的速度与资源效率；它运行在用户态、使用 Linux KVM 创建 microVM，每个函数/容器（组）可被一个 VM 屏障封装，使不同客户的工作负载同机运行。 [A · https://firecracker-microvm.github.io/ ]

NSDI'20 原始论文（Agache et al.）给出的设计命题是本领域的标准表述：传统观点认为要在「强隔离高开销的虚拟化」与「弱隔离低开销的容器」之间二选一，Firecracker 的目标是两者兼得；实现上用 KVM 提供最小 VM、REST 配置 API、受限的设备模拟（disk/network/serial）、可配置的网络与磁盘限速（且限速在 VMM/宿主侧强制，因为 guest 不可信、不能指望它自限），以及一个 Firecracker 进程对应一个 microVM 的简单隔离模型。 [A · https://www.usenix.org/conference/nsdi20/presentation/agache ]

### 2.2 Firecracker 设备模型如何缩小攻击面

官方 FAQ 的量化口径：与通用 VMM QEMU 相比，Firecracker 用 Rust 编写、只给 guest 提供最小必需设备模型、排除非必需功能——**仅 5 个模拟设备：virtio-net、virtio-block、virtio-vsock、serial console、以及一个仅用于停止 microVM 的极简键盘控制器**；配合精简的内核加载流程，得到 <125 ms 启动时间与 <5 MiB 内存占用（官方口径，测试条件以官方/论文为准）。 [A · https://firecracker-microvm.github.io/ ]

为什么「少设备 = 小攻击面」成立（机制层）：
1. 每个虚拟设备都是宿主侧 VMM 中一段处理 guest 可控输入的解析/状态机代码；guest 可以任意构造设备请求，因此设备实现就是 guest→host 的直接攻击面。砍掉 USB、显卡、声卡、完整 PCI、BIOS 等传统设备，等于直接删掉这些解析器。
2. virtio 是半虚拟化标准接口，语义窄、已被多方实现与审计，比模拟真实硬件寄存器行为的设备模型更容易收敛行为。
3. VMM 本身再被 jailer 二次围栏：官方说明每个 microVM 还被 jailer 用常见 Linux 用户态安全屏障进一步隔离，作为虚拟化屏障万一被攻破时的第二道防线。 [A · https://firecracker-microvm.github.io/ ]
4. Rust 实现消除内存安全类缺陷中的一大类——这是官方与论文共同强调的实现语言选择（论文报告的代码量级与 QEMU 的对比数字属论文口径，本稿不转引二手数字）。

**剩余攻击面（不能因「只剩 5 个设备」就宣称安全）**：KVM 本身的 ioctl 接口与宿主内核虚拟化子系统、virtio 实现的缺陷、VMM 的 API 面（REST over Unix socket，宿主侧必须做访问控制）、jailer 配置错误。边界变小 ≠ 边界消失。

### 2.3 Cloud Hypervisor：同族、不同取舍

Cloud Hypervisor 官方 README：开源 VMM，运行在 KVM 之上（现亦支持 MSHV），专注现代云工作负载——I/O 以 virtio 半虚拟化设备为主、不需要 legacy 设备、64 位 CPU；用 Rust 实现、基于 rust-vmm 组件；高层目标明确写有 Minimal emulation、Low memory footprint、Small attack surface，同时保留 CPU/内存/PCI 热插拔与机器间迁移等 Firecracker 刻意不做的能力；支持 64 位 Linux 与 Windows guest。 [A · https://raw.githubusercontent.com/ahmedaabouzied/cloud-hypervisor/master/README.md ]

**对比结论**：Firecracker 是「为 serverless/容器函数极致做减法」，Cloud Hypervisor 是「为通用云工作负载做适度减法」。设备/功能集更大 ⇒ 宿主侧代码更多 ⇒ 攻击面与 Firecracker 不可直接等同评价；选型时应按工作负载是否需要热插拔/迁移/Windows guest 来分，而不是笼统地说「MicroVM 都一样」。

其他同族（Kata Containers 以 VM 承载 Pod/容器、crosvm 源于 Chromium OS）只在此登记为技术路线，深度源码分析归线 E，本稿不展开（未验证部分不写）。

### 2.4 Snapshot / Restore：为什么「恢复了」≠「毫秒级可用」

Firecracker 快照的组成（据其官方快照文档的二手镜像整理——官方原文归线 E 源码核验，此处标**待核验**）：guest 内存文件 + microVM 状态文件（vCPU/设备状态）+ 磁盘文件（用户自管）；恢复时内存可按需以 MAP_PRIVATE 懒加载。此段机制描述与业界通行实现一致，但在取得官方文档原文前，本稿只把它作为 C 级线索，不作为 A 级结论引用。

可以确立的 A 级判断只有两条：
1. 官方对外口径的启动数字（<125 ms）指的是**冷启动到 microVM 运行**这一段，不含业务运行时初始化、依赖加载、连接池/缓存预热、外部服务握手。 [A · https://firecracker-microvm.github.io/ 的数字语义范围]
2. NSDI 论文的性能数字是其特定实验环境（宿主、guest 内核、配置）下的测量，不可直接移植为任何 Agent 平台的 SLA。 [A · https://www.usenix.org/conference/nsdi20/presentation/agache ]

「恢复 ≠ 可用」的工程分解（分析框架，非测量结论）：
- **懒加载缺页风暴**：懒加载把启动时延摊到首次访问每一页时，工作集越大，恢复后头几秒的尾延迟越差——测 p50 会很好看，p99 才是真相。
- **guest 内状态重建**：时钟跳变（guest 看到时间不连续）、熵池状态、网络连接（快照不含宿主侧已建立连接的对端状态）、DNS 缓存、TLS session、/proc/stat 等单调量异常，都需要 guest 侧 agent 配合处理。
- **编排开销**：调度、镜像/快照分发、网络接线（tap/路由/策略）、元数据注入往往比 VMM 本身的 restore 更慢（此条为架构分析，量化数据未验证）。

### 2.5 快照中的密钥、网络状态与租户状态泄露

这是 snapshot 路线最容易被低估的安全面，机制是确定的（由快照语义直接推出）：

1. **同一快照恢复出多个克隆 ⇒ 内存状态逐字节相同**：进程内已生成的密钥、随机数发生器的内部状态、UUID/机器 ID、TLS 临时密钥、session token 都会重复。两个克隆若都用「恢复后首次随机数」生成密钥，可能生成相同密钥——这是快照克隆的经典事故模型。缓解需要恢复后强制重播种熵源、guest agent 在 restore 事件后轮换身份材料；Firecracker 生态对此有专门讨论，但本稿未取得官方原文，**具体机制与版本行为标未验证，待线 E 查官方 snapshot 文档与 VMGenID 相关实现后补**。
2. **快照文件本身 = 完整内存转储**：内含 guest 内全部明文秘密（环境变量、解密后的凭证、用户数据）。快照存储必须按「最高密级数据」对待：加密、访问审计、租户间严格分桶、销毁时连同快照一并销毁。只删 VM 不删快照 = 数据没删。
3. **跨租户复用快照/模板是污染源**：模板镜像里残留的主机密钥、云元数据缓存、shell 历史、临时凭证会在所有派生实例中复现。模板制作必须有「密封」步骤（清密钥、清日志、清 machine-id），且恢复后由平台重新注入租户身份——模板与租户数据必须分通道注入，不能把租户 A 的状态烘焙进会被租户 B 使用的快照。

### 2.6 大规模 MicroVM 调度要点（设计约束，非产品结论）

- 每 VM 一个 VMM 进程 ⇒ 宿主进程数、FD、内存页表开销随密度线性增长，密度上限由 VMM 常驻开销（官方 <5 MiB 口径）+ guest 页表 + jailer 开销共同决定。 [A · 官方开销口径同 2.2]
- 资源可超卖是官方设计目标之一（站点称 all hardware compute resources can be safely oversubscribed），但超卖比必须与 cgroup/限速器联动，否则密度收益会以尾延迟为代价。 [A · https://firecracker-microvm.github.io/ ]
- 调度器必须处理：快照的版本兼容（宿主内核/VMM 版本变化后旧快照能否恢复——**未验证，待实验**）、NUMA 与 CPU 模板一致性、故障域（同宿主多租户的爆炸半径）。

### 2.7 本专题最小实验设想（只设计 · 待执行）

- **假设 H1**：快照恢复的端到端可用时延（首个业务请求成功）显著大于 VMM 报告的 restore 时延，且差距随工作集增大而增大。
  验证方法（待执行）：同一 microVM 分别测冷启动、快照恢复后立即请求、恢复后预热 5 s 再请求三组 p50/p99；记录缺页次数（uffd/主缺页计数）与时延的相关性。
- **假设 H2**：同一快照恢复的两个克隆，在未做恢复后重播种时，会产生可观测的重复随机输出/相同临时标识。
  验证方法（待执行）：在无害自建 guest 内，恢复后立即读取 /proc/sys/kernel/random/uuid、getrandom 首段哈希与预置测试程序的密钥指纹，两克隆对照；仅在自有实验环境、不用任何真实凭证。

**本专题证据条数：4 条 A 级**（Firecracker 官方站、NSDI'20 论文、Cloud Hypervisor 官方 README、Firecracker jailer/限速官方说明同站计 1 族）+ 1 条 C 级线索（快照内部组成，待官方原文核验）。

---

## 专题 3 · gVisor 与安全容器

### 3.1 机制：Sentry 与 Gofer

gVisor 官方安全导论的定义：gVisor 是一个**应用内核（application kernel）**，不是 hypervisor，也不是 syscall 过滤器；它在用户态充当工作负载眼中的内核，拦截并处理工作负载的系统调用与缺页，该组件叫 Sentry；Sentry 是用内存安全的 Go 从零重写的 Linux 实现（syscall 接口、内存管理、文件系统、网络栈、进程管理、信号、namespace 等），**从不把任何系统调用透传给宿主内核**——未在 gVisor 中实现的功能，工作负载就用不了。 [A · https://gvisor.dev/docs/architecture_guide/intro/ ]

文件访问的纵深：Sentry 本身被关在极受限环境中（seccomp 过滤禁止它直接 exec/connect 等、mount ns 隔离文件系统视图、user ns 最小 capability），它**不能直接打开宿主文件**；超出沙箱的文件操作经 9P 类协议交给一个略高信任的伴随进程 Gofer 代理，Gofer 才是打开宿主文件的一方。 [A · 同上]

拦截平台（platform）有两条路线：Systrap（默认，基于 seccomp-bpf 做 syscall *拦截*而非通常的过滤，不需要硬件虚拟化，适合跑在 VM 内）与 KVM（用 KVM 做地址空间隔离与缺页拦截，需要虚拟化支持，嵌套虚拟化下通常更慢）。 [A · 同上]

### 3.2 与原生容器、MicroVM 的边界差异

gVisor 官方的三分法（本稿直接采用其论证结构）：

| 路线 | 强制者 | 工作负载 syscall 的去向 | 攻破所需 |
|---|---|---|---|
| 原生容器（Linux 原语） | 宿主单体内核 | 直接进宿主内核 | 命中保留面内的一个内核缺陷即可，距宿主沦陷「一个 syscall」 [A · 同上] |
| VM / MicroVM | hypervisor + 硬件虚拟化 | 进 guest 内核，出界只能经 VM-exit 到 hypervisor | 攻破 guest 内核还不够，还需再破虚拟化边界；代价是预分配资源 + 启动完整 guest 内核 [A · 同上] |
| gVisor | 用户态 Sentry（第二内核） | 进 Sentry（Go 实现），Sentry 只向宿主发出少量、且不与工作负载 syscall 一一对应的宿主调用 | 需同时利用 Sentry 内核与宿主内核——两者不共享代码；且资源可运行时动态分配/释放，效率接近容器模型 [A · 同上] |

官方同时诚实地列了**不防的范围**：沙箱/运行时之上的高层组件漏洞（如 containerd 在启动 gVisor 之前就被攻破）、Spectre 类侧信道（gVisor 只拦 syscall 与缺页，CPU 侧信道需在宿主内核/硬件层缓解）、以及工作负载自身应用层被攻破后在其被授权范围内作恶（故不同客户必须用不同沙箱）。 [A · 同上]

### 3.3 兼容性边界

Sentry 是重写而非透传，所以兼容性边界 = 已实现的 syscall/子系统子集。官方导论明言未实现者不可用；这带来三类典型不兼容：依赖冷门 syscall/flag 语义的程序行为差异、/proc 与 /sys 的合成视图与真实内核不一致（观测类工具、依赖内核日志的程序会看到 gVisor 的合成输出——官方以 dmesg 在 runsc 下返回 gVisor 自身启动日志为演示）、以及需要真实设备/特权操作的负载不适用。 [A · 同上] 具体 syscall 覆盖清单应以 gVisor 官方兼容性文档为准（本稿未逐项核，标未验证）。

### 3.4 性能代价：只引官方性能指南的定性结论

gVisor 官方 Performance Guide 把代价分为两类：**结构性代价**（多一层 Sentry、syscall 必须多穿一层软件、用安全语言实现的取舍）与**实现性代价**（作为独立实现的各子系统成熟度不如 Linux 本体，如其网络栈仍在演进、CPU 效率较低）。 [A · https://gvisor.dev/docs/architecture_guide/performance/ ]

该指南可确立的定性结论（其图表数字基于旧 ptrace 平台与特定 GCE 机型，官方自己注明不代表当前 Systrap 平台的最优情形，故本稿**只引结论、不引数字**）：
- 纯 CPU 计算与原始内存访问：基本无额外开销（应用指令原生执行、映射建立后无中介）。 [A · 同上]
- syscall 密集型负载（如小操作为主的 Redis 类负载）：开销显著，且单次操作做的功越少、相对开销越大。 [A · 同上]
- 文件系统：经 Gofer 的路径有固定穿越开销，VFS 元数据密集场景（小文件静态服务）表现差；原始磁盘 I/O 很快被设备本身瓶颈掩盖。 [A · 同上]
- 网络：以实现性代价为主，吞吐与 CPU 效率弱于原生栈（指南时点口径，当前版本差距**未验证**）。 [A · 同上]

**禁止事项**：不得把该指南中 ptrace 平台时代的倍数数字写进选型结论。需要数字时，必须按线 D 的评测设计在目标版本/Systrap 平台上自测。

### 3.5 适用与不适用

- 适用：syscall 面中等、以用户态计算为主、需要比容器强但不想付 VM 资源模型的不可信多租户负载；跑在云 VM 内（无嵌套 KVM 需求时 Systrap 正合适）。 [A · 平台特性同 3.1]
- 不适用/慎用：syscall 与小 I/O 极密集的负载、对内核行为保真度要求高的负载（驱动、底层网络、需要真实 /proc 语义的观测栈）、以及把 gVisor 当作可以混跑互不信任客户于同一沙箱的理由——官方明确要求不同客户分沙箱。 [A · 同上]

### 3.6 本专题最小实验设想（只设计 · 待执行）

- **假设 H1**：同一负载在 runc 与 runsc(Systrap) 下，CPU 密集任务时延差 <10%，而小包网络/syscall 密集任务差显著放大。
  验证方法（待执行）：自建测试机上跑 sysbench cpu、fio 随机小 I/O、redis-benchmark 小 pipeline 三组对照，记录两平台比值与 Sentry 的 CPU 占用。
- **假设 H2**：在 runsc 下执行一个依赖未实现 syscall 的探针程序，会得到 ENOSYS/合成行为而非宿主内核行为。
  验证方法（待执行）：探针依次调用一组冷门 syscall 并打印 dmesg 输出，与宿主对照，记录差异清单。

**本专题证据条数：3 条 A 级**（gVisor 官方安全导论、gVisor 官方 Performance Guide、gVisor 官方 Sentry/Gofer 架构说明与前者同源计 1 族，合计 2 个独立官方文档 + 其平台说明）。

> 计数口径修正：独立官方文档 2 篇，证据条（可独立引用的结论簇）3 条。

---

## 专题 4 · WebAssembly Sandbox

### 4.1 核心安全模型：无环境权威 + 显式导入

Wasmtime 官方安全文档对 Wasm 核心规范的概括：Wasm 天生沙箱化——调用栈不可被应用访问（返回地址不放在应用可及内存中，传统栈溢出改返回地址不可行）；指针被编译为线性内存内的偏移且每次访问做边界检查；所有控制转移都到已知且经类型检查的目的地；与外界的全部交互只能经 imports/exports，**没有原始 syscall 或 I/O 通道，只能做被显式链接进来的接口允许的事**；且无未定义行为。 [A · https://docs.wasmtime.dev/security.html ]

Wasmtime 的纵深加固（官方同页）：线性内存前设 2 GiB guard region 防符号扩展类实现缺陷、实例结束后清零内存防实例间信息残留、栈 guard page、部分 Spectre 缓解（call_indirect 与 br_table 的投机缓解等，明言仍是持续研究课题）、以及用 Rust 实现运行时与「用错 API 也不会 segfault」的嵌入者安全 API。 [A · 同上]

### 4.2 WASI 与能力安全：从「进程权限」到「句柄授权」

WASI 官方安全页：WASI 建立在能力安全（capability-based security）之上——在 WASI 下运行的代码**没有环境权威（no ambient authority）**：模块/组件启动时对外部世界零访问，只能做宿主显式授予的操作；这与 Linux/Windows 进程继承用户广泛权限、需额外叠沙箱的模型相反，WASI 是默认拒绝（更准确说：默认无能力句柄）。 [A · https://wasi.dev/security ]

授予机制按代际区分（同页）：
- WASI 0.1（preview1）模块：只能操作运行时在启动时交给它的预打开 FD，没有办法申请新 FD；授权发生在运行时调用时。 [A · 同上]
- WASI 0.2 组件：能力直接以 WIT 接口表达——文件系统、网络、环境、时钟、随机数各是一个独立 import，宿主只用被授予的 import 实例化组件，组件的接口契约即其能力面，且可在二进制中静态检查。 [A · 同上]
- WASI 0.3：继续该模型，部分能力的句柄传递改为 world 级隐式，但授权仍在 world 边界由宿主完成。 [A · 同上]

Component Model 的意义：它把「一个 Wasm 二进制能做什么」从运行时黑盒变成可静态审计的接口声明——对 Agent 插件/工具沙箱而言，这意味着权限审查可以在加载前完成（imports 清单即权限清单）。此判断是基于上文机制的直接推论。

### 4.3 Wasmtime 与 WasmEdge 的定位差异

- Wasmtime（Bytecode Alliance）：官方安全文档即上文所引，其 WASI 文件系统实现遵循能力模型，应用只能访问被授予的文件与目录。 [A · https://docs.wasmtime.dev/security.html ] 定位：通用、标准先行、安全文档最完整的服务端运行时。
- WasmEdge（CNCF 生态）：本轮**未取得其官方安全架构文档原文**，其与 Wasmtime 在 WASI 覆盖、扩展（如网络 socket、AI 推理插件）与宿主函数面上的差异标**未验证**，待下一轮查其官方文档后补——不在此凭印象对比。这本身是一个研究缺口记录。

共同的关键提醒：**宿主函数即新的 syscall 面**。Wasm 把攻击面从内核 syscall 移到宿主提供的 imports：宿主函数实现中的缺陷、过宽的目录授权、把「读文件」import 实现成任意路径读取，都会让能力模型名存实亡。能力安全保证的是「未授予的能力不可获得」，不保证「已授予的能力被安全实现」。

### 4.4 能否替代容器/VM：适用边界

适合 Wasm 的场景（由其机制推出）：
- 短生命周期、冷启动敏感的函数/插件：无 guest 内核、无完整 OS 启动，实例化开销远小于 MicroVM（定性判断；具体数字未在本稿证据内，标未验证需自测）。
- 权限粒度细到单个目录/单个 HTTP 能力的工具调用、插件、UDF、多租户代码片段。
- 跨平台分发同一二进制（Wasm 的可移植性是规范目标）。

不适合、不能替代的场景：
- 需要完整 Linux 语义的 Agent 工作负载：任意 shell 工具链、包管理器、编译器、浏览器、需要 fork/exec 任意原生二进制、需要 /proc 真实语义、需要内核特性（挂载、设备、网络命名空间操作）的任务。WASI 提供的是受控的类 POSIX 子集，不是 Linux 本身；把一个通用 Agent 的工作区硬塞进 Wasm，等于先把工具链逐个移植/模拟一遍。
- 需要强多租户资源隔离但宿主进程内混跑多实例时：Wasm 实例隔离是语言/内存模型级隔离，同一宿主进程内一个运行时缺陷可能影响同进程全部实例——高保障场景通常把 Wasm 再放进进程/容器/MicroVM 里跑（分层而非替代）。

**结论**：Wasm 与容器/VM 不是替代关系而是分层关系——Wasm 解决「细粒度能力授权的插件/函数层」，容器/MicroVM 解决「完整 OS 语义的执行环境层」。Agent 平台的合理形态是混合：Agent 主体跑在 MicroVM/容器中，单个工具/插件以 Wasm 组件运行并按 imports 最小授权。

### 4.5 本专题最小实验设想（只设计 · 待执行）

- **假设 H1**：未授予目录能力的 Wasm 组件尝试打开 /etc/passwd 类路径必然失败，且失败发生在宿主授权层而非 guest 代码自觉。
  验证方法（待执行）：写一个只 import 时钟能力的组件尝试文件读，与授予只读 /tmp/data 的版本对照，记录错误类型与审计日志。
- **假设 H2**：同一计算负载的 Wasm 实例化时延比 MicroVM 冷启动低一个数量级以上，但跑需要 shell 工具链的任务时 Wasm 方案不可行（兼容性而非性能失败）。
  验证方法（待执行）：测 Wasmtime 实例化+首调用时延 vs Firecracker 冷启动（同机），并尝试在 Wasm 侧完成一个依赖管道与外部编译器的任务，记录失败点。

**本专题证据条数：3 条 A 级**（WASI 官方安全页、Wasmtime 官方安全文档、WASI 能力模型设计原则（WASI 官方仓设计文档，经搜索结果引）计入同族）+ 缺口 1 项（WasmEdge 官方安全文档未取得）。

---

## 专题 5 · 浏览器与 GUI Sandbox

### 5.1 Chromium 多进程架构：浏览器进程是特权代理

Chromium 官方进程模型文档：多进程架构下，每个多进程模式中渲染进程都运行在沙箱化进程内，对用户计算机的访问受限——它们没有直接访问用户文件系统、显示等资源的权限，只能经浏览器进程获得被允许的资源，浏览器进程可对该访问施加安全策略；因此浏览器进程能减轻被攻破的渲染引擎造成的损害。单进程模式仅供测试/开发，不安全、不健壮。 [A · https://chromium.googlesource.com/playground/chromium-org-site/+/refs/heads/main/developers/design-documents/process-models.md ]

ChromeOS/Chrome 安全白皮书的同义表述：浏览器实现多进程架构，把处理不可信输入的部分（网页）与访问系统资源/用户数据的部分分开进程；网页只得到极有限的资源（绘图、执行 JS），不能直接访问用户文件；网页运行在称为 Chrome sandbox 的强受限环境中，Linux 上由 namespace 保证页面看不到 Chrome 之外的进程、由 seccomp 限制其对内核的访问。 [A · https://www.chromium.org/chromium-os/developer-library/reference/security/security-whitepaper/ ]

### 5.2 站点隔离（Site Isolation）：进程边界对齐信任边界

Chromium 官方 Site Isolation 页：站点隔离确保不同网站的页面永远被放进不同进程，每个进程运行在限制其权限的沙箱中，并阻止进程接收来自其他站点的大多数敏感数据，使恶意网站即使攻破自身进程内的规则也难以窃取其他站点数据；「site」定义为 scheme + 注册域名（忽略子域、端口、路径）。 [A · https://www.chromium.org/Home/chromium-security/site-isolation/ ]

官方给出的威胁模型三件套值得 Agent 场景直接借用：① 被攻破的 renderer（任意代码执行）必须被假定会发生——历史上每个版本都有可利用的 renderer bug；② UXSS 类绕过同源策略的 bug；③ Spectre 类侧信道可在无 bug 时读取同进程任意内存——这正是「同进程即同信任域」必须被进程拆分打破的原因。隔离的代价官方亦明示：桌面端全站隔离时内存开销约 +10–13%（Chrome 67 时点、多标签场景口径）。 [A · 同上]

### 5.3 Linux 上的两层沙箱实现

Chromium 官方 Linux Sandboxing 文档：采用两层方法——Layer-1（语义层，setuid sandbox 或现代的 user-namespace sandbox）阻止进程访问大多数资源；Layer-2（攻击面削减层，seccomp-BPF）限制进程可达的内核攻击面；多进程模型使不同权限等级的部件（renderer 处理不可信输入、假定易被攻破）用 IPC 向特权的浏览器进程申请资源。 [A · https://chromium.googlesource.com/chromium/src/+/b98e6c2bf39155864da71b8b69470ebc58913719/docs/linux_sandboxing.md ]

注意 `--no-sandbox` 会关闭全部沙箱（官方文档明示其仅用于测试）——云端浏览器服务若在容器中图省事加此参数，等于把 5.1/5.2/5.3 的全部边界一次性拆除，这是部署审计的第一检查项。 [A · 同上]

### 5.4 CDP（Chrome DevTools Protocol）的风险面

CDP 官方文档（Chrome DevTools Protocol 页）：协议定义在 Chromium 源码（browser_protocol.pdl / js_protocol.pdl），经 --remote-debugging-port 暴露后，完整协议可从 localhost:9222/json/protocol 取得，浏览器级端点经 /json/version 的 webSocketDebuggerUrl 暴露；Chrome 63 起支持多客户端。 [A · https://developer.chrome.google.cn/devtools/docs/debugger-protocol?hl=id ]

风险面（由协议能力面直接推出，属机制分析）：
1. **CDP ≈ 浏览器级完全控制**：它能执行任意 JS（Runtime 域）、读写 DOM、拦截/改写网络、读取 cookie 与存储、下载文件、截屏。谁拿到 CDP WebSocket，谁就拥有该浏览器 profile 的全部会话身份——CDP 端点本身没有内建的调用方认证（官方文档未描述任何认证机制，此「无认证」判断以官方文档为准、表述为「官方协议文档未提供认证机制」）。
2. **暴露面事故模型**：remote-debugging-port 若绑定 0.0.0.0 或被 SSRF/内网穿透够到，攻击者不需要浏览器漏洞即可接管会话。云端浏览器必须把 CDP 端口限制在控制面网络内、经带认证的网关代理、且一租户一浏览器实例。
3. **Agent 特有放大**：Browser Agent 把 CDP 交给 LLM 驱动的控制循环后，网页内容（不可信）可经 prompt injection 影响 Agent 的 CDP 操作序列——浏览器沙箱防的是网页攻破浏览器，防不了 Agent 被网页「说服」去把 cookie 读出来发走。防御必须在 Agent 层做动作白名单与敏感域（cookie/凭证类命令）拦截，不能指望 Chromium。

### 5.5 云端浏览器会话隔离要点（检查清单）

以下每条都对应上文一个已确立的机制，不是经验口号：

1. **一会话一浏览器实例、一实例一独立 user-data-dir**：profile 目录含 cookie/localStorage/登录态，复用 profile = 跨租户/跨任务状态串扰（与专题 2 的快照复用问题同构）。实例销毁时连同 profile 一并销毁。
2. **浏览器跑在外层沙箱里**：Chromium 自身沙箱（5.3）是内层；云端部署还必须有外层——每实例独立容器/MicroVM + net ns，使 renderer 逃逸后仍不直达宿主与邻居（纵深来自专题 1/2 的边界叠加）。
3. **禁止 --no-sandbox 上线**；若宿主不支持 user ns 导致必须二选一，应换宿主而不是关沙箱。 [A · 依据同 5.3]
4. **保持站点隔离开启**，不要为省内存关 site-per-process：关掉它等于把 Spectre/UXSS 的进程级防线撤掉，而内存收益官方口径仅约一成量级。 [A · 依据同 5.2]
5. **出站网络经受控 egress**：浏览器是 SSRF 的完美跳板（能访问云元数据 169.254.169.254、内网管理面）。net ns 默认拒绝 + 代理白名单 + 元数据地址硬拦截，属网络层职责（专题 1 的 net ns 只给栈不给策略，策略必须另配）。
6. **下载/上传/剪贴板通道单独设闸**：下载文件落地到隔离目录并做恶意文件处置后再交付任务侧；上传只允许任务工作区内的文件；剪贴板在多租户 GUI 场景默认禁用或单向。
7. **GUI/Desktop 场景（noVNC/远程桌面）**：桌面会话与浏览器会话同生命周期、同租户绑定；VNC 通道必须加密 + 一次性凭证，空闲超时销毁整个桌面环境而不是只关浏览器（桌面里残留的终端/文件管理器同样是执行面）。此条为架构建议，其 VNC 协议层依据未在本轮取得 A 级来源，标**建议（待补证据）**。
8. **扩展与自动化指纹面**：预装扩展等于预装特权代码，须纳入供应链审计；自动化特征（webdriver 标志等）引发的风控问题属可用性议题，不应以削弱沙箱的方式「解决」。

### 5.6 本专题最小实验设想（只设计 · 待执行）

- **假设 H1**：开启站点隔离时，跨站 iframe 位于不同 renderer 进程；关闭（--disable-features=SiteIsolation）后同进程共存可被 /proc 与 chrome://process-internals 观测到差异。
  验证方法（待执行）：自建两站点页互嵌 iframe，两种配置下记录进程列表与站点→进程映射对照。
- **假设 H2**：CDP 端口一旦可被另一 net ns 中的进程连通，即可在无任何凭证的情况下读出测试站点的 cookie。
  验证方法（待执行）：隔离实验网内，一台测试机开 remote-debugging（绑定内网地址），另一台用裸 WebSocket 客户端发 Network.getAllCookies 类命令，记录是否成功；实验只用自建测试账号与测试站点，结束即销毁环境。

**本专题证据条数：5 条 A 级**（Chromium 进程模型官方文档、Site Isolation 官方页、Linux Sandboxing 官方文档、Chrome 安全白皮书、CDP 官方协议文档）。

---

## 附 · 本稿证据总账与缺口

| 专题 | A 级证据条数（独立结论簇） | 主要缺口（下一轮补） |
|---|---|---|
| 1 Linux 隔离 | 9 | 各发行版 unprivileged user ns 默认策略；运行时 setup 期 CVE 的一手公告核验 |
| 2 MicroVM/KVM | 4 | Firecracker 官方 snapshot 文档原文（组成/懒加载/CRC）；恢复后熵/身份处理（VMGenID 类）官方口径 |
| 3 gVisor | 3 | 当前版本 syscall 兼容清单原文；Systrap 平台的现行性能数字（官方新版 benchmark） |
| 4 Wasm | 3 | WasmEdge 官方安全/架构文档；Wasmtime 实例化时延的官方 benchmark 口径 |
| 5 浏览器/GUI | 5 | noVNC/远程桌面通道的官方安全文档；Playwright/Browserbase 类服务的会话隔离官方说明（归线 B 交叉） |
| **合计** | **24** | — |

使用约束：本稿数字仅有两个且均为官方口径并已注明语义范围（Firecracker <125 ms / <5 MiB；Site Isolation 内存 +10–13% 的 Chrome 67 时点口径）。其余性能比较均为定性，未自测前不得在选型材料中量化引用。
