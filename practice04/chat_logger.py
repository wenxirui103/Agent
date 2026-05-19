"""
聊天日志管理模块
实现基于5W规则的聊天信息提取和本地存储
"""

import os
import json
from datetime import datetime


class ChatLogger:
    """聊天日志管理器 - 负责记录和分析聊天历史"""
    
    def __init__(self, log_file_path=r"D:\chat-log\log.txt"):
        """
        初始化聊天日志管理器
        
        参数:
            log_file_path: 日志文件路径
        """
        self.log_file_path = log_file_path
        # 确保目录存在
        log_dir = os.path.dirname(log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def extract_5w_info(self, conversation_text):
        """
        从对话文本中提取5W信息（需要调用LLM）
        
        参数:
            conversation_text: 对话文本
            
        返回:
            dict: 包含5W信息的字典
        """
        # 这个方法会在 SmartAIAgent 中通过 LLM 调用
        # 这里只提供数据结构定义
        return {
            'who': '',      # 谁
            'what': '',     # 做了什么事
            'when': '',     # 什么时候（可选）
            'where': '',    # 在何处（可选）
            'why': ''       # 为什么（可选）
        }
    
    def format_log_entry(self, five_w_info, timestamp=None):
        """
        格式化日志条目
        
        参数:
            five_w_info: 5W信息字典
            timestamp: 时间戳，默认为当前时间
            
        返回:
            str: 格式化的日志条目
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"\n{'='*60}\n"
        log_entry += f"📅 时间: {timestamp}\n"
        log_entry += f"{'='*60}\n"
        
        if five_w_info.get('who'):
            log_entry += f"👤 Who (谁): {five_w_info['who']}\n"
        if five_w_info.get('what'):
            log_entry += f"📝 What (做了什么): {five_w_info['what']}\n"
        if five_w_info.get('when'):
            log_entry += f"⏰ When (何时): {five_w_info['when']}\n"
        if five_w_info.get('where'):
            log_entry += f"📍 Where (何地): {five_w_info['where']}\n"
        if five_w_info.get('why'):
            log_entry += f"💡 Why (为何): {five_w_info['why']}\n"
        
        log_entry += f"{'='*60}\n"
        
        return log_entry
    
    def append_to_log(self, log_entry):
        """
        追加日志到文件（增量更新）
        
        参数:
            log_entry: 格式化的日志条目
            
        返回:
            bool: 是否成功
        """
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            return True
        except Exception as e:
            print(f"❌ 写入日志失败: {e}")
            return False
    
    def read_log(self):
        """
        读取完整的日志文件
        
        返回:
            str: 日志内容
        """
        if not os.path.exists(self.log_file_path):
            return ""
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ 读取日志失败: {e}")
            return ""
    
    def search_in_log(self, keyword):
        """
        在日志中搜索关键词
        
        参数:
            keyword: 搜索关键词
            
        返回:
            list: 匹配的日志条目列表
        """
        if not os.path.exists(self.log_file_path):
            return []
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单关键词匹配
            lines = content.split('\n')
            matches = []
            current_entry = []
            
            for line in lines:
                current_entry.append(line)
                if line.startswith('=' * 60):
                    # 检查这个条目是否包含关键词
                    entry_text = '\n'.join(current_entry)
                    if keyword.lower() in entry_text.lower():
                        matches.append(entry_text)
                    current_entry = []
            
            return matches
        except Exception as e:
            print(f"❌ 搜索日志失败: {e}")
            return []
    
    def get_log_stats(self):
        """
        获取日志统计信息
        
        返回:
            dict: 统计信息
        """
        if not os.path.exists(self.log_file_path):
            return {
                'total_entries': 0,
                'file_size': 0,
                'file_exists': False
            }
        
        try:
            file_size = os.path.getsize(self.log_file_path)
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 计算条目数（每个条目以 ====== 分隔）
            entries = content.split('=' * 60)
            total_entries = len([e for e in entries if e.strip()])
            
            return {
                'total_entries': total_entries,
                'file_size': file_size,
                'file_size_kb': round(file_size / 1024, 2),
                'file_exists': True
            }
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {
                'total_entries': 0,
                'file_size': 0,
                'file_exists': False
            }


def create_chat_logger(log_file_path=None):
    """
    工厂函数：创建聊天日志管理器
    
    参数:
        log_file_path: 日志文件路径，默认 D:\chat-log\log.txt
        
    返回:
        ChatLogger 实例
    """
    if log_file_path is None:
        log_file_path = r"D:\chat-log\log.txt"
    
    return ChatLogger(log_file_path)
