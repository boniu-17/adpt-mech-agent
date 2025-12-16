#!/usr/bin/env python3
"""
MySQL配置中心安装脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    if sys.version_info < (3, 7):
        print("❌ Python版本过低，需要3.7或更高版本")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("\n📦 安装依赖包...")
    
    dependencies = [
        "mysql-connector-python>=8.0.0",
        "redis>=4.5.0"
    ]
    
    for dep in dependencies:
        try:
            print(f"正在安装 {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {dep} 安装失败: {e}")
            return False
    
    return True

def check_mysql_service():
    """检查MySQL服务状态"""
    print("\n🔍 检查MySQL服务...")
    
    # 尝试连接MySQL
    try:
        import mysql.connector
        
        # 测试基本连接
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password=""
        )
        
        if conn.is_connected():
            print("✅ MySQL服务正常运行")
            conn.close()
            return True
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL连接失败: {e}")
        print("💡 请确保MySQL服务正在运行")
        return False
    except ImportError:
        print("❌ mysql-connector-python未正确安装")
        return False
    
    return False

def create_database():
    """创建数据库和表结构"""
    print("\n🗄️  创建数据库...")
    
    schema_file = Path("configs/database_schema.sql")
    if not schema_file.exists():
        print("❌ 数据库初始化脚本不存在")
        return False
    
    try:
        # 执行SQL脚本
        result = subprocess.run([
            "mysql", "-u", "root", "-p", "-e", f"source {schema_file.absolute()}"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 数据库初始化成功")
            return True
        else:
            print(f"❌ 数据库初始化失败: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ mysql命令未找到，请确保MySQL客户端已安装")
        return False
    except Exception as e:
        print(f"❌ 数据库创建失败: {e}")
        return False

def verify_configuration():
    """验证配置"""
    print("\n🔧 验证配置...")
    
    # 检查配置文件
    config_file = Path("configs/mysql_config.yaml")
    if not config_file.exists():
        print("⚠️  MySQL配置文件不存在，将创建默认配置")
        
        # 创建默认配置
        config_file.parent.mkdir(exist_ok=True)
        config_file.write_text("""# MySQL数据库配置
# 用于智能体配置的持久化存储

database:
  host: "localhost"
  port: 3306
  user: "root"
  password: ""
  database: "agent_config_center"
  charset: "utf8mb4"
  pool_size: 5

# Redis配置（可选，用于高频状态缓存）
redis:
  enabled: false
  host: "localhost"
  port: 6379
  password: ""
  db: 0

# 存储策略配置
storage_strategy: "mysql_only"  # mysql_only, redis_only, hybrid
sync_strategy: "async"      # sync, async
""")
        print("✅ 默认配置文件已创建")
    else:
        print("✅ MySQL配置文件存在")
    
    return True

def run_tests():
    """运行测试"""
    print("\n🧪 运行测试...")
    
    test_files = ["test_mysql_connection.py", "test_mysql_config.py"]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"运行 {test_file}...")
            try:
                result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {test_file} 测试通过")
                else:
                    print(f"❌ {test_file} 测试失败: {result.stderr}")
            except Exception as e:
                print(f"❌ {test_file} 执行失败: {e}")
        else:
            print(f"⚠️  {test_file} 不存在")
    
    return True

def main():
    """主安装流程"""
    print("🚀 MySQL配置中心安装程序")
    print("=" * 50)
    
    steps = [
        ("检查Python版本", check_python_version),
        ("安装依赖包", install_dependencies),
        ("检查MySQL服务", check_mysql_service),
        ("创建数据库", create_database),
        ("验证配置", verify_configuration),
        ("运行测试", run_tests)
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for step_name, step_func in steps:
        print(f"\n[{success_count + 1}/{total_steps}] {step_name}")
        if step_func():
            success_count += 1
        else:
            print(f"❌ {step_name} 失败")
            break
    
    print("\n" + "=" * 50)
    print(f"📊 安装结果: {success_count}/{total_steps} 步骤完成")
    
    if success_count == total_steps:
        print("🎉 MySQL配置中心安装成功！")
        print("\n📋 下一步操作:")
        print("1. 修改 configs/mysql_config.yaml 中的数据库密码")
        print("2. 运行 python examples/run_customer_manager_demo.py 测试完整功能")
        print("3. 查看 docs/MYSQL_CONFIGURATION.md 了解更多使用方法")
    else:
        print("❌ 安装失败，请检查上述错误信息")
        print("\n🔧 故障排除:")
        print("1. 确保MySQL服务正在运行")
        print("2. 检查网络连接")
        print("3. 查看详细错误日志")

if __name__ == "__main__":
    main()