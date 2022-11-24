# Mount/unmount helper functions

import ctypes
import ctypes.util
import os


# Mount flags
MS_NONE = 0                 # No flags.
MS_RDONLY = 1               # Mount read-only.
MS_NOSUID = 2               # Ignore suid and sgid bits.
MS_NODEV = 4                # Disallow access to device special files.
MS_NOEXEC = 8               # Disallow program execution.
MS_SYNCHRONOUS = 16         # Writes are synced at once.
MS_REMOUNT = 32             # Alter flags of a mounted filesystem.
MS_MANDLOCK = 64            # Allow mandatory locks on an FS.
MS_DIRSYNC = 128            # Directory modifications are synchronous.
MS_BIND = 4096              # Bind directory at different place.
MS_MOVE = 8192
MS_REC = 16384
MS_SHARED = 1 << 20         # Set propagation type to shared.
MS_RELATIME = 1 << 21       # Update atime relative to mtime/ctime.
MS_STRICTATIME = 1 << 24    # Always perform atime updates.  


# Unmount flags
MU_NONE = 0                 # No flags.


libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
libc.mount.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p)
libc.umount2.argtypes = (ctypes.c_char_p, ctypes.c_int)


def mount (source: str, target: str, fs: str, flags: int = MS_NONE, options=''):
    """Mount a filesystem."""
    ret = libc.mount(source.encode(), target.encode(), fs.encode(), flags, options.encode())
    if ret < 0:
        errno = ctypes.get_errno()
        raise OSError(errno, f"Error mounting {source} ({fs}) on {target} with flags {flags} and options '{options}': {os.strerror(errno)}")


def unmount (target: str, flags: int = MU_NONE):
    """Unmount a filesystem."""
    ret = libc.umount2(target.encode(), flags)
    if ret < 0:
        errno = ctypes.get_errno()
        raise OSError(errno, f"Error unmounting {target}: {os.strerror(errno)}")


#     MS_NOSYMFOLLOW = 256,         /* Do not follow symlinks.  */
#     MS_NOATIME = 1024,            /* Do not update access times.  */
#     MS_NODIRATIME = 2048,         /* Do not update directory access times.  */
#     MS_SILENT = 32768,
#     MS_POSIXACL = 1 << 16,        /* VFS does not apply the umask.  */
#     MS_UNBINDABLE = 1 << 17,      /* Change to unbindable.  */
#     MS_PRIVATE = 1 << 18,         /* Change to private.  */
#     MS_SLAVE = 1 << 19,           /* Change to slave.  */
#     MS_KERNMOUNT = 1 << 22,       /* This is a kern_mount call.  */
#     MS_I_VERSION =  1 << 23,      /* Update inode I_version field.  */
#     MS_LAZYTIME = 1 << 25,        /* Update the on-disk [acm]times lazily.  */
#     MS_ACTIVE = 1 << 30,
#     MS_NOUSER = 1 << 31
