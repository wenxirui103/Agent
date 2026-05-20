"""
链式工具调用集成示例
展示如何在实际应用中集成和使用链式调用功能
"""

from agent_with_compression import create_smart_agent
from chained_tool_call import execute_chained_tool_call


def example_1_simple_notice():
    """示例 1: 简单通知生成（单步调用）"""
    print("\n" + "="*70)
    print("示例 1: 简单通知生成")
    print("="*70)
    
    agent = create_smart_agent(enable_logging=False)
    
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="帮我写一个技术部关于系统维护的通知",
        max_iterations=3,
        temperature=0.7
    )
    
    if result['success']:
        print("\n✅ 生成的通知:\n")
        print(result['answer'])
        print(f"\n📊 执行统计:")
        print(f"   - 迭代次数: {result['context'].current_iteration}")
        print(f"   - 工具调用: {len(result['context'].call_history)} 次")
    else:
        print(f"\n❌ 执行失败: {result.get('error')}")


def example_2_research_and_report():
    """示例 2: 研究并生成报告（多步调用）"""
    print("\n" + "="*70)
    print("示例 2: 网页内容研究与总结")
    print("="*70)
    
    agent = create_smart_agent(enable_logging=False)
    
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="访问 https://httpbin.org/html 并用中文简要总结页面内容（100字以内）",
        max_iterations=4,
        temperature=0.7
    )
    
    if result['success']:
        print("\n✅ 研究结果:\n")
        print(result['answer'])
        print(f"\n📊 执行统计:")
        print(f"   - 迭代次数: {result['context'].current_iteration}")
        print(f"   - 工具调用: {len(result['context'].call_history)} 次")
        
        # 显示详细的调用历史
        if result['context'].call_history:
            print("\n🔍 调用历史:")
            for i, call in enumerate(result['context'].call_history, 1):
                print(f"   {i}. {call['tool_name']} - {'成功' if call['success'] else '失败'}")
    else:
        print(f"\n❌ 执行失败: {result.get('error')}")


def example_3_custom_system_prompt():
    """示例 3: 使用自定义系统提示"""
    print("\n" + "="*70)
    print("示例 3: 专业商务助手（自定义系统提示）")
    print("="*70)
    
    agent = create_smart_agent(enable_logging=False)
    
    # 自定义系统提示
    custom_prompt = """你是一个专业的商务写作助手，具有以下特点：
- 语言风格：正式、专业、简洁
- 格式规范：严格遵循商务文档格式
- 内容要求：准确、清晰、条理分明
- 语气：礼貌、得体、适度正式

在生成任何文档时，请确保：
1. 使用专业的商务用语
2. 结构清晰，层次分明
3. 信息完整但不过于冗长
4. 符合中国商务文档的惯例"""
    
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="帮我写一个财务部关于年度预算提交截止日期的通知",
        system_prompt=custom_prompt,
        max_iterations=5,
        temperature=0.5  # 降低温度以获得更稳定的输出
    )
    
    if result['success']:
        print("\n✅ 生成的专业通知:\n")
        print(result['answer'])
        print(f"\n📊 执行统计:")
        print(f"   - 迭代次数: {result['context'].current_iteration}")
        print(f"   - 工具调用: {len(result['context'].call_history)} 次")
    else:
        print(f"\n❌ 执行失败: {result.get('error')}")


def example_4_context_inspection():
    """示例 4: 检查上下文详情"""
    print("\n" + "="*70)
    print("示例 4: 详细上下文检查")
    print("="*70)
    
    agent = create_smart_agent(enable_logging=False)
    
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="生成一个人力资源部关于员工培训的通知",
        max_iterations=5,
        temperature=0.7
    )
    
    if result['success']:
        context = result['context']
        
        print("\n✅ 任务完成！\n")
        print("最终答案:")
        print("-" * 70)
        print(result['answer'])
        print("-" * 70)
        
        print("\n📊 详细执行历史:")
        print("-" * 70)
        
        # 打印完整的调用历史
        for i, call in enumerate(context.call_history, 1):
            print(f"\n步骤 {i}:")
            print(f"  工具: {call['tool_name']}")
            print(f"  参数: {call['arguments']}")
            print(f"  成功: {'是' if call['success'] else '否'}")
            
            if call['success']:
                # 显示结果预览
                result_preview = str(call['result'].get('content', 
                                    call['result'].get('response', '')))[:200]
                print(f"  结果预览: {result_preview}...")
            else:
                print(f"  错误: {call['result'].get('error')}")
        
        print("\n" + "-" * 70)
        print("上下文变量:")
        print("-" * 70)
        if context.context_variables:
            for key, value in context.context_variables.items():
                value_str = str(value)[:100]
                print(f"  {key}: {value_str}...")
        else:
            print("  无上下文变量")
        
        print("\n" + "-" * 70)
        print("执行摘要:")
        print("-" * 70)
        summary = context.get_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
    else:
        print(f"\n❌ 执行失败: {result.get('error')}")


def example_5_error_handling():
    """示例 5: 错误处理演示"""
    print("\n" + "="*70)
    print("示例 5: 错误处理演示")
    print("="*70)
    
    agent = create_smart_agent(enable_logging=False)
    
    # 这个请求可能会导致 LLM 尝试调用不存在的工具或遇到其他问题
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="帮我查询今天的天气（注意：我们没有天气查询工具，看看系统如何处理）",
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
            status = "成功" if call['success'] else "失败"
            print(f"   {i}. {call['tool_name']} - {status}")
            if not call['success']:
                print(f"      错误: {call['result'].get('error')}")


def example_6_iterative_refinement():
    """示例 6: 迭代优化"""
    print("\n" + "="*70)
    print("示例 6: 复杂任务的迭代优化")
    print("="*70)
    
    agent = create_smart_agent(enable_logging=False)
    
    # 复杂任务，需要多次迭代
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="""请完成以下任务：
1. 生成一个销售部关于季度销售目标的通知
2. 然后告诉我这个通知的关键要点是什么
3. 最后给出改进建议""",
        max_iterations=8,
        temperature=0.7
    )
    
    if result['success']:
        print("\n✅ 最终结果:\n")
        print(result['answer'])
        
        context = result['context']
        print(f"\n📊 执行统计:")
        print(f"   - 总迭代次数: {context.current_iteration}/{context.max_iterations}")
        print(f"   - 工具调用次数: {len(context.call_history)}")
        print(f"   - 成功调用: {sum(1 for c in context.call_history if c['success'])}")
        print(f"   - 失败调用: {sum(1 for c in context.call_history if not c['success'])}")
        
        if context.call_history:
            print("\n🔍 执行流程:")
            for i, call in enumerate(context.call_history, 1):
                print(f"   {i}. {call['tool_name']} ({'✓' if call['success'] else '✗'})")
    else:
        print(f"\n❌ 执行失败: {result.get('error')}")


def interactive_mode():
    """交互模式：让用户自己输入请求"""
    print("\n" + "="*70)
    print("交互模式：链式工具调用")
    print("="*70)
    print("请输入你的请求，输入 'quit' 或 'exit' 退出")
    print("可用工具: generate_notice, fetch_webpage, anythingllm_query")
    print("-" * 70)
    
    agent = create_smart_agent(enable_logging=False)
    
    while True:
        try:
            user_input = input("\n📝 你的请求: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
            
            if not user_input:
                continue
            
            print("\n⏳ 正在处理...")
            
            result = execute_chained_tool_call(
                llm_client=agent.llm_client,
                user_request=user_input,
                max_iterations=5,
                temperature=0.7
            )
            
            if result['success']:
                print("\n✅ 结果:\n")
                print(result['answer'])
                
                # 显示简要统计
                context = result['context']
                print(f"\n[执行统计: {context.current_iteration} 次迭代, "
                      f"{len(context.call_history)} 次工具调用]")
            else:
                print(f"\n❌ 执行失败: {result.get('error')}")
                
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("链式工具调用集成示例")
    print("="*70)
    print("\n请选择要运行的示例:")
    print("1. 简单通知生成")
    print("2. 网页内容研究与总结")
    print("3. 专业商务助手（自定义系统提示）")
    print("4. 详细上下文检查")
    print("5. 错误处理演示")
    print("6. 复杂任务的迭代优化")
    print("7. 交互模式")
    print("0. 运行所有示例（1-6）")
    
    try:
        choice = input("\n请输入选择 (0-7): ").strip()
        
        examples = {
            '1': example_1_simple_notice,
            '2': example_2_research_and_report,
            '3': example_3_custom_system_prompt,
            '4': example_4_context_inspection,
            '5': example_5_error_handling,
            '6': example_6_iterative_refinement,
        }
        
        if choice == '0':
            # 运行所有示例
            for i in range(1, 7):
                examples[str(i)]()
                input("\n按回车继续下一个示例...")
        elif choice in examples:
            examples[choice]()
        elif choice == '7':
            interactive_mode()
        else:
            print("无效选择")
            
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
