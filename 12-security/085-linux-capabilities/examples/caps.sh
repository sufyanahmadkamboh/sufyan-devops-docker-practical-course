#!/bin/sh
# caps.sh: print the names of this process's effective capabilities (decodes CapEff from /proc/self/status)
names="CHOWN DAC_OVERRIDE DAC_READ_SEARCH FOWNER FSETID KILL SETGID SETUID SETPCAP LINUX_IMMUTABLE NET_BIND_SERVICE
NET_BROADCAST NET_ADMIN NET_RAW IPC_LOCK IPC_OWNER SYS_MODULE SYS_RAWIO SYS_CHROOT SYS_PTRACE SYS_PACCT SYS_ADMIN
SYS_BOOT SYS_NICE SYS_RESOURCE SYS_TIME SYS_TTY_CONFIG MKNOD LEASE AUDIT_WRITE AUDIT_CONTROL SETFCAP MAC_OVERRIDE
MAC_ADMIN SYSLOG WAKE_ALARM BLOCK_SUSPEND AUDIT_READ PERFMON BPF CHECKPOINT_RESTORE"
hex=$(awk '/^CapEff/ {print $2}' /proc/self/status)
value=$((0x$hex))
bit=0
found=""
for name in $names; do
  [ $(( (value >> bit) & 1 )) -eq 1 ] && found="$found $name"
  bit=$((bit + 1))
done
echo "CapEff=$hex:${found:- (none)}"
