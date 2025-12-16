#!/usr/bin/env python3
"""
前端演示服务器 - 提供Web界面和API接口
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="量子销售经理智能体演示", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟会话存储
sessions: Dict[str, Dict[str, Any]] = {}

class ChatService:
    """聊天服务类 - 对接实际的agent_service"""
    
    def __init__(self):
        self.conversation_history = []
    
    async def process_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """处理用户消息并返回AI响应"""
        try:
            # 这里应该调用实际的agent_service
            # 暂时使用模拟响应
            response = await self._generate_response(message)
            
            # 更新会话历史
            if session_id not in sessions:
                sessions[session_id] = {
                    'id': session_id,
                    'created_at': datetime.now().isoformat(),
                    'messages': []
                }
            
            sessions[session_id]['messages'].extend([
                {'role': 'user', 'content': message, 'timestamp': datetime.now().isoformat()},
                {'role': 'assistant', 'content': response, 'timestamp': datetime.now().isoformat()}
            ])
            
            return {
                'success': True,
                'message': response,
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
    
    async def _generate_response(self, message: str) -> str:
        """生成AI响应（模拟实现）"""
        # 基于预设知识库的响应
        knowledge_base = {
            "量子计算优势": [
                "量子计算在处理复杂优化问题、大规模数据分析和密码学方面具有显著优势",
                "相比传统计算机，量子计算机能够并行处理大量可能性，解决NP难问题",
                "在药物研发、金融风险分析、物流优化等领域有突破性应用"
            ],
            "实施时间": [
                "标准量子解决方案实施周期通常为6-12个月",
                "具体时间取决于业务复杂度、数据准备和技术集成需求",
                "我们提供分阶段实施方案，确保平稳过渡"
            ],
            "成本范围": [
                "企业级量子解决方案年费在50-200万元之间",
                "价格根据量子比特数、算法复杂度和支持服务而定",
                "我们提供灵活的定价模式，包括按使用量计费"
            ],
            "应用案例": [
                "某金融机构使用量子算法优化投资组合，年收益提升15%",
                "制药公司利用量子计算加速药物筛选，研发周期缩短40%",
                "物流企业通过量子优化算法降低运输成本20%"
            ],
            "合作流程": [
                "第一步：需求分析和可行性评估（1-2周）",
                "第二步：技术方案定制和POC验证（2-4周）",
                "第三步：系统集成和团队培训（4-8周）",
                "第四步：上线运行和持续优化"
            ]
        }
        
        # 关键词匹配
        keywords = {
            "优势": "量子计算优势",
            "好处": "量子计算优势", 
            "强项": "量子计算优势",
            "时间": "实施时间",
            "周期": "实施时间",
            "多久": "实施时间",
            "成本": "成本范围",
            "价格": "成本范围",
            "费用": "成本范围",
            "案例": "应用案例",
            "例子": "应用案例",
            "实例": "应用案例",
            "合作": "合作流程",
            "开始": "合作流程",
            "流程": "合作流程"
        }
        
        # 查找匹配的关键词
        matched_topic = None
        for keyword, topic in keywords.items():
            if keyword in message:
                matched_topic = topic
                break
        
        if matched_topic and matched_topic in knowledge_base:
            responses = knowledge_base[matched_topic]
            import random
            return random.choice(responses)
        
        # 默认响应
        default_responses = [
            "感谢您的咨询！我是量子销售经理，专门负责量子计算解决方案。请问您对量子计算的哪个方面感兴趣？",
            "很高兴为您服务！我可以帮您解答关于量子计算的优势、应用场景、实施时间和成本等问题。",
            "作为量子销售专家，我专注于帮助企业理解量子技术的商业价值。请告诉我您的具体需求。"
        ]
        
        import random
        return random.choice(default_responses)

# 创建服务实例
chat_service = ChatService()

@app.get("/")
async def read_root():
    """根路径 - 返回主页面"""
    return FileResponse("chat.html")

@app.post("/api/chat/")
async def chat_endpoint(request: dict):
    """普通聊天接口"""
    try:
        message = request.get('message', '')
        session_id = request.get('session_id')
        
        if not message:
            raise HTTPException(status_code=400, detail="消息内容不能为空")
        
        result = await chat_service.process_message(message, session_id)
        return result
        
    except Exception as e:
        logger.error(f"聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/api/chat/stream")
async def websocket_chat(websocket: WebSocket):
    """WebSocket流式聊天接口"""
    await websocket.accept()
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            request = json.loads(data)
            
            message = request.get('message', '')
            session_id = request.get('session_id')
            
            if not message:
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': '消息内容不能为空'
                }))
                continue
            
            # 发送流开始信号
            await websocket.send_text(json.dumps({
                'type': 'stream_start',
                'session_id': session_id or f'session_{datetime.now().timestamp()}'
            }))
            
            # 模拟流式输出
            response = await chat_service._generate_response(message)
            words = response.split()
            
            for i, word in enumerate(words):
                await asyncio.sleep(0.1)  # 模拟思考时间
                await websocket.send_text(json.dumps({
                    'type': 'chunk',
                    'content': word + (' ' if i < len(words) - 1 else '')
                }))
            
            # 发送流结束信号
            await websocket.send_text(json.dumps({
                'type': 'stream_end',
                'message': '对话完成'
            }))
            
    except WebSocketDisconnect:
        logger.info("WebSocket连接断开")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        await websocket.send_text(json.dumps({
            'type': 'error',
            'message': str(e)
        }))

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话历史"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return sessions[session_id]

@app.post("/api/export/{session_id}")
async def export_conversation(session_id: str):
    """导出对话记录"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    session = sessions[session_id]
    export_content = f"量子销售经理对话记录\n会话ID: {session_id}\n创建时间: {session['created_at']}\n\n"
    
    for msg in session['messages']:
        role = "用户" if msg['role'] == 'user' else "AI助手"
        export_content += f"[{msg['timestamp']}] {role}: {msg['content']}\n"
    
    # 在实际应用中，这里应该生成文件并提供下载链接
    return {
        'success': True,
        'filename': f'conversation_{session_id}.txt',
        'content': export_content
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "quantum_sales_agent_demo"
    }

if __name__ == "__main__":
    # 挂载静态文件
    app.mount("/", StaticFiles(directory=".", html=True), name="static")
    
    # 启动服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )