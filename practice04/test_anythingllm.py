"""
AnythingLLM 工具测试脚本
测试 anythingllm_query 函数的功能
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# 自动加载 .env 文件
from practice04.load_env import load_env_file
load_env_file()

from practice04.tool_chat_client import anythingllm_query, get_tool_description


def test_anythingllm_query():
    """测试 AnythingLLM 查询功能"""
    
    print("="*70)
    print("🧪 AnythingLLM 工具测试")
    print("="*70)
    
    # 从环境变量或 .env 文件读取 API Key
    api_key = os.getenv('ANYTHINGLLM_API_KEY', '')
    
    if not api_key:
        print("\n⚠️  警告: 未设置 ANYTHINGLLM_API_KEY 环境变量")
        print("   请通过以下方式之一配置:")
        print("\n   方式1: 在 .env 文件中添加:")
        print("   ANYTHINGLLM_API_KEY=H52K9Y6-E5TM68E-M4ZXEEH-E7A4C7Q")
        print("\n   方式2: Windows PowerShell:")
        print("   $env:ANYTHINGLLM_API_KEY='your-api-key-here'")
        print("\n   方式3: Windows CMD:")
        print("   set ANYTHINGLLM_API_KEY=your-api-key-here")
        return False
    
    print(f"\n✅ API Key 已配置")
    print(f"📍 API Base URL: http://localhost:3001")
    
    # 测试1: 基本查询
    print("\n" + "-"*70)
    print("📝 测试1: 基本查询")
    print("-"*70)
    
    result = anythingllm_query(
        message="你好，请介绍一下你自己",
        api_key=api_key
    )
    
    if result['success']:
        print(f"✅ 查询成功！")
        print(f"📄 回复: {result['response'][:200]}...")
        print(f"🔢 状态码: {result['status_code']}")
    else:
        print(f"❌ 查询失败: {result['error']}")
        print(f"🔢 状态码: {result.get('status_code', 'N/A')}")
        return False
    
    # 测试2: 带工作空间的查询（如果有的话）
    print("\n" + "-"*70)
    print("📝 测试2: 查询特定主题")
    print("-"*70)
    
    result = anythingllm_query(
        message="Python是什么？",
        api_key=api_key
    )
    
    if result['success']:
        print(f"✅ 查询成功！")
        print(f"📄 回复: {result['response'][:200]}...")
    else:
        print(f"❌ 查询失败: {result['error']}")
    
    # 测试3: 缺少API密钥
    print("\n" + "-"*70)
    print("📝 测试3: 缺少API密钥（预期失败）")
    print("-"*70)
    
    result = anythingllm_query(
        message="测试消息",
        api_key=""
    )
    
    if not result['success']:
        print(f"✅ 正确捕获错误: {result['error']}")
    else:
        print(f"❌ 应该失败但成功了")
    
    # 测试4: 查看工具描述
    print("\n" + "-"*70)
    print("📝 测试4: 工具描述信息")
    print("-"*70)
    
    tools = get_tool_description()
    print(f"✅ 可用工具数量: {len(tools)}")
    
    for tool in tools:
        func_name = tool['function']['name']
        description = tool['function']['description']
        params = tool['function']['parameters']
        
        print(f"\n🔧 工具: {func_name}")
        print(f"   描述: {description}")
        print(f"   必需参数: {params.get('required', [])}")
        print(f"   所有参数: {list(params.get('properties', {}).keys())}")
    
    print("\n" + "="*70)
    print("✅ 测试完成！")
    print("="*70)
    
    return True


if __name__ == '__main__':
    success = test_anythingllm_query()
    
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查配置")
        sys.exit(1)
