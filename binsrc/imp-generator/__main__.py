#! /usr/bin/env python3

import os
import sys

import units

def entrypoint():
    """Entry point for the imp-generator."""

    # Check the command-line arguments; test the resulting normal dir path.
    if (len (sys.argv) < 2):
        sys.exit ("imp-generator requires the path of the target directory")

    normal_dir = os.path.abspath(sys.argv[1])

    if not os.path.exists(normal_dir):
        sys.exit ("generated-file directory must exist")

    # System units: enable systemd-machined if not already so.
    units.enable_system_unit ('systemd-machined.service', 'multi-user.target.wants', normal_dir)

    # Write out the units and make their links.
    units.enable_imp_unit ('imp-fixshm.service', units.imp_fixshm, 'sysinit.target.wants', normal_dir)
    units.enable_imp_unit ('imp-pstorefs.service', units.imp_pstorefs, 'sysinit.target.wants', normal_dir)
    units.enable_imp_unit ('imp-securityfs.service', units.imp_securityfs, 'sysinit.target.wants', normal_dir)
    units.enable_imp_unit ('imp-remount-root-shared.service', units.imp_remount_root_shared, 'sysinit.target.wants', normal_dir)

    units.enable_imp_unit ('imp-wslg-socket.service', units.imp_wslg_socket, 'multi-user.target.wants', normal_dir)

    # Write out the override files.
    units.enable_override_conf ('user-runtime-dir@.service', units.user_runtime_dir_override, normal_dir)


entrypoint()

# End of file.
