#! /usr/bin/env python3

import argparse
import os
import signal
import subprocess
import sys
import time

import helpers

# Global variables
version = "0.11"

verbose = False
login = None

# Command line parser
def parse_command_line():
    """Create the command-line option parser and parse arguments."""
    parser = argparse.ArgumentParser(
        description = "Helper for using WSL systemd native support.",
        epilog = "For more information, see https://github.com/arkane-systems/bottle-imp/"
    )

    # Version command
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + version)

    # Verbose option
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="display verbose progress messages")

    # Specify username option
    parser.add_argument('-a', '--as-user', action='store',
                        help="specify user to run shell or command as (use with -s or -c)", dest='user')

    # Commands
    group2 = parser.add_argument_group('commands')
    group = group2.add_mutually_exclusive_group(required=True)

    group.add_argument('-i', '--initialize', action='store_true',
                       help='initialize WSL interop for user sessions and hold WSL open until explicit shutdown')
    group.add_argument('-s', '--shell', action='store_true',
                       help='open or connect to a systemd user session, and run a shell in it')
    group.add_argument('-l', '--login', action='store_true',
                       help='open a login prompt for a systemd user session')
    group.add_argument(
        '-c', '--command', help='open or connect to a systemd user session, and run the specified command in it\n(preserves working directory)', nargs=argparse.REMAINDER)
    group.add_argument('-u', '--shutdown', action='store_true',
                       help='shut down systemd and the WSL instance')

    return parser.parse_args()


# Subordinate functions.
def wait_for_systemd():
    """Check if systemd is in the running state, and if not, wait for it."""

    # Unlike in genie, we can presume here that systemd does exist.
    # But it may not be accessible yet. Check for system dbus.
    if not os.path.exists('/run/dbus/system_bus_socket'):
        # wait for it
        print("imp: dbus is not available yet, please wait...", end="", flush=True)

        timeout = 240 # hardcode this for now

        while not os.path.exists('/run/dbus/system_bus_socket'):
            time.sleep(1)
            print(".", end="", flush=True)

            timeout -= 1

        print("")

        if timeout <= 0:
            sys.exit("imp: dbus still not available; cannot continue")

    # Now dbus is available, check for systemd.
    state = helpers.get_systemd_state()

    if 'stopping' in state:
        sys.exit("imp: systemd is shutting down, cannot proceed")

    if 'initializing' in state or 'starting' in state:
        # wait for it
        print("imp: systemd is starting up, please wait...", end="", flush=True)

        timeout = 240 # hardcode this for now

        while ('running' not in state and 'degraded' not in state) and timeout > 0:
            time.sleep(1)
            state = helpers.get_systemd_state()

            print(".", end="", flush=True)

            timeout -= 1

        print("")

        if timeout <= 0:
            print("imp: WARNING: timeout waiting for bottle to start")

    if 'degraded' in state:
        print('imp: WARNING: systemd is in degraded state, issues may occur!')

    if not ('running' in state or 'degraded' in state):
        sys.exit("imp: systemd in unsupported state '"
                 + state + "'; cannot proceed")


# Commands
def do_initialize():
    """Initialize WSL_INTEROP, then fork a blocker, holding the session open until systemctl poweroff."""
    wait_for_systemd()

    # Update the base environment with interop-fu.
    subprocess.run(['systemctl', 'import-environment',
        'WSL_INTEROP', 'WSL2_GUI_APPS_ENABLED', 'WSL_DISTRO_NAME', 'WSLENV', 'NAME', 'HOSTTYPE'])

    # Run wait-forever subprocess.
    subprocess.Popen(['/usr/lib/bottle-imp/wait-forever.sh'],
                     stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     start_new_session = True,
                     preexec_fn=(lambda: signal.signal(signal.SIGHUP, signal.SIG_IGN)))

    print ("imp: systemd environment initialized and instance holding")

    # Exit
    sys.exit(0)


def do_login():
    """Start a systemd login prompt."""
    wait_for_systemd()

    if not helpers.get_systemd_machined_active():
        sys.exit ("imp: cannot launch login; systemd-machined is not active")

    if verbose:
        print("imp: starting login prompt")

    os.execv ('/usr/bin/machinectl', ['machinectl', 'login', '.host'])
    # never get here


def do_shell():
    """Start/connect to a systemd user session with a shell."""
    wait_for_systemd()

    if not helpers.get_systemd_machined_active():
        sys.exit ("imp: cannot launch shell; systemd-machined is not active")

    if verbose:
        print("imp: starting shell")

    if helpers.get_in_windows_terminal():
        os.execv ('/usr/bin/machinectl', ['machinectl',
            '-E', 'WT_SESSION', '-E', 'WT_PROFILE_ID',
            'shell', '-q', login + '@.host'])
    else:
        os.execv ('/usr/bin/machinectl', ['machinectl',
            'shell', '-q', login + '@.host'])
    
    # never get here


def do_command(commandline):
    """Start/connect to a systemd user session with a command."""
    wait_for_systemd()

    if not helpers.get_systemd_machined_active():
        sys.exit ("imp: cannot launch command; systemd-machined is not active")

    if verbose:
        print("imp: running command " + ' '.join(commandline))

    if len(commandline) == 0:
        sys.exit("imp: no command specified")

    if helpers.get_in_windows_terminal():
        command = ['machinectl',
            '-E', 'WT_SESSION', '-E', 'WT_PROFILE_ID',
            'shell', '-q', login + '@.host', '/usr/bin/env', '-C', os.getcwd()] + commandline;
    else:
        command = ['machinectl',
            'shell', '-q', login + '@.host', '/usr/bin/env', '-C', os.getcwd()] + commandline;

    os.execv ('/usr/bin/machinectl', command)


def do_shutdown():
    """Shut down systemd and the WSL instance."""
    wait_for_systemd()

    if verbose:
        print ("imp: shutting down WSL instance")

    os.execv('/usr/bin/systemctl', ['systemctl', 'poweroff'])


# Entrypoint
def entrypoint():
    """Entrypoint of the application."""
    global verbose
    global login

    helpers.prelaunch_checks()
    arguments = parse_command_line()

    # Set globals.
    verbose = arguments.verbose
    login = helpers.get_login_session_user()

    # Check user
    if arguments.user is not None:

        # Abort if user specified and not -c or -s
        if not (arguments.shell or (arguments.command is not None)):
            sys.exit(
                "imp: error: argument -a/--as-user can only be used with -c/--command or -s/--shell")

        # Check if arguments.user is a real user
        helpers.validate_is_real_user(arguments.user)

        login = arguments.user

        if verbose:
            print(f"imp: executing as user {login}")

    # Decide what to do.
    if arguments.initialize:
        do_initialize()
    elif arguments.shell:
        do_shell()
    elif arguments.login:
        do_login()
    elif arguments.shutdown:
        do_shutdown()
    elif arguments.command is not None:
        do_command(arguments.command)
    else:
        sys.exit("imp: impossible argument - how did we get here?")


entrypoint()

# End of file.
