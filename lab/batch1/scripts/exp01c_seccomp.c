/* EXP-01c seccomp probe (C version). Usage: exp01c_seccomp <0|1>
 * 1 = install seccomp filter blocking mount/umount2/reboot/init_module/
 *     delete_module/finit_module with EPERM, then try mount.
 * Prints machine-parseable result lines. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/socket.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <linux/audit.h>
#include <stddef.h>

static int install_filter(void) {
    long blocked[] = {165, 166, 169, 175, 176, 313};
    int nb = 6;
    struct sock_filter f[64];
    int n = 0;
    f[n++] = (struct sock_filter){BPF_LD | BPF_W | BPF_ABS, 0, 0, offsetof(struct seccomp_data, arch)};
    f[n++] = (struct sock_filter){BPF_JMP | BPF_JEQ | BPF_K, 1, 0, AUDIT_ARCH_X86_64};
    f[n++] = (struct sock_filter){BPF_RET | BPF_K, 0, 0, SECCOMP_RET_ERRNO | (1 & SECCOMP_RET_DATA)};
    for (int i = 0; i < nb; i++) {
        f[n++] = (struct sock_filter){BPF_LD | BPF_W | BPF_ABS, 0, 0, offsetof(struct seccomp_data, nr)};
        f[n++] = (struct sock_filter){BPF_JMP | BPF_JEQ | BPF_K, 0, 1, (unsigned)blocked[i]};
        f[n++] = (struct sock_filter){BPF_RET | BPF_K, 0, 0, SECCOMP_RET_ERRNO | (1 & SECCOMP_RET_DATA)};
    }
    f[n++] = (struct sock_filter){BPF_RET | BPF_K, 0, 0, SECCOMP_RET_ALLOW};
    struct sock_fprog prog = {(unsigned short)n, f};
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) return -1;
    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) != 0) return -2;
    return 0;
}

int main(int argc, char **argv) {
    int filtered = argc > 1 && argv[1][0] == '1';
    if (filtered) {
        int rc = install_filter();
        printf("SECCOMP install_rc=%d errno=%d\n", rc, errno);
        if (rc != 0) return 1;
    }
    const char *target = "/tmp/exp01c_mnt_target";
    mkdir("/tmp/exp01c_mnt_target", 0755);
    errno = 0;
    long rc = syscall(SYS_mount, "tmpfs", target, "tmpfs", 0, NULL);
    int e = errno;
    int mounted = 0;
    FILE *m = fopen("/proc/self/mounts", "r");
    char line[512];
    while (m && fgets(line, sizeof line, m))
        if (strstr(line, target) && strstr(line, "tmpfs")) mounted = 1;
    if (m) fclose(m);
    printf("MOUNT rc=%ld errno=%d (%s) mounted=%d\n", rc, e, strerror(e), mounted);
    /* other functionality */
    int fd = open("/tmp/exp01c_io.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    int io_ok = 0;
    if (fd >= 0) { io_ok = write(fd, "canary-io", 9) == 9; close(fd); }
    int s = socket(AF_INET, SOCK_STREAM, 0);
    printf("OTHER getpid=%d io_ok=%d socket_ok=%d\n", getpid(), io_ok, s >= 0);
    if (s >= 0) close(s);
    return 0;
}
