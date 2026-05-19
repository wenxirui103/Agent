# 链式工具调用 - 快速开始指南

## 🚀 5分钟快速上手

### 1. 基础用法

```python
from agent_with_compression import create_smart_agent
from chained_tool_call import execute_chained_tool_call

# 创建智能体
agent = create_smart_agent(enable_logging=False)

# 执行链式调用
result = execute_chained_tool_call(
    llm_client=agent.llm_client,
    user_request="帮我写一个技术部关于五一放假的通知",
    max_iterations=5
)

# 获取结果
if result['success']:
    print(result['answer'])
```

### 2. 查看执行过程

```python
# 获取上下文信息
context = result['context']

# 查看执行统计
print(f"迭代次数: {context.current_iteration}")
print(f"工具调用: {len(context.call_history)} 次")

# 查看详细历史
for i, call in enumerate(context.call_history, 1):
    print(f"步骤 {i}: {call['tool_name']}")
    print(f"  参数: {call['arguments']}")
    print(f"  成功: {call['success']}")
```

### 3. 自定义系统提示

```python
custom_prompt = """你是一个专业的商务助手，语言风格正式、简洁。"""

result = execute_chained_tool_call(
    llm_client=agent.llm_client,
    user_request="帮我写一个财务部关于预算审批的通知",
    system_prompt=custom_prompt,
    max_iterations=5,
    temperature=0.5
)
```

## 📋 可用工具

当前支持的工具：

1. **generate_notice** - 生成部门通知
   ```python
   # LLM 会自动调用
   generate_notice(topic="五一放假", department="技术部")
   ```

2. **fetch_webpage** - 访问网页
   ```python
   # LLM 会自动调用
   fetch_webpage(url="https://example.com")
   ```

3. **anythingllm_query** - 查询知识库（需要 API 密钥）
   ```python
   # LLM 会自动调用
   anythingllm_query(message="查询内容", api_key="your-key")
   ```

## 🎯 典型场景

### 场景 1: 单步任务
```python
# 直接生成通知
result = execute_chained_tool_call(
    llm_client=agent.llm_client,
    user_request="生成一个销售部关于年会的通知",
    max_iterations=3
)
```

### 场景 2: 多步任务
```python
# 先查询信息，再生成内容
result = execute_chained_tool_call(
    llm_client=agent.llm_client,
    user_request="查询公司放假政策，然后写一个人力资源部的通知",
    max_iterations=6
)
```

### 场景 3: 网页研究
```python
# 访问网页并总结
result = execute_chained_tool_call(
    llm_client=agent.llm_client,
    user_request="访问 https://httpbin.org/html 并总结内容",
    max_iterations=4
)
```

## 🔧 运行测试

### 基础测试（不需要 API）
```bash
cd practice04
python test_chained_simple.py
```

### 完整测试（需要配置 .env）
```bash
cd practice04
python test_chained_call.py
```

### 运行示例
```bash
cd practice04
python example_chained_call.py
```

## 📊 理解输出

### 成功响应
```python
{
    'success': True,
    'answer': '最终答案文本...',
    'context': ChainedCallContext 实例
}
```

### 失败响应
```python
{
    'success': False,
    'error': '错误描述',
    'context': ChainedCallContext 实例
}
```

### 上下文对象
```python
context.call_history          # 工具调用历史
context.context_variables     # 中间变量
context.current_iteration     # 当前迭代次数
context.max_iterations        # 最大迭代次数
context.is_completed          # 是否完成
context.final_answer          # 最终答案

# 实用方法
context.get_summary()         # 获取执行摘要
context.get_history_text()    # 获取格式化历史
```

## 💡 最佳实践

### 1. 设置合理的迭代次数
- 简单任务: 3-5 次
- 中等任务: 5-8 次
- 复杂任务: 8-10 次

### 2. 调整温度参数
- 需要创造性: temperature=0.7-0.9
- 需要稳定性: temperature=0.3-0.5
- 默认值: temperature=0.7

### 3. 监控执行情况
```python
result = execute_chained_tool_call(...)

# 检查是否成功
if not result['success']:
    print(f"错误: {result['error']}")

# 检查执行效率
context = result['context']
if context.current_iteration >= context.max_iterations:
    print("警告: 达到最大迭代次数，可能需要增加限制")
```

### 4. 调试技巧
```python
# 打印详细历史
print(context.get_history_text())

# 查看所有变量
print(context.context_variables)

# 检查每次调用的结果
for call in context.call_history:
    if not call['success']:
        print(f"失败: {call['tool_name']}")
        print(f"错误: {call['result'].get('error')}")
```

## ❓ 常见问题

### Q1: 为什么工具调用失败？
A: 检查以下几点：
- 是否配置了必要的 API 密钥
- 外部服务是否正常运行
- 网络连接是否正常

### Q2: 如何添加新工具？
A: 在 `tool_chat_client.py` 中注册：
```python
AVAILABLE_TOOLS = {
    'my_tool': {
        'function': my_function,
        'description': '工具描述',
        'parameters': {...}
    }
}
```

### Q3: 如何避免无限循环？
A: 
- 设置合理的 `max_iterations`
- LLM 会自动判断何时完成任务
- 系统有内置的防循环机制

### Q4: JSON 解析失败怎么办？
A: 
- 系统会自动重试一次
- 降低 temperature 参数
- 检查 LLM 是否正确理解指令

## 📚 更多信息

- 详细文档: `CHAIN_CALL_GUIDE.md`
- 实现总结: `IMPLEMENTATION_SUMMARY.md`
- 演示脚本: `demo_chained_call.py`
- 示例代码: `example_chained_call.py`

## 🎉 开始使用

现在就试试：

```bash
# 进入目录
cd practice04

# 运行交互示例
python example_chained_call.py

# 选择选项 7 进入交互模式
# 输入你的请求，体验链式工具调用！
```

祝你使用愉快！🚀
