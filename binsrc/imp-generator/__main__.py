#! /usr/bin/env python3

import os
import sys

from definitions import Generatee

import genhelper
import generatees

def entrypoint():
    """Entry point for the imp-generator."""

    # Check the command-line arguments; test the resulting normal dir path.
    if (len (sys.argv) < 2):
        sys.exit ("imp-generator requires the path of the target directory")

    normal_dir = os.path.abspath(sys.argv[1])

    if not os.path.exists(normal_dir):
        sys.exit ("generated-file directory must exist")

    # Create generator helper.
    gh = genhelper.GeneratorHelper(normal_dir)

    # Iterate through generatees.
    for g in generatees.generatees:
        g.generate(gh)


entrypoint()

# End of file.
