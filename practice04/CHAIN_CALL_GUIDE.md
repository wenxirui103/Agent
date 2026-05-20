# 链式工具调用模块使用指南

## 概述

`chained_tool_call.py` 模块实现了智能体的链式工具调用能力，允许 AI 助手通过多步推理和工具调用来完成复杂任务。

## 核心组件

### 1. ChainedCallContext 类

上下文管理器，用于在多个工具调用之间传递数据和状态。

#### 主要功能：
- **记录调用历史**：跟踪每一步的工具调用和结果
- **存储中间变量**：保存中间结果供后续步骤使用
- **迭代控制**：设置最大迭代次数，防止无限循环
- **状态管理**：跟踪任务完成状态

#### 使用方法：

```python
from chained_tool_call import ChainedCallContext

# 创建上下文（默认最大迭代10次）
context = ChainedCallContext(max_iterations=10)

# 存储中间变量
context.set_variable("user_name", "张三")
context.set_variable("query_result", {"data": "..."})

# 获取变量
value = context.get_variable("user_name")

# 记录工具调用
context.add_tool_call(
    tool_name="fetch_webpage",
    arguments={"url": "https://example.com"},
    result={"success": True, "content": "..."}
)

# 增加迭代计数
context.increment_iteration()

# 检查是否可以继续
if context.can_continue():
    # 继续执行
    pass

# 标记任务完成
context.complete("最终答案")

# 获取执行摘要
summary = context.get_summary()
print(summary)
# 输出:
# {
#     'total_iterations': 5,
#     'max_iterations': 10,
#     'total_tool_calls': 3,
#     'successful_calls': 3,
#     'failed_calls': 0,
#     'context_variables_count': 2,
#     'is_completed': True
# }

# 获取格式化的历史记录
history = context.get_history_text()
```

### 2. build_analysis_prompt 函数

构建分析提示词，指导 LLM 进行下一步决策。

#### 功能：
- 包含用户原始请求
- 展示已执行的工具调用历史
- 提供决策规则说明
- 明确 JSON 输出格式要求

#### 使用方法：

```python
from chained_tool_call import build_analysis_prompt

prompt = build_analysis_prompt(
    user_request="帮我查询天气并生成报告",
    context=context_instance
)
```

#### 提示词内容包括：
1. **用户请求**：原始任务描述
2. **当前状态**：迭代次数、工具调用次数
3. **已执行的步骤历史**：每个工具的名称、参数、结果
4. **可用的上下文变量**：之前步骤保存的中间结果
5. **可用工具列表**：所有可以调用的工具名称
6. **决策规则**：如何判断完成任务或继续调用
7. **输出格式要求**：JSON 格式规范
8. **示例**：具体的使用示例

### 3. parse_llm_response 函数

解析 LLM 的响应，提取决策信息。

#### 支持的格式：

**完成任务时：**
```json
{
  "done": true,
  "answer": "最终回答内容"
}
```

**继续调用工具时：**
```json
{
  "done": false,
  "tool_call": {
    "name": "工具名称",
    "arguments": {
      "参数名": "参数值"
    }
  }
}
```

#### 使用方法：

```python
from chained_tool_call import parse_llm_response

# 解析 LLM 响应
decision = parse_llm_response(llm_response_text)

if decision['success']:
    if decision['done']:
        # 任务完成，获取最终答案
        print(decision['answer'])
    else:
        # 需要继续调用工具
        tool_name = decision['tool_call']['name']
        arguments = decision['tool_call']['arguments']
        # 执行工具...
else:
    # 解析失败
    print(f"错误: {decision['error']}")
```

#### 特性：
- 自动处理 Markdown 代码块标记（```json ... ```）
- 验证必要字段是否存在
- 提供详细的错误信息

### 4. execute_chained_tool_call 函数

执行链式工具调用的完整流程。

#### 工作流程：
1. 初始化消息历史，包含 system prompt
2. 循环最多 `max_iterations` 次：
   - 构建分析提示词（包含用户请求和已执行的步骤历史）
   - 调用 LLM 决定下一步操作
   - 解析 LLM 响应（支持 JSON 格式）
   - 如果任务完成，返回最终回答
   - 如果需继续调用，执行工具并记录到上下文
   - 将结果添加到消息历史，继续下一轮
3. 返回执行结果和完整的上下文信息

#### 使用方法：

```python
from agent_with_compression import create_smart_agent
from chained_tool_call import execute_chained_tool_call

# 创建智能体
agent = create_smart_agent(enable_logging=False)

# 执行链式调用
result = execute_chained_tool_call(
    llm_client=agent.llm_client,
    user_request="帮我写一个技术部关于五一放假的通知",
    max_iterations=5,
    temperature=0.7
)

if result['success']:
    print(f"答案: {result['answer']}")
    
    # 查看执行过程
    context = result['context']
    print(f"迭代次数: {context.current_iteration}")
    print(f"工具调用: {len(context.call_history)} 次")
    
    # 查看每次调用的详情
    for i, call in enumerate(context.call_history, 1):
        print(f"\n步骤 {i}:")
        print(f"  工具: {call['tool_name']}")
        print(f"  参数: {call['arguments']}")
        print(f"  成功: {'是' if call['success'] else '否'}")
else:
    print(f"执行失败: {result['error']}")
```

#### 参数说明：
- `llm_client`: LLM 客户端实例
- `user_request`: 用户的请求文本
- `system_prompt`: 可选的自定义系统提示（会添加到默认提示之前）
- `max_iterations`: 最大迭代次数（默认 10）
- `temperature`: LLM 温度参数（默认 0.7）

#### 返回值：
```python
{
    'success': True/False,
    'answer': '最终答案文本',
    'context': ChainedCallContext 实例,
    'error': '错误信息（如果失败）'
}
```

## 系统提示词设计

默认的 system prompt 包含以下关键内容：

### 1. 工具调用的顺序依赖关系
```
某些任务需要先获取信息再生成内容
例如：生成通知前可能需要先查询公司政策
例如：回答问题前可能需要先访问网页获取最新信息
```

### 2. LLM 决策指导
```
- 根据用户请求判断是否需要工具调用
- 如果需要，选择合适的工具并设置正确的参数
- 根据工具返回的结果决定下一步操作
- 当收集到足够信息时，立即生成最终答案
```

### 3. 上下文变量使用说明
```
- 可以将重要的中间结果存储为上下文变量
- 在后续决策中可以利用这些变量
- 例如：将查询到的政策保存为变量，用于生成通知
```

### 4. 错误处理指导
```
- 如果工具调用失败，尝试其他方法
- 可以向用户说明遇到的问题
- 避免无限重试同一个失败的调用
```

### 5. 具体示例
提供了两个典型场景的完整示例：
- 生成部门通知（可能需要先查询政策）
- 查询并总结网页内容

## 使用示例

### 示例 1：简单的单步工具调用

```python
result = execute_chained_tool_call(
    llm_client=agent.llm_client,
    user_request="生成一个销售部关于年会的通知",
    max_iterations=3
)

# LLM 可能直接调用 generate_notice 工具并完成任务
print(result['answer'])
```

### 示例 2：多步链式调用

```python
result = execute_chained_tool_call(
    llm_client=agent.llm_client,
    user_request="查询公司五一放假政策，然后写一个人力资源部的通知",
    max_iterations=5
)

# LLM 可能执行以下步骤：
# 1. 调用 anythingllm_query 查询放假政策
# 2. 基于查询结果，调用 generate_notice 生成通知
# 3. 返回最终的通知内容

print(result['answer'])
print(f"共执行了 {result['context'].current_iteration} 次迭代")
```

### 示例 3：网页内容分析

```python
result = execute_chained_tool_call(
    llm_client=agent.llm_client,
    user_request="访问 https://example.com 并总结主要内容，然后用简洁的语言告诉我",
    max_iterations=4
)

# LLM 可能执行以下步骤：
# 1. 调用 fetch_webpage 获取网页内容
# 2. 分析并总结内容
# 3. 返回简洁的总结

print(result['answer'])
```

### 示例 4：自定义系统提示

```python
custom_prompt = """你是一个专业的商务助手，语言风格正式、简洁。
在生成内容时，请使用专业的商务用语。
优先使用公司内部知识库获取准确信息。"""

result = execute_chained_tool_call(
    llm_client=agent.llm_client,
    user_request="帮我写一个财务部关于预算审批流程的通知",
    system_prompt=custom_prompt,
    max_iterations=5,
    temperature=0.5  # 降低温度以获得更稳定的输出
)

print(result['answer'])
```

## 最佳实践

### 1. 设置合理的最大迭代次数
- 简单任务：3-5 次
- 中等复杂任务：5-8 次
- 复杂任务：8-10 次
- 避免设置过大，防止资源浪费

### 2. 利用上下文变量
LLM 可以在决策时请求存储重要的中间结果：
```json
{
  "done": false,
  "tool_call": {
    "name": "set_context_variable",
    "arguments": {
      "key": "policy_info",
      "value": "查询到的政策内容"
    }
  }
}
```

### 3. 错误处理
- 检查 `result['success']` 判断整体执行是否成功
- 查看 `context.call_history` 了解哪些工具调用失败
- 根据失败原因调整策略或提示用户

### 4. 调试和监控
使用上下文的摘要和历史功能进行调试：
```python
# 打印执行摘要
summary = context.get_summary()
print(f"执行统计: {summary}")

# 查看详细历史
print(context.get_history_text())

# 查看保存的变量
print(f"上下文变量: {context.context_variables}")
```

## 测试

运行基础功能测试（不需要 API）：
```bash
python test_chained_simple.py
```

运行完整功能测试（需要配置 API）：
```bash
python test_chained_call.py
```

运行演示：
```bash
python demo_chained_call.py
```

## 注意事项

1. **API 密钥配置**：使用 `anythingllm_query` 工具前，确保在 `.env` 文件中配置了 `ANYTHINGLLM_API_KEY`

2. **工具可用性**：确保所需的外部服务正在运行（如 AnythingLLM、curl 等）

3. **迭代限制**：达到最大迭代次数时，任务会被强制结束，返回提示信息

4. **JSON 格式**：LLM 必须严格按照指定的 JSON 格式返回，否则会导致解析失败

5. **错误恢复**：当工具调用失败时，LLM 会收到错误信息并可以尝试其他方法

## 扩展开发

如需添加新工具，只需在 `tool_chat_client.py` 中的 `AVAILABLE_TOOLS` 字典中注册：

```python
AVAILABLE_TOOLS = {
    # ... 现有工具 ...
    'my_new_tool': {
        'function': my_tool_function,
        'description': '工具描述',
        'parameters': {
            'param1': '参数1说明（必需）',
            'param2': '参数2说明（可选）'
        }
    }
}
```

新工具会自动出现在可用工具列表中，LLM 可以根据需要调用它。
