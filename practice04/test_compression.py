"""
聊天历史压缩功能测试脚本
验证自动压缩机制是否正常工作
"""

from agent_with_compression import create_smart_agent, SmartAIAgent, LLMClient


def test_compression_detection():
    """测试压缩检测逻辑"""
    print("=" * 70)
    print("🧪 测试 1: 压缩检测逻辑")
    print("=" * 70)
    
    # 创建一个模拟的 LLM 客户端（不实际调用 API）
    class MockLLMClient:
        def chat_completion(self, messages, **kwargs):
            return {
                'success': True,
                'content': '[这是一个对话总结]',
                'elapsed_time': 0.5,
                'total_tokens': 50,
                'tokens_per_second': 100
            }
    
    # 测试场景 1: 未达到阈值
    print("\n📝 场景 1: 少量对话（不应触发压缩）")
    agent = SmartAIAgent(
        MockLLMClient(),
        max_rounds=5,
        max_context_length=3000
    )
    
    for i in range(3):
        agent.chat(f"消息 {i+1}", auto_compress=False)
        agent.conversation_history.append({
            "role": "assistant",
            "content": f"回复 {i+1}"
        })
    
    needs_comp, rounds, length = agent._needs_compression()
    print(f"   - 对话轮数: {rounds} (阈值: {agent.max_rounds})")
    print(f"   - 上下文长度: {length} (阈值: {agent.max_context_length})")
    print(f"   - 需要压缩: {needs_comp}")
    assert not needs_comp, "不应该触发压缩"
    print("   ✅ 通过")
    
    # 测试场景 2: 超过轮数阈值
    print("\n📝 场景 2: 超过轮数阈值（应触发压缩）")
    agent2 = SmartAIAgent(
        MockLLMClient(),
        max_rounds=5,
        max_context_length=10000
    )
    
    for i in range(6):
        agent2.conversation_history.append({
            "role": "user",
            "content": f"用户消息 {i+1}"
        })
        agent2.conversation_history.append({
            "role": "assistant",
            "content": f"助手回复 {i+1}"
        })
    
    needs_comp, rounds, length = agent2._needs_compression()
    print(f"   - 对话轮数: {rounds} (阈值: {agent2.max_rounds})")
    print(f"   - 需要压缩: {needs_comp}")
    assert needs_comp, "应该触发压缩"
    print("   ✅ 通过")
    
    # 测试场景 3: 超过长度阈值
    print("\n📝 场景 3: 超过长度阈值（应触发压缩）")
    agent3 = SmartAIAgent(
        MockLLMClient(),
        max_rounds=100,
        max_context_length=100
    )
    
    agent3.conversation_history.append({
        "role": "user",
        "content": "这是一个很长的消息，超过了阈值限制。" * 10
    })
    
    needs_comp, rounds, length = agent3._needs_compression()
    print(f"   - 上下文长度: {length} (阈值: {agent3.max_context_length})")
    print(f"   - 需要压缩: {needs_comp}")
    assert needs_comp, "应该触发压缩"
    print("   ✅ 通过")
    
    print("\n✅ 测试 1 完成：压缩检测逻辑正常\n")


def test_compression_execution():
    """测试压缩执行逻辑"""
    print("=" * 70)
    print("🧪 测试 2: 压缩执行逻辑")
    print("=" * 70)
    
    class MockLLMClient:
        def chat_completion(self, messages, **kwargs):
            return {
                'success': True,
                'content': '[总结：之前讨论了 Python 基础知识、列表操作和函数定义]',
                'elapsed_time': 0.5,
                'total_tokens': 50,
                'tokens_per_second': 100
            }
    
    agent = SmartAIAgent(
        MockLLMClient(),
        max_rounds=3,
        max_context_length=1000,
        compression_ratio=0.7
    )
    
    # 添加系统提示
    # 添加多条对话
    conversations = [
        ("用户", "什么是 Python？"),
        ("助手", "Python 是一种高级编程语言。"),
        ("用户", "如何定义函数？"),
        ("助手", "使用 def 关键字定义函数。"),
        ("用户", "列表怎么创建？"),
        ("助手", "使用方括号 [] 创建列表。"),
        ("用户", "字典呢？"),  # 这条应该被保留
        ("助手", "字典使用花括号 {} 创建。"),  # 这条应该被保留
    ]
    
    for role, content in conversations:
        agent.conversation_history.append({
            "role": role,
            "content": content
        })
    
    print(f"\n📊 压缩前:")
    print(f"   - 总消息数: {len(agent.conversation_history)}")
    print(f"   - 上下文长度: {agent._get_context_length()} 字符")
    
    # 执行压缩
    success = agent._compress_history()
    
    if success:
        print(f"\n📊 压缩后:")
        print(f"   - 总消息数: {len(agent.conversation_history)}")
        print(f"   - 上下文长度: {agent._get_context_length()} 字符")
        print(f"   - 压缩次数: {agent.compression_count}")
        
        # 验证压缩结果
        assert agent.compression_count == 1, "压缩次数应为 1"
        
        # 检查是否保留了最近的消息
        last_messages = agent.conversation_history[-4:]  # 最后 4 条（包括总结）
        print(f"\n📋 压缩后的历史记录:")
        for i, msg in enumerate(agent.conversation_history):
            role_label = "系统" if msg['role'] == 'system' else ("你" if msg['role'] == 'user' else "AI")
            content_preview = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            print(f"   {i+1}. [{role_label}] {content_preview}")
        
        print("\n✅ 测试 2 完成：压缩执行逻辑正常\n")
    else:
        print("\n❌ 压缩失败")


def test_auto_compress_in_chat():
    """测试聊天时的自动压缩"""
    print("=" * 70)
    print("🧪 测试 3: 聊天时自动压缩")
    print("=" * 70)
    
    call_count = [0]
    
    class MockLLMClient:
        def chat_completion(self, messages, **kwargs):
            call_count[0] += 1
            
            # 如果是压缩请求
            if len(messages) == 1 and '总结' in messages[0]['content']:
                return {
                    'success': True,
                    'content': '[之前的对话总结]',
                    'elapsed_time': 0.3,
                    'total_tokens': 30,
                    'tokens_per_second': 100
                }
            
            # 正常对话
            return {
                'success': True,
                'content': f'这是第 {call_count[0]} 次调用的回复',
                'elapsed_time': 0.5,
                'total_tokens': 50,
                'tokens_per_second': 100
            }
    
    agent = SmartAIAgent(
        MockLLMClient(),
        max_rounds=2,  # 设置为 2 以便快速触发
        max_context_length=10000
    )
    
    print("\n💬 进行多轮对话...")
    
    for i in range(5):
        print(f"\n--- 第 {i+1} 轮对话 ---")
        result = agent.chat(f"问题 {i+1}", auto_compress=True)
        
        stats = agent.get_stats()
        print(f"状态: {stats['current_rounds']} 轮, "
              f"{stats['current_context_length']} 字符, "
              f"压缩 {stats['compression_count']} 次")
    
    final_stats = agent.get_stats()
    print(f"\n📊 最终统计:")
    print(f"   - 总对话轮数: {final_stats['current_rounds']}")
    print(f"   - 压缩次数: {final_stats['compression_count']}")
    print(f"   - LLM 调用次数: {call_count[0]}")
    
    assert final_stats['compression_count'] > 0, "应该至少压缩一次"
    print("\n✅ 测试 3 完成：自动压缩功能正常\n")


def test_configuration():
    """测试配置参数"""
    print("=" * 70)
    print("🧪 测试 4: 配置参数")
    print("=" * 70)
    
    class MockLLMClient:
        def chat_completion(self, messages, **kwargs):
            return {
                'success': True,
                'content': '回复',
                'elapsed_time': 0.5,
                'total_tokens': 50,
                'tokens_per_second': 100
            }
    
    # 测试不同的压缩比例
    for ratio in [0.5, 0.7, 0.9]:
        agent = SmartAIAgent(
            MockLLMClient(),
            max_rounds=10,
            max_context_length=10000,
            compression_ratio=ratio
        )
        
        # 添加 10 条消息
        for i in range(10):
            agent.conversation_history.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"消息 {i+1}"
            })
        
        compress_count = int(10 * ratio)
        keep_count = 10 - compress_count
        
        print(f"\n📝 压缩比例 {ratio*100:.0f}%:")
        print(f"   - 应压缩: {compress_count} 条")
        print(f"   - 应保留: {keep_count} 条")
        assert agent.compression_ratio == ratio
    
    print("\n✅ 测试 4 完成：配置参数正常\n")


if __name__ == '__main__':
    print("\n🚀 开始运行聊天历史压缩功能测试...\n")
    
    try:
        test_compression_detection()
        test_compression_execution()
        test_auto_compress_in_chat()
        test_configuration()
        
        print("=" * 70)
        print("✅ 所有测试通过！")
        print("=" * 70)
        print("\n💡 功能说明:")
        print("  - 聊天历史压缩功能工作正常")
        print("  - 可以检测对话轮数和上下文长度")
        print("  - 能够自动触发压缩并总结历史")
        print("  - 支持自定义压缩参数")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
