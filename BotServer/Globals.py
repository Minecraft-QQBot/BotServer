from Scripts.Config import config

cpu_occupation: dict[str, list] = {}
ram_occupation: dict[str, list] = {}

openai = None
render_template = None

if config.ai_enabled:
    import openai
if config.image_mode:
    from Scripts.Render import render_template

# LtNsttMj1tUSaieZRjvHHk2h2AZOEKIG
# https://crafatar.com/avatars/{uuid}
