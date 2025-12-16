"""
将YAML文件中的Prompt模板迁移到数据库
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.services.prompt_template_service import PromptTemplateService
from configs import config

def migrate_prompts():
    """迁移Prompt模板到数据库"""
    
    # 获取数据库配置
    db_config = config.get_database_config()
    
    if db_config['dialect'] == 'sqlite':
        db_path = db_config['database']
        if not db_path.startswith('/'):
            db_path = project_root / db_path
        connection_string = f"sqlite:///{db_path}"
    else:
        # 其他数据库类型（MySQL、PostgreSQL）
        username = db_config.get('username', '')
        password = db_config.get('password', '')
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', '')
        database = db_config.get('database', '')
        
        if db_config['dialect'] == 'mysql':
            connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        elif db_config['dialect'] == 'postgresql':
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"不支持的数据库方言: {db_config['dialect']}")
    
    # 创建数据库连接
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 创建服务实例
        prompt_service = PromptTemplateService(session)
        
        # YAML文件路径
        yaml_file = project_root / "configs" / "prompts" / "agent_prompts.yaml"
        
        if not yaml_file.exists():
            print(f"❌ YAML文件不存在: {yaml_file}")
            return False
        
        print(f"📁 开始迁移Prompt模板从: {yaml_file}")
        
        # 导入模板
        templates = prompt_service.import_from_yaml(str(yaml_file), created_by="migration")
        
        print(f"✅ 成功迁移 {len(templates)} 个Prompt模板到数据库")
        
        # 显示迁移结果
        for template in templates:
            print(f"   📝 {template.name} (v{template.version}) - {template.description}")
        
        # 验证迁移结果
        active_templates = prompt_service.get_active_templates()
        print(f"\n📊 数据库中共有 {len(active_templates)} 个活跃模板")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def backup_yaml_prompts():
    """备份YAML文件到备份目录"""
    
    prompts_dir = project_root / "configs" / "prompts"
    backup_dir = project_root / "configs" / "prompts" / "backup"
    
    # 创建备份目录
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 备份所有YAML文件
    for yaml_file in prompts_dir.glob("*.yaml"):
        if yaml_file.name != "agent_prompts.yaml":
            continue
            
        backup_file = backup_dir / f"{yaml_file.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{yaml_file.suffix}"
        
        import shutil
        shutil.copy2(yaml_file, backup_file)
        print(f"📦 已备份: {yaml_file} -> {backup_file}")

if __name__ == "__main__":
    from datetime import datetime
    
    print("🚀 Prompt模板数据库迁移工具")
    print("=" * 50)
    
    # 备份现有YAML文件
    print("\n1. 备份YAML文件...")
    backup_yaml_prompts()
    
    # 执行迁移
    print("\n2. 执行数据库迁移...")
    success = migrate_prompts()
    
    if success:
        print("\n🎉 迁移完成！")
        print("\n💡 后续使用建议：")
        print("   • 通过 PromptTemplateService 管理模板")
        print("   • 使用 render_template() 方法渲染模板")
        print("   • 可以通过Web界面或API动态修改模板")
    else:
        print("\n❌ 迁移失败，请检查错误信息")
    
    print("\n" + "=" * 50)