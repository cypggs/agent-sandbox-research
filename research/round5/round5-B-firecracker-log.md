# Round 5 线 B 过程日志：Firecracker 源码深研

- 日期：2026-10-27（Asia/Shanghai）
- 对象：https://github.com/firecracker-microvm/firecracker
- 克隆：`git clone --depth 50` → hidden_files/research/firecracker-src
- HEAD（分析时 rev-parse 实测）：`f0f48ff`（全哈希 f0f48ffcf24748aefde00d606c0bd026039ca95d，2026-10-27 10:02 UTC，"tests: pin the VMM thread whatever order the threads are listed in"）
  - 注：克隆后台完成回执中曾出现一段与本仓不符的 HEAD/目录输出（疑为回执串扰），本日志与报告一律以本会话内多次 `git rev-parse`/`git log` 直接实测为准：f0f48ff，分支 main 与 origin/main 一致。
  - 浅克隆内无 tag（git describe 无输出），版本号以 gh API 为准。
- 最新 release（gh API 实测）：v1.17.0，published 2026-09-10T14:19:40Z —— 与 Round 1 记录一致，无更新。仓库 archived=false，pushed_at 2026-10-27（当日活跃）。
- License：Apache-2.0（gh API spdx + 仓内 LICENSE 原文双证）。
- 规模（实测）：src/**/*.rs 共 128,706 行；vmm crate 263 个 .rs 文件、单元测试函数约 912 个（grep `fn test` 口径）；TODO/FIXME 全 src 共 43 处（vmm 42、seccompiler 1、jailer/firecracker/snapshot-editor/utils 均为 0）；集成测试为 Python pytest 框架（tests/integration_tests，95 个 test_*.py，分 build/functional/performance/security/style 五类）+ Kani 形式化验证入口（test_kani.py、docs/formal-verification.md）。
- 方法：纯静态分析（读 docs 原文 + grep/定点读源码）。未编译、未运行、未建 VM（本机无 /dev/kvm，符合任务约束）。
- 关键证据文件清单：
  - 设备：docs/design.md（Machine Model/Threat Containment）、src/vmm/src/devices/{virtio,legacy,acpi,pseudo}/、docs/device-hotplug.md、docs/entropy.md、docs/ballooning.md
  - seccomp：docs/seccomp.md、src/firecracker/src/seccomp.rs（SeccompConfig）、src/vmm/src/seccomp.rs（BpfThreadMap/get_empty_filters）、resources/seccomp/*.json、src/seccompiler/
  - jailer：docs/jailer.md、src/jailer/src/{main.rs,env.rs,cgroup.rs,chroot.rs,resource_limits.rs}（Env::run 顺序：join netns → resource_limits → cgroup → chroot → 建 /dev 节点 → fork/降权 exec）
  - snapshot/Q13：docs/snapshotting/{snapshot-support.md,handling-page-faults-on-snapshot-resume.md,random-for-clones.md,network-for-clones.md,versioning.md}、src/vmm/src/persist.rs（create_snapshot/restore_from_snapshot/snapshot_state_sanity_check/validate_cpu_vendor）、src/vmm/src/snapshot/{mod.rs,crc.rs}（CRC64Writer、Snapshot::load）、src/vmm/src/devices/acpi/vmgenid.rs（VmGenId::make_genid/do_post_restore/activate）、src/vmm/src/builder.rs:543 注释（恢复 DeviceManager 后于 VMGenID 中断）、src/vmm/src/devices/acpi/vmclock.rs、src/rebase-snap/（diff 合并）、src/snapshot-editor/
  - 兼容：docs/cpu_templates/cpu-templates.md、README Tested platforms、docs/kernel-policy.md、docs/prod-host-setup.md
- 未做：未读完全部 device 实现细节（net/block 的限速器内部、dumbo TCP 栈只登记存在）；未核对每个 virtio 设备的引入版本（报告不写未核实的版本归属）。
