"""
LLM 连接测试工具
使用 Python 标准 HTTP 库访问 OpenAI 兼容协议的 LLM
"""

import os
import json
import time
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse


def load_env_file():
    """读取项目根目录的 .env 文件"""
    # 获取项目根目录（practice01 的父目录）
    project_root = os.path.dirname(os.path.dirname(__file__))
    env_path = os.path.join(project_root, '.env')
    
    if not os.path.exists(env_path):
        print(f"❌ 错误: .env 文件不存在于 {env_path}")
        print("📝 请先复制 env.example 为 .env 并填写正确的配置")
        return None
    
    config = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config


def test_llm_connection(base_url, model, api_token=None, timeout=30, temperature=0.7, max_tokens=50):
    """
    使用标准 HTTP 库测试 LLM 连接
    
    参数:
        base_url: LLM API 的基础 URL
        model: 模型名称
        api_token: API 认证令牌（可选）
        timeout: 请求超时时间（秒）
        temperature: 温度参数（0.0-1.0）
        max_tokens: 最大生成 token 数
    
    返回:
        dict: 包含测试结果和响应数据
    """
    
    print("=" * 70)
    print("🤖 LLM 连接测试")
    print("=" * 70)
    print(f"📍 Base URL: {base_url}")
    print(f"📦 Model: {model}")
    print(f"🔑 API Token: {'已设置' if api_token else '未设置'}")
    print(f"⏱️  Timeout: {timeout}s")
    print(f"🌡️  Temperature: {temperature}")
    print(f"📝 Max Tokens: {max_tokens}")
    print("-" * 70)
    
    try:
        # 解析 URL
        parsed_url = urlparse(base_url)
        host = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        path = parsed_url.path.rstrip('/') + '/chat/completions'
        
        # 构建请求数据
        request_data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "你好，请简单回复'连接成功'即可。"
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        body = json.dumps(request_data).encode('utf-8')
        
        # 构建请求头
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(body))
        }
        
        if api_token and api_token != 'your_api_token_here':
            headers['Authorization'] = f'Bearer {api_token}'
        
        # 创建 HTTP 连接
        if parsed_url.scheme == 'https':
            conn = HTTPSConnection(host, port, timeout=timeout)
        else:
            conn = HTTPConnection(host, port, timeout=timeout)
        
        print(f"🔗 正在连接到 {host}:{port}...")
        
        # 记录开始时间
        start_time = time.time()
        
        # 发送请求
        conn.request('POST', path, body=body, headers=headers)
        
        # 获取响应
        response = conn.getresponse()
        response_body = response.read().decode('utf-8')
        
        # 记录结束时间
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        conn.close()
        
        # 检查响应状态
        if response.status == 200:
            response_data = json.loads(response_body)
            
            print(f"✅ 连接成功！状态码: {response.status}")
            print("-" * 70)
            
            # 提取并显示回复内容
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0]['message']['content']
                print(f"💬 AI 回复:\n{content}")
            
            # 显示性能统计
            print(f"\n⏱️  性能统计:")
            print(f"   - 响应时间: {elapsed_time:.3f} 秒")
            
            # 显示 token 使用情况
            if 'usage' in response_data:
                usage = response_data['usage']
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                total_tokens = usage.get('total_tokens', 0)
                
                print(f"\n📊 Token 使用统计:")
                print(f"   - Prompt tokens: {prompt_tokens}")
                print(f"   - Completion tokens: {completion_tokens}")
                print(f"   - Total tokens: {total_tokens}")
                
                # 计算 token/s 速度
                if elapsed_time > 0 and total_tokens > 0:
                    tokens_per_second = total_tokens / elapsed_time
                    print(f"   - Token 速度: {tokens_per_second:.2f} tokens/秒")
            else:
                print(f"\n📊 Token 使用统计: 未提供")
            
            print("=" * 70)
            
            return {
                'success': True,
                'status_code': response.status,
                'response': response_data,
                'elapsed_time': elapsed_time,
                'usage': response_data.get('usage', {})
            }
        else:
            print(f"❌ 连接失败！状态码: {response.status}")
            print(f"📄 响应内容:\n{response_body}")
            print("=" * 70)
            
            return {
                'success': False,
                'status_code': response.status,
                'error': response_body
            }
    
    except ConnectionRefusedError:
        print(f"❌ 连接被拒绝：无法连接到 {host}:{port}")
        print("💡 提示：请确保 LLM 服务正在运行")
        print("=" * 70)
        return {'success': False, 'error': 'Connection refused'}
    
    except TimeoutError:
        print(f"❌ 连接超时：超过 {timeout} 秒")
        print("💡 提示：可以嘗試增加 REQUEST_TIMEOUT 值")
        print("=" * 70)
        return {'success': False, 'error': 'Timeout'}
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        print(f"📄 原始响应:\n{response_body}")
        print("=" * 70)
        return {'success': False, 'error': f'JSON decode error: {e}'}
    
    except Exception as e:
        print(f"❌ 发生错误: {type(e).__name__}: {e}")
        print("=" * 70)
        return {'success': False, 'error': str(e)}


def main():
    """主函数：加载配置并测试 LLM 连接"""
    
    print("\n🚀 开始加载配置...\n")
    
    # 加载 .env 文件
    config = load_env_file()
    
    if config is None:
        return
    
    # 提取配置参数
    base_url = config.get('LLM_BASE_URL', 'http://localhost:11434/v1')
    model = config.get('LLM_MODEL', 'llama2')
    api_token = config.get('LLM_API_TOKEN', None)
    timeout = int(config.get('REQUEST_TIMEOUT', '30'))
    temperature = float(config.get('TEMPERATURE', '0.7'))
    max_tokens = int(config.get('MAX_TOKENS', '50'))
    
    # 执行测试
    result = test_llm_connection(
        base_url=base_url,
        model=model,
        api_token=api_token,
        timeout=timeout,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # 输出测试结果总结
    print("\n📋 测试总结:")
    if result['success']:
        print("✅ LLM 连接测试通过！配置正确。")
    else:
        print("❌ LLM 连接测试失败。请检查配置和服务状态。")
        print(f"   错误信息: {result.get('error', '未知错误')}")


if __name__ == '__main__':
    main()
