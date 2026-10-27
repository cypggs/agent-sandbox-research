# Round 5 · 线 C：gVisor 选读（三线）+ OWASP 2026 双标注落地

> 执行：2026-10-27（Asia/Shanghai），retrieved_at 统一 2026-10-27
> 输入：files/OPEN-QUESTIONS.md Q12/Q31、round1-C-principles.md 专题 3（gVisor）、round1-D-threat-bench.md §1、round2-A-evidence-debt.md §1（OWASP 映射依据）
> 方法：只追 Sentry / Gofer / 平台三线，不全仓通读。官方文档原文（gvisor.dev）+ 源码结构定位双轨。
> 源码：浅克隆 `hidden_files/research/gvisor-src`，HEAD `4777ee7`（4777ee7811e235e66d5825f6c6ae5ccd3ccccfb3，2026-10-27 当日）。注：`--depth 30` 克隆两次因 index-pack 失败未完成（残留 shallow.lock、无 commit），改 `--depth 1` 成功，工作树完整、足够结构定位；历史深度对本任务无影响。
> 纪律：未运行 gVisor、未改 products.csv；除任务二指定的 D 线底稿标注段外未改任何既有文件。

---

## 任务一 · gVisor 选读

### 线 1 · Sentry：syscall 拦截、实现调用路径与 Sentry 自身隔离

**关键文件/目录（克隆实测存在）**

| 位置 | 角色 |
|---|---|
| `runsc/main.go`、`runsc/boot/loader.go`、`runsc/boot/controller.go` | 入口与装配：runsc 启动后由 boot loader 按配置创建平台与 Sentry 内核，controller 提供运行时控制面 |
| `pkg/sentry/platform/`（`platform.go` 的 `Platform`/`Context`/`AddressSpace` 接口） | 拦截层抽象：平台负责 syscall 拦截、上下文切换、地址空间映射 |
| `pkg/sentry/platform/systrap/`（`README.md`、`filters.go`、`context_queue.go`、`lib_amd64.s`/`lib_arm64.s`） | 默认平台实现：stub 线程 + seccomp trap + sysmsg 协议 |
| `pkg/sentry/kernel/task_syscall.go`、`pkg/sentry/kernel/task_run.go` | Sentry 内核的任务执行循环：进入 Sentry 后按 syscall 号分发 |
| `pkg/sentry/syscalls/linux/linux64.go` | amd64 syscall 实现表本体：`AMD64 = &kernel.SyscallTable{...}`，每条为 `SupportedPoint`（全实现）/ 带注记的部分实现 / `syscalls.Error(..., ENOSYS, ...)`（未实现） |
| `pkg/seccomp/`（含 `precompiledseccomp/`）、`runsc/boot/filter/` | runsc 进程群（含 Sentry）自身 seccomp 滤镜的定义与装配位置 |

**机制结论**

1. **调用路径**：应用线程发出 syscall → 平台层拦截（Systrap 路径：stub 线程预装 seccomp 过滤以 `SECCOMP_RET_TRAP` 触发 `SIGSYS`，sysmsg stub 信号处理程序把事件通知 Sentry；KVM 路径：借硬件虚拟化做地址空间隔离与切换）→ Sentry 的 `kernel.Task` 执行循环按 `SyscallTable` 分发到 `pkg/sentry/syscalls/linux` 的独立实现 → 结果回写 stub 线程恢复应用。**全程不存在透传**：官方 Security Model 的第一条工程原则即 "No system call is passed through directly to the host"，未实现的 syscall 在表里直接是 ENOSYS 条目（如 134 uselib、136 ustat、139 sysfs，本轮源码与官网兼容表逐字对上）。[A · 源码定位 + https://gvisor.dev/docs/architecture_guide/security/ ]
2. **Sentry 自身的隔离**：Sentry 是被反过来关住的一方——官方 Security Model 明示 Sentry 对宿主的全部高层交互只剩三件：① 经已连接 socket 与 Gofer 通信并接收其回传的 FD；② 一个显式枚举的**最小宿主 syscall 集**（FD 复制/关闭、同步、定时器、信号类；**不含**新建 socket 与打开文件，除非分别启用 host networking / directfs）；③ 向虚拟以太设备收发包。Sentry 运行在**空 mount namespace** 中、本身无文件系统视图；其进程的 seccomp 滤镜定义与装配位于 `pkg/seccomp/` 与 `runsc/boot/filter/`（本轮定位到目录与包，未逐行审滤镜条目，该粒度标 B）。[A（交互枚举与空 mount ns，官方文档）/ B（滤镜装配细节定位）]
3. 平台层现状：现行三实现为 Systrap（默认）、KVM、ptrace（已停止支持），另有 `pkg/sentry/platform/slimvm/` 目录存在，本轮未展开，其定位标未证实，不写入结论。

**对选型的含义（一句）**：gVisor 的兼容性与性能由 Sentry 这个"第二内核"的实现子集决定而不是由过滤规则决定，选型前必须拿目标负载的真实 syscall 面对着兼容表先验核对，不能按"加强版容器"估算。

### 线 2 · Gofer：协议面、代理路径与权限收敛

**关键文件/目录**

| 位置 | 角色 |
|---|---|
| `runsc/cmd/gofer.go` | Gofer 进程入口（runsc 的 gofer 子命令）：按 mount 配置提供文件服务、捐赠 FD |
| `pkg/lisafs/`（`channel.go`、`client.go` 等） | **现行** Sentry↔Gofer 协议 LISAFS 的实现（通道与客户端） |
| `pkg/sentry/fsimpl/gofer/`（`gofer.go`、`filesystem.go`、`directfs_inode.go`、`handle.go`） | Sentry 侧 gofer 文件系统：以 `lisafs.Client` 经 socket 连接 Gofer，`initClientAndGetRoot` 取得根 inode 与宿主 FD |
| `pkg/p9/` | 9P 协议包仍在树内，但本轮 grep 其在 `pkg/sentry` 与 `runsc` 下的引用为**零命中**——现行文件路径已不经 9P |

**机制结论**

1. **协议面已换代（对 Round 1 线 C 表述的精化修正）**：Round 1 线 C 底稿称文件操作经"9P 类协议"交 Gofer——按当前源码，现行协议是 **LISAFS**（`pkg/lisafs`），fsimpl/gofer 与 runsc/cmd/gofer.go 均以 lisafs 为据；9P 是前代协议，`pkg/p9` 仅作遗留保留。后续报告引用 Gofer 协议应写 LISAFS，写"9P"须注明为历史沿革。[A · 源码引用关系实测]
2. **代理路径与收敛点**：Sentry 不能直接打开宿主文件（见线 1），文件打开由 Gofer 在宿主侧执行并**回传已打开的 FD**，Sentry 之后对 FD 直接读写（官方 Security Model 原文）。权限收敛因此落在两处：Gofer 的挂载根/导出范围（runsc mount 配置，即沙箱文件面的全集）与 Gofer 打开时的校验；Sentry 即使被攻破，其文件面也不能凭空越出 Gofer 导出的挂载集合——除下条例外。[A · 官方文档 + 源码定位]
3. **例外：directfs**。`runsc/config` 的 `FileAccess`/`FileAccessMounts` 与 fsimpl/gofer 的 directfs 路径构成一个可配置的旁路：启用 directfs 时 Sentry 可对 Gofer 捐赠的宿主 FD 直接操作（官方 Security Model 明示这是 Sentry"打开文件"禁令的例外条件），以性能换取代理收敛的弱化。选型与安全评审时 directfs 必须当**安全参数**而非性能开关审查。[A · 官方文档 + `pkg/sentry/fsimpl/gofer/directfs_inode.go`、`runsc/cmd/gofer.go` 的 io-fds 捐赠逻辑定位]

**对选型的含义（一句）**：Gofer/LISAFS 是 gVisor 文件面的信任收敛点，挂载导出范围就是文件安全边界；凡启用 directfs 的部署，其隔离结论不能沿用默认形态的评估。

### 线 3 · 平台：Systrap 默认的官方依据、KVM 适用场景、兼容清单（Q12）

**关键文件/目录与文档**

| 位置 | 内容 |
|---|---|
| `pkg/sentry/platform/systrap/README.md`、`filters.go` | Systrap 机制原文：`SECCOMP_RET_TRAP` → `SIGSYS` → sysmsg stub 与 Sentry 的通信协议、stub 线程初始化（装过滤、共享备用信号栈、注册 SIGSYS/SIGSEGV 等处理） |
| https://gvisor.dev/docs/architecture_guide/platforms/ | Platform Guide：三实现对比与默认沿革的官方原文（下引） |
| https://gvisor.dev/docs/user_guide/compatibility/ + `/linux/amd64/` | 兼容性文档现行位置（Q12，详见下节） |

**机制结论**

1. **Systrap 为何成为默认（官方依据，三点均有原文）**：① Platform Guide 明载 "`systrap` replaced `ptrace` as the default gVisor platform in mid-2023"，且 ptrace 平台"no longer supported and is expected to eventually be removed entirely"；② ptrace 的问题是**上下文切换开销高**，syscall 密集型应用代价显著（`PTRACE_SYSEMU` 逐次陷入），Systrap 以 seccomp trap + 共享信号栈/sysmsg 协议替代该路径；③ Systrap **不需要硬件虚拟化**，在 VM 内与无虚拟化支持的机器上可用，覆盖面大于 KVM 平台。即默认之争的裁决标准是"无虚拟化依赖 + 低拦截开销 + 可维护性"，不是隔离强度排序。[A · Platform Guide + systrap README]
2. **当前平台选型口径（官方）**：Platform Guide 的现行指引是情境化的——"when running on bare-metal (not inside a VM), the KVM platform will provide the best performance. The systrap platform is a better choice when running inside a VM, or on a machine without virtualization support."[A · 同上]
3. **KVM 平台的适用场景**：KVM 平台下 Sentry 同时充当 guest OS 与 VMM，借处理器虚拟化扩展提升地址空间切换的隔离与性能，**裸金属最佳**；嵌套 VM 内可行但因嵌套虚拟化开销，官方称 Systrap 在该场景"often provide better performance"。[A · 同上]

**对选型的含义（一句）**：平台选择按宿主形态而非偏好——裸金属才考虑 KVM，云上 VM 内（含本项目的 LAB-MINI 类嵌套环境）默认 Systrap 就是官方最优解，不要为"用上虚拟化"而强切 KVM。

### Q12 专项：兼容清单在哪里维护、覆盖口径如何声明、旧性能数字为何不可引用

**兼容清单（本问前半，已结案级证据）**

- **现行位置**：总览页 https://gvisor.dev/docs/user_guide/compatibility/ （"What works / What doesn't work"），逐 syscall 表按架构分开：https://gvisor.dev/docs/user_guide/compatibility/linux/amd64/ 与同路径 arm64。[A]
- **维护方式**：amd64 表页首自述 "**This page is automatically generated from the source code.**"——其源头即线 1 的 `pkg/sentry/syscalls/linux/linux64.go` 的 `AMD64.SyscallTable` 条目元数据（全实现/部分实现注记/ENOSYS 未实现三态逐条对应，本轮抽查 uselib、ustat、sysfs 三条与网页表述逐字一致）。即清单不是独立维护的文档，而是**随源码生成的派生视图**，版本口径 = 抓取时点的源码/站点生成版本。[A · 网页自述 + 源码抽查互证]
- **覆盖口径（2026-10-27 抓取时点）**：amd64 共 352 条 syscall，292 条 full-or-partial、60 条 unsupported。**该数字是生成时点快照，会随源码演进而变，引用必须带抓取日期，不得当固定常数。**[A]
- **官方对覆盖口径的自我限定（引用清单时必须连带）**：总览页明示 ①"未实现 ≠ 应用不可用"——未实现部分多为已有 syscall 的替代变体，语言运行时/库会探测回退（如 io_uring 不全但其他 I/O syscall 可用，程序实际照常工作），并直言"looking through the list of supported syscalls is not necessarily a good measure of how widely compatible gVisor is"；②发布流程对 Python、Java、Node.js、PHP、Go 五种语言运行时跑回归测试保兼容。[A · 兼容总览页]
- **官方自列的已知缺口（选型硬约束，均出自总览页）**：沙箱内 cgroups 只做资源**记账**不做**限额**（限额靠宿主 cgroup 包裹整个 gVisor，且沙箱内进程间无法互相限额）；块设备文件系统（ext4/fat32 等）不能在沙箱内挂载；iptables 仅部分支持；io_uring **默认禁用**、启用后仅基础 I/O；沙箱内使用 KVM 不支持；自定义硬件设备文件一般不支持（NVIDIA GPU、TPU 为明示例外）；K8s 集成另有 GKE Sandbox 的不兼容清单。[A · 同上]

**Systrap 现行性能数字（本问后半，结论为"官方缺位"）**

- 本轮检索范围：Platform Guide、Performance Guide（https://gvisor.dev/docs/architecture_guide/performance/ ，Round 1 线 C 已读）、兼容总览与 systrap README。Platform Guide 只给**定性**选型指引（KVM 裸金属最佳 / VM 内 Systrap 更好），**没有任何 Systrap 平台的现行基准数字**；Performance Guide 的图表数字仍是旧 ptrace 平台口径。即官方现行公开材料中不存在可引用的 Systrap 性能数字集。[A · 上列页面逐页核查后的否定性结论，检索范围已声明]
- **旧 ptrace 数字为何不可引用（再确认）**：①其测量对象平台已被官方标为不再支持、预期移除，拦截机制（PTRACE_SYSEMU 逐 syscall 陷入）与 Systrap（seccomp trap + sysmsg stub + 共享栈）完全不同，倍数关系不迁移；②Performance Guide 自身即注明其数字基于旧平台与特定 GCE 机型、不代表当前 Systrap 的最优情形（Round 1 线 C 已录）。继续引用等于把已退役实现的开销安到现行默认实现头上。[A]

**Q12 结案建议**：**建议结案，分两段口径**——①兼容清单部分以 A 级解答结案：位置、生成式维护方式、覆盖声明口径与官方限定、企业级缺口如上，后续引用带抓取日期即可；②Systrap 性能数字部分以"**官方现行材料未提供**"结案登记：这不是待查问题而是已查实的缺位，数字只能由 D 线 B7 在目标版本/Systrap 上自测产生（依赖 LAB-REF），不再作为独立未决问题挂起。建议 OPEN-QUESTIONS Q12 状态改写为"已结案（清单 A 级；性能数字官方缺位、转 B7 自测）"，最终改判由整合线执行。

---

## 任务二 · OWASP 2026 双标注落地（Q31 执行）

**实际修改（唯一被改动的既有文件）**：`hidden_files/research/round1-D-threat-bench.md`
- 位置：§1 内、§1.0（方法）之后、T01 之前，新增 **§1.0.1「编号双标注说明（OWASP LLM Top 10，Round 5 线 C 补入，2026-10-27）」**，占修改后文件第 **49–61 行**（文件总行数 517 → 531）。
- 内容：双标注规则声明（正文保留 2025 编号、后续引用一律带年份、裸编号视为歧义）+ 五条映射表 + LLM07 补注 + 证据等级注。**未改动任何威胁条目正文、编号、§1.27 来源表及其他章节。**

**映射表副本（与底稿 §1.0.1 内表一致；映射以 round2-A §1 的回原文核实结果为准）**

| 本底稿编号（2025） | 2026 版编号 | 变化 | 在本矩阵的引用位置与用途 |
|---|---|---|---|
| LLM01:2025 Prompt Injection | LLM01:2026 Prompt Injection | 不变 | T19 的治理框架锚点 |
| LLM02:2025 Sensitive Information Disclosure | LLM02:2026 Sensitive Information Disclosure | 不变 | T17 的泄露面归类（凭证/上下文回显） |
| LLM03:2025 Supply Chain | LLM04:2026 Supply Chain | 03 → 04 | T13 恶意依赖的治理思路出处（§1.27 之 S1） |
| LLM06:2025 Excessive Agency | LLM03:2026 Excessive Agency | 06 → 03 | T20 的定义锚点（权限/工具/自主度过量） |
| LLM10:2025 Unbounded Consumption | LLM06:2026 Unbounded Consumption | 10 → 06 | T22 的资源维度归类出处 |

补注（同底稿）：T17 另引用的 LLM07:2025 System Prompt Leakage → LLM08:2026 Hidden Context Exposure（更名扩围）。
证据等级：2025 侧 A（Round 2 回原文逐条核）；2026 侧 A-/B+（官网新闻稿 + 官网 roundup 用法 + 多源转录互证；2026 版 PDF 全文未逐字核，见 round2-A §1.2、Q31）。

**遗留提示（不在本线改动范围，留整合线）**：D 线底稿 §1.27 的 S1 来源行等级仍标 "B（待回原文升 A）"、S10 同理——Round 2 回填建议第 11 条曾建议将其升 A 并加注。本线按任务书只加标注段未动来源表；§1.0.1 已实质覆盖加注需求，S1/S10 的等级单元格是否回填请整合线裁定。

---

## 本线自检与未证实项

- 三线结论一句版：Sentry 线——拦截靠平台层、实现靠 Sentry 独立重写且零透传，Sentry 自身被最小宿主面反向关住；Gofer 线——现行协议是 LISAFS 而非 9P，Gofer 的挂载导出即文件信任边界，directfs 是必须单独审查的旁路；平台线——Systrap 凭无虚拟化依赖与低拦截开销成默认，KVM 只在裸金属占优，平台按宿主形态选。
- 未证实/未展开：`pkg/sentry/platform/slimvm/` 的定位；Sentry seccomp 滤镜的逐条内容（只定位到 `pkg/seccomp/` 与 `runsc/boot/filter/`）；Gofer 打开时校验的逐项规则（只定位到 fsimpl/gofer 与 cmd/gofer.go）；2026 版 OWASP PDF 全文（沿用 Round 2 的 A-/B+ 口径）。
- 数字纪律：本文件唯一的性能相关数字是兼容覆盖计数（352/292/60，官方生成页快照，已带日期与限定），无任何 Systrap/Firecracker 性能倍数被引用。
