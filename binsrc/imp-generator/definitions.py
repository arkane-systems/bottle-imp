# Class definitions for the contents.

from abc import abstractmethod
import genhelper

class Generatee:
    """A generatable item."""
    @abstractmethod
    def generate (self, gh: genhelper.GeneratorHelper):
        pass

class BinFmt (Generatee):
    """Defines a binary format."""
    binfmt_name: str = None
    binfmt_text: str = None

    def __init__ (self, binfmt_name: str, binfmt_text: str):
        self.binfmt_name = binfmt_name
        self.binfmt_text = binfmt_text

    def generate (self, gh: genhelper.GeneratorHelper):
        """Generate the config file."""
        gh.generate_binfmt (self.binfmt_name, self.binfmt_text)

class EnableSystemUnit (Generatee):
    """Defines an existing system unit and the target to enable it for."""
    unit_name: str = None
    target: str = None

    def __init__ (self, unit_name: str, target: str):
        self.unit_name = unit_name
        self.target = target

    def generate (self, gh: genhelper.GeneratorHelper):
        """Generate the config file."""
        gh.enable_system_unit (self.unit_name, self.target)

class ImpUnit (Generatee):
    """Defines a new systemd unit and the target to enable it for."""
    unit_name: str = None
    unit_text: str = None
    target: str = None

    def __init__ (self, unit_name: str, target: str, unit_text: str):
        self.unit_name = unit_name
        self.unit_text = unit_text
        self.target = target

    def generate (self, gh: genhelper.GeneratorHelper):
        """Generate the config file."""
        gh.generate_and_enable_imp_unit (self.unit_name, self.unit_text, self.target)

class TmpFile (Generatee):
    """Defines a temporary file operations file."""
    tmpfile_name: str = None
    tmpfile_text: str = None

    def __init__ (self, tmpfile_name: str, tmpfile_text: str):
        self.tmpfile_name = tmpfile_name
        self.tmpfile_text = tmpfile_text

    def generate (self, gh: genhelper.GeneratorHelper):
        """Generate the config file."""
        gh.generate_tmpfile (self.tmpfile_name, self.tmpfile_text)

class UnitOverride (Generatee):
    """Defines a unit override file and the unit to override."""
    unit_name: str = None
    override_text: str = None

    def __init__ (self, unit_name: str, override_text: str):
        self.unit_name = unit_name
        self.override_text = override_text

    def generate (self, gh: genhelper.GeneratorHelper):
        """Generate the config file."""
        gh.generate_override_conf (self.unit_name, self.override_text)
