from Scripts.Config import config

uuid_caches: dict[str, str] = {}
cpu_occupation: dict[str, list] = {}
ram_occupation: dict[str, list] = {}

render_template = None

if config.image_mode:
    from .Render import render_template

# LtNsttMj1tUSaieZRjvHHk2h2AZOEKIG
# https://crafatar.com/avatars/{uuid}
