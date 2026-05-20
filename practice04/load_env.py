"""
环境变量加载工具
从 .env 文件中加载环境变量
"""

import os


def load_env_file(env_path=None):
    """
    从 .env 文件加载环境变量
    
    参数:
        env_path: .env 文件路径，如果为 None 则自动查找项目根目录的 .env 文件
    
    返回:
        dict: 加载的配置字典
    """
    if env_path is None:
        # 自动定位项目根目录的 .env 文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        env_path = os.path.join(project_root, '.env')
    
    if not os.path.exists(env_path):
        print(f"⚠️  警告: .env 文件不存在: {env_path}")
        return {}
    
    config = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # 解析键值对
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 只有当环境变量中不存在时才设置
                if key not in os.environ:
                    os.environ[key] = value
                    config[key] = value
    
    return config


if __name__ == '__main__':
    # 测试加载
    print("🔧 正在加载 .env 文件...")
    config = load_env_file()
    
    print(f"\n✅ 已加载 {len(config)} 个配置项:")
    for key, value in config.items():
        # 隐藏敏感信息
        if 'KEY' in key or 'TOKEN' in key or 'SECRET' in key:
            display_value = value[:4] + '****' if len(value) > 4 else '****'
        else:
            display_value = value
        print(f"   {key} = {display_value}")
