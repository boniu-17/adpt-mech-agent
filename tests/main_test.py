"""
专门测试量子销售经理智能体的脚本
"""

import asyncio
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.agent_service import AgentService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


async def quantum_sales_agent():
    """专门测试量子销售经理智能体"""

    print("🎯 量子销售经理智能体专项测试")
    print("=" * 60)

    try:
        question = "你好，我们对你们的产品很感兴趣，能介绍一下么？"
        agent_service = AgentService()
        await agent_service.initialize()
        agent = await agent_service.create_agent_from_db(1)
        agent = await agent_service.get_active_agent()
        print(f"✅ 智能体创建成功！ID: {agent.instance_id}")
        await agent_service.create_agent_from_db(1)
        inst_id = agent.instance_id
        full_cfg = agent_service.get_agent_config(agent.instance_id)
        print(full_cfg.prompt_templates)
        print(agent.get_config())
        await agent.initialize(full_cfg)
        print(agent.get_config())

        # 模拟流式输出
        full_response = ""
        generator = agent.process_stream(question)
        async for chunk in generator:
            print(chunk, end="", flush=True)
            full_response += chunk
        print(agent.get_detailed_metrics())
        print(agent.get_conversation_summary())
        print(agent.get_conversation_stats())
        print(agent.get_conversation_history())
        print(agent.get_template_stats('角色定义'))
        print(agent.get_template_stats('推理框架'))
        print(agent.get_template_stats('检索策略'))
        print(agent.get_template_stats('安全策略'))
        print(agent.get_template_stats('流程指导'))
        print(agent.list_templates())
        print(agent.template_manager.validate_required_templates())
        print(agent.get_conversation_summary())

        print(f"\n\n📊 流式输出统计:")
        print(f"  总字符数: {len(full_response)}")
        print(
            f"  是否包含量子知识点: {'是' if any(keyword in full_response for keyword in ['量子比特', '叠加态', '纠缠', '优化问题']) else '否'}")

        await agent_service.close_all()

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

        print("\n✅ 测试完成")


if __name__ == "__main__":
    # 运行销售场景测试
    asyncio.run(quantum_sales_agent())
