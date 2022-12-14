# bottle-imp

[ ![ci](https://github.com/arkane-systems/bottle-imp/workflows/ci/badge.svg?branch=master) ](https://github.com/arkane-systems/bottle-imp/actions?query=workflow%3Aci+branch%3Amaster)

## A helper for using WSL's native systemd support

_bottle-imp_ is a spinoff of _[systemd-genie](http://github.com/arkane-systems/genie)_
to supplement WSL's [new built-in systemd support](https://devblogs.microsoft.com/commandline/systemd-support-is-now-available-in-wsl/).

**Why is this necessary?**

Well, awesome as the native _systemd_ support is, there are some things it
doesn't do, and others that it does in notably different ways from _genie_
or other existing _systemd_ solutions. For more information, you can see my
[migrating from systemd-genie to native WSL systemd](https://randombytes.substack.com/p/migrating-from-systemd-genie-to-native)
article here.

**What does it do, exactly?**

The following features are provided by _bottle-imp_ (see the above article for more in-depth explanations):

  * Ensures that _securityfs_ (needed for AppArmor and LSMs) and _pstorefs_ (for debugging panics) are mounted.
  * Ensures that the shared memory area filesystem is mounted at _/dev/shm_ and _/run/shm_, not vice versa.
  * Ensures that the root file system is mounted with shared propagation.
  * Ensures that the bind mount of `/tmp/.X11-unix/X0`, which makes WSLg work, is restored after _systemd_ clears out `/tmp`.
  * Ensures that WSL interop is working, even after _systemd_ rebuilds the binfmts.
  * Ensures that the WSLg-created user runtime directory is mounted for the appropriate user, and is not mounted for other users.
  * Makes sure _systemd_ is up and running before proceeding.
  * Keeps the WSL instance running even when you have no active sessions.

and the big one

  * Creates a login session for you, along with a user _systemd_ and a session dbus.

## REQUIREMENTS

First, obviously, if you were previously a user of _systemd-genie_ or one of the other systemd solutions, uninstall it _before_ attempting to set up native _systemd_ support or _bottle-imp_.

It is a good idea to set your _systemd_ default target to _multi-user.target_ before enabling _systemd_ native support. The default _graphical.target_ used by many distributions includes services for the graphical desktop that would take, at minimum, considerable reconfiguration before operating properly under the WSL/WSLg environment.

If you are using a custom kernel for WSL, it should comply with the suggested means of detecting WSL given in [microsoft/WSL#423](https://github.com/microsoft/WSL/issues/423) - i.e., the string "microsoft" should be present in the kernel version string, which can be found in `/proc/sys/kernel/osrelease`. You can check this by running _systemd-detect-virt_; it should return "wsl".

Obviously, since native _systemd_ support only works under WSL 2, the same can be said for _imp_.

Some _systemd_ units were problematic for various reasons under _genie_, and continue to be so under native support.
A list of common problematic units and solutions [is available here](https://randombytes.substack.com/p/problematic-systemd-units-under-wsl).

## INSTALLATION

If there is a package available for your distribution, this is the recommended method of installing _bottle-imp_.

### Debian
Dependent packages on Debian are _libc6_ (>= 2.34), _python3_ (>= 3.7), _python3-pip_, _python3-psutil_, _systemd_ (>= 232-25), and _systemd-container_ (>= 232-25). These should all be in the distro and able to be installed automatically.

To install, add the wsl-translinux repository here by following the instructions here:

https://arkane-systems.github.io/wsl-transdebian/

then install _bottle-imp_ using the commands:

```bash
sudo apt update
sudo apt install -y bottle-imp
```

### Arch

An Arch package (.zst) for amd64 can be downloaded from the releases, to right. Install it manually, using `pacman -U <file>`.

### Other Distros

If your distribution supports any of the package formats available, you may wish to try downloading the relevant format and giving it a try. This will almost certainly need some tweaking to work properly.

Debian is the "native" distribution for _bottle-imp_, for which read, "what the author uses". Specifically, Debian bullseye+, with _usrmerge_ installed.

#### TAR

There is a .tar.gz of a complete _bottle-imp_ install available from the releases, to right. As a last resort, you can try untarring this (it contains every needed file, with the correct permissions, in the correct path from /) onto your system while root. Don't do this unless you're confident you know what you're doing, you're willing to go looking for any resulting issues yourself, and you aren't afraid of accidentally breaking things. You will need to install the dependencies listed above beforehand.

You should use the _-p_ flag when untarring this release to preserve file permissions and the setuid flag on `/usr/bin/imp`. As some versions of _tar(1)_ always remove the high bits, you should also check the setuid status of `/usr/bin/imp` after installing.

## USAGE

```
usage: imp [-h] [-V] [-v] [-a USER] (-i | -s | -l | -c ...)

Helper for using WSL systemd native support.

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -v, --verbose         display verbose progress messages
  -a USER, --as-user USER
                        specify user to run shell or command as (use with -s or -c)

commands:
  -i, --initialize      initialize WSL interop for user sessions and hold WSL open until explicit shutdown
  -s, --shell           open or connect to a systemd user session, and run a shell in it
  -l, --login           open a login prompt for a systemd user session
  -c ..., --command ...
                        open or connect to a systemd user session, and run the specified command within it (preserves working directory)
  -u, --shutdown        shut down systemd and the WSL instance

For more information, see https://github.com/arkane-systems/bottle-imp/
```

There are four primary commands available in _bottle-imp_.

_imp -i_ should be run first to set up your WSL instance. It has two effects (apart from waiting for systemd to be ready); it copies the necessary information to ensure that Windows interoperability works inside _systemd_-managed login sessions and even services, and it starts a lifetime-running process to ensure that the WSL instance does not terminate even when you have no interactive sessions open.

**NOTE:** For technical reasons, it is not currently possible to separate these functions; you can't have reliable Windows interop without the lifetime-running process.

**NOTE 2:** The below commands will still work even if you do not run `imp -i`; however, Windows interop will not function inside _systemd_-managed sessions, and the WSL instance will idle-terminate as soon as there are no interactive sessions (technically defined as processes that are children of the Microsoft _init_) running.

_imp -s_ runs your login shell inside a _systemd_ login session; basically, Windows-side, `wsl imp -s` is your substitute for just `wsl` to get started, or for the shortcut you get to start a shell in the distro. It follows _login_ semantics, and as such does not preserve the current working directory.

_imp -c [command]_ runs _command_ inside a _systemd_ login session, then exits. It follows _sudo_ semantics, and so does preserve the cwd.

With either of the above, the _imp -a [user]_ option may be used to specify a particular user to start a shell for, or to run a command as, rather than using the currently logged-in user. For example, _imp -a bongo -s_ would start a shell as the user _bongo_.

_imp -l_ opens a login prompt. This permits you to log in to the WSL distribution via _systemd_ as any user. The login prompt will return when you log out; to terminate the session, press `^]` three times within one second. It follows _login_ semantics, and as such does not preserve the current working directory.

_imp -u_ will shut down _systemd_ cleanly and exit the WSL instance. This uses the _systemctl poweroff_ command to
simulate a normal Linux system shutting down. It is suggested that this be used before shutting down the Windows machine or force-terminating WSL to ensure a clean shutdown of _systemd_ services.

Shutting down the WSL instance in this way causes it to exit completely. You should wait for the instance to show as stopped before attempting to restart it or execute further commands inside it.

### Configuration file

While one is not supplied by default, a configuration file can be created at `/etc/imp.ini`, with contents similar to the following:

```
[imp]
dbus-timeout=240
systemd-timeout=240
```

The _*-timeout_ settings control how long _imp_ will wait for the system dbus socket to be available, and how long, once it is, _imp_ will wait for _systemd_ to enter either the running or degraded state before giving up. Under normal circumstances, there is no need to set either of these, since _imp_ will move immediately to the next state when it is ready. However, if engaged in extensive _systemd_ debugging or if one is using a particularly slow machine, these timeouts can be controlled here.

## BUGS

1. Using _imp_ to create a session is required for the user login session (and its concomitants, such as a user _systemd_ instance and a session dbus) to be created properly. Simply starting a process with _wsl_ (or using a Linux GUI app shortcut) does not do this, although the problem is less serious than with _genie_, since the process will still be started with _systemd_ as pid 1.

For information about starting Visual Studio Code remote sessions in login sessions, see https://github.com/arkane-systems/bottle-imp/discussions/19 .

2. While the Windows Terminal environment variables, WT_SESSION and WT_PROFILE_ID, will be passed through to shell and command prompt invocations of _imp_, they will not be passed through to login sessions created with _imp -l_, due to a limitation in _machinectl_.

3. _imp_ requires the python package _psutil_, which due to technical limitations of _zipapp_ can't be wrapped into the _imp_ executable. As such, _imp_ depends on this package for the system _python_. If you are inside another python environment, _imp_ may fail unless you install the _psutil_ package into this environment also.
