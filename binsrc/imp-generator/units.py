# Module containing definitions of the systemd units.

import os

def enable_system_unit(unit, target, normal_dir):

    # Create target directory if it does not already exist.
    if not os.path.isdir (os.path.join (normal_dir, target)):
        os.mkdir (os.path.join (normal_dir, target))

    # Link to the system unit.
    if os.path.exists(os.path.join(normal_dir, target, unit)):
        os.unlink(os.path.join(normal_dir, target, unit))

    os.symlink(os.path.join('/lib/systemd/system', unit),
        os.path.join(normal_dir, target, unit))


def enable_imp_unit(unit, unit_text, target, normal_dir):
    # Create the target directory if it does not already exist.
    if not os.path.isdir (os.path.join (normal_dir, target)):
        os.mkdir (os.path.join (normal_dir, target))

    # Write out the unit file.
    with open (os.path.join (normal_dir, unit), 'w') as u:
        u.write (unit_text)

    # Link to the just-created unit.
    if os.path.exists(os.path.join(normal_dir, target, unit)):
        os.unlink(os.path.join(normal_dir, target, unit))

    os.symlink (os.path.join (normal_dir, unit),
        os.path.join(normal_dir, target, unit))


def enable_override_conf (unit, override_text, normal_dir):
    # Create the override directory if it does not already exist.
    override_dir = os.path.join (normal_dir, unit + '.d')

    if not os.path.isdir (override_dir):
        os.mkdir (override_dir)

    # Write out the override file.
    with open (os.path.join(override_dir, 'override.conf'), 'w') as o:
        o.write (override_text)


def enable_binfmt(binfmt, binfmt_text):
    # Create the dynamic binfmt.d if it does not already exist.
    if not os.path.isdir ('/run/binfmt.d'):
        os.mkdir ('/run/binfmt.d')

    # Write out the override file.
    with open (os.path.join ('/run/binfmt.d', binfmt), 'w') as b:
        b.write (binfmt_text)


def enable_tmpfile(tmpfile, tmpfile_text):
    # Create the dynamic tmpfiles.d if it does not already exist.
    if not os.path.isdir ('/run/tmpfiles.d'):
        os.mkdir ('/run/tmpfiles.d')

    # Write out the override file.
    with open (os.path.join ('/run/tmpfiles.d', tmpfile), 'w') as t:
        t.write (tmpfile_text)


## Units

### imp-fixshm.service / bottle-imp - Fix the /dev/shm symlink to be a mount

imp_fixshm = """# imp-generator

[Unit]
Description=bottle-imp - Fix the /dev/shm symlink to be a mount
DefaultDependencies=no
Before=local-fs-pre.target.target
Before=procps.service syslog.service systemd-firstboot.service systemd-sysctl.service systemd-sysusers.service systemd-tmpfiles-clean.service systemd-tmpfiles-setup-dev.service systemd-tmpfiles-setup.service
ConditionPathExists=/dev/shm
ConditionPathIsSymbolicLink=/dev/shm
ConditionPathIsMountPoint=/run/shm

[Service]
Type=oneshot
ExecStart=/usr/lib/bottle-imp/imp-executor devshm

[Install]
WantedBy=local-fs-pre.target
"""

### imp-pstorefs.service / bottle-imp - Kernel Persistent Storage File System

imp_pstorefs = """# imp-generator

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
"""

### imp-securityfs.service / bottle-imp - Kernel Security File System

imp_securityfs="""# imp-generator

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
"""

### imp-remount-root-shared.service / bottle-imp - Remount Root Filesystem Shared

imp_remount_root_shared="""# imp-generator

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
"""

### imp-wslg-socket.service / bottle-imp - WSLg socket remount service

imp_wslg_socket = """# imp-generator

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
"""

## Override files.

### user-runtime-dir@.service.d/override.conf - fix up user runtime directory

user_runtime_dir_override="""# imp-generator

[Service]
ExecStart=
ExecStart=/usr/lib/bottle-imp/imp-user-runtime-dir.sh start %i
ExecStop=
ExecStop=/usr/lib/bottle-imp/imp-user-runtime-dir.sh stop %i
"""

## Binfmts

### WSLInterop.conf

bin_WSLInterop=""":WSLInterop:M::MZ::/init:PF"""

## Tmpfiles

### imp-x11.conf

tmp_imp_x11="""# imp-generator

# Does what systemd does but does not automatically remove an existing
# /tmp/.X11-unix (protect WSLg link).

# Make sure these are created by default so that nobody else can
d! /tmp/.X11-unix 1777 root root 10d
D! /tmp/.ICE-unix 1777 root root 10d
D! /tmp/.XIM-unix 1777 root root 10d
D! /tmp/.font-unix 1777 root root 10d

# Unlink the X11 lock files
r! /tmp/.X[0-9]*-lock
"""
