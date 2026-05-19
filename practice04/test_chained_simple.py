"""
链式工具调用简单测试 - 不需要外部 API
"""

from chained_tool_call import ChainedCallContext, parse_llm_response


def test_parse_json_response():
    """测试 JSON 响应解析"""
    print("="*60)
    print("测试: JSON 响应解析")
    print("="*60)
    
    # 测试 1: 完成状态
    json_done = '{"done": true, "answer": "这是最终答案"}'
    result = parse_llm_response(json_done)
    assert result['success'] == True
    assert result['done'] == True
    assert result['answer'] == "这是最终答案"
    print("✅ 测试 1 通过: 完成状态解析")
    
    # 测试 2: 继续调用工具
    json_continue = '{"done": false, "tool_call": {"name": "generate_notice", "arguments": {"topic": "放假通知"}}}'
    result = parse_llm_response(json_continue)
    assert result['success'] == True
    assert result['done'] == False
    assert result['tool_call']['name'] == "generate_notice"
    assert result['tool_call']['arguments']['topic'] == "放假通知"
    print("✅ 测试 2 通过: 继续调用解析")
    
    # 测试 3: 带 markdown 标记的 JSON
    json_markdown = '''```json
{"done": true, "answer": "Markdown 格式的答案"}
```'''
    result = parse_llm_response(json_markdown)
    assert result['success'] == True
    assert result['done'] == True
    print("✅ 测试 3 通过: Markdown 格式解析")
    
    # 测试 4: 无效的 JSON
    invalid_json = '这不是 JSON'
    result = parse_llm_response(invalid_json)
    assert result['success'] == False
    print("✅ 测试 4 通过: 无效 JSON 处理")
    
    # 测试 5: 缺少必要字段
    incomplete_json = '{"done": true}'
    result = parse_llm_response(incomplete_json)
    assert result['success'] == False
    print("✅ 测试 5 通过: 不完整 JSON 处理")
    
    print("\n✅ 所有 JSON 解析测试通过！\n")


def test_context_manager():
    """测试上下文管理器"""
    print("="*60)
    print("测试: ChainedCallContext 上下文管理")
    print("="*60)
    
    # 创建上下文
    context = ChainedCallContext(max_iterations=5)
    
    # 测试初始状态
    assert context.current_iteration == 0
    assert context.max_iterations == 5
    assert len(context.call_history) == 0
    assert context.is_completed == False
    assert context.can_continue() == True
    print("✅ 测试 1 通过: 初始状态正确")
    
    # 测试变量存储和获取
    context.set_variable("user_name", "张三")
    context.set_variable("department", "技术部")
    assert context.get_variable("user_name") == "张三"
    assert context.get_variable("department") == "技术部"
    assert context.get_variable("non_exist", "默认值") == "默认值"
    print("✅ 测试 2 通过: 变量存储和获取")
    
    # 测试添加工具调用记录
    context.add_tool_call(
        "generate_notice",
        {"topic": "放假通知", "department": "技术部"},
        {"success": True, "content": "通知内容..."}
    )
    assert len(context.call_history) == 1
    assert context.call_history[0]['tool_name'] == "generate_notice"
    assert context.call_history[0]['success'] == True
    print("✅ 测试 3 通过: 工具调用记录")
    
    # 测试迭代控制
    context.increment_iteration()
    assert context.current_iteration == 1
    context.increment_iteration()
    assert context.current_iteration == 2
    print("✅ 测试 4 通过: 迭代计数")
    
    # 测试完成标记
    context.complete("最终答案")
    assert context.is_completed == True
    assert context.final_answer == "最终答案"
    assert context.can_continue() == False
    print("✅ 测试 5 通过: 完成标记")
    
    # 测试达到最大迭代次数
    context2 = ChainedCallContext(max_iterations=2)
    context2.increment_iteration()
    context2.increment_iteration()
    assert context2.can_continue() == False
    print("✅ 测试 6 通过: 最大迭代限制")
    
    # 测试获取摘要
    summary = context.get_summary()
    assert summary['total_iterations'] == 2
    assert summary['max_iterations'] == 5
    assert summary['total_tool_calls'] == 1
    assert summary['successful_calls'] == 1
    assert summary['failed_calls'] == 0
    assert summary['is_completed'] == True
    print(f"✅ 测试 7 通过: 执行摘要生成\n{summary}")
    
    # 测试获取历史文本
    history_text = context.get_history_text()
    assert "generate_notice" in history_text
    assert "放假通知" in history_text
    print(f"✅ 测试 8 通过: 历史文本生成\n{history_text}")
    
    print("\n✅ 所有上下文管理测试通过！\n")


def test_edge_cases():
    """测试边界情况"""
    print("="*60)
    print("测试: 边界情况")
    print("="*60)
    
    # 测试 1: 空历史记录
    context = ChainedCallContext()
    history = context.get_history_text()
    assert "尚未执行任何工具调用" in history
    print("✅ 测试 1 通过: 空历史记录")
    
    # 测试 2: 多次添加工具调用
    for i in range(5):
        context.add_tool_call(
            f"tool_{i}",
            {"param": i},
            {"success": i % 2 == 0, "result": f"result_{i}"}
        )
    assert len(context.call_history) == 5
    assert context.get_summary()['successful_calls'] == 3
    assert context.get_summary()['failed_calls'] == 2
    print("✅ 测试 2 通过: 多次工具调用")
    
    # 测试 3: 复杂嵌套变量
    context.set_variable("complex_data", {
        "nested": {"key": "value"},
        "list": [1, 2, 3],
        "mixed": {"a": 1, "b": [4, 5, 6]}
    })
    retrieved = context.get_variable("complex_data")
    assert retrieved["nested"]["key"] == "value"
    assert retrieved["list"] == [1, 2, 3]
    print("✅ 测试 3 通过: 复杂嵌套变量")
    
    print("\n✅ 所有边界情况测试通过！\n")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("开始链式工具调用基础功能测试")
    print("="*60 + "\n")
    
    try:
        test_parse_json_response()
        test_context_manager()
        test_edge_cases()
        
        print("="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
