def create_agent(enable_tools):
    passctice02 模块添加了 **curl 网页访问功能** 和 **工具调用支持**。

---

## 🆕 新增文件

### 1. `tool_chat_client.py` - 工具函数模块
提供 AI 智能体可调用的实用工具函数。

**核心功能：**
- ✅ `fetch_webpage(url, timeout)` - 使用 curl 访问网页并返回内容
- ✅ `get_tool_description()` - 生成符合 OpenAI 标准的工具描述
- ✅ `execute_tool(tool_name, **kwargs)` - 动态执行指定工具

**特点：**
- 跨平台支持（Windows/Linux/Mac）
- 自动跟随重定向
- HTTP 状态码检测
- 完善的错误处理和超时控制

### 2. `test_tools.py` - 工具测试脚本
用于验证工具函数的功能是否正常。

**运行方式：**
```powershell
python practice02/test_tools.py
```

---

## 🔧 修改文件

### 1. `agent.py` - AI 智能体核心模块

**主要变更：**
- ✅ `LLMClient.chat_completion()` 添加 `tools` 参数，支持 Function Calling
- ✅ `AIAgent.__init__()` 添加 `tools` 参数，支持工具注册
- ✅ `AIAgent.chat()` 添加 `enable_tools` 参数，可控制是否启用工具
- ✅ `create_agent()` 添加 `enable_tools` 参数，创建时可启用工具

**使用示例：**
```python
# 创建带工具的智能体
agent = create_agent(enable_tools=True)

# 对话时启用工具
result = agent.chat("请帮我访问 https://www.baidu.com", enable_tools=True)
```

### 2. `README.md` - 项目文档

**更新内容：**
- ✅ 添加 practice02 模块的详细说明
- ✅ 新增 tool_chat_client.py 和 test_tools.py 的文档
- ✅ 更新学习路径，添加"智能体与工具集成"阶段
- ✅ 更新快速开始指南，添加工具测试命令
- ✅ 更新教学目标，添加工具开发相关内容

---

## 🎯 功能演示

### 1. 直接调用工具函数

```python
from practice02.tool_chat_client import fetch_webpage

# 访问网页
result = fetch_webpage("https://www.baidu.com", timeout=5)

if result['success']:
    print(f"状态码: {result['status_code']}")
    print(f"内容长度: {len(result['content'])} 字符")
    print(f"内容预览: {result['content'][:200]}")
else:
    print(f"错误: {result['error']}")
```

### 2. 通过 execute_tool 调用

```python
from practice02.tool_chat_client import execute_tool

result = execute_tool('fetch_webpage', url='https://httpbin.org/html', timeout=5)
```

### 3. 在智能体中使用工具

```python
from practice02.agent import create_agent

# 创建带工具的智能体
agent = create_agent(
    system_prompt="你是一个有用的助手，可以使用工具获取网页信息。",
    enable_tools=True
)

# 对话（模型会自动决定是否使用工具）
result = agent.chat("请帮我查看百度首页的内容")
```

### 4. 运行测试脚本

```powershell
# 测试所有工具函数
python practice02/test_tools.py

# 交互式聊天
python practice02/chat_demo.py

# 演示模式
python practice02/chat_demo.py --demo
```

---

## 📚 技术要点

### 1. subprocess 模块使用
```python
import subprocess

result = subprocess.run(
    ['curl', '-s', '-L', url],
    capture_output=True,
    text=True,
    timeout=10
)
```

### 2. 工具描述格式（OpenAI Function Calling）
```python
{
    "type": "function",
    "function": {
        "name": "fetch_webpage",
        "description": "使用 curl 访问指定 URL 并返回网页内容",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "要访问的网页 URL（必需）"
                }
            },
            "required": ["url"]
        }
    }
}
```

### 3. 跨平台兼容
```python
import sys

if sys.platform == 'win32':
    # Windows 特定处理
    pass
else:
    # Linux/Mac 处理
    pass
```

---

## ⚠️ 注意事项

### 1. 系统要求
- 需要安装 curl 命令
- Windows 10+ 已内置 curl
- Linux/Mac 通常预装 curl

### 2. 检查 curl 是否可用
```powershell
curl --version
```

### 3. 常见问题

**问题 1：找不到 curl 命令**
```
错误：系统中未找到 curl 命令，请确保已安装 curl
```
**解决：** 安装 curl 或将其添加到系统 PATH

**问题 2：请求超时**
```
错误：请求超时（10秒）
```
**解决：** 增加 timeout 参数值

**问题 3：HTTP 错误**
```
错误：HTTP 错误: 404
```
**解决：** 检查 URL 是否正确

---

## 🚀 扩展开发

### 添加新工具

在 `tool_chat_client.py` 中添加新工具非常简单：

```python
# 1. 实现工具函数
def my_new_tool(param1, param2):
    """你的工具函数"""
    # 实现逻辑
    return {'success': True, 'result': '...'}

# 2. 注册到 AVAILABLE_TOOLS
AVAILABLE_TOOLS = {
    'fetch_webpage': {...},
    'my_new_tool': {
        'function': my_new_tool,
        'description': '工具描述',
        'parameters': {
            'param1': '参数1说明（必需）',
            'param2': '参数2说明（可选）'
        }
    }
}
```

工具描述会自动生成，无需手动维护！

---

## 📖 相关资源

- [Python subprocess 文档](https://docs.python.org/3/library/subprocess.html)
- [curl 官方文档](https://curl.se/docs/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

---

**祝使用愉快！🎉**
