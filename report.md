# AI 智能体开发学习项目

## 📚 项目简介

这是一个基于 Python 的 AI 智能体开发学习环境，通过实践项目逐步掌握大语言模型（LLM）的集成、配置和优化技术。

**学习目标：**
- 掌握 LLM API 的基本调用方法
- 理解 OpenAI 兼容协议的工作原理
- 学会测试和优化不同模型的参数配置
- 找到最适合自己硬件环境的 LLM 配置方案

---

## 📁 项目结构

```
人工智能提示/
├── .gitignore                      # Git 版本控制排除文件
├── env.example                     # 环境变量配置模板
├── main.py                         # 主程序入口（示例文件）
├── practice01/                     # 练习模块 01
│   ├── __init__.py                 # Python 包初始化
│   └── test_llm_connection.py      # LLM 连接测试工具
├── practice02/                     # 练习模块 02
│   ├── __init__.py                 # Python 包初始化
│   ├── agent.py                    # AI 智能体核心模块
│   ├── chat_demo.py                # 交互式聊天演示
│   ├── tool_chat_client.py         # 工具函数模块（网页访问等）
│   └── test_tools.py               # 工具函数测试脚本
├── practice03/                     # 练习模块 03
│   ├── __init__.py                 # Python 包初始化
│   ├── agent_with_compression.py   # 带自动压缩和日志功能的智能体
│   ├── chat_logger.py              # 聊天日志管理模块（5W规则）
│   ├── chat_demo_compression.py    # 压缩功能交互演示
│   ├── test_compression.py         # 压缩功能测试脚本
│   └── test_logging_and_search.py  # 日志和搜索功能测试
├── practice04/                     # 练习模块 04
│   ├── __init__.py                 # Python 包初始化
│   ├── anythingllm_tools.py        # AnythingLLM API 查询工具
│   ├── tool_chat_client.py         # 集成工具函数（网页访问 + AnythingLLM + Notice Skill）
│   ├── chat_demo_anythingllm.py    # AnythingLLM 集成演示
│   ├── demo_notice_skill.py        # 🆕 Notice Skill 与 LLM 集成演示
│   ├── test_anythingllm.py         # AnythingLLM 工具测试
│   ├── test_notice_skill.py        # 🆕 Notice Skill 功能测试
│   └── quick_test.py               # 快速模块测试
└── .venv/                          # Python 虚拟环境
```

---

## 💻 代码文件说明

### 1. `main.py`
**功能用途：**
- 项目的主入口文件（当前为 PyCharm 生成的示例代码）
- 后续可扩展为完整的 AI 智能体应用

**教学目标：**
- 了解 Python 程序的基本结构
- 理解 `if __name__ == '__main__':` 的作用
- 掌握函数定义和调用的基本语法

---

### 2. `practice01/test_llm_connection.py`
**功能用途：**
- 读取项目根目录的 `.env` 配置文件
- 使用 Python 标准 HTTP 库（http.client）访问 LLM API
- 测试与 OpenAI 兼容协议的 LLM 服务的连接
- 显示详细的测试结果和响应信息

**核心功能模块：**

#### `load_env_file()` 函数
- **功能**：解析 `.env` 文件，提取配置参数
- **实现要点**：
  - 自动定位项目根目录
  - 跳过注释和空行
  - 处理键值对分割
- **教学目标**：
  - 掌握文件读写操作
  - 学习字符串处理方法
  - 理解路径操作（os.path）
  - 了解环境变量配置的最佳实践

#### `test_llm_connection()` 函数
- **功能**：发送 HTTP POST 请求到 LLM API，测试连接
- **实现要点**：
  - 使用 `http.client` 标准库（无需第三方依赖）
  - 构建符合 OpenAI 协议的 JSON 请求体
  - 处理 HTTPS 和 HTTP 两种协议
  - 完整的异常处理机制
  - 详细的日志输出
- **教学目标**：
  - 掌握 HTTP 协议基础知识
  - 学习 RESTful API 调用方法
  - 理解 JSON 数据格式
  - 掌握异常处理技巧
  - 了解 URL 解析和处理
  - 学习请求头的构造（Content-Type, Authorization）

#### `main()` 函数
- **功能**：程序主入口，协调配置加载和测试执行
- **实现要点**：
  - 从配置中提取参数并转换类型
  - 调用测试函数
  - 输出测试结果总结
- **教学目标**：
  - 理解程序的组织结构
  - 学习数据类型转换
  - 掌握字典的 get 方法和默认值

**关键技术点：**
1. **标准库优先**：仅使用 Python 内置库，降低学习门槛
2. **错误处理**：覆盖网络错误、超时、JSON 解析等常见异常
3. **用户友好**：使用 Emoji 和清晰的提示信息
4. **可扩展性**：模块化设计，便于添加新功能

---

### 3. `practice02/agent.py`
**功能用途：**
- AI 智能体核心模块，实现对话代理功能
- 支持上下文记忆和多轮对话
- 集成工具调用能力（Function Calling）

**核心类：**

#### `LLMClient` 类
- **功能**：封装 LLM API 调用逻辑
- **主要方法**：
  - `chat_completion()`: 发送聊天请求，支持工具调用
- **教学目标**：
  - 掌握 API 客户端设计模式
  - 理解 HTTPS 连接管理
  - 学习性能监控和统计

#### `AIAgent` 类
- **功能**：具有记忆能力的对话代理
- **主要方法**：
  - `chat()`: 与智能体对话，支持工具启用/禁用
  - `clear_history()`: 清空对话历史
  - `get_history()`: 获取对话历史
- **教学目标**：
  - 理解状态管理和上下文维护
  - 学习模块化设计和职责分离
  - 掌握工具集成模式

#### `create_agent()` 函数
- **功能**：工厂函数，创建配置好的智能体实例
- **参数**：
  - `system_prompt`: 自定义系统提示
  - `enable_tools`: 是否启用工具调用
- **教学目标**：
  - 理解工厂模式
  - 学习依赖注入
  - 掌握配置管理

---

### 4. `practice02/chat_demo.py`
**功能用途：**
- 交互式聊天演示程序
- 展示智能体的使用方法和功能特性

**运行方式：**
```powershell
# 交互模式
python practice02/chat_demo.py

# 演示模式（自动执行示例对话）
python practice02/chat_demo.py --demo
```

**功能特性：**
- 实时对话交互
- 对话历史管理
- 性能指标显示
- 特殊命令支持（quit, clear, history, stats）

**教学目标：**
- 学习命令行交互程序设计
- 掌握用户输入处理
- 理解异常处理和用户体验

---

### 5. `practice02/tool_chat_client.py`
**功能用途：**
- 提供 AI 智能体可调用的工具函数
- 实现网页访问、数据处理等实用功能
- 支持工具描述和动态执行

**核心功能：**

#### `fetch_webpage(url, timeout)` 函数
- **功能**：使用 curl 命令访问网页并返回内容
- **实现要点**：
  - 跨平台支持（Windows/Linux/Mac）
  - 自动跟随重定向
  - HTTP 状态码检测
  - 超时控制和错误处理
- **教学目标**：
  - 掌握 subprocess 模块使用
  - 学习外部命令调用
  - 理解进程间通信
  - 掌握输出解析技巧

#### `get_tool_description()` 函数
- **功能**：生成符合 OpenAI 标准的工具描述
- **用途**：让 LLM 理解可用工具的功能和参数
- **教学目标**：
  - 理解 Function Calling 机制
  - 学习 JSON Schema 定义
  - 掌握 API 设计规范

#### `execute_tool(tool_name, **kwargs)` 函数
- **功能**：动态执行指定工具
- **用途**：根据 LLM 的决策调用相应工具
- **教学目标**：
  - 学习反射和动态调用
  - 理解插件化架构
  - 掌握错误隔离

**扩展性：**
- 通过 `AVAILABLE_TOOLS` 字典轻松添加新工具
- 统一的接口设计便于集成
- 支持工具描述自动生成

---

### 6. `practice02/test_tools.py`
**功能用途：**
- 工具函数测试脚本
- 验证网页访问等功能是否正常

**运行方式：**
```powershell
python practice02/test_tools.py
```

**测试内容：**
- 正常网页访问
- 无效 URL 处理
- 工具调用接口
- 工具描述生成

**教学目标：**
- 学习单元测试编写
- 掌握边界情况测试
- 理解自动化测试的重要性

---

### 7. `practice03/agent_with_compression.py`
**功能用途：**
- 带自动聊天历史压缩和日志功能的智能 AI 智能体
- 基于 practice02 扩展，添加上下文长度管理
- 🆕 智能检测并压缩过长的对话历史
- 🆕 自动记录压缩内容到本地文件（5W规则）
- 🆕 支持 /search 命令搜索聊天历史

**核心特性：**

#### 自动压缩触发机制
- **轮数检测**：当对话超过设定轮数（默认 5 轮）时触发
- **长度检测**：当上下文超过设定长度（默认 3000 字符）时触发
- **双重保障**：任一条件满足即触发压缩

#### 压缩策略
- **智能总结**：调用 LLM 对前 70% 的对话进行总结
- **保留最近**：保留最后 30% 的原始对话内容
- **保持连贯**：确保压缩后对话仍然保持上下文连贯性

#### 🆕 聊天日志记录
- **5W规则提取**：从压缩内容中提取 Who、What、When、Where、Why
- **本地存储**：记录到 D:\chat-log\log.txt
- **增量更新**：每次压缩后追加新记录
- **格式规范**：统一的日志格式，便于阅读和检索

#### 🆕 智能搜索功能
- **/search 命令**：以 /search 开头触发搜索
- **自然语言识别**：识别“查找聊天”、“搜索历史”等表达
- **LLM 辅助搜索**：将日志发送给 LLM 进行智能检索
- **结果整合**：结合搜索结果和用户问题生成完整回复

#### `SmartAIAgent` 类
- **主要方法**：
  - `chat()`: 对话方法，支持自动压缩和搜索
  - `_needs_compression()`: 检测是否需要压缩
  - `_compress_history_with_logging()`: 执行压缩并记录日志
  - `_extract_5w_from_compressed()`: 从压缩内容提取5W信息
  - `_search_chat_history()`: 搜索聊天历史
  - `_is_search_intent()`: 检测搜索意图
  - `get_stats()`: 获取统计信息（包括日志统计）
- **配置参数**：
  - `max_rounds`: 最大对话轮数阈值
  - `max_context_length`: 最大上下文长度阈值
  - `compression_ratio`: 压缩比例（0.7 = 压缩前 70%）
  - `enable_logging`: 是否启用聊天日志
  - `log_file_path`: 日志文件路径

**教学目标：**
- 理解上下文管理的重要性
- 学习智能压缩算法设计
- 掌握 LLM 总结能力应用
- 了解 Token 优化技巧
- 🆕 学习信息提取和结构化记录
- 🆕 掌握本地数据存储和搜索

---

### 8. `practice03/chat_demo_compression.py`
**功能用途：**
- 展示聊天历史自动压缩功能的交互演示
- 提供交互模式和演示模式两种运行方式

**运行方式：**
```powershell
# 交互模式
python practice03/chat_demo_compression.py

# 演示模式（自动多轮对话，展示压缩效果）
python practice03/chat_demo_compression.py --demo
```

**特殊命令：**
- `stats`: 查看统计信息（包括压缩次数、日志统计）
- `config`: 查看压缩配置参数
- `history`: 查看当前对话历史
- `clear`: 清空对话历史
- 🆕 `/search 关键词`: 搜索聊天历史
- 🆕 `查找/搜索/之前聊过`: 自然语言触发搜索

**演示模式特点：**
- 自动进行 10 轮对话
- 清晰展示何时触发压缩
- 显示压缩前后的对比数据
- 帮助理解压缩机制

**教学目标：**
- 观察压缩触发时机
- 理解压缩效果
- 学习参数调优

---

### 9. `practice03/chat_logger.py`
**功能用途：**
- 🆕 聊天日志管理模块
- 基于 5W 规则提取和记录关键信息
- 支持聊天历史搜索功能

**核心功能：**

#### 5W 规则信息提取
- **Who (谁)**: 涉及的人物或主体
- **What (做了什么)**: 发生的主要事件或行为
- **When (何时)**: 时间信息（可选）
- **Where (何地)**: 地点信息（可选）
- **Why (为何)**: 原因或目的（可选）

#### `ChatLogger` 类
- **主要方法**：
  - `extract_5w_info()`: 从对话中提取5W信息
  - `format_log_entry()`: 格式化日志条目
  - `append_to_log()`: 增量追加到日志文件
  - `read_log()`: 读取完整日志
  - `search_in_log()`: 在日志中搜索关键词
  - `get_log_stats()`: 获取日志统计信息

#### 日志文件管理
- **默认路径**: `D:\chat-log\log.txt`
- **自动创建**: 目录和文件不存在时自动创建
- **增量更新**: 每次压缩后追加新记录
- **格式规范**: 统一的日志格式，便于阅读和搜索

**教学目标：**
- 理解信息提取的重要性
- 学习结构化数据记录
- 掌握文件增量更新技巧
- 了解本地数据存储方案

---

### 10. `practice03/test_logging_and_search.py`
**功能用途：**
- 🆕 聊天日志和搜索功能的单元测试脚本
- 验证5W规则提取、日志记录和搜索意图检测

**测试内容：**
- 聊天日志管理器功能
- 5W信息格式化
- 日志文件读写和搜索
- 搜索意图检测准确性
- 日志文件自动创建

**运行方式：**
```powershell
python practice03/test_logging_and_search.py
```

**教学目标：**
- 学习复杂功能测试
- 掌握多模块集成测试
- 理解自动化验证的重要性

---

### 12. `practice03/test_compression.py`

**测试内容：**
- 压缩检测逻辑（轮数、长度阈值）
- 压缩执行逻辑（总结生成、历史重组）
- 自动压缩集成测试
- 配置参数验证

**运行方式：**
```powershell
python practice03/test_compression.py
```

**教学目标：**
- 学习单元测试编写
- 掌握边界情况测试
- 理解自动化验证的重要性

---

### 11. `practice04/anythingllm_tools.py`
**功能用途：**
- 🆕 AnythingLLM API 查询工具模块
- 使用 subprocess 调用 curl 命令访问 AnythingLLM 知识库
- 支持工作空间选择和API密钥认证

**核心功能：**

#### `anythingllm_query()` 函数
- **功能**：通过 curl 命令查询 AnythingLLM API
- **实现要点**：
  - 使用 subprocess 模块执行外部命令
  - 构建符合 AnythingLLM API 规范的请求
  - 支持 Bearer Token 认证
  - 跨平台兼容（Windows/Linux/Mac）
  - 完整的错误处理和状态码检测
  - JSON 响应解析和内容提取
- **参数说明**：
  - `message`: 要查询的问题或消息（必需）
  - `workspace_slug`: 工作空间标识符（可选）
  - `api_base_url`: API 基础 URL，默认 http://localhost:3001
  - `api_key`: AnythingLLM API 密钥（必需）
  - `timeout`: 超时时间（秒），默认 30 秒
- **教学目标**：
  - 掌握 subprocess 模块的高级用法
  - 学习外部 API 集成方法
  - 理解 Bearer Token 认证机制
  - 掌握命令行工具调用技巧
  - 了解 AnythingLLM 平台架构

---

### 12. `practice04/tool_chat_client.py`
**功能用途：**
- 🆕 集成多种工具函数的客户端模块
- 包含网页访问、AnythingLLM 查询和部门通知生成三大功能
- 统一的工具注册和执行接口

**核心特性：**
- **多工具支持**：同时提供 fetch_webpage、anythingllm_query 和 generate_notice
- **统一接口**：所有工具遵循相同的调用规范
- **动态描述**：自动生成符合 OpenAI 标准的工具描述
- **灵活扩展**：通过 AVAILABLE_TOOLS 字典轻松添加新工具

**工具列表：**
1. `fetch_webpage`: 访问指定 URL 获取网页内容
2. `anythingllm_query`: 查询 AnythingLLM 知识库
3. `generate_notice`: 🆕 生成部门通知文档（notice skill）

**generate_notice 工具说明：**
- **功能**：根据用户请求自动生成部门通知文档
- **参数**：
  - `topic`（必需）：通知主题，例如“五一节放假”、“年会安排”等
  - `department`（可选）：部门名称，例如“销售部”、“技术部”等。不提供则使用“XX部”
- **输出格式**：
  - 如果未提供部门：以“XX部通知”开头
  - 如果提供部门：以“{部门}通知”开头，例如“销售部通知”
- **应用场景**：
  - 用户要求撰写放假通知
  - 用户需要生成会议通知
  - 用户要求起草公告文档

**系统提示词设计：**
```python
system_prompt = """
你是一个智能AI助手，具备以下能力：

1. **通用对话**：回答日常问题、提供建议
2. **网页访问**：可以访问指定的URL获取网页内容
3. **知识库查询**：可以查询 AnythingLLM 本地知识库

**anythingllm_query 工具使用时机**：
- 用户询问公司政策、内部流程
- 用户查询项目文档、技术规范
- 用户需要了解已上传到知识库的内容
- 用户明确要求查询知识库或文档
"""
```

**教学目标：**
- 学习多工具集成架构
- 掌握工具描述生成
- 理解系统提示词设计
- 了解工具选择策略

---

### 13. `practice04/chat_demo_anythingllm.py`
**功能用途：**
- 🆕 AnythingLLM 集成交互演示程序
- 展示如何使用知识库查询工具
- 支持压缩功能和工具调用的完整演示

**运行方式：**
```powershell
# 设置 AnythingLLM API Key
$env:ANYTHINGLLM_API_KEY='your-api-key-here'

# 运行交互演示
python practice04/chat_demo_anythingllm.py
```

**特殊命令：**
- `stats`: 查看统计信息
- `config`: 查看配置参数
- `history`: 查看对话历史
- `clear`: 清空对话历史
- `compress`: 手动触发压缩
- `quit/exit`: 退出程序

**教学目标：**
- 体验 AnythingLLM 集成效果
- 学习环境变量配置
- 掌握交互式程序设计

---

### 14. `practice04/test_anythingllm.py`
**功能用途：**
- 🆕 AnythingLLM 工具功能测试脚本
- 验证 API 连接和查询功能

**测试内容：**
- 基本查询功能
- 带参数的查询
- 错误处理（缺少API密钥）
- 工具描述生成
- 参数验证

**运行方式：**
```powershell
# 设置 API Key
$env:ANYTHINGLLM_API_KEY='your-api-key-here'

# 运行测试
python practice04/test_anythingllm.py
```

**教学目标：**
- 学习 API 集成测试
- 掌握错误场景覆盖
- 理解自动化测试流程

---

### 15. `practice04/demo_notice_skill.py`
**功能用途：**
- 🆕 Notice Skill 与 LLM 集成演示程序
- 展示 LLM 如何根据用户请求自动调用 generate_notice 工具
- 验证智能体能否正确提取部门信息并生成相应通知

**运行方式：**
```powershell
python practice04/demo_notice_skill.py
```

**演示场景：**
1. **场景一**：用户不说明部门，要求生成五一节放假通知
   - 预期：LLM 自动调用 generate_notice(topic="五一节放假")
   - 结果：通知以"XX部通知"开头
2. **场景二**：用户说明部门为"销售部"，要求生成五一节放假通知
   - 预期：LLM 自动调用 generate_notice(topic="五一节放假", department="销售部")
   - 结果：通知以"销售部通知"开头

**教学目标：**
- 理解 LLM Function Calling 机制
- 学习工具描述设计技巧
- 掌握参数提取和传递
- 了解智能体决策过程

---

### 16. `practice04/test_notice_skill.py`
**功能用途：**
- 🆕 Notice Skill 功能测试脚本
- 验证部门通知生成功能是否正常工作

**测试场景：**
1. **场景一**：用户不说明部门，要求生成五一节放假通知
   - 预期结果：通知以"XX部通知"开头
2. **场景二**：用户说明部门为"销售部"，要求生成五一节放假通知
   - 预期结果：通知以"销售部通知"开头
3. **场景三**：用户说明部门为"技术部"，要求生成五一节放假通知
   - 预期结果：通知以"技术部通知"开头

**运行方式：**
```powershell
python practice04/test_notice_skill.py
```

**教学目标：**
- 学习工具函数的参数设计
- 掌握条件逻辑处理
- 理解工具调用的灵活性
- 了解智能体如何根据上下文选择工具参数

---

### 17. `env.example`
**功能用途：**
- 环境变量配置模板文件
- 定义 LLM 服务所需的所有配置项

**配置项说明：**
- `LLM_BASE_URL`: LLM API 的基础 URL
- `LLM_MODEL`: 使用的模型名称
- `LLM_API_TOKEN`: API 认证令牌（可选）
- `REQUEST_TIMEOUT`: 请求超时时间（秒）
- `MAX_TOKENS`: 最大生成 token 数
- `TEMPERATURE`: 温度参数（控制随机性）
- `TOP_P`: Top-p 采样参数

**教学目标：**
- 理解环境变量管理的最佳实践
- 了解敏感信息不应该硬编码在代码中
- 学习配置文件的结构设计

---

### 15. `.gitignore`
**功能用途：**
- 指定 Git 版本控制应该忽略的文件和目录

**排除内容：**
- Python 缓存文件（`__pycache__/`, `*.pyc`）
- 虚拟环境目录（`.venv/`, `venv/`）
- 环境变量文件（`.env`）
- IDE 配置文件（`.idea/`, `.vscode/`）
- 测试覆盖率报告
- 系统文件（`.DS_Store`, `Thumbs.db`）

**教学目标：**
- 理解版本控制的最佳实践
- 了解哪些文件不应该提交到 Git
- 保护敏感信息不被泄露

---

## 🎯 学习路径

### 第一阶段：基础准备
- [ ] 理解项目结构和文件组织
- [ ] 配置 Python 虚拟环境
- [ ] 学习 `.env` 文件的创建和使用
- [ ] 了解 OpenAI 兼容协议

### 第二阶段：API 调用实践
- [ ] 阅读并理解 `test_llm_connection.py` 的代码
- [ ] 学习 HTTP 请求的基本原理
- [ ] 掌握 JSON 数据的构造和解析
- [ ] 理解异常处理的重要性

### 第三阶段：本地 LLM 部署
- [ ] 安装 Ollama 或其他 LLM 服务
- [ ] 下载适合的模型（根据硬件配置）
- [ ] 配置 `.env` 文件
- [ ] 运行测试脚本验证连接

### 第四阶段：参数优化
- [ ] 测试不同的 temperature 值（0.0-1.0）
- [ ] 调整 max_tokens 观察响应长度
- [ ] 尝试不同的 top_p 值
- [ ] 记录每种配置的性能和效果

### 第五阶段：智能体与工具集成
- [ ] 理解 AI 智能体的架构设计
- [ ] 学习 Function Calling 机制
- [ ] 掌握工具函数的开发和注册
- [ ] 实现网页访问等实用工具
- [ ] 运行 `test_tools.py` 验证工具功能

### 第六阶段：上下文管理与优化
- [ ] 理解聊天历史压缩的必要性
- [ ] 学习自动检测触发机制
- [ ] 掌握智能总结算法
- [ ] 实现 practice03 的压缩功能
- [ ] 运行 `test_compression.py` 验证功能
- [ ] 体验演示模式观察压缩效果

### 第七阶段：聊天日志与搜索
- [ ] 理解5W规则信息提取
- [ ] 学习本地日志存储方案
- [ ] 掌握增量文件更新技巧
- [ ] 实现 /search 命令和智能搜索
- [ ] 运行 `test_logging_and_search.py` 验证
- [ ] 体验完整的压缩+日志+搜索流程

### 第八阶段：AnythingLLM 集成
- [ ] 了解 AnythingLLM 平台架构
- [ ] 学习 subprocess 模块调用外部命令
- [ ] 掌握 Bearer Token 认证机制
- [ ] 实现 anythingllm_query 工具函数
- [ ] 学习多工具集成架构
- [ ] 运行 `test_anythingllm.py` 验证功能
- [ ] 体验知识库查询演示

### 第九阶段：Notice Skill 开发
- [ ] 理解工具函数的参数设计原则
- [ ] 学习条件逻辑处理（可选参数）
- [ ] 实现 generate_notice 工具函数
- [ ] 掌握通知模板生成技巧
- [ ] 运行 `test_notice_skill.py` 验证功能
- [ ] 测试不同场景下的通知生成效果

### 第十阶段：进阶开发
- [ ] 实现更复杂的 AI 智能体
- [ ] 添加 RAG（检索增强生成）功能
- [ ] 集成向量数据库
- [ ] 构建完整的 AI 应用

---

## 🚀 快速开始

### 1. 环境检查
```powershell
python --version  # 确认 Python 3.x 已安装
```

### 2. 配置环境变量
```powershell
# 复制模板文件
cp env.example .env

# 编辑 .env 文件，填入你的配置
```

### 3. 配置示例（Ollama）
```env
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama2
LLM_API_TOKEN=
REQUEST_TIMEOUT=30
MAX_TOKENS=2048
TEMPERATURE=0.7
```

### 4. 运行测试
```powershell
# 测试 LLM 连接
python practice01/test_llm_connection.py

# 运行交互式聊天（practice02）
python practice02/chat_demo.py

# 测试工具函数
python practice02/test_tools.py

# 测试聊天历史压缩功能
python practice03/test_compression.py

# 🆕 测试日志和搜索功能
python practice03/test_logging_and_search.py

# 运行带压缩功能的智能体（交互模式）
python practice03/chat_demo_compression.py

# 运行带压缩功能的智能体（演示模式）
python practice03/chat_demo_compression.py --demo

# 🆕 测试 AnythingLLM 工具
$env:ANYTHINGLLM_API_KEY='your-api-key-here'
python practice04/test_anythingllm.py

# 🆕 运行 AnythingLLM 集成演示
$env:ANYTHINGLLM_API_KEY='your-api-key-here'
python practice04/chat_demo_anythingllm.py

# 🆕 测试 Notice Skill 功能
python practice04/test_notice_skill.py

# 🆕 运行 Notice Skill 与 LLM 集成演示（需要 LLM 服务运行）
python practice04/demo_notice_skill.py
```

---

## 🔧 常用 LLM 服务配置

### Ollama（推荐本地部署）
```env
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama2
```

### LM Studio
```env
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=local-model
```

### OpenAI API
```env
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
LLM_API_TOKEN=sk-your-api-key
```

### 阿里云通义千问
```env
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
LLM_API_TOKEN=your-dashscope-api-key
```

### AnythingLLM（本地知识库）
```env
# LLM 服务配置（使用 LM Studio 或 Ollama）
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=qwen2.5-0.5b

# AnythingLLM API Key（环境变量）
$env:ANYTHINGLLM_API_KEY='your-anythingllm-api-key'
```

---

## 📊 参数调优指南

### Temperature（温度参数）
- **范围**：0.0 - 1.0
- **作用**：控制输出的随机性和创造性
- **建议**：
  - 0.0-0.3：确定性任务（代码生成、事实问答）
  - 0.4-0.7：平衡创造性和准确性
  - 0.8-1.0：创意写作、头脑风暴

### Max Tokens（最大 Token 数）
- **作用**：限制响应的最大长度
- **建议**：
  - 50-200：简单问答
  - 500-1000：详细解释
  - 2000+：长文本生成

### Top-p（核采样参数）
- **范围**：0.0 - 1.0
- **作用**：控制词汇选择的多样性
- **建议**：通常设置为 0.9，与 temperature 配合使用

---

## 💡 常见问题

### Q1: 连接被拒绝（Connection Refused）
**原因**：LLM 服务未启动  
**解决**：确保 Ollama 或其他 LLM 服务正在运行

### Q2: 请求超时（Timeout）
**原因**：模型加载慢或响应时间长  
**解决**：增加 `REQUEST_TIMEOUT` 值，或使用更小的模型

### Q3: 模型不存在
**原因**：模型名称错误或未下载  
**解决**：检查模型名称，使用 `ollama list` 查看已安装的模型

### Q4: 内存不足
**原因**：模型太大，超出显存/内存  
**解决**：使用参数量更小的模型（如 llama2:7b 而非 70b）

---

## 📝 学习资源

### 官方文档
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Ollama 官方文档](https://ollama.ai/docs)
- [Python http.client 文档](https://docs.python.org/3/library/http.client.html)

### 推荐阅读
- RESTful API 设计原则
- JSON 数据格式规范
- HTTP 协议基础
- 大语言模型参数详解

---

## 🎓 教学目标总结

通过本项目，你将掌握：

1. **Python 基础技能**
   - 文件读写和路径操作
   - 字符串处理和解析
   - 异常处理机制
   - 模块化编程

2. **网络编程能力**
   - HTTP 协议理解
   - RESTful API 调用
   - JSON 数据处理
   - 网络连接管理

3. **工程实践能力**
   - 环境变量管理
   - 配置文件设计
   - 版本控制规范
   - 代码组织和文档

4. **AI 开发基础**
   - LLM API 集成
   - 参数调优方法
   - 性能测试技巧
   - 本地模型部署

5. **智能体与工具开发**
   - AI 智能体架构设计
   - Function Calling 机制
   - 工具函数开发和注册
   - subprocess 外部命令调用
   - 跨平台兼容性处理

6. **上下文管理与优化**
   - 聊天历史压缩算法
   - 自动检测触发机制
   - LLM 总结能力应用
   - Token 消耗优化
   - 上下文连贯性保持

7. **聊天日志与搜索**
   - 5W规则信息提取
   - 本地日志存储方案
   - 增量文件更新技巧
   - 智能搜索功能实现
   - 自然语言意图识别

8. **Notice Skill 开发**
   - 工具函数参数设计原则
   - 条件逻辑处理（可选参数）
   - 通知模板生成技巧
   - 多场景测试验证
   - 智能体工具调用策略

---

## 🔄 持续更新

本项目会随着学习进度不断更新，添加新的练习模块和功能。

**下一步计划：**
- practice05: 实现 RAG（检索增强生成）
- practice06: 创建多智能体协作系统

---

## 📄 许可证

本项目仅供学习使用。

---

**祝你学习愉快！🚀**
