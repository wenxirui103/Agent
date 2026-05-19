"""
AI 智能体工具函数模块
提供网页访问、数据处理等实用工具
"""

import subprocess
import sys


def fetch_webpage(url, timeout=10):
    """
    使用 curl 访问网页并返回内容
    
    参数:
        url: 要访问的网页 URL
        timeout: 超时时间（秒），默认 10 秒
        
    返回:
        dict: 包含成功状态、网页内容或错误信息
            - success (bool): 是否成功
            - content (str): 网页内容（成功时）
            - error (str): 错误信息（失败时）
            - status_code (int): HTTP 状态码（成功时）
    """
    try:
        # 检查系统是否安装了 curl
        if sys.platform == 'win32':
            # Windows 系统
            cmd = [
                'curl', '-s', '-L',  # -s: 静默模式, -L: 跟随重定向
                '--max-time', str(timeout),  # 超时设置
                '-w', '\n%{http_code}',  # 输出 HTTP 状态码
                url
            ]
        else:
            # Linux/Mac 系统
            cmd = [
                'curl', '-s', '-L',
                '--max-time', str(timeout),
                '-w', '\n%{http_code}',
                url
            ]
        
        # 执行 curl 命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',  # 指定 UTF-8 编码
            errors='ignore',   # 忽略解码错误
            timeout=timeout + 5  # 给 subprocess 额外的缓冲时间
        )
        
        # 解析输出（最后一行是状态码）
        output_lines = result.stdout.rsplit('\n', 1)
        if len(output_lines) == 2:
            content = output_lines[0]
            status_code = int(output_lines[1])
        else:
            content = result.stdout
            status_code = 0
        
        # 检查是否有错误
        if result.returncode != 0:
            return {
                'success': False,
                'error': f'curl 执行失败: {result.stderr}',
                'status_code': status_code
            }
        
        # 检查 HTTP 状态码
        if status_code >= 400:
            return {
                'success': False,
                'error': f'HTTP 错误: {status_code}',
                'status_code': status_code
            }
        
        return {
            'success': True,
            'content': content,
            'status_code': status_code
        }
        
    except FileNotFoundError:
        return {
            'success': False,
            'error': '系统中未找到 curl 命令，请确保已安装 curl'
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': f'请求超时（{timeout}秒）'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'发生错误: {str(e)}'
        }


# 可用的工具函数映射表
AVAILABLE_TOOLS = {
    'fetch_webpage': {
        'function': fetch_webpage,
        'description': '使用 curl 访问指定 URL 并返回网页内容',
        'parameters': {
            'url': '要访问的网页 URL（必需）',
            'timeout': '超时时间（秒），可选，默认 10 秒'
        }
    }
}


def get_tool_description():
    """
    获取所有可用工具的描述信息（用于 LLM 理解）
    
    返回:
        list: 工具描述列表，符合 OpenAI function calling 格式
    """
    tools = []
    
    for tool_name, tool_info in AVAILABLE_TOOLS.items():
        tool_desc = {
            'type': 'function',
            'function': {
                'name': tool_name,
                'description': tool_info['description'],
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
        }
        
        # 添加参数定义
        for param_name, param_desc in tool_info['parameters'].items():
            is_required = '必需' in param_desc
            tool_desc['function']['parameters']['properties'][param_name] = {
                'type': 'string' if param_name == 'url' else 'number',
                'description': param_desc
            }
            if is_required:
                tool_desc['function']['parameters']['required'].append(param_name)
        
        tools.append(tool_desc)
    
    return tools


def execute_tool(tool_name, **kwargs):
    """
    执行指定的工具函数
    
    参数:
        tool_name: 工具名称
        **kwargs: 工具函数的参数
        
    返回:
        dict: 工具执行结果
    """
    if tool_name not in AVAILABLE_TOOLS:
        return {
            'success': False,
            'error': f'未知工具: {tool_name}'
        }
    
    try:
        func = AVAILABLE_TOOLS[tool_name]['function']
        result = func(**kwargs)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': f'工具执行失败: {str(e)}'
        }
