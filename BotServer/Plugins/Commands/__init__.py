from Scripts.Config import config


from .About import *
if 'send' in config.command_enabled:
    from .Send import *
if 'help' in config.command_enabled:
    from .Help import *
if 'list' in config.command_enabled:
    from .List import *
if 'luck' in config.command_enabled:
    from .Luck import *
if 'mcdr' in config.command_enabled:
    from .Mcdr import *
if 'command' in config.command_enabled:
    from .Command import *
if 'bound' in config.command_enabled:
    from .Bound import *
if 'server' in config.command_enabled:
    from .Server import *
