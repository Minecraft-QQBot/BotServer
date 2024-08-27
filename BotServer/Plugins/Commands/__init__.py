from importlib import import_module

from Scripts.Config import config

for command in config.command_enabled:
    import_module('.' + command.capitalize())
