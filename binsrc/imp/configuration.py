# Configuration data module

import configparser

# Global variables

_config = None


# functions
def dbus_timeout():
    """Return the configured timeout for the system dbus socket appearing."""
    return _config.getint('imp', 'dbus-timeout', fallback=240)


def systemd_timeout():
    """Return the configured timeout for systemd to enter the running state."""
    return _config.getint('imp', 'systemd-timeout', fallback=240)


# Initialization
def load():
    """Load the configuration from the config file ('/etc/imp.ini')."""
    global _config

    _config = configparser.ConfigParser()
    _config.read('/etc/imp.ini')
