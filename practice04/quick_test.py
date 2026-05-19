"""快速测试 practice04 模块导入"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from practice04.tool_chat_client import get_tool_description, AVAILABLE_TOOLS

print("="*70)
print("🧪 Practice04 模块测试")
print("="*70)

# 测试工具描述
tools = get_tool_description()
print(f"\n✅ 可用工具数量: {len(tools)}")

for tool in tools:
    func_name = tool['function']['name']
    description = tool['function']['description']
    params = tool['function']['parameters']
    
    print(f"\n🔧 工具: {func_name}")
    print(f"   描述: {description}")
    print(f"   必需参数: {params.get('required', [])}")
    print(f"   所有参数: {list(params.get('properties', {}).keys())}")

print("\n" + "="*70)
print("✅ 模块导入成功！")
print("="*70)
