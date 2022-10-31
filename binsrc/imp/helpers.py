# Helper functions module

import os
import subprocess
import sys
import psutil
import pwd


def get_in_windows_terminal():
    """Are we inside a Windows Terminal session?"""
    if 'WT_SESSION' in os.environ:
        return True
    else:
        return False


def get_login_session_user():
    """Get the user logged into the current session, pre-setuid."""
    # This environment variable is set by the setuid wrapper.
    return os.environ["IMP_LOGNAME"]


def get_systemd_state():
    """Get the systemd state."""
    sc = subprocess.run(["systemctl", "is-system-running"],
                        capture_output=True, text=True)
    return sc.stdout.rstrip()


def get_systemd_machined_active():
    """Get the systemd-machined service state."""
    sc = subprocess.run(["systemctl", "is-active", "systemd-machined.service", "--quiet"])
    return (sc.returncode == 0)


def prelaunch_checks():
    """Check that we are on the correct platform, and as the correct user."""

    # Is this Linux?
    if not sys.platform.startswith('linux'):
        sys.exit("imp: not executing on the Linux platform - how did we get here?")

    # Is this WSL 1?
    root_type = list(filter(lambda x: x.mountpoint == '/',
                            psutil.disk_partitions(all=True)))[0].fstype
    if root_type == 'lxfs' or root_type == 'wslfs':
        sys.exit("imp: systemd is not supported under WSL 1.")

    # Is this WSL 2?
    if not os.path.exists('/run/WSL'):
        if 'microsoft' not in os.uname().release:
            sys.exit("imp: not executing under WSL 2 - how did we get here?")

    # Is systemd already running as pid 1?
    if not psutil.Process(1).name() == 'systemd':
        sys.exit("imp: systemd support does not appear to be enabled.")

    # Are we effectively root?
    if os.geteuid() != 0:
        sys.exit("imp: must execute as root - has the setuid bit gone astray?")


def validate_is_real_user(username):
    """Check that the supplied username is a real user; otherwise exit."""
    try:
        pwd.getpwnam(username)
    except KeyError:
        sys.exit("imp: specified user does not exist")
