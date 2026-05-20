"""
链式工具调用演示脚本
展示如何使用 ChainedCallContext 和 execute_chained_tool_call
"""

from agent_with_compression import create_smart_agent
from chained_tool_call import execute_chained_tool_call


def demo_simple_task():
    """演示简单任务：生成通知"""
    print("="*70)
    print("演示 1: 简单任务 - 生成部门通知")
    print("="*70)
    
    # 创建智能体
    agent = create_smart_agent(enable_logging=False)
    
    # 执行链式调用
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="帮我写一个人力资源部关于年会安排的通知",
        max_iterations=5,
        temperature=0.7
    )
    
    if result['success']:
        print("\n✅ 任务完成！\n")
        print(result['answer'])
        
        # 查看执行统计
        context = result['context']
        print(f"\n📊 执行统计:")
        print(f"   - 迭代次数: {context.current_iteration}")
        print(f"   - 工具调用: {len(context.call_history)} 次")
    else:
        print(f"\n❌ 任务失败: {result.get('error')}")


def demo_web_research():
    """演示网页研究任务"""
    print("\n" + "="*70)
    print("演示 2: 网页研究 - 访问并总结网页内容")
    print("="*70)
    
    agent = create_smart_agent(enable_logging=False)
    
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="访问 https://httpbin.org/html 并用一句话总结页面内容",
        max_iterations=3,
        temperature=0.7
    )
    
    if result['success']:
        print("\n✅ 任务完成！\n")
        print(result['answer'])
    else:
        print(f"\n❌ 任务失败: {result.get('error')}")


def demo_custom_system_prompt():
    """演示自定义系统提示"""
    print("\n" + "="*70)
    print("演示 3: 自定义系统提示 - 专业风格助手")
    print("="*70)
    
    agent = create_smart_agent(enable_logging=False)
    
    # 自定义系统提示
    custom_prompt = """你是一个专业的商务助手，语言风格正式、简洁。
在生成内容时，请使用专业的商务用语。"""
    
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="帮我写一个财务部关于预算审批流程的通知",
        system_prompt=custom_prompt,
        max_iterations=5,
        temperature=0.5  # 降低温度以获得更稳定的输出
    )
    
    if result['success']:
        print("\n✅ 任务完成！\n")
        print(result['answer'])
    else:
        print(f"\n❌ 任务失败: {result.get('error')}")


def demo_context_inspection():
    """演示检查上下文信息"""
    print("\n" + "="*70)
    print("演示 4: 检查上下文 - 查看详细的执行历史")
    print("="*70)
    
    agent = create_smart_agent(enable_logging=False)
    
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="生成一个技术部关于系统维护的通知",
        max_iterations=5,
        temperature=0.7
    )
    
    if result['success']:
        context = result['context']
        
        print("\n✅ 任务完成！\n")
        print("最终答案:")
        print(result['answer'])
        
        print("\n" + "-"*70)
        print("详细执行历史:")
        print("-"*70)
        
        # 打印完整的调用历史
        for i, call in enumerate(context.call_history, 1):
            print(f"\n步骤 {i}:")
            print(f"  工具: {call['tool_name']}")
            print(f"  参数: {call['arguments']}")
            print(f"  成功: {'是' if call['success'] else '否'}")
            
            if call['success']:
                result_preview = str(call['result'].get('content', 
                                    call['result'].get('response', '')))[:200]
                print(f"  结果预览: {result_preview}...")
            else:
                print(f"  错误: {call['result'].get('error')}")
        
        print("\n" + "-"*70)
        print("上下文变量:")
        print("-"*70)
        if context.context_variables:
            for key, value in context.context_variables.items():
                print(f"  {key}: {str(value)[:100]}...")
        else:
            print("  无上下文变量")
        
        print("\n" + "-"*70)
        print("执行摘要:")
        print("-"*70)
        summary = context.get_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")


def demo_error_handling():
    """演示错误处理"""
    print("\n" + "="*70)
    print("演示 5: 错误处理 - 测试无效工具调用")
    print("="*70)
    
    agent = create_smart_agent(enable_logging=False)
    
    # 这个请求可能会导致 LLM 尝试调用不存在的工具
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="帮我查询今天的天气（注意：我们没有天气查询工具）",
        max_iterations=3,
        temperature=0.7
    )
    
    print("\n📊 执行结果:")
    print(f"   成功: {result['success']}")
    print(f"   答案: {result['answer'][:200]}...")
    
    context = result['context']
    print(f"\n📊 执行统计:")
    print(f"   - 迭代次数: {context.current_iteration}")
    print(f"   - 工具调用: {len(context.call_history)} 次")
    
    if context.call_history:
        print("\n🔍 工具调用历史:")
        for i, call in enumerate(context.call_history, 1):
            print(f"   {i}. {call['tool_name']} - {'成功' if call['success'] else '失败'}")
            if not call['success']:
                print(f"      错误: {call['result'].get('error')}")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("链式工具调用演示")
    print("="*70)
    print("\n本演示展示了如何使用链式工具调用功能来完成复杂任务。")
    print("每个演示都会展示不同的使用场景和特性。\n")
    
    try:
        # 运行所有演示
        demo_simple_task()
        demo_web_research()
        demo_custom_system_prompt()
        demo_context_inspection()
        demo_error_handling()
        
        print("\n" + "="*70)
        print("✅ 所有演示完成！")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断演示")
    except Exception as e:
        print(f"\n\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
