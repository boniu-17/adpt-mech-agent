#!/usr/bin/env python3
"""
快速启动脚本
一键配置和测试智能体系统
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print("❌ Python版本过低，需要Python 3.9+")
        return False
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查依赖
    try:
        import requests
        import yaml
        import chromadb
        print("✅ 核心依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        return False
    
    # 检查配置文件
    config_path = project_root / "configs" / "llm_config.yaml"
    if not config_path.exists():
        print("⚠️  配置文件不存在，将创建默认配置")
        create_default_config()
    else:
        print("✅ 配置文件存在")
    
    # 检查环境变量文件
    env_path = project_root / ".env"
    if not env_path.exists():
        print("⚠️  环境变量文件不存在，将创建模板")
        create_env_template()
    else:
        print("✅ 环境变量文件存在")
    
    return True


def create_default_config():
    """创建默认配置文件"""
    config_dir = project_root / "configs"
    config_dir.mkdir(exist_ok=True)
    
    config_content = """# LLM配置
llm:
  type: "mock"  # mock, deepseek, openai
  model_name: "deepseek-chat"
  api_key: "${DEEPSEEK_API_KEY}"
  base_url: "https://api.deepseek.com"
  temperature: 0.7
  max_tokens: 2048

# 智能体配置
agents:
  simple_assistant:
    name: "简单助手"
    description: "基础对话助手"
    system_prompt: "你是一个乐于助人的AI助手"
    
  reasoning_assistant:
    name: "推理助手"
    description: "擅长逻辑推理的助手"
    system_prompt: "你是一个擅长逻辑推理和分析的AI助手"
"""
    
    config_path = config_dir / "llm_config.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("✅ 默认配置文件已创建")


def create_env_template():
    """创建环境变量模板"""
    env_content = """# LLM API密钥配置
# DeepSeek API密钥
DEEPSEEK_API_KEY="your-deepseek-api-key-here"

# OpenAI API密钥
OPENAI_API_KEY="your-openai-api-key-here"

# 其他配置
DEBUG=true
LOG_LEVEL=INFO
"""
    
    env_path = project_root / ".env"
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("✅ 环境变量模板已创建")


def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    
    requirements_path = project_root / "requirements.txt"
    if not requirements_path.exists():
        print("❌ requirements.txt 不存在")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_path)
        ], check=True)
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False


def run_basic_tests():
    """运行基础测试"""
    print("🧪 运行基础测试...")
    
    test_script = project_root / "examples" / "test_basic_functionality.py"
    if not test_script.exists():
        print("❌ 测试脚本不存在")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, str(test_script)
        ], cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 基础测试通过")
            print(result.stdout)
            return True
        else:
            print("❌ 基础测试失败")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ 测试执行异常: {e}")
        return False


def run_demo():
    """运行演示"""
    print("🚀 运行客户经理智能体演示...")
    
    demo_script = project_root / "examples" / "final_customer_manager_demo.py"
    if not demo_script.exists():
        print("❌ 演示脚本不存在")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, str(demo_script)
        ], cwd=project_root)
        
        if result.returncode == 0:
            print("✅ 演示运行成功")
            return True
        else:
            print("❌ 演示运行失败")
            return False
    except Exception as e:
        print(f"❌ 演示执行异常: {e}")
        return False


def main():
    """主函数"""
    print("🎯 智能体系统快速启动")
    print("="*50)
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败")
        return
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        return
    
    # 运行基础测试
    if not run_basic_tests():
        print("❌ 基础测试失败")
        return
    
    # 运行演示
    if not run_demo():
        print("❌ 演示运行失败")
        return
    
    print("\n" + "="*50)
    print("🎉 快速启动完成！")
    print("\n📚 下一步操作建议：")
    print("1. 编辑 configs/llm_config.yaml 配置真实LLM API")
    print("2. 设置 DEEPSEEK_API_KEY 环境变量")
    print("3. 查看 docs/configuration_guide.md 了解更多配置选项")
    print("4. 运行 examples/final_customer_manager_demo.py 体验完整功能")
    print("\n💡 提示：当前使用Mock LLM进行演示，请配置真实API以获得更好的体验")


if __name__ == "__main__":
    main()