"""
AnythingLLM 查询工具模块
提供访问 AnythingLLM API 的功能
"""

import subprocess
import sys
import json


def anythingllm_query(message, workspace_slug=None, api_base_url="http://localhost:3001", api_key=None, timeout=30):
    """
    使用 curl 命令查询 AnythingLLM API
    
    参数:
        message: 要发送给 AnythingLLM 的消息内容（必需）
        workspace_slug: 工作空间标识符（可选，如果不提供则使用默认工作空间）
        api_base_url: AnythingLLM API 基础 URL，默认 http://localhost:3001
        api_key: AnythingLLM API 密钥（必需）
        timeout: 超时时间（秒），默认 30 秒
        
    返回:
        dict: 包含成功状态、回复内容或错误信息
            - success (bool): 是否成功
            - response (str): AI 回复内容（成功时）
            - error (str): 错误信息（失败时）
            - status_code (int): HTTP 状态码
    """
    if not api_key:
        return {
            'success': False,
            'error': 'API 密钥未提供，请设置 api_key 参数'
        }
    
    try:
        # 构建 API 端点 URL
        if workspace_slug:
            endpoint = f"{api_base_url}/api/v1/workspace/{workspace_slug}/chat"
        else:
            endpoint = f"{api_base_url}/api/v1/workspace/chat"
        
        # 构建请求数据
        payload = {
            "message": message
        }
        
        # 在 Windows 上使用 PowerShell 执行 curl
        if sys.platform == 'win32':
            # 将 payload 转换为 JSON 字符串
            json_payload = json.dumps(payload)
            
            # 构建 curl 命令
            cmd = [
                'curl', '-s', '-X', 'POST',
                endpoint,
                '-H', 'Content-Type: application/json',
                '-H', f'Authorization: Bearer {api_key}',
                '-d', json_payload,
                '--max-time', str(timeout),
                '-w', '\n%{http_code}'
            ]
        else:
            # Linux/Mac 系统
            json_payload = json.dumps(payload)
            cmd = [
                'curl', '-s', '-X', 'POST',
                endpoint,
                '-H', 'Content-Type: application/json',
                '-H', f'Authorization: Bearer {api_key}',
                '-d', json_payload,
                '--max-time', str(timeout),
                '-w', '\n%{http_code}'
            ]
        
        # 执行 curl 命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=timeout + 5
        )
        
        # 解析输出（最后一行是状态码）
        output_lines = result.stdout.rsplit('\n', 1)
        if len(output_lines) == 2:
            response_body = output_lines[0]
            status_code = int(output_lines[1])
        else:
            response_body = result.stdout
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
                'error': f'HTTP 错误 {status_code}: {response_body}',
                'status_code': status_code
            }
        
        # 解析响应 JSON
        try:
            response_data = json.loads(response_body)
            
            # 提取回复内容（根据 AnythingLLM API 响应格式）
            # AnythingLLM 通常返回 {text: "...", sources: [...]}
            reply_text = response_data.get('text', response_data.get('response', str(response_data)))
            
            return {
                'success': True,
                'response': reply_text,
                'status_code': status_code,
                'raw_response': response_data
            }
        except json.JSONDecodeError:
            return {
                'success': False,
                'error': f'无法解析响应 JSON: {response_body}',
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
    'anythingllm_query': {
        'function': anythingllm_query,
        'description': '查询 AnythingLLM 知识库，获取基于本地文档的AI回答',
        'parameters': {
            'message': '要查询的问题或消息（必需）',
            'workspace_slug': '工作空间标识符（可选）',
            'api_base_url': 'API 基础 URL（可选，默认 http://localhost:3001）',
            'api_key': 'API 密钥（必需）',
            'timeout': '超时时间（秒），可选，默认 30 秒'
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
            
            # 确定参数类型
            if param_name in ['message', 'workspace_slug', 'api_base_url', 'api_key']:
                param_type = 'string'
            elif param_name == 'timeout':
                param_type = 'number'
            else:
                param_type = 'string'
            
            tool_desc['function']['parameters']['properties'][param_name] = {
                'type': param_type,
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


if __name__ == '__main__':
    # 测试代码
    print("测试 AnythingLLM 查询工具...")
    
    # 从环境变量或配置文件读取 API Key
    import os
    api_key = os.getenv('ANYTHINGLLM_API_KEY', 'your-api-key-here')
    
    # 测试查询
    result = anythingllm_query(
        message="你好，请介绍一下你自己",
        api_key=api_key
    )
    
    if result['success']:
        print(f"\n✅ 查询成功！")
        print(f"回复: {result['response']}")
    else:
        print(f"\n❌ 查询失败: {result['error']}")
