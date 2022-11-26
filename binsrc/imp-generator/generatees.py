# Module containing definitions of the systemd units.

from definitions import *

generatees = {
    ## Binfmts
    BinFmt("WSLInterop.conf", ":WSLInterop:M::MZ::/init:PF"),

    ## System units to enable
    EnableSystemUnit("systemd-machined.service", "multi-user.target"),

    ## Units
    ### imp-fixshm.service / bottle-imp - Fix the /dev/shm symlink to be a mount
    ImpUnit("imp-fixshm.service",
        "local-fs-pre.target",
        """# imp-generator

[Unit]
Description=bottle-imp - Fix the /dev/shm symlink to be a mount
DefaultDependencies=no
Before=local-fs-pre.target
Before=imp-remount-root-shared.service
Before=procps.service syslog.service systemd-firstboot.service systemd-sysctl.service systemd-sysusers.service systemd-tmpfiles-clean.service systemd-tmpfiles-setup-dev.service systemd-tmpfiles-setup.service
ConditionPathExists=/dev/shm
ConditionPathIsSymbolicLink=/dev/shm
ConditionPathIsMountPoint=/run/shm

[Service]
Type=oneshot
ExecStart=/usr/lib/bottle-imp/imp-executor devshm

[Install]
WantedBy=local-fs-pre.target
"""),

    ### imp-pstorefs.service / bottle-imp - Kernel Persistent Storage File System
    ImpUnit ("imp-pstorefs.service",
        "local-fs-pre.target",
        """# imp-generator

[Unit]
Description=bottle-imp - Kernel Persistent Storage File System
DefaultDependencies=no
Before=local-fs-pre.target
Before=systemd-pstore.service
ConditionPathExists=/sys/fs/pstore
ConditionPathIsMountPoint=!/sys/fs/pstore

[Service]
Type=oneshot
ExecStart=/usr/lib/bottle-imp/imp-executor pstore

[Install]
WantedBy=local-fs-pre.target
"""),

    ### imp-remount-root-shared.service / bottle-imp - Remount Root Filesystem Shared
    ImpUnit ("imp-remount-root-shared.service",
        "local-fs-pre.target",
        """# imp-generator

[Unit]
Description=bottle-imp - Remount Root Filesystem Shared
DefaultDependencies=no
Before=local-fs-pre.target
Before=systemd-remount-fs.service

[Service]
Type=oneshot
ExecStart=/usr/lib/bottle-imp/imp-executor rrfs

[Install]
WantedBy=local-fs-pre.target
"""),

    ### imp-securityfs.service / bottle-imp - Kernel Security File System
    ImpUnit ("imp-securityfs.service",
        "local-fs-pre.target",
        """# imp-generator

[Unit]
Description=bottle-imp - Kernel Security File System
DefaultDependencies=no
Before=local-fs-pre.target
Before=apparmor.service
ConditionSecurity=apparmor
ConditionPathExists=/sys/kernel/security
ConditionPathIsMountPoint=!/sys/kernel/security

[Service]
Type=oneshot
ExecStart=/usr/lib/bottle-imp/imp-executor security

[Install]
WantedBy=local-fs-pre.target
"""),

    ### imp-wslg-socket.service / bottle-imp - WSLg socket remount service
    ImpUnit ("imp-wslg-socket.service",
        "multi-user.target",
        """# imp-generator

[Unit]
Description=bottle-imp - WSLg socket remount service
After=tmp.mount
After=systemd-tmpfiles-setup.service
Before=multi-user.target
ConditionPathExists=/tmp/.X11-unix
ConditionPathIsMountPoint=!/tmp/.X11-unix
ConditionPathExists=/mnt/wslg/.X11-unix

[Service]
Type=oneshot
ExecStart=/usr/lib/bottle-imp/imp-executor wslg

[Install]
WantedBy=multi-user.target
"""),

    ## Tmpfiles

    ### imp-x11.conf
    TmpFile ("imp-x11.conf",
        """# imp-generator

# Does what systemd does but does not automatically remove an existing
# /tmp/.X11-unix (protect WSLg link).

# Make sure these are created by default so that nobody else can
d! /tmp/.X11-unix 1777 root root 10d
D! /tmp/.ICE-unix 1777 root root 10d
D! /tmp/.XIM-unix 1777 root root 10d
D! /tmp/.font-unix 1777 root root 10d

# Unlink the X11 lock files
r! /tmp/.X[0-9]*-lock
"""),

    ## Override files.

    ### user-runtime-dir@.service.d/override.conf - fix up user runtime directory
    UnitOverride ("user-runtime-dir@.service", """# imp-generator

[Service]
ExecStart=
ExecStart=/usr/lib/bottle-imp/imp-user-runtime-dir.sh start %i
ExecStop=
ExecStop=/usr/lib/bottle-imp/imp-user-runtime-dir.sh stop %i
"""),

}
