"""
链式工具调用测试脚本
测试 ChainedCallContext 和 execute_chained_tool_call 的功能
"""

from agent_with_compression import create_smart_agent
from chained_tool_call import execute_chained_tool_call, ChainedCallContext


def test_context_basic():
    """测试上下文管理器的基本功能"""
    print("="*60)
    print("测试 1: ChainedCallContext 基本功能")
    print("="*60)
    
    context = ChainedCallContext(max_iterations=5)
    
    # 测试变量存储
    context.set_variable("test_var", "test_value")
    assert context.get_variable("test_var") == "test_value"
    assert context.get_variable("non_exist", "default") == "default"
    print("✅ 变量存储测试通过")
    
    # 测试迭代控制
    assert context.can_continue() == True
    context.increment_iteration()
    assert context.current_iteration == 1
    print("✅ 迭代控制测试通过")
    
    # 添加工具调用记录
    context.add_tool_call("test_tool", {"param": "value"}, {"success": True, "result": "ok"})
    assert len(context.call_history) == 1
    print("✅ 工具调用记录测试通过")
    
    # 测试完成标记
    context.complete("Final answer")
    assert context.is_completed == True
    assert context.final_answer == "Final answer"
    assert context.can_continue() == False
    print("✅ 完成标记测试通过")
    
    # 获取摘要
    summary = context.get_summary()
    print(f"📊 执行摘要: {summary}")
    
    # 获取历史文本
    history_text = context.get_history_text()
    print(f"📝 历史文本:\n{history_text}")
    
    print("\n✅ 所有基本功能测试通过！\n")


def test_generate_notice():
    """测试生成通知的链式调用"""
    print("="*60)
    print("测试 2: 生成部门通知")
    print("="*60)
    
    agent = create_smart_agent(enable_logging=False)
    
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="帮我写一个技术部关于五一放假的通知",
        max_iterations=5,
        temperature=0.7
    )
    
    if result['success']:
        print(f"\n✅ 执行成功！")
        print(f"\n📄 最终答案:\n{result['answer']}")
        
        # 打印上下文信息
        context = result['context']
        print(f"\n📊 执行统计:")
        print(f"   - 迭代次数: {context.current_iteration}")
        print(f"   - 工具调用: {len(context.call_history)} 次")
        for i, call in enumerate(context.call_history, 1):
            print(f"     {i}. {call['tool_name']} - {'成功' if call['success'] else '失败'}")
    else:
        print(f"\n❌ 执行失败: {result.get('error')}")
        if 'context' in result:
            print(f"   已执行迭代: {result['context'].current_iteration}")
    
    print()


def test_fetch_webpage():
    """测试访问网页的链式调用"""
    print("="*60)
    print("测试 3: 访问网页并总结")
    print("="*60)
    
    agent = create_smart_agent(enable_logging=False)
    
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="访问 https://httpbin.org/html 并简要描述页面内容（一句话即可）",
        max_iterations=3,
        temperature=0.7
    )
    
    if result['success']:
        print(f"\n✅ 执行成功！")
        print(f"\n📄 最终答案:\n{result['answer']}")
        
        context = result['context']
        print(f"\n📊 执行统计:")
        print(f"   - 迭代次数: {context.current_iteration}")
        print(f"   - 工具调用: {len(context.call_history)} 次")
    else:
        print(f"\n❌ 执行失败: {result.get('error')}")
    
    print()


def test_multi_step_task():
    """测试多步骤任务"""
    print("="*60)
    print("测试 4: 多步骤任务（生成通知 + 查询信息）")
    print("="*60)
    
    agent = create_smart_agent(enable_logging=False)
    
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="先生成一个销售部关于年会的通知，然后告诉我这个通知的主题是什么",
        max_iterations=8,
        temperature=0.7
    )
    
    if result['success']:
        print(f"\n✅ 执行成功！")
        print(f"\n📄 最终答案:\n{result['answer']}")
        
        context = result['context']
        print(f"\n📊 执行统计:")
        print(f"   - 迭代次数: {context.current_iteration}")
        print(f"   - 工具调用: {len(context.call_history)} 次")
        for i, call in enumerate(context.call_history, 1):
            print(f"     {i}. {call['tool_name']} - {'成功' if call['success'] else '失败'}")
    else:
        print(f"\n❌ 执行失败: {result.get('error')}")
    
    print()


def test_max_iterations():
    """测试最大迭代次数限制"""
    print("="*60)
    print("测试 5: 最大迭代次数限制")
    print("="*60)
    
    agent = create_smart_agent(enable_logging=False)
    
    # 设置很小的迭代次数，测试限制功能
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="帮我写一个关于春节放假的通知",
        max_iterations=2,  # 只允许 2 次迭代
        temperature=0.7
    )
    
    print(f"\n📊 执行结果:")
    print(f"   - 成功: {result['success']}")
    print(f"   - 答案: {result['answer'][:100]}...")
    
    context = result['context']
    print(f"   - 实际迭代: {context.current_iteration}")
    print(f"   - 达到限制: {context.current_iteration >= 2}")
    
    print()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("开始链式工具调用测试")
    print("="*60 + "\n")
    
    try:
        # 运行测试
        test_context_basic()
        test_generate_notice()
        test_fetch_webpage()
        test_multi_step_task()
        test_max_iterations()
        
        print("="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
