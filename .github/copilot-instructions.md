# bottle-imp Copilot Instructions

bottle-imp is a WSL helper tool that supplements WSL's native systemd support. It is written in Python (zipapp) with a small C setuid wrapper.

## Build Commands

```bash
# Build all binaries (C wrapper + all three Python zipapps)
make build-binaries

# Package for Debian (amd64 + arm64)
make package-debian

# Package as tarball (amd64 + arm64)
make package-tar

# Package for Arch Linux
make package-arch

# Clean all build artifacts
make clean
```

Building requires `python3`, `python3-pip`, `gcc` (and `gcc-aarch64-linux-gnu` for arm64 cross-compilation), `debhelper`, and `devscripts`.

There are no automated tests.

## Architecture

The project has four compiled components and two shell scripts, all installed under `/usr/lib/bottle-imp/` except the setuid wrapper.

### Component overview

```
/usr/bin/imp                              ← C setuid wrapper (mode 6755, root-owned)
/usr/lib/bottle-imp/imp                   ← Python zipapp: main CLI
/usr/lib/bottle-imp/imp-executor          ← Python zipapp: privileged mount operations
/usr/lib/systemd/system-generators/imp-generator  ← Python zipapp: systemd generator
/usr/lib/bottle-imp/imp-user-runtime-dir.sh
/usr/lib/bottle-imp/wait-forever.sh
```

### Execution flow

1. User runs `/usr/bin/imp` (the C setuid wrapper in `binsrc/imp-wrapper/imp.c`). The wrapper captures the *real* user's username into `IMP_LOGNAME` before escalating to root, then `execv`s `/usr/lib/bottle-imp/imp`.
2. The main `imp` zipapp (`binsrc/imp/`) reads `IMP_LOGNAME` to know which user to act on, waits for systemd/dbus, and dispatches to `machinectl shell/login` or `systemctl`.
3. `imp-executor` (`binsrc/imp-executor/`) is called by generated systemd units to perform low-level mount operations (using `ctypes` to call `libc.mount` directly via `mountie.py`).
4. `imp-generator` (`binsrc/imp-generator/`) is a systemd generator: at boot it writes unit files, binfmt.d entries, tmpfiles.d entries, and unit overrides to the generator output directory. All items to generate are declared as objects in `generatees.py` using classes from `definitions.py`.

### Python zipapp build pattern

Each Python component (`imp`, `imp-executor`, `imp-generator`) is built with:
```bash
python3 -m pip install -r requirements.txt --target <component>/dp --upgrade
python3 -m zipapp -o out/<component> -p "/usr/bin/env python3" -c <component>
```
Dependencies are bundled into the `dp/` subdirectory inside the zipapp. **Exception**: `psutil` cannot be bundled this way (C extension) and is listed in `requirements.txt` as a comment only — it must be installed system-wide.

### Shared code

`binsrc/shared/configuration.py` is the reference copy of the configuration module. Each component that uses it has its own copy (currently `imp/` and `imp-executor/` each have a `configuration.py` with the same content). Keep them in sync when making changes.

## Key Conventions

- Every Python function has a docstring.
- `__main__.py` files end with `# End of file.`
- The `IMP_LOGNAME` environment variable is the mechanism for passing the pre-setuid username from the C wrapper to the Python zipapp.
- `generatees.py` holds all systemd unit/binfmt/tmpfile definitions as a set of `Generatee` subclass instances. Add new generated artifacts there.
- The `mountie.py` module wraps `libc.mount`/`libc.umount2` via `ctypes` for direct syscall-level mount operations.
- Cross-architecture builds are controlled by `DEB_TARGET_ARCH` (e.g., `DEB_TARGET_ARCH=arm64 make build-binaries`).
- The setuid bit on `/usr/bin/imp` must be preserved; the Debian rules file explicitly excludes it from `dh_fixperms`.
