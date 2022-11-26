#! /usr/bin/env python3

import os
import sys

import mountie

def print_help_message():
    """Display a help message for imp-executor."""

    print ("""imp-executor: internal functions for bottle-imp

    You should not use this directly under normal circumstances.
    It should only be called by bottle-imp provided services.

    Operations:

    help        Display this message.

    rrfs        Remount root filesystem shared.
    devshm      Fix /dev/shm mount.
    pstore      Mount pstore filesystem.
    security    Mount security filesystem.
    wslg        Bind mount WSL .X11-unix.
    """)


def fix_dev_shm():
    """Move the tmpfs for shared memory to /dev/shm and bind mount it from /run/shm."""
    os.unlink ("/dev/shm")
    os.mkdir ("/dev/shm")
    mountie.mount ("/run/shm", "/dev/shm", "", mountie.MS_MOVE)
    mountie.mount ("/dev/shm", "/run/shm", "", mountie.MS_BIND)
    # os.rmdir ("/run/shm")
    # os.symlink ("/dev/shm", "/run/shm")


def mount_pstore_filesystem():
    """Mount the pstore filesystem."""
    mountie.mount ("pstore", "/sys/fs/pstore", "pstore",
        mountie.MS_NOSUID | mountie.MS_NODEV | mountie.MS_NOEXEC)
    

def mount_security_filesystem():
    """Mount the security filesystem."""
    mountie.mount ("securityfs", "/sys/kernel/security", "securityfs",
        mountie.MS_NOSUID | mountie.MS_NODEV | mountie.MS_NOEXEC)


def remount_root_shared():
    """Remount the root filesystem shared."""
    mountie.mount ("none", "/", "", mountie.MS_REC | mountie.MS_SHARED, "")


def remount_wslg():
    """Remount the WSLg socket in the appropriate place."""
    mountie.mount ("/mnt/wslg/.X11-unix", "/tmp/.X11-unix", "",
        mountie.MS_BIND | mountie.MS_RDONLY)
    # required because flags other than MS_BIND ignored in first call.
    mountie.mount ("none", "/tmp/.X11-unix", "",
        mountie.MS_REMOUNT | mountie.MS_BIND | mountie.MS_RDONLY)


def entrypoint():
    """Entry point for the imp-executor."""

    # Check the command-line arguments.
    if (len (sys.argv) < 2):
        sys.exit ("imp-executor requires the operation to perform")

    operation = sys.argv[1]

    if operation == "help":
        print_help_message()
    elif operation == "rrfs":
        remount_root_shared()
    elif operation == "pstore":
        mount_pstore_filesystem()
    elif operation == "security":
        mount_security_filesystem()
    elif operation == "devshm":
        fix_dev_shm()
    elif operation == "wslg":
        remount_wslg()
    else:
        print ("imp-executor: operation not recognized")


entrypoint()

# End of file.
