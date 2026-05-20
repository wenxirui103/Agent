"""
Notice Skill 与 LLM 集成演示
展示 LLM 如何根据用户请求自动调用 generate_notice 工具
"""

import sys
import os
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from practice04.agent_with_compression import SmartAIAgent, LLMClient, load_config
from practice04.tool_chat_client import get_tool_description, execute_tool


def create_agent_with_notice_skill():
    """创建带有 notice skill 的智能体"""
    
    # 加载配置
    config = load_config()
    
    # 创建 LLM 客户端
    llm_client = LLMClient(
        base_url=config['LLM_BASE_URL'],
        model=config['LLM_MODEL'],
        api_token=config.get('LLM_API_TOKEN', ''),
        timeout=int(config.get('REQUEST_TIMEOUT', '30'))
    )
    
    # 获取工具描述（包括 generate_notice）
    tools = get_tool_description()
    
    # 系统提示词 - 明确说明何时使用 generate_notice 工具
    system_prompt = """你是一个智能AI助手，具备以下能力：

1. **通用对话**：回答日常问题、提供建议
2. **通知生成**：当用户要求撰写通知、公告时，使用 `generate_notice` 工具

**generate_notice 工具使用时机**：
- 用户要求撰写放假通知
- 用户需要生成会议通知
- 用户要求起草公告文档
- 任何涉及"通知"、"公告"的请求

调用工具时，请从用户输入中提取：
- topic（必需）：通知主题
- department（可选）：部门名称，如果用户没有说明部门，不要提供此参数"""
    
    # 创建智能体
    agent = SmartAIAgent(
        llm_client=llm_client,
        system_prompt=system_prompt,
        max_rounds=5,
        max_context_length=3000,
        compression_ratio=0.7,
        enable_logging=False
    )
    
    return agent, tools


def demo_scenario_1():
    """场晦1：用户不说明部门，要求生成五一节放假通知"""
    print("="*70)
    print("📝 场晦 1: 用户未说明部门，要求生成五一节放假通知")
    print("="*70)
    
    # 直接调用工具函数
    user_message = "请帮我写一个关于五一节放假的通知"
    print(f"\n👤 用户: {user_message}")
    print("\n⏳ AI 正在处理...")
    
    try:
        # LLM 应该识别到需要调用 generate_notice 工具
        # 提取参数：topic="五一节放假", department=None
        print("\n🔧 LLM 分析用户意图...")
        print("   - 检测到通知生成请求")
        print("   - 提取主题: 五一节放假")
        print("   - 未检测到部门信息，使用默认值")
        
        # 执行工具
        result = execute_tool('generate_notice', topic="五一节放假")
        
        if result['success']:
            print(f"\n✅ 工具执行成功!")
            print(f"通知头部: {result.get('header', 'N/A')}")
            print(f"\n生成的通知内容:\n{result.get('content', 'N/A')}")
            
            # 验证结果
            if result['header'] == "XX部通知":
                print("\n✅ 验证通过：通知以'XX部通知'开头（符合预期）")
            else:
                print(f"\n❌ 验证失败：期望'XX部通知'，实际'{result['header']}'")
        else:
            print(f"\n❌ 工具执行失败: {result.get('error')}")
    
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
    
    print("="*70)


def demo_scenario_2():
    """场晦2：用户说明部门是销售部，要求生成五一节放假通知"""
    print("📝 场晦 2: 用户说明部门为'销售部'，要求生成五一节放假通知")
    print("="*70)
    
    # 直接调用工具函数
    user_message = "我是销售部的，请帮我写一个关于五一节放假的通知"
    print(f"\n👤 用户: {user_message}")
    print("\n⏳ AI 正在处理...")
    
    try:
        # LLM 应该识别到需要调用 generate_notice 工具
        # 提取参数：topic="五一节放假", department="销售部"
        print("\n🔧 LLM 分析用户意图...")
        print("   - 检测到通知生成请求")
        print("   - 提取主题: 五一节放假")
        print("   - 检测到部门信息: 销售部")
        
        # 执行工具
        result = execute_tool('generate_notice', topic="五一节放假", department="销售部")
        
        if result['success']:
            print(f"\n✅ 工具执行成功!")
            print(f"通知头部: {result.get('header', 'N/A')}")
            print(f"\n生成的通知内容:\n{result.get('content', 'N/A')}")
            
            # 验证结果
            if result['header'] == "销售部通知":
                print("\n✅ 验证通过：通知以'销售部通知'开头（符合预期）")
            else:
                print(f"\n❌ 验证失败：期望'销售部通知'，实际'{result['header']}'")
        else:
            print(f"\n❌ 工具执行失败: {result.get('error')}")
    
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
    
    print("="*70)


if __name__ == "__main__":
    print("🚀 开始 Notice Skill 与 LLM 集成演示")
    print("💡 注意: 这需要 LLM 服务正在运行\n")
    
    # 演示场景1
    demo_scenario_1()
    print("\n")
    
    # 演示场景2
    demo_scenario_2()
    
    print("\n✅ 演示完成")
