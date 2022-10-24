#!/bin/sh

if [ ! -d /mnt/wslg/runtime-dir ]
then
    # WSLg is not present, so default to doing the standard thing.
    /lib/systemd/systemd-user-runtime-dir $1 $2
    exit
fi

# Get the UID of the WSLg runtime directory.
WSLGUID=$(stat -c "%u" /mnt/wslg/runtime-dir)

if [ "$1" = "start" ]
then
    # Setting up runtime dir.
    # At this point, the WSLg runtime dir will be mounted at this point anyway;
    # regardless of UID.
    if [ $2 -eq $WSLGUID ]
    then
        # We are the WSLg user, so leave the status quo.
        exit
    fi

    # Otherwise, unmount the runtime dir, and then default to the standard.
    /bin/umount /run/user/$2
    /lib/systemd/systemd-user-runtime-dir $1 $2
    exit
fi

if [ $1 = "stop" ]
then
    # Unsetting up runtime dir.
    if [ $2 -eq $WSLGUID ]
    then
        # We are the WSLg user, so leave the status quo.
        exit
    fi

    # Otherwise, default to the standard.
    /lib/systemd/systemd-user-runtime-dir $1 $2
fi
