"""
智能 AI 智能体交互演示 - 带自动压缩功能
展示聊天历史自动压缩的工作机制
"""

from agent_with_compression import create_smart_agent


def interactive_chat():
    """交互式聊天模式 - 演示自动压缩功能"""
    
    print("=" * 70)
    print("🤖 智能 AI 智能体 - 聊天历史自动压缩演示")
    print("=" * 70)
    print("\n💡 功能说明:")
    print("  - 当对话超过 5 轮或上下文超过 3000 字符时，自动触发压缩")
    print("  - 压缩策略：总结前 70% 的内容，保留最近 30% 的原始对话")
    print("  - 这样可以保持上下文连贯性，同时控制 token 消耗")
    print("  - 🆕 自动记录压缩内容到 D:\\chat-log\\log.txt（5W规则）")
    print("  - 🆕 支持 /search 命令搜索聊天历史")
    print("\n📝 命令:")
    print("  - 输入消息与 AI 对话")
    print("  - 'quit' 或 'exit': 退出")
    print("  - 'clear': 清空对话历史")
    print("  - 'history': 查看对话历史")
    print("  - 'stats': 查看统计信息（包括压缩次数和日志统计）")
    print("  - 'config': 查看压缩配置")
    print("  - '/search 关键词': 搜索聊天历史")
    print("  - '查找/搜索/之前聊过': 也会触发搜索功能")
    print("=" * 70)
    
    # 创建智能体（可以自定义压缩参数）
    system_prompt = """你是一个友好的AI助手，擅长回答问题、提供建议和进行有趣的对话。
请用简洁、清晰的方式回答，必要时提供示例。"""
    
    try:
        # 创建智能体，设置压缩阈值
        agent = create_smart_agent(
            system_prompt=system_prompt,
            max_rounds=5,           # 超过 5 轮触发压缩
            max_context_length=3000, # 超过 3000 字符触发压缩
            compression_ratio=0.7    # 压缩前 70%
        )
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
                print("\n👋 再见！感谢使用智能 AI 智能体。")
                break
            
            elif user_input.lower() == 'clear':
                agent.clear_history()
                print("✨ 对话历史已清空")
                total_messages = 0
                total_tokens = 0
                total_time = 0
                continue
            
            elif user_input.lower() == 'history':
                history = agent.get_history()
                print(f"\n📜 对话历史 (共 {len(history)} 条消息):")
                print("-" * 70)
                for i, msg in enumerate(history, 1):
                    role = "🤖 AI" if msg['role'] == 'assistant' else "👤 你" if msg['role'] == 'user' else "⚙️ 系统"
                    content = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
                    print(f"{i}. {role}: {content}")
                continue
            
            elif user_input.lower() == 'stats':
                stats = agent.get_stats()
                print(f"\n📊 会话统计:")
                print(f"   - 当前对话轮数: {stats['current_rounds']}")
                print(f"   - 当前上下文长度: {stats['current_context_length']} 字符")
                print(f"   - 总消息数: {stats['total_messages']}")
                print(f"   - 压缩次数: {stats['compression_count']}")
                print(f"   - 累计压缩字符: {stats['total_compressed_tokens']}")
                print(f"\n📈 性能统计:")
                print(f"   - 消息数量: {total_messages}")
                print(f"   - 总 Token 数: {total_tokens}")
                print(f"   - 总耗时: {total_time:.2f} 秒")
                if total_time > 0:
                    avg_speed = total_tokens / total_time
                    print(f"   - 平均速度: {avg_speed:.2f} tokens/秒")
                continue
            
            elif user_input.lower() == 'config':
                print(f"\n⚙️ 压缩配置:")
                print(f"   - 最大对话轮数: {agent.max_rounds}")
                print(f"   - 最大上下文长度: {agent.max_context_length} 字符")
                print(f"   - 压缩比例: {agent.compression_ratio * 100:.0f}%")
                print(f"   - 保留比例: {(1 - agent.compression_ratio) * 100:.0f}%")
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
    """演示模式 - 自动执行多个对话以触发压缩"""
    
    print("=" * 70)
    print("🤖 智能 AI 智能体 - 自动压缩演示模式")
    print("=" * 70)
    print("\n💡 本演示将自动进行多轮对话，展示压缩功能")
    print("=" * 70)
    
    try:
        agent = create_smart_agent(
            max_rounds=5,
            max_context_length=3000,
            compression_ratio=0.7
        )
        print("\n✅ 智能体已就绪！\n")
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        return
    
    # 设计一系列对话，确保触发压缩
    conversations = [
        "你好！请介绍一下你自己。",
        "Python 中列表和元组有什么区别？",
        "能给我一个快速排序的实现示例吗？",
        "这个算法的时间复杂度是多少？",
        "有没有更优化的排序算法？",
        "请解释一下归并排序的原理。",  # 第 6 轮，应该触发压缩
        "归并排序和快速排序哪个更好？",
        "在实际项目中如何选择排序算法？",
        "Python 的标准库中有哪些排序相关的函数？",
        "sorted() 和 list.sort() 有什么区别？",  # 第 10 轮，再次触发压缩
    ]
    
    for i, message in enumerate(conversations, 1):
        print(f"\n{'=' * 70}")
        print(f"对话 {i}/{len(conversations)}")
        print(f"{'=' * 70}")
        print(f"\n👤 你: {message}\n")
        
        # 显示当前状态
        stats = agent.get_stats()
        print(f"📊 当前状态: {stats['current_rounds']} 轮, {stats['current_context_length']} 字符, 压缩 {stats['compression_count']} 次")
        
        result = agent.chat(message)
        
        if result['success']:
            print(f"\n🤖 AI: {result['content']}\n")
            print(f"📈 性能: {result['elapsed_time']:.3f}s | {result['total_tokens']} tokens | {result['tokens_per_second']:.2f} t/s")
        else:
            print(f"❌ 错误: {result.get('error', '未知错误')}")
            break
        
        if i < len(conversations):
            input("\n按 Enter 继续下一轮对话...")
    
    # 最终统计
    print(f"\n{'=' * 70}")
    final_stats = agent.get_stats()
    print("✅ 演示完成！")
    print(f"{'=' * 70}")
    print(f"\n📊 最终统计:")
    print(f"   - 总对话轮数: {final_stats['current_rounds']}")
    print(f"   - 最终上下文长度: {final_stats['current_context_length']} 字符")
    print(f"   - 总消息数: {final_stats['total_messages']}")
    print(f"   - 压缩次数: {final_stats['compression_count']}")
    print(f"   - 累计压缩字符: {final_stats['total_compressed_tokens']}")
    print(f"\n💡 观察要点:")
    print(f"   - 注意看何时触发了压缩（第 6 轮和第 10 轮左右）")
    print(f"   - 压缩后上下文长度明显减少")
    print(f"   - 但对话仍然保持连贯性")


if __name__ == '__main__':
    import sys
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        demo_mode()
    else:
        interactive_chat()
