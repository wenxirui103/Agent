"""
AI 智能体交互演示
展示如何创建和使用智能体进行对话
"""

from agent import create_agent


def interactive_chat():
    """交互式聊天模式"""
    
    print("=" * 70)
    print("🤖 AI 智能体交互演示")
    print("=" * 70)
    print("\n💡 提示:")
    print("  - 输入消息与 AI 对话")
    print("  - 输入 'quit' 或 'exit' 退出")
    print("  - 输入 'clear' 清空对话历史")
    print("  - 输入 'history' 查看对话历史")
    print("  - 输入 'stats' 查看统计信息")
    print("=" * 70)
    
    # 创建智能体（可以自定义系统提示）
    system_prompt = """你是一个友好的AI助手，擅长回答问题、提供建议和进行有趣的对话。
请用简洁、清晰的方式回答，必要时提供示例。"""
    
    try:
        agent = create_agent(system_prompt)
        print("\n✅ 智能体已就绪！开始对话吧...\n")
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        print("\n💡 请确保:")
        print("  1. .env 文件存在且配置正确")
        print("  2. DeepSeek API 密钥有效")
        print("  3. 网络连接正常")
        return
    
    # 统计信息
    total_messages = 0
    total_tokens = 0
    total_time = 0
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 你: ").strip()
            
            if not user_input:
                continue
            
            # 处理特殊命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 再见！感谢使用 AI 智能体。")
                break
            
            elif user_input.lower() == 'clear':
                agent.clear_history()
                print("✨ 对话历史已清空")
                continue
            
            elif user_input.lower() == 'history':
                history = agent.get_history()
                print(f"\n📜 对话历史 (共 {len(history)} 条消息):")
                print("-" * 70)
                for i, msg in enumerate(history, 1):
                    role = "🤖 AI" if msg['role'] == 'assistant' else "👤 你" if msg['role'] == 'user' else "⚙️ 系统"
                    content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                    print(f"{i}. {role}: {content}")
                continue
            
            elif user_input.lower() == 'stats':
                print(f"\n📊 会话统计:")
                print(f"   - 消息数量: {total_messages}")
                print(f"   - 总 Token 数: {total_tokens}")
                print(f"   - 总耗时: {total_time:.2f} 秒")
                if total_time > 0:
                    avg_speed = total_tokens / total_time
                    print(f"   - 平均速度: {avg_speed:.2f} tokens/秒")
                continue
            
            # 发送消息到智能体
            print("\n⏳ AI 正在思考...")
            result = agent.chat(user_input)
            
            if result['success']:
                # 显示回复
                print(f"\n🤖 AI: {result['content']}")
                
                # 更新统计
                total_messages += 1
                total_tokens += result.get('total_tokens', 0)
                total_time += result.get('elapsed_time', 0)
                
                # 显示本次性能
                print(f"\n📈 性能指标:")
                print(f"   - 响应时间: {result['elapsed_time']:.3f} 秒")
                print(f"   - Token 消耗: {result['total_tokens']}")
                print(f"   - 生成速度: {result['tokens_per_second']:.2f} tokens/秒")
            else:
                print(f"\n❌ 错误: {result.get('error', '未知错误')}")
                print("\n💡 可能的原因:")
                print("  1. API 密钥无效或已过期")
                print("  2. 网络连接问题")
                print("  3. API 配额已用完")
        
        except KeyboardInterrupt:
            print("\n\n👋 检测到中断，再见！")
            break
        except EOFError:
            print("\n\n👋 输入结束，再见！")
            break


def demo_mode():
    """演示模式 - 自动执行几个示例对话"""
    
    print("=" * 70)
    print("🤖 AI 智能体演示模式")
    print("=" * 70)
    
    try:
        agent = create_agent()
        print("\n✅ 智能体已就绪！\n")
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        return
    
    # 示例问题
    questions = [
        "你好！请简单介绍一下自己。",
        "Python 中列表和元组有什么区别？",
        "能给我一个快速排序的实现示例吗？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'=' * 70}")
        print(f"示例 {i}/{len(questions)}")
        print(f"{'=' * 70}")
        print(f"\n👤 问题: {question}\n")
        
        result = agent.chat(question)
        
        if result['success']:
            print(f"🤖 回答: {result['content']}\n")
            print(f"📊 性能:")
            print(f"   - 响应时间: {result['elapsed_time']:.3f} 秒")
            print(f"   - Token 消耗: {result['total_tokens']}")
            print(f"   - 生成速度: {result['tokens_per_second']:.2f} tokens/秒")
        else:
            print(f"❌ 错误: {result.get('error', '未知错误')}")
            break
        
        if i < len(questions):
            input("\n按 Enter 继续下一个示例...")
    
    print(f"\n{'=' * 70}")
    print("✅ 演示完成！")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    import sys
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        demo_mode()
    else:
        interactive_chat()
