# 量子销售经理智能体 - 前端演示界面

## 项目概述

这是一个基于DeepSeek风格的量子销售经理智能体Web演示界面，提供流式对话功能和预设对话流程演示。

## 功能特性

- 🎯 **DeepSeek风格界面** - 现代化的深色主题设计
- 💬 **流式对话** - 实时显示AI思考过程
- 🔄 **预设对话流程** - 一键启动完整的销售对话演示
- 📱 **响应式设计** - 支持桌面和移动设备
- 💾 **对话导出** - 支持导出对话记录
- ⚡ **WebSocket支持** - 实时双向通信

## 快速开始

### 方法一：使用启动脚本（推荐）

```bash
# 进入frontend目录
cd frontend

# 运行启动脚本
python start_server.py
```

### 方法二：手动启动

```bash
# 安装依赖
pip install fastapi uvicorn

# 启动服务器
cd frontend
python server.py
```

### 访问界面

打开浏览器访问: http://localhost:8000

## 文件结构

```
frontend/
├── chat.html          # 主界面HTML文件
├── server.py          # FastAPI后端服务器
├── start_server.py    # 自动启动脚本
└── README.md          # 说明文档
```

## API接口

### 普通聊天接口

```http
POST /api/chat/
Content-Type: application/json

{
    "message": "你好",
    "session_id": "optional_session_id",
    "agent_id": "quantum_sales_manager"
}
```

### WebSocket流式聊天

```javascript
// 连接WebSocket
const ws = new WebSocket('ws://localhost:8000/api/chat/stream');

// 发送消息
ws.send(JSON.stringify({
    message: "你好",
    session_id: "session_123",
    agent_id: "quantum_sales_manager"
}));

// 接收流式响应
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch(data.type) {
        case 'stream_start':
            console.log('流开始:', data.session_id);
            break;
        case 'chunk':
            console.log('内容块:', data.content);
            break;
        case 'stream_end':
            console.log('流结束');
            break;
        case 'error':
            console.error('错误:', data.message);
            break;
    }
};
```

### 获取会话历史

```http
GET /api/sessions/{session_id}
```

### 导出对话

```http
POST /api/export/{session_id}
```

## 界面功能

### 左侧边栏
- **角色卡切换** - 显示当前激活的智能体
- **工具选择** - 可用的功能工具列表
- **用户配置** - 点击头像进行设置

### 主聊天区
- **实时对话** - 用户和AI的消息显示
- **流式输出** - AI回复时的打字动画效果
- **预设对话** - 一键启动完整销售流程演示

### 操作按钮
- **预设对话** - 启动预设的7轮销售对话
- **导出对话** - 下载当前对话记录
- **用户配置** - 打开设置菜单

## 技术栈

### 前端
- **HTML5/CSS3** - 页面结构和样式
- **Tailwind CSS** - 现代化CSS框架
- **React (CDN)** - 组件化开发
- **WebSocket** - 实时通信
- **Font Awesome** - 图标库

### 后端
- **FastAPI** - 高性能Python Web框架
- **Uvicorn** - ASGI服务器
- **WebSocket** - 双向实时通信

## 开发说明

### 自定义知识库

在 `server.py` 中的 `knowledge_base` 字典可以添加更多专业知识：

```python
knowledge_base = {
    "新主题": [
        "回答1",
        "回答2",
        "回答3"
    ]
}
```

### 对接真实Agent Service

修改 `ChatService.process_message()` 方法，替换模拟响应为真实的agent_service调用：

```python
async def process_message(self, message: str, session_id: Optional[str] = None):
    # 调用真实的agent_service
    from src.services.agent_service import AgentService
    
    agent_service = AgentService()
    response = await agent_service.chat(
        message=message,
        session_id=session_id,
        agent_id="quantum_sales_manager"
    )
    
    return response
```

### 样式定制

主要样式定义在 `chat.html` 的 `<style>` 标签中，可以修改颜色、字体、布局等。

## 故障排除

### 端口被占用

如果8000端口被占用，可以修改 `server.py` 中的端口号：

```python
uvicorn.run(app, host="0.0.0.0", port=8080)  # 改为8080端口
```

### 依赖安装失败

手动安装依赖：

```bash
pip install fastapi uvicorn
```

### 浏览器无法访问

检查防火墙设置，确保8000端口可访问。

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。