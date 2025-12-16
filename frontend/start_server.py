#!/usr/bin/env python3
"""
前端演示服务器启动脚本
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = ['fastapi', 'uvicorn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装依赖...")
        
        # 安装依赖
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ 已安装 {package}")
            except subprocess.CalledProcessError:
                print(f"✗ 安装 {package} 失败")
                return False
    
    return True

def start_server():
    """启动服务器"""
    # 切换到frontend目录
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    print("🚀 启动量子销售经理智能体演示界面...")
    print("📁 工作目录:", os.getcwd())
    print("🌐 服务地址: http://localhost:8000")
    print("⏳ 正在启动服务器...")
    
    try:
        # 启动服务器
        subprocess.run([
            sys.executable, "server.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("🤖 量子销售经理智能体 - 前端演示界面")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，请手动安装依赖包")
        return
    
    # 检查文件是否存在
    required_files = ['server.py', 'chat.html']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少必要文件: {file}")
            return
    
    print("✅ 所有依赖和文件检查通过")
    
    # 询问是否自动打开浏览器
    try:
        response = input("是否自动打开浏览器？(y/n, 默认y): ").strip().lower()
        if response in ['', 'y', 'yes']:
            # 延迟打开浏览器
            import threading
            import time
            
            def open_browser():
                time.sleep(2)  # 等待服务器启动
                webbrowser.open('http://localhost:8000')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
    except:
        pass
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()