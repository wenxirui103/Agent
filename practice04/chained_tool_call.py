"""
链式工具调用模块 - 支持多步骤工具调用的上下文管理和执行
实现智能体在多个工具调用之间传递数据和状态的能力
"""

import json
from tool_chat_client import execute_tool, get_tool_description


class ChainedCallContext:
    """
    链式调用上下文管理器
    
    用于在多个工具调用之间传递数据和状态：
    - 记录每一步的调用和结果
    - 存储中间变量供后续步骤使用
    - 设置最大迭代次数，防止无限循环
    """
    
    def __init__(self, max_iterations=10):
        """
        初始化链式调用上下文
        
        参数:
            max_iterations: 最大迭代次数，防止无限循环（默认 10）
        """
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.call_history = []  # 记录所有工具调用的历史
        self.context_variables = {}  # 存储中间变量
        self.is_completed = False
        self.final_answer = None
        
    def add_tool_call(self, tool_name, arguments, result):
        """
        添加工具调用记录
        
        参数:
            tool_name: 工具名称
            arguments: 调用参数
            result: 执行结果
        """
        call_record = {
            'iteration': self.current_iteration,
            'tool_name': tool_name,
            'arguments': arguments,
            'result': result,
            'success': result.get('success', False)
        }
        self.call_history.append(call_record)
        
    def set_variable(self, key, value):
        """
        设置上下文变量
        
        参数:
            key: 变量名
            value: 变量值
        """
        self.context_variables[key] = value
        
    def get_variable(self, key, default=None):
        """
        获取上下文变量
        
        参数:
            key: 变量名
            default: 默认值（如果变量不存在）
            
        返回:
            变量值或默认值
        """
        return self.context_variables.get(key, default)
        
    def can_continue(self):
        """
        检查是否可以继续迭代
        
        返回:
            bool: 是否可以继续
        """
        return (not self.is_completed and 
                self.current_iteration < self.max_iterations)
        
    def increment_iteration(self):
        """增加迭代计数"""
        self.current_iteration += 1
        
    def complete(self, answer):
        """
        标记任务完成
        
        参数:
            answer: 最终答案
        """
        self.is_completed = True
        self.final_answer = answer
        
    def get_summary(self):
        """
        获取执行摘要
        
        返回:
            dict: 包含执行统计信息
        """
        return {
            'total_iterations': self.current_iteration,
            'max_iterations': self.max_iterations,
            'total_tool_calls': len(self.call_history),
            'successful_calls': sum(1 for c in self.call_history if c['success']),
            'failed_calls': sum(1 for c in self.call_history if not c['success']),
            'context_variables_count': len(self.context_variables),
            'is_completed': self.is_completed
        }
        
    def get_history_text(self):
        """
        获取格式化的调用历史文本（用于提示词）
        
        返回:
            str: 格式化的历史记录
        """
        if not self.call_history:
            return "尚未执行任何工具调用。"
        
        history_text = "已执行的工具调用历史：\n\n"
        for i, call in enumerate(self.call_history, 1):
            history_text += f"步骤 {i}:\n"
            history_text += f"  工具: {call['tool_name']}\n"
            history_text += f"  参数: {json.dumps(call['arguments'], ensure_ascii=False)}\n"
            
            if call['success']:
                result_str = str(call['result'].get('content', 
                              call['result'].get('response', 
                              str(call['result']))))
                # 限制结果长度
                if len(result_str) > 500:
                    result_str = result_str[:500] + "..."
                history_text += f"  结果: {result_str}\n"
            else:
                history_text += f"  错误: {call['result'].get('error', '未知错误')}\n"
            
            history_text += "\n"
        
        return history_text


def build_analysis_prompt(user_request, context):
    """
    构建分析提示词
    
    提示词包含：
    - 用户原始请求
    - 已执行的工具调用历史
    - 决策规则说明
    - JSON输出格式要求
    
    参数:
        user_request: 用户原始请求
        context: ChainedCallContext 实例
        
    返回:
        str: 完整的分析提示词
    """
    prompt = f"""你是一个智能助手，需要通过链式工具调用来完成用户的请求。

## 用户请求
{user_request}

## 当前状态
- 迭代次数: {context.current_iteration}/{context.max_iterations}
- 已执行工具调用: {len(context.call_history)} 次

## 已执行的步骤历史
{context.get_history_text()}

## 可用的上下文变量
{json.dumps(context.context_variables, ensure_ascii=False, indent=2) if context.context_variables else "暂无上下文变量"}

## 可用工具
{json.dumps([t['function']['name'] for t in get_tool_description()], ensure_ascii=False)}

## 决策规则
请根据当前情况做出决策：

1. **如果已经收集到足够信息来回答用户问题**：
   - 设置 done = true
   - 提供完整、准确的最终答案

2. **如果需要更多信息**：
   - 设置 done = false
   - 指定下一步要调用的工具和参数
   - 考虑之前工具调用的结果来决定下一步

3. **重要原则**：
   - 每次只调用一个工具
   - 充分利用之前工具调用的结果
   - 避免重复调用相同的工具
   - 如果工具调用失败，尝试其他方法或工具
   - 在达到最大迭代次数前必须完成任务

## 输出格式要求
你必须严格按照以下 JSON 格式返回决策（不要添加任何其他内容）：

### 完成任务时：
```json
{{"done": true, "answer": "最终回答内容"}}
```

### 继续调用工具时：
```json
{{"done": false, "tool_call": {{"name": "工具名称", "arguments": {{"参数名": "参数值"}}}}}}
```

## 示例

### 示例 1：需要查询知识库后生成通知
用户请求："帮我写一个关于五一放假的通知"

第一次决策（需要查询公司政策）：
```json
{{"done": false, "tool_call": {{"name": "anythingllm_query", "arguments": {{"message": "五一放假政策是什么", "api_key": "your-api-key"}}}}}}
```

第二次决策（基于查询结果生成通知）：
```json
{{"done": true, "answer": "根据公司的五一放假政策，我为您生成了以下通知：\\n\\nXX部通知\\n\\n关于五一节放假的通知\\n\\n各位同事：\\n\\n根据公司安排，五一劳动节放假时间为5月1日至5月5日，共5天。请各部门提前做好工作安排...\\n\\n特此通知。"}}
```

### 示例 2：需要访问网页获取信息
用户请求："查询 example.com 网站的内容并总结"

决策：
```json
{{"done": false, "tool_call": {{"name": "fetch_webpage", "arguments": {{"url": "https://example.com"}}}}}}
```

现在，请根据用户请求和当前状态，做出你的决策："""
    
    return prompt


def parse_llm_response(response_content):
    """
    解析 LLM 响应，提取决策信息
    
    支持两种格式：
    1. JSON 格式（推荐）
    2. tool_calls 格式（OpenAI 标准格式）
    
    参数:
        response_content: LLM 返回的内容
        
    返回:
        dict: 解析后的决策信息
            - done: 是否完成
            - answer: 最终答案（如果完成）
            - tool_call: 工具调用信息（如果未完成）
    """
    try:
        # 尝试直接解析 JSON
        content = response_content.strip()
        
        # 移除可能的 markdown 代码块标记
        if content.startswith('```'):
            content = content.split('\n', 1)[-1]
        if content.endswith('```'):
            content = content.rsplit('\n', 1)[0]
        
        # 尝试找到 JSON 对象
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            decision = json.loads(json_str)
            
            # 验证必要字段
            if 'done' not in decision:
                return {
                    'success': False,
                    'error': '响应中缺少 "done" 字段'
                }
            
            if decision['done']:
                if 'answer' not in decision:
                    return {
                        'success': False,
                        'error': '任务完成但缺少 "answer" 字段'
                    }
                return {
                    'success': True,
                    'done': True,
                    'answer': decision['answer']
                }
            else:
                if 'tool_call' not in decision:
                    return {
                        'success': False,
                        'error': '任务未完成但缺少 "tool_call" 字段'
                    }
                tool_call = decision['tool_call']
                if 'name' not in tool_call or 'arguments' not in tool_call:
                    return {
                        'success': False,
                        'error': 'tool_call 缺少 "name" 或 "arguments" 字段'
                    }
                return {
                    'success': True,
                    'done': False,
                    'tool_call': tool_call
                }
        else:
            return {
                'success': False,
                'error': '无法找到有效的 JSON 对象'
            }
            
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'JSON 解析失败: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'解析响应时出错: {str(e)}'
        }


def execute_chained_tool_call(llm_client, user_request, system_prompt=None, 
                               max_iterations=10, temperature=0.7):
    """
    执行链式工具调用的完整流程
    
    实现步骤：
    1. 初始化消息历史，包含 system prompt
    2. 循环最多 max_iterations 次：
       - 构建分析提示词（包含用户请求和已执行的步骤历史）
       - 调用 LLM 决定下一步操作
       - 解析 LLM 响应（支持 JSON 格式）
       - 如果任务完成，返回最终回答
       - 如果需继续调用，执行工具并记录到上下文
       - 将结果添加到消息历史，继续下一轮
    
    参数:
        llm_client: LLM 客户端实例
        user_request: 用户请求
        system_prompt: 可选的系统提示（会添加到默认提示之前）
        max_iterations: 最大迭代次数
        temperature: LLM 温度参数
        
    返回:
        dict: 包含执行结果
            - success: 是否成功
            - answer: 最终答案
            - context: ChainedCallContext 实例（包含完整执行历史）
            - error: 错误信息（如果失败）
    """
    # 创建上下文管理器
    context = ChainedCallContext(max_iterations=max_iterations)
    
    # 构建系统提示
    default_system_prompt = """你是一个智能助手，能够通过链式工具调用来完成复杂任务。

## 链式调用规则

1. **顺序依赖关系**：
   - 某些任务需要先获取信息再生成内容
   - 例如：生成通知前可能需要先查询公司政策
   - 例如：回答问题前可能需要先访问网页获取最新信息

2. **决策指导**：
   - 根据用户请求判断是否需要工具调用
   - 如果需要，选择合适的工具并设置正确的参数
   - 根据工具返回的结果决定下一步操作
   - 当收集到足够信息时，立即生成最终答案

3. **上下文变量使用**：
   - 可以将重要的中间结果存储为上下文变量
   - 在后续决策中可以利用这些变量
   - 例如：将查询到的政策保存为变量，用于生成通知

4. **错误处理**：
   - 如果工具调用失败，尝试其他方法
   - 可以向用户说明遇到的问题
   - 避免无限重试同一个失败的调用

## 示例场景

### 场景 1：生成部门通知
用户："帮我写一个销售部关于五一放假的通知"

步骤：
1. （可选）查询公司五一放假政策 → anythingllm_query
2. 生成通知文档 → generate_notice(topic="五一放假", department="销售部")
3. 返回生成的通知

### 场景 2：查询并总结网页内容
用户："访问 https://example.com 并总结主要内容"

步骤：
1. 访问网页 → fetch_webpage(url="https://example.com")
2. 分析网页内容并总结
3. 返回总结

记住：每次只做一件事，循序渐进地完成任务。"""
    
    if system_prompt:
        full_system_prompt = system_prompt + "\n\n" + default_system_prompt
    else:
        full_system_prompt = default_system_prompt
    
    # 初始化消息历史
    messages = [
        {"role": "system", "content": full_system_prompt}
    ]
    
    print(f"\n🚀 开始链式工具调用")
    print(f"📝 用户请求: {user_request}")
    print(f"🔄 最大迭代次数: {max_iterations}")
    print("-" * 60)
    
    # 主循环
    while context.can_continue():
        context.increment_iteration()
        print(f"\n📍 迭代 {context.current_iteration}/{max_iterations}")
        
        # 构建分析提示词
        analysis_prompt = build_analysis_prompt(user_request, context)
        messages.append({"role": "user", "content": analysis_prompt})
        
        # 调用 LLM
        print("🤖 正在调用 LLM 进行决策...")
        result = llm_client.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=1024
        )
        
        if not result['success']:
            print(f"❌ LLM 调用失败: {result.get('error')}")
            return {
                'success': False,
                'error': f"LLM 调用失败: {result.get('error')}",
                'context': context
            }
        
        llm_response = result['content']
        print(f"💬 LLM 响应: {llm_response[:200]}...")
        
        # 添加到消息历史
        messages.append({"role": "assistant", "content": llm_response})
        
        # 解析 LLM 响应
        decision = parse_llm_response(llm_response)
        
        if not decision['success']:
            print(f"⚠️ 解析失败: {decision.get('error')}")
            # 尝试让 LLM 重新格式化
            retry_message = {
                "role": "user",
                "content": f"你的响应格式不正确。{decision.get('error')}\n请严格按照要求的 JSON 格式重新响应。"
            }
            messages.append(retry_message)
            
            # 重试一次
            retry_result = llm_client.chat_completion(
                messages=messages,
                temperature=0.3,  # 降低温度以获得更规范的输出
                max_tokens=1024
            )
            
            if retry_result['success']:
                llm_response = retry_result['content']
                messages.append({"role": "assistant", "content": llm_response})
                decision = parse_llm_response(llm_response)
                
                if not decision['success']:
                    print(f"❌ 重试后仍然解析失败")
                    context.complete(f"抱歉，我无法正确处理您的请求。解析错误: {decision.get('error')}")
                    break
            else:
                print(f"❌ 重试调用失败")
                context.complete(f"抱歉，处理您的请求时遇到错误。")
                break
        
        # 检查是否完成
        if decision['done']:
            print(f"✅ 任务完成！")
            print(f"💡 最终答案: {decision['answer'][:200]}...")
            context.complete(decision['answer'])
            break
        else:
            # 执行工具调用
            tool_call = decision['tool_call']
            tool_name = tool_call['name']
            arguments = tool_call['arguments']
            
            print(f"🔧 执行工具: {tool_name}")
            print(f"📋 参数: {json.dumps(arguments, ensure_ascii=False)}")
            
            # 执行工具
            tool_result = execute_tool(tool_name, **arguments)
            
            # 记录到上下文
            context.add_tool_call(tool_name, arguments, tool_result)
            
            if tool_result.get('success'):
                print(f"✅ 工具执行成功")
                # 尝试从结果中提取有用的信息存储为上下文变量
                result_content = tool_result.get('content', 
                                tool_result.get('response', ''))
                if result_content and len(result_content) < 1000:
                    var_key = f"{tool_name}_result_{context.current_iteration}"
                    context.set_variable(var_key, result_content)
            else:
                print(f"❌ 工具执行失败: {tool_result.get('error')}")
            
            # 将工具结果添加到消息历史
            tool_result_str = json.dumps(tool_result, ensure_ascii=False, indent=2)
            if len(tool_result_str) > 2000:
                tool_result_str = tool_result_str[:2000] + "...（结果过长，已截断）"
            
            messages.append({
                "role": "user",
                "content": f"工具 '{tool_name}' 执行结果:\n{tool_result_str}"
            })
    
    # 循环结束，检查结果
    if not context.is_completed:
        print(f"\n⚠️ 达到最大迭代次数 ({max_iterations})")
        context.complete("抱歉，任务过于复杂，未能在规定的迭代次数内完成。")
    
    # 打印执行摘要
    summary = context.get_summary()
    print(f"\n{'='*60}")
    print(f"📊 执行摘要:")
    print(f"   - 总迭代次数: {summary['total_iterations']}")
    print(f"   - 工具调用次数: {summary['total_tool_calls']}")
    print(f"   - 成功调用: {summary['successful_calls']}")
    print(f"   - 失败调用: {summary['failed_calls']}")
    print(f"   - 上下文变量: {summary['context_variables_count']}")
    print(f"   - 任务状态: {'已完成' if summary['is_completed'] else '未完成'}")
    print(f"{'='*60}")
    
    return {
        'success': True,
        'answer': context.final_answer,
        'context': context
    }


if __name__ == '__main__':
    # 测试代码
    from agent_with_compression import create_smart_agent
    
    print("测试链式工具调用...")
    
    # 创建智能体
    agent = create_smart_agent(enable_logging=False)
    
    # 测试用例 1：生成通知
    print("\n" + "="*60)
    print("测试用例 1: 生成部门通知")
    print("="*60)
    
    result = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="帮我写一个技术部关于五一放假的通知",
        max_iterations=5
    )
    
    if result['success']:
        print(f"\n✅ 最终答案:\n{result['answer']}")
    else:
        print(f"\n❌ 执行失败: {result.get('error')}")
    
    # 测试用例 2：访问网页
    print("\n" + "="*60)
    print("测试用例 2: 访问网页并总结")
    print("="*60)
    
    result2 = execute_chained_tool_call(
        llm_client=agent.llm_client,
        user_request="访问 https://httpbin.org/html 并简要描述页面内容",
        max_iterations=3
    )
    
    if result2['success']:
        print(f"\n✅ 最终答案:\n{result2['answer'][:500]}")
    else:
        print(f"\n❌ 执行失败: {result2.get('error')}")
