# Class of functions to write out the generated files.

import os

class GeneratorHelper:
    """A class of helpers for writing systemd generators."""
    unit_dir = None
    binfmt_dir = '/run/binfmt.d'
    tmpfiles_dir = '/run/tmpfiles.d'


    def __init__ (self, unit_dir: str):
        self.unit_dir = unit_dir


    def enable_system_unit (self, unit_name: str, target: str):
        """Enable an existing system unit for a specific target."""
        # Create the target directory if it does not already exist.
        target_dir = os.path.join (self.unit_dir, target + '.wants')
        if not os.path.isdir (target_dir):
            os.mkdir (target_dir)

        # Link to the system unit.
        unit_link = os.path.join (target_dir, unit_name)
        unit_file = os.path.join ('/lib/systemd/system', unit_name)

        if os.path.exists (unit_link):
            os.unlink (unit_link)

        os.symlink (unit_file, unit_link)


    def generate_binfmt(self, binfmt_name: str, binfmt_text: str):
        """Generate a dynamic binfmt.d format definition file."""
        # Create the dynamic binfmt.d if it does not already exist.
        if not os.path.isdir (self.binfmt_dir):
            os.mkdir (self.binfmt_dir)

        # Write out the override file.
        with open (os.path.join (self.binfmt_dir, binfmt_name), 'w') as b:
            b.write (binfmt_text)


    def generate_and_enable_imp_unit (self, unit_name: str, unit_text: str, target: str = ''):
        """Generate an imp unit and enable it for a specified target."""
        # Write out the unit file.
        unit_file = os.path.join (self.unit_dir, unit_name)

        with open (unit_file, 'w') as u:
            u.write (unit_text)

        # If a target was not specified, exit.
        if target == '':
            return

        # Create the target directory if it does not already exist.
        target_dir = os.path.join (self.unit_dir, target + '.wants')

        if not os.path.isdir (target_dir):
            os.mkdir (target_dir)

        # Link to the just-created unit.
        unit_link = os.path.join (target_dir, unit_name)

        if os.path.exists (unit_link):
            os.unlink (unit_link)

        os.symlink (unit_file, unit_link)

    
    def generate_override_conf (self, unit_name: str, override_text: str):
        """Generate an override configuration file for an existing systemd unit."""
        # Create the override directory if it does not already exist.
        override_dir = os.path.join (self.unit_dir, unit_name + '.d')

        if not os.path.isdir (override_dir):
            os.mkdir (override_dir)

        # Write out the override file.
        with open (os.path.join(override_dir, 'override.conf'), 'w') as o:
            o.write (override_text)


    def generate_tmpfile(self, tmpfile_name: str, tmpfile_text: str):
        """Generate a tmpfiles.d operations file."""
        # Create the dynamic tmpfiles.d if it does not already exist.
        if not os.path.isdir (self.tmpfiles_dir):
            os.mkdir (self.tmpfiles_dir)

        # Write out the override file.
        with open (os.path.join (self.tmpfiles_dir, tmpfile_name), 'w') as t:
            t.write (tmpfile_text)
