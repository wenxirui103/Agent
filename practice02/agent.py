"""
AI 智能体核心模块
实现基于 DeepSeek 的智能对话代理
"""

import os
import json
import time
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlparse


class LLMClient:
    """LLM 客户端 - 使用标准 HTTP 库与 DeepSeek API 交互"""
    
    def __init__(self, base_url, model, api_token, timeout=30):
        self.base_url = base_url
        self.model = model
        self.api_token = api_token
        self.timeout = timeout
        
    def chat_completion(self, messages, temperature=0.7, max_tokens=2048, tools=None):
        """
        发送聊天请求到 LLM
        
        参数:
            messages: 消息列表，格式为 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数 (0.0-1.0)
            max_tokens: 最大生成 token 数
            tools: 可选的工具列表，用于 function calling
            
        返回:
            dict: 包含回复内容、token使用和性能统计
        """
        parsed_url = urlparse(self.base_url)
        host = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        path = parsed_url.path.rstrip('/') + '/chat/completions'
        
        # 根据协议选择连接类型
        use_https = parsed_url.scheme == 'https'
        
        # 构建请求数据
        request_data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # 如果提供了工具，添加到请求中
        if tools:
            request_data["tools"] = tools
            request_data["tool_choice"] = "auto"  # 让模型自动决定是否使用工具
        
        body = json.dumps(request_data).encode('utf-8')
        
        # 构建请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 发送请求
            if use_https:
                conn = HTTPSConnection(host, port, timeout=self.timeout)
            else:
                conn = HTTPConnection(host, port, timeout=self.timeout)
            conn.request('POST', path, body=body, headers=headers)
            
            # 获取响应
            response = conn.getresponse()
            response_body = response.read().decode('utf-8')
            elapsed_time = time.time() - start_time
            
            conn.close()
            
            if response.status == 200:
                response_data = json.loads(response_body)
                
                # 提取回复内容
                content = response_data['choices'][0]['message']['content']
                
                # 提取 token 使用信息
                usage = response_data.get('usage', {})
                total_tokens = usage.get('total_tokens', 0)
                
                # 计算 token/s
                tokens_per_second = total_tokens / elapsed_time if elapsed_time > 0 else 0
                
                return {
                    'success': True,
                    'content': content,
                    'elapsed_time': elapsed_time,
                    'total_tokens': total_tokens,
                    'tokens_per_second': tokens_per_second,
                    'usage': usage
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status}: {response_body}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class AIAgent:
    """AI 智能体 - 具有记忆和上下文理解的对话代理"""
    
    def __init__(self, llm_client, system_prompt=None, tools=None):
        self.llm_client = llm_client
        self.conversation_history = []
        self.tools = tools  # 可用工具列表
        
        # 设置系统提示
        if system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })
        else:
            # 默认系统提示
            self.conversation_history.append({
                "role": "system",
                "content": "你是一个有用的AI助手，能够回答问题、提供建议和进行对话。"
            })
    
    def chat(self, user_message, temperature=0.7, max_tokens=2048, enable_tools=True):
        """
        与智能体对话
        
        参数:
            user_message: 用户输入的消息
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            enable_tools: 是否启用工具调用
            
        返回:
            dict: 包含回复和性能统计
        """
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 调用 LLM
        result = self.llm_client.chat_completion(
            messages=self.conversation_history,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self.tools if enable_tools else None
        )
        
        if result['success']:
            # 添加助手回复到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": result['content']
            })
        
        return result
    
    def clear_history(self):
        """清空对话历史（保留系统提示）"""
        if self.conversation_history and self.conversation_history[0]['role'] == 'system':
            self.conversation_history = [self.conversation_history[0]]
        else:
            self.conversation_history = []
    
    def get_history(self):
        """获取对话历史"""
        return self.conversation_history.copy()


def load_config():
    """从 .env 文件加载配置"""
    project_root = os.path.dirname(os.path.dirname(__file__))
    env_path = os.path.join(project_root, '.env')
    
    if not os.path.exists(env_path):
        raise FileNotFoundError(f".env 文件不存在: {env_path}")
    
    config = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config


def create_agent(system_prompt=None, enable_tools=False):
    """
    创建 AI 智能体实例
    
    参数:
        system_prompt: 可选的系统提示，定义智能体的角色和行为
        enable_tools: 是否启用工具调用功能
        
    返回:
        AIAgent 实例
    """
    config = load_config()
    
    llm_client = LLMClient(
        base_url=config['LLM_BASE_URL'],
        model=config['LLM_MODEL'],
        api_token=config['LLM_API_TOKEN'],
        timeout=int(config.get('REQUEST_TIMEOUT', '30'))
    )
    
    # 如果启用工具，加载工具描述
    tools = None
    if enable_tools:
        try:
            from tool_chat_client import get_tool_description
            tools = get_tool_description()
        except ImportError:
            print("⚠️ 警告: 无法导入工具模块，将使用无工具模式")
    
    return AIAgent(llm_client, system_prompt, tools)
