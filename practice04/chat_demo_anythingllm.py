"""
AI 智能体交互演示 - practice04 版本
集成 AnythingLLM 知识库查询功能
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# 自动加载 .env 文件
from practice04.load_env import load_env_file
load_env_file()

from practice04.agent_with_compression import SmartAIAgent, LLMClient, load_config
from practice04.tool_chat_client import get_tool_description, execute_tool


def create_agent_with_tools():
    """创建带有工具的智能体"""
    
    # 加载配置
    config = load_config()
    
    # 创建 LLM 客户端
    llm_client = LLMClient(
        base_url=config['LLM_BASE_URL'],
        model=config['LLM_MODEL'],
        api_token=config.get('LLM_API_TOKEN', ''),
        timeout=int(config.get('REQUEST_TIMEOUT', '30'))
    )
    
    # 获取工具描述
    tools = get_tool_description()
    
    # 系统提示词 - 明确说明何时使用 anythingllm_query 工具
    system_prompt = """你是一个智能AI助手，具备以下能力：

1. **通用对话**：回答日常问题、提供建议、进行聊天
2. **网页访问**：可以访问指定的URL获取网页内容
3. **知识库查询**：可以查询 AnythingLLM 本地知识库

**工具使用说明**：
- 当用户询问关于公司内部文档、项目资料、特定知识库内容时，请使用 `anythingllm_query` 工具
- 当用户需要访问外部网页时，请使用 `fetch_webpage` 工具
- 对于普通问题，直接回答即可

**anythingllm_query 工具使用时机**：
- 用户询问公司政策、内部流程
- 用户查询项目文档、技术规范
- 用户需要了解已上传到知识库的内容
- 用户明确要求查询知识库或文档

调用工具时，请提供必要的参数。如果缺少API密钥等必需信息，请告知用户。"""
    
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


def handle_tool_calls(agent, tools):
    """处理工具调用"""
    
    print("\n" + "="*70)
    print("🤖 AI 智能体交互演示 (practice04 - AnythingLLM 集成)")
    print("="*70)
    print("\n💡 提示:")
    print("  - 输入消息与 AI 对话")
    print("  - 输入 'quit' 或 'exit' 退出")
    print("  - 输入 'clear' 清空对话历史")
    print("  - 输入 'history' 查看对话历史")
    print("  - 输入 'stats' 查看统计信息")
    print("  - 输入 'compress' 手动触发压缩")
    print("="*70)
    print("\n✅ 智能体已就绪！开始对话吧...\n")
    
    # 从环境变量或 .env 文件读取 AnythingLLM API Key
    anythingllm_api_key = os.getenv('ANYTHINGLLM_API_KEY', '')
    
    if not anythingllm_api_key:
        print("⚠️  警告: 未设置 ANYTHINGLLM_API_KEY")
        print("   请在 .env 文件中配置或在环境中设置该变量\n")
    
    while True:
        try:
            user_input = input("👤 你: ").strip()
            
            if not user_input:
                continue
            
            # 检查退出命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 再见！")
                break
            
            # 检查清空历史
            if user_input.lower() == 'clear':
                agent.clear_history()
                print("✅ 对话历史已清空")
                continue
            
            # 查看历史
            if user_input.lower() == 'history':
                history = agent.get_history()
                print(f"\n📜 对话历史 (共 {len(history)} 条消息):")
                for i, msg in enumerate(history, 1):
                    role = msg['role']
                    content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                    print(f"  {i}. [{role}] {content}")
                continue
            
            # 查看统计
            if user_input.lower() == 'stats':
                rounds = agent._get_conversation_rounds()
                context_length = agent._get_context_length()
                print(f"\n📊 统计信息:")
                print(f"  - 对话轮数: {rounds}")
                print(f"  - 上下文长度: {context_length} 字符")
                print(f"  - 压缩次数: {agent.compression_count}")
                print(f"  - 最大轮数阈值: {agent.max_rounds}")
                print(f"  - 最大上下文阈值: {agent.max_context_length} 字符")
                continue
            
            # 手动压缩
            if user_input.lower() == 'compress':
                print("\n⏳ 正在压缩对话历史...")
                success = agent.compress_history()
                if success:
                    print("✅ 压缩完成")
                else:
                    print("ℹ️  无需压缩或压缩失败")
                continue
            
            # 发送消息到 AI
            print("\n⏳ AI 正在思考...")
            result = agent.chat(
                user_message=user_input,
                temperature=float(os.getenv('TEMPERATURE', '0.7')),
                max_tokens=int(os.getenv('MAX_TOKENS', '2048')),
                auto_compress=True
            )
            
            if result['success']:
                response = result['content']
                
                # 检查是否需要调用工具
                # 注意：这里简化处理，实际应该解析 LLM 返回的工具调用
                # 如果需要更复杂的工具调用逻辑，可以扩展
                
                print(f"\n🤖 AI: {response}")
                
                # 显示性能统计
                print(f"\n⏱️  性能统计:")
                print(f"   - 响应时间: {result['elapsed_time']:.3f} 秒")
                print(f"   - Token 速度: {result['tokens_per_second']:.2f} tokens/秒")
                
            else:
                print(f"\n❌ 错误: {result.get('error', '未知错误')}")
                print("\n💡 可能的原因:")
                print("  1. LM Studio 未启动")
                print("  2. 模型未正确加载")
                print("  3. 网络连接问题")
        
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    # 检查是否提供了 AnythingLLM API Key
    if not os.getenv('ANYTHINGLLM_API_KEY'):
        print("⚠️  警告: 未设置 ANYTHINGLLM_API_KEY 环境变量")
        print("   如需使用 AnythingLLM 查询功能，请设置该环境变量\n")
    
    # 创建智能体
    agent, tools = create_agent_with_tools()
    
    # 运行交互
    handle_tool_calls(agent, tools)
