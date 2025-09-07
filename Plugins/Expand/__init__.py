from importlib import import_module

from Scripts.Config import config

if config.ai_enabled:
    import_module('Plugins.Expand.Ai')
if config.auto_reply_enabled:
    import_module('Plugins.Expand.Keywords')
