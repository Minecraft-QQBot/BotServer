# 从配置模块导入配置信息
from Scripts.Config import config

# 定义一个字典，用于缓存UUID到字符串的映射
uuid_caches: dict[str, str] = {}
# 定义一个字典，用于存储CPU占用信息，每个键对应一个列表
cpu_occupation: dict[str, list] = {}
# 定义一个字典，用于存储RAM占用信息，每个键对应一个列表
ram_occupation: dict[str, list] = {}

# 初始化openai变量为None，用于后续条件导入
openai = None
# 初始化render_template变量为None，用于后续条件导入
render_template = None

# 根据配置信息决定是否导入openai库
if config.ai_enabled:
    import openai
# 根据配置信息决定是否导入渲染模板函数
if config.image_mode:
    from Scripts.Render import render_template

# 示例UUID字符串，用于演示或测试
# LtNsttMj1tUSaieZRjvHHk2h2AZOEKIG
# 通过访问crafatar API获取玩家头像的URL格式示例
# https://crafatar.com/avatars/{uuid}
