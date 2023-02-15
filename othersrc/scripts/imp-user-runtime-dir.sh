#!/bin/sh

if [ ! -d /mnt/wslg/runtime-dir ]
then
    # WSLg is not present, so default to doing the standard thing.
    /lib/systemd/systemd-user-runtime-dir $1 $2
    exit
fi

USERNAME=$(/bin/id -un $2)

# Make directory names
RUNDIR="/run/user/$2"
WORKDIR="/run/user/$2.work"

# Start
if [ "$1" = "start" ]
then

    # If (for whatever reason) the runtime dir is already a mount point,
    # unmount it.
    if /bin/mountpoint -q $RUNDIR
    then
      /bin/umount $RUNDIR
    fi

    # Create the runtime and work directories and set their permissions appropriately.
    /bin/mkdir -p $RUNDIR
    /bin/chown $USERNAME: $RUNDIR

    /bin/mkdir -p $WORKDIR
    /bin/chown $USERNAME: $WORKDIR

    # Perform the magic overlay mount.
    /bin/mount -t overlay overlay -o lowerdir=/mnt/wslg/runtime-dir,upperdir=$RUNDIR,workdir=$WORKDIR $RUNDIR
fi

# Stop
if [ "$1" = "stop" ]
then
    # The runtime dir should be a mount point, so unmount it if so.
    if /bin/mountpoint -q $RUNDIR
    then
      /bin/umount $RUNDIR
    fi

    # If the working dir exists, clean it up.
    if [ -d $WORKDIR ]
    then
        rm -rf $WORKDIR
    fi

    # If the runtime dir exists, clean it up.
    if [ -d $RUNDIR ]
    then
        rm -rf $RUNDIR
    fi
fi
