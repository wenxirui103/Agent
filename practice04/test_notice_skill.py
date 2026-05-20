"""
测试 notice skill 功能
验证两个场景：
1. 模拟提交一个用户请求，不说自己所在的部门，要求LLM撰写关于五一节放假的通知
2. 模拟提交一个用户请求，用户表明自己的部门是"销售部"要求LLM撰写关于五一节放假的通知
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from practice04.tool_chat_client import execute_tool


def test_scenario_1_no_department():
    """测试场景1：用户不说明部门，要求生成五一节放假通知"""
    print("="*70)
    print("🧪 测试场景 1: 用户未说明部门，要求生成五一节放假通知")
    print("="*70)
    
    # 模拟用户请求：不提供部门信息，要求生成五一节放假通知
    result = execute_tool('generate_notice', topic="五一节放假")
    
    print(f"工具执行结果: {result['success']}")
    if result['success']:
        print(f"通知头部: {result['header']}")
        print(f"通知内容预览:\n{result['content'][:200]}...")
        print(f"完整通知内容:\n{result['content']}")
        
        # 验证是否以"XX部通知"开头
        if result['header'] == "XX部通知":
            print("✅ 验证通过：通知以'XX部通知'开头")
        else:
            print(f"❌ 验证失败：期望'XX部通知'开头，实际'{result['header']}'开头")
    else:
        print(f"❌ 工具执行失败: {result['error']}")
    
    print("="*70)


def test_scenario_2_with_sales_department():
    """测试场景2：用户提供销售部门，要求生成五一节放假通知"""
    print("🧪 测试场景 2: 用户说明部门为'销售部'，要求生成五一节放假通知")
    print("="*70)
    
    # 模拟用户请求：提供销售部门，要求生成五一节放假通知
    result = execute_tool('generate_notice', topic="五一节放假", department="销售部")
    
    print(f"工具执行结果: {result['success']}")
    if result['success']:
        print(f"通知头部: {result['header']}")
        print(f"通知内容预览:\n{result['content'][:200]}...")
        print(f"完整通知内容:\n{result['content']}")
        
        # 验证是否以"销售部通知"开头
        if result['header'] == "销售部通知":
            print("✅ 验证通过：通知以'销售部通知'开头")
        else:
            print(f"❌ 验证失败：期望'销售部通知'开头，实际'{result['header']}'开头")
    else:
        print(f"❌ 工具执行失败: {result['error']}")
    
    print("="*70)


def test_scenario_3_other_department():
    """测试场景3：用户提供其他部门，要求生成五一节放假通知"""
    print("🧪 测试场景 3: 用户说明部门为'技术部'，要求生成五一节放假通知")
    print("="*70)
    
    # 模拟用户请求：提供技术部门，要求生成五一节放假通知
    result = execute_tool('generate_notice', topic="五一节放假", department="技术部")
    
    print(f"工具执行结果: {result['success']}")
    if result['success']:
        print(f"通知头部: {result['header']}")
        print(f"通知内容预览:\n{result['content'][:200]}...")
        print(f"完整通知内容:\n{result['content']}")
        
        # 验证是否以"技术部通知"开头
        if result['header'] == "技术部通知":
            print("✅ 验证通过：通知以'技术部通知'开头")
        else:
            print(f"❌ 验证失败：期望'技术部通知'开头，实际'{result['header']}'开头")
    else:
        print(f"❌ 工具执行失败: {result['error']}")
    
    print("="*70)


if __name__ == "__main__":
    print("🚀 开始测试 notice skill 功能")
    print()
    
    # 测试场景1：没有指定部门
    test_scenario_1_no_department()
    
    # 测试场景2：指定销售部
    test_scenario_2_with_sales_department()
    
    # 测试场景3：指定技术部
    test_scenario_3_other_department()
    
    print("✅ 所有测试完成")