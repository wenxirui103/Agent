"""
AI 智能体核心模块 - 支持聊天历史自动压缩
基于 practice02 扩展，添加上下文长度管理功能
"""

import os
import json
import time
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlparse
from chat_logger import ChatLogger


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
            request_data["tool_choice"] = "auto"
        
        body = json.dumps(request_data).encode('utf-8')
        
        # 构建请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 根据协议选择连接类型
            if use_https:
                conn = HTTPSConnection(host, port, timeout=self.timeout)
            else:
                conn = HTTPConnection(host, port, timeout=self.timeout)
            
            # 发送请求
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


class SmartAIAgent:
    """智能 AI 智能体 - 具有自动聊天历史压缩功能"""
    
    def __init__(self, llm_client, system_prompt=None, 
                 max_rounds=5, max_context_length=3000,
                 compression_ratio=0.7, enable_logging=True,
                 log_file_path=r"D:\chat-log\log.txt"):
        """
        初始化智能体
        
        参数:
            llm_client: LLM 客户端实例
            system_prompt: 系统提示
            max_rounds: 最大对话轮数阈值（超过则触发压缩）
            max_context_length: 最大上下文长度阈值（字符数，超过则触发压缩）
            compression_ratio: 压缩比例（0.7 表示压缩前 70% 的内容）
            enable_logging: 是否启用聊天日志记录
            log_file_path: 日志文件路径
        """
        self.llm_client = llm_client
        self.conversation_history = []
        self.max_rounds = max_rounds
        self.max_context_length = max_context_length
        self.compression_ratio = compression_ratio
        
        # 统计信息
        self.compression_count = 0
        self.total_compressed_tokens = 0
        
        # 聊天日志管理器
        self.enable_logging = enable_logging
        if enable_logging:
            self.chat_logger = ChatLogger(log_file_path)
            print(f"✅ 聊天日志已启用: {log_file_path}")
        else:
            self.chat_logger = None
        
        # 设置系统提示
        if system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })
        else:
            self.conversation_history.append({
                "role": "system",
                "content": "你是一个有用的AI助手，能够回答问题、提供建议和进行对话。"
            })
    
    def _get_context_length(self):
        """计算当前上下文的总字符数"""
        total_length = 0
        for msg in self.conversation_history:
            total_length += len(msg.get('content', ''))
        return total_length
    
    def _get_conversation_rounds(self):
        """获取对话轮数（用户+助手算一轮）"""
        user_messages = sum(1 for msg in self.conversation_history if msg['role'] == 'user')
        return user_messages
    
    def _needs_compression(self):
        """检查是否需要压缩聊天记录"""
        rounds = self._get_conversation_rounds()
        context_length = self._get_context_length()
        
        needs_by_rounds = rounds > self.max_rounds
        needs_by_length = context_length > self.max_context_length
        
        return needs_by_rounds or needs_by_length, rounds, context_length
    
    def _compress_history(self):
        """
        压缩聊天历史记录
        
        策略：
        - 保留最后 30% 的原始对话
        - 将前 70% 的内容压缩成总结
        - 保留系统提示
        """
        if len(self.conversation_history) <= 1:
            return False
        
        print("\n🔄 检测到上下文过长，正在压缩聊天历史...")
        
        # 保留系统提示
        system_message = None
        if self.conversation_history and self.conversation_history[0]['role'] == 'system':
            system_message = self.conversation_history[0]
        
        # 获取所有对话消息（排除系统提示）
        conversation_messages = self.conversation_history[1:] if system_message else self.conversation_history[:]
        
        if not conversation_messages:
            return False
        
        # 计算分割点
        total_messages = len(conversation_messages)
        compress_count = int(total_messages * self.compression_ratio)
        keep_count = total_messages - compress_count
        
        # 确保至少保留一条消息
        if keep_count < 1:
            keep_count = 1
            compress_count = total_messages - 1
        
        # 需要压缩的消息
        to_compress = conversation_messages[:compress_count]
        # 需要保留的消息
        to_keep = conversation_messages[compress_count:]
        
        # 构建压缩请求
        compress_prompt = """请对以下对话历史进行简洁总结，保留关键信息和上下文。
总结应该简明扼要，但要确保后续对话能够理解之前的讨论内容。

对话历史：
"""
        for msg in to_compress:
            role_label = "用户" if msg['role'] == 'user' else "助手"
            compress_prompt += f"{role_label}: {msg['content']}\n\n"
        
        compress_prompt += "\n请提供简洁的总结："
        
        try:
            # 调用 LLM 进行总结
            result = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": compress_prompt}],
                temperature=0.3,  # 使用较低的温度以获得更一致的总结
                max_tokens=500
            )
            
            if result['success']:
                summary = result['content']
                
                # 构建新的历史记录
                new_history = []
                
                # 添加系统提示
                if system_message:
                    new_history.append(system_message)
                
                # 添加总结消息
                new_history.append({
                    "role": "system",
                    "content": f"[之前的对话总结]\n{summary}"
                })
                
                # 添加保留的最近对话
                new_history.extend(to_keep)
                
                # 更新历史记录
                old_length = self._get_context_length()
                self.conversation_history = new_history
                new_length = self._get_context_length()
                
                # 更新统计信息
                self.compression_count += 1
                compressed_tokens = old_length - new_length
                self.total_compressed_tokens += compressed_tokens
                
                print(f"✅ 压缩完成！")
                print(f"   - 压缩前: {old_length} 字符, {total_messages} 条消息")
                print(f"   - 压缩后: {new_length} 字符, {len(new_history)} 条消息")
                print(f"   - 减少: {compressed_tokens} 字符 ({compressed_tokens/old_length*100:.1f}%)")
                print(f"   - 累计压缩次数: {self.compression_count}")
                
                return True
            else:
                print(f"⚠️ 压缩失败: {result.get('error', '未知错误')}")
                return False
                
        except Exception as e:
            print(f"⚠️ 压缩过程出错: {e}")
            return False
    
    def chat(self, user_message, temperature=0.7, max_tokens=2048, auto_compress=True):
        """
        与智能体对话
        
        参数:
            user_message: 用户输入的消息
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            auto_compress: 是否启用自动压缩
            
        返回:
            dict: 包含回复和性能统计
        """
        # 检查是否需要压缩
        if auto_compress:
            needs_comp, rounds, length = self._needs_compression()
            if needs_comp:
                print(f"\n📊 上下文状态: {rounds} 轮对话, {length} 字符")
                self._compress_history()
        
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 调用 LLM
        result = self.llm_client.chat_completion(
            messages=self.conversation_history,
            temperature=temperature,
            max_tokens=max_tokens
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
    
    def get_stats(self):
        """获取智能体统计信息"""
        stats = {
            'compression_count': self.compression_count,
            'total_compressed_tokens': self.total_compressed_tokens,
            'current_rounds': self._get_conversation_rounds(),
            'current_context_length': self._get_context_length(),
            'total_messages': len(self.conversation_history)
        }
        
        # 添加日志统计
        if self.chat_logger:
            log_stats = self.chat_logger.get_log_stats()
            stats['log_entries'] = log_stats['total_entries']
            stats['log_file_size_kb'] = log_stats.get('file_size_kb', 0)
        
        return stats
    
    def _extract_5w_from_compressed(self, compressed_summary):
        """
        从压缩的聊天总结中提取5W信息
        
        参数:
            compressed_summary: 压缩后的聊天总结文本
            
        返回:
            dict: 5W信息字典
        """
        if not self.chat_logger:
            return {}
        
        print("\n🔍 正在从压缩内容中提取关键信息...")
        
        # 构建提取 prompt
        extract_prompt = f"""请分析以下对话总结，按照5W规则提取关键信息：

对话总结：
{compressed_summary}

请提取以下信息（如果某项信息不存在，请填写“未提及”）：
- Who (谁): 涉及的人物或主体
- What (做了什么): 发生的主要事件或行为
- When (何时): 时间信息（可选）
- Where (何地): 地点信息（可选）
- Why (为何): 原因或目的（可选）

请以 JSON 格式返回，例如：
{{
  "who": "张三",
  "what": "讨论了Python编程",
  "when": "昨天下午",
  "where": "办公室",
  "why": "为了解决技术问题"
}}
"""
        
        try:
            result = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": extract_prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            if result['success']:
                # 尝试解析 JSON
                content = result['content'].strip()
                # 移除可能的 markdown 代码块标记
                if content.startswith('```'):
                    content = content.split('\n', 1)[-1]
                if content.endswith('```'):
                    content = content.rsplit('\n', 1)[0]
                
                five_w_info = json.loads(content)
                print(f"✅ 成功提取5W信息")
                return five_w_info
            else:
                print(f"⚠️ 提取失败: {result.get('error', '未知错误')}")
                return {}
        except Exception as e:
            print(f"⚠️ 提取过程出错: {e}")
            return {}
    
    def _record_compressed_chat(self, compressed_summary):
        """
        记录压缩的聊天内容到日志文件
        
        参数:
            compressed_summary: 压缩后的聊天总结
        """
        if not self.enable_logging or not self.chat_logger:
            return
        
        # 提取5W信息
        five_w_info = self._extract_5w_from_compressed(compressed_summary)
        
        if five_w_info:
            # 格式化日志条目
            log_entry = self.chat_logger.format_log_entry(five_w_info)
            
            # 追加到日志文件
            if self.chat_logger.append_to_log(log_entry):
                print("✅ 已记录到日志文件")
            else:
                print("⚠️ 日志记录失败")
    
    def _search_chat_history(self, search_query):
        """
        搜索聊天历史
        
        参数:
            search_query: 搜索查询
            
        返回:
            str: 搜索结果
        """
        if not self.chat_logger:
            return "❌ 日志功能未启用"
        
        print(f"\n🔍 正在搜索聊天历史: '{search_query}'")
        
        # 读取日志文件
        log_content = self.chat_logger.read_log()
        
        if not log_content:
            return "📝 暂无聊天历史记录"
        
        # 构建搜索 prompt
        search_prompt = f"""请在以下聊天历史记录中查找与 "{search_query}" 相关的信息。

聊天记录：
{log_content}

请：
1. 找出所有相关的记录
2. 总结关键信息
3. 如果没有找到相关内容，请说明

请用中文回答。"""
        
        try:
            result = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": search_prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            if result['success']:
                print(f"✅ 搜索完成")
                return result['content']
            else:
                return f"❌ 搜索失败: {result.get('error', '未知错误')}"
        except Exception as e:
            return f"❌ 搜索出错: {e}"
    
    def _is_search_intent(self, user_message):
        """
        检测用户是否有搜索意图
        
        参数:
            user_message: 用户消息
            
        返回:
            bool: 是否是搜索意图
        """
        # 检查是否以 /search 开头
        if user_message.strip().startswith('/search'):
            return True
        
        # 检查是否包含搜索关键词
        search_keywords = [
            '查找聊天', '搜索历史', '查一下之前', '之前说过',
            '我记得我们聊过', '之前的对话', '历史记录',
            '找一下', '搜索一下', '查查'
        ]
        
        message_lower = user_message.lower()
        for keyword in search_keywords:
            if keyword in message_lower:
                return True
        
        return False
    
    def chat(self, user_message, temperature=0.7, max_tokens=2048, auto_compress=True):
        """
        与智能体对话
        
        参数:
            user_message: 用户输入的消息
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            auto_compress: 是否启用自动压缩
            
        返回:
            dict: 包含回复和性能统计
        """
        # 检查是否是搜索命令
        if self._is_search_intent(user_message):
            # 提取搜索关键词
            if user_message.strip().startswith('/search'):
                search_query = user_message.strip()[7:].strip()  # 移除 /search
            else:
                search_query = user_message
            
            print("\n🔎 检测到搜索意图，正在查找聊天历史...")
            search_result = self._search_chat_history(search_query)
            
            # 将搜索结果作为系统提示，继续正常对话
            enhanced_message = f"""根据聊天历史搜索结果：

{search_result}

用户问题：{user_message}

请结合以上信息回答用户的问题。"""
            
            # 使用增强后的消息进行正常对话
            user_message = enhanced_message
        
        # 检查是否需要压缩
        if auto_compress:
            needs_comp, rounds, length = self._needs_compression()
            if needs_comp:
                print(f"\n📊 上下文状态: {rounds} 轮对话, {length} 字符")
                # 执行压缩
                if self._compress_history_with_logging():
                    print("✅ 压缩并记录完成")
        
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 调用 LLM
        result = self.llm_client.chat_completion(
            messages=self.conversation_history,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if result['success']:
            # 添加助手回复到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": result['content']
            })
        
        return result
    
    def _compress_history_with_logging(self):
        """
        压缩聊天历史并记录到日志
        
        返回:
            bool: 是否成功
        """
        if len(self.conversation_history) <= 1:
            return False
        
        print("\n🔄 检测到上下文过长，正在压缩聊天历史...")
        
        # 保留系统提示
        system_message = None
        if self.conversation_history and self.conversation_history[0]['role'] == 'system':
            system_message = self.conversation_history[0]
        
        # 获取所有对话消息（排除系统提示）
        conversation_messages = self.conversation_history[1:] if system_message else self.conversation_history[:]
        
        if not conversation_messages:
            return False
        
        # 计算分割点
        total_messages = len(conversation_messages)
        compress_count = int(total_messages * self.compression_ratio)
        keep_count = total_messages - compress_count
        
        # 确保至少保留一条消息
        if keep_count < 1:
            keep_count = 1
            compress_count = total_messages - 1
        
        # 需要压缩的消息
        to_compress = conversation_messages[:compress_count]
        # 需要保留的消息
        to_keep = conversation_messages[compress_count:]
        
        # 构建压缩请求
        compress_prompt = """请对以下对话历史进行简洁总结，保留关键信息和上下文。
总结应该简明扼要，但要确保后续对话能够理解之前的讨论内容。

对话历史：
"""
        for msg in to_compress:
            role_label = "用户" if msg['role'] == 'user' else "助手"
            compress_prompt += f"{role_label}: {msg['content']}\n\n"
        
        compress_prompt += "\n请提供简洁的总结："
        
        try:
            # 调用 LLM 进行总结
            result = self.llm_client.chat_completion(
                messages=[{"role": "user", "content": compress_prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            if result['success']:
                summary = result['content']
                
                # 记录到日志文件
                if self.enable_logging:
                    self._record_compressed_chat(summary)
                
                # 构建新的历史记录
                new_history = []
                
                # 添加系统提示
                if system_message:
                    new_history.append(system_message)
                
                # 添加总结消息
                new_history.append({
                    "role": "system",
                    "content": f"[之前的对话总结]\n{summary}"
                })
                
                # 添加保留的最近对话
                new_history.extend(to_keep)
                
                # 更新历史记录
                old_length = self._get_context_length()
                self.conversation_history = new_history
                new_length = self._get_context_length()
                
                # 更新统计信息
                self.compression_count += 1
                compressed_tokens = old_length - new_length
                self.total_compressed_tokens += compressed_tokens
                
                print(f"✅ 压缩完成！")
                print(f"   - 压缩前: {old_length} 字符, {total_messages} 条消息")
                print(f"   - 压缩后: {new_length} 字符, {len(new_history)} 条消息")
                print(f"   - 减少: {compressed_tokens} 字符 ({compressed_tokens/old_length*100:.1f}%)")
                print(f"   - 累计压缩次数: {self.compression_count}")
                
                return True
            else:
                print(f"⚠️ 压缩失败: {result.get('error', '未知错误')}")
                return False
                
        except Exception as e:
            print(f"⚠️ 压缩过程出错: {e}")
            return False


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


def create_smart_agent(system_prompt=None, max_rounds=5, max_context_length=3000, 
                       compression_ratio=0.7, enable_logging=True,
                       log_file_path=r"D:\chat-log\log.txt"):
    """
    创建智能 AI 智能体实例（带自动压缩和日志功能）
    
    参数:
        system_prompt: 可选的系统提示
        max_rounds: 最大对话轮数阈值
        max_context_length: 最大上下文长度阈值
        compression_ratio: 压缩比例
        enable_logging: 是否启用聊天日志
        log_file_path: 日志文件路径
        
    返回:
        SmartAIAgent 实例
    """
    config = load_config()
    
    llm_client = LLMClient(
        base_url=config['LLM_BASE_URL'],
        model=config['LLM_MODEL'],
        api_token=config['LLM_API_TOKEN'],
        timeout=int(config.get('REQUEST_TIMEOUT', '30'))
    )
    
    return SmartAIAgent(
        llm_client, 
        system_prompt,
        max_rounds=max_rounds,
        max_context_length=max_context_length,
        compression_ratio=compression_ratio,
        enable_logging=enable_logging,
        log_file_path=log_file_path
    )
