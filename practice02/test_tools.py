"""
工具函数测试脚本
测试网页访问等功能
"""

from tool_chat_client import fetch_webpage, execute_tool, get_tool_description
import json


def test_fetch_webpage():
    """测试网页访问功能"""
    print("=" * 70)
    print("🌐 测试 curl 网页访问功能")
    print("=" * 70)
    
    # 测试用例 1: 访问百度首页
    print("\n📝 测试 1: 访问百度首页")
    print("-" * 70)
    result = fetch_webpage("https://www.baidu.com", timeout=5)
    
    if result['success']:
        print(f"✅ 成功! HTTP 状态码: {result['status_code']}")
        print(f"📄 内容长度: {len(result['content'])} 字符")
        print(f"📋 内容预览 (前200字符):")
        print(result['content'][:200] + "..." if len(result['content']) > 200 else result['content'])
    else:
        print(f"❌ 失败: {result['error']}")
    
    # 测试用例 2: 访问不存在的网站
    print("\n📝 测试 2: 访问无效 URL")
    print("-" * 70)
    result = fetch_webpage("https://this-domain-does-not-exist-12345.com", timeout=3)
    
    if result['success']:
        print(f"✅ 成功 (意外): {result['status_code']}")
    else:
        print(f"❌ 预期失败: {result['error']}")
    
    # 测试用例 3: 使用 execute_tool 调用
    print("\n📝 测试 3: 通过 execute_tool 调用")
    print("-" * 70)
    result = execute_tool('fetch_webpage', url='https://httpbin.org/html', timeout=5)
    
    if result['success']:
        print(f"✅ 成功! HTTP 状态码: {result['status_code']}")
        print(f"📄 内容长度: {len(result['content'])} 字符")
        print(f"📋 内容预览 (前200字符):")
        print(result['content'][:200] + "..." if len(result['content']) > 200 else result['content'])
    else:
        print(f"❌ 失败: {result['error']}")


def test_tool_description():
    """测试工具描述功能"""
    print("\n" + "=" * 70)
    print("📚 测试工具描述功能")
    print("=" * 70)
    
    tools = get_tool_description()
    print(f"\n🔧 可用工具数量: {len(tools)}")
    print("\n📋 工具详情:")
    print(json.dumps(tools, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    print("\n🧪 开始运行工具函数测试...\n")
    
    try:
        test_fetch_webpage()
        test_tool_description()
        
        print("\n" + "=" * 70)
        print("✅ 所有测试完成!")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
