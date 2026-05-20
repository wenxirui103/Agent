"""
AI 智能体工具函数模块 - practice04 版本
集成 AnythingLLM 查询工具和网页访问工具
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
    """
    try:
        if sys.platform == 'win32':
            cmd = [
                'curl', '-s', '-L',
                '--max-time', str(timeout),
                '-w', '\n%{http_code}',
                url
            ]
        else:
            cmd = [
                'curl', '-s', '-L',
                '--max-time', str(timeout),
                '-w', '\n%{http_code}',
                url
            ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=timeout + 5
        )
        
        output_lines = result.stdout.rsplit('\n', 1)
        if len(output_lines) == 2:
            content = output_lines[0]
            status_code = int(output_lines[1])
        else:
            content = result.stdout
            status_code = 0
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': f'curl 执行失败: {result.stderr}',
                'status_code': status_code
            }
        
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


def anythingllm_query(message, workspace_slug=None, api_base_url="http://localhost:3001", api_key=None, timeout=30):
    """
    使用 curl 命令查询 AnythingLLM API
    
    参数:
        message: 要发送给 AnythingLLM 的消息内容（必需）
        workspace_slug: 工作空间标识符（可选）
        api_base_url: AnythingLLM API 基础 URL，默认 http://localhost:3001
        api_key: AnythingLLM API 密钥（必需）
        timeout: 超时时间（秒），默认 30 秒
        
    返回:
        dict: 包含成功状态、回复内容或错误信息
    """
    import json
    
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
        
        # 执行 curl 命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=timeout + 5
        )
        
        # 解析输出
        output_lines = result.stdout.rsplit('\n', 1)
        if len(output_lines) == 2:
            response_body = output_lines[0]
            status_code = int(output_lines[1])
        else:
            response_body = result.stdout
            status_code = 0
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': f'curl 执行失败: {result.stderr}',
                'status_code': status_code
            }
        
        if status_code >= 400:
            return {
                'success': False,
                'error': f'HTTP 错误 {status_code}: {response_body}',
                'status_code': status_code
            }
        
        # 解析响应 JSON
        try:
            response_data = json.loads(response_body)
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


def generate_notice(topic, department=None):
    """
    生成部门通知文档
    
    参数:
        topic: 通知主题（必需），例如：五一节放假、年会安排等
        department: 部门名称（可选），如果不提供则使用通用格式
        
    返回:
        dict: 包含成功状态和生成的通知内容
    """
    try:
        if not topic:
            return {
                'success': False,
                'error': '通知主题不能为空'
            }
        
        # 根据是否提供部门名称，设置通知开头
        if department and department.strip():
            notice_header = f"{department.strip()}通知"
        else:
            notice_header = "XX部通知"
        
        # 生成通知模板
        notice_content = f"""{notice_header}

关于{topic}的通知

各位同事：

根据公司安排，现就{topic}相关事宜通知如下：

一、时间安排
请各部门提前做好工作安排，确保工作有序进行。

二、注意事项
1. 请各位同事合理安排工作时间
2. 做好相关工作交接
3. 注意安全防范

三、其他事项
如有特殊情况，请及时与部门负责人联系。

特此通知。

{notice_header}
日期：2026年4月23日"""
        
        return {
            'success': True,
            'content': notice_content,
            'header': notice_header,
            'topic': topic,
            'department': department
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'生成通知失败: {str(e)}'
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
    },
    'anythingllm_query': {
        'function': anythingllm_query,
        'description': '查询 AnythingLLM 知识库，获取基于本地文档的AI回答。当用户询问关于公司文档、内部知识、特定项目信息时使用此工具',
        'parameters': {
            'message': '要查询的问题或消息（必需）',
            'workspace_slug': '工作空间标识符（可选）',
            'api_base_url': 'API 基础 URL（可选，默认 http://localhost:3001）',
            'api_key': 'API 密钥（必需）',
            'timeout': '超时时间（秒），可选，默认 30 秒'
        }
    },
    'generate_notice': {
        'function': generate_notice,
        'description': '生成部门通知文档。当用户要求撰写通知、公告时自动调用此工具。可以指定部门名称，如果不指定则使用通用格式',
        'parameters': {
            'topic': '通知主题（必需），例如：五一节放假、年会安排等',
            'department': '部门名称（可选），例如：销售部、技术部等。不提供则使用XX部'
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
            if param_name in ['url', 'message', 'workspace_slug', 'api_base_url', 'api_key', 'topic', 'department']:
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
