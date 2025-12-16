class ChatApp {
    constructor() {
        this.currentSessionId = null;
        this.isStreaming = false;
        this.conversationHistory = [];
        this.currentAgentId = 'quantum_sales_manager';
        
        this.initializeElements();
        this.bindEvents();
        this.loadAgentsAndTools();
        this.startDemoConversation();
    }

    initializeElements() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.sessionIdElement = document.getElementById('sessionId');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.agentCardsContainer = document.getElementById('agentCards');
        this.toolListContainer = document.getElementById('toolList');
        this.userAvatar = document.getElementById('userAvatar');
        this.userMenu = document.getElementById('userMenu');
        this.exportBtn = document.getElementById('exportBtn');
    }

    bindEvents() {
        // 发送消息事件
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // 输入框事件
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 用户头像点击事件
        this.userAvatar.addEventListener('click', (e) => {
            e.stopPropagation();
            this.userMenu.classList.toggle('hidden');
        });

        // 点击其他地方关闭菜单
        document.addEventListener('click', () => {
            this.userMenu.classList.add('hidden');
        });

        // 导出对话事件
        this.exportBtn.addEventListener('click', () => this.exportConversation());
    }

    loadAgentsAndTools() {
        // 加载智能体角色卡
        const agents = [
            {
                id: 'quantum_sales_manager',
                name: '量子销售经理',
                description: '企业级量子计算解决方案销售专家',
                avatar: 'https://via.placeholder.com/60x60?text=QS',
                isActive: true
            }
        ];

        this.agentCardsContainer.innerHTML = agents.map(agent => `
            <div class="agent-card p-3 rounded-lg border cursor-pointer transition-colors ${agent.isActive ? 'active-sidebar-item' : 'sidebar-item hover:bg-gray-50'}" 
                 data-agent-id="${agent.id}">
                <div class="flex items-center space-x-3">
                    <img src="${agent.avatar}" alt="${agent.name}" class="w-10 h-10 rounded-full">
                    <div>
                        <h3 class="font-medium text-sm">${agent.name}</h3>
                        <p class="text-xs text-gray-500 truncate">${agent.description}</p>
                    </div>
                </div>
            </div>
        `).join('');

        // 加载工具列表
        const tools = [
            { id: 'knowledge_base', name: '知识库查询', icon: 'fa-book', enabled: true },
            { id: 'calculator', name: '计算器', icon: 'fa-calculator', enabled: true },
            { id: 'search', name: '网络搜索', icon: 'fa-search', enabled: false }
        ];

        this.toolListContainer.innerHTML = tools.map(tool => `
            <div class="tool-item flex items-center justify-between p-2 rounded ${tool.enabled ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-400'}">
                <div class="flex items-center space-x-2">
                    <i class="fas ${tool.icon} text-sm"></i>
                    <span class="text-sm">${tool.name}</span>
                </div>
                <span class="text-xs px-1 rounded">${tool.enabled ? '启用' : '禁用'}</span>
            </div>
        `).join('');

        // 绑定智能体切换事件
        document.querySelectorAll('.agent-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const agentId = e.currentTarget.dataset.agentId;
                this.switchAgent(agentId);
            });
        });
    }

    async startDemoConversation() {
        // 生成会话ID
        this.currentSessionId = 'demo_' + Date.now();
        this.sessionIdElement.textContent = this.currentSessionId.substring(0, 8) + '...';

        // 预设演示对话
        const demoMessages = [
            { role: 'assistant', content: '您好！我是量子销售经理，专门为企业提供量子计算解决方案。请问您对量子计算有什么具体需求吗？' },
            { role: 'user', content: '我们公司主要做金融风控，想了解量子计算能带来什么优势？' },
            { role: 'assistant', content: '量子计算在金融风控领域有显著优势：\n\n1. **风险建模优化**：量子算法可以处理传统计算机难以解决的复杂风险模型\n2. **实时风险评估**：量子并行计算能力可大幅提升风险评估速度\n3. **投资组合优化**：解决大规模投资组合优化的NP难问题\n4. **欺诈检测**：量子机器学习可提高欺诈模式识别准确率' },
            { role: 'user', content: '实施这样的方案需要多长时间？成本如何？' },
            { role: 'assistant', content: '实施时间通常为3-6个月，具体取决于您的系统复杂度：\n\n**时间安排：**\n• 第1个月：需求分析和方案设计\n• 第2-3个月：系统集成和测试\n• 第4-6个月：部署和优化\n\n**成本范围：**\n• 基础方案：50-100万元\n• 标准方案：100-300万元\n• 高级方案：300万元以上\n\n我们会根据您的具体需求提供定制化报价。' }
        ];

        // 逐步显示演示对话
        for (let i = 0; i < demoMessages.length; i++) {
            await this.displayMessageWithDelay(demoMessages[i], i * 1500);
        }

        // 演示结束后显示提示
        setTimeout(() => {
            this.addSystemMessage('演示对话已完成，现在您可以继续提问了！');
        }, demoMessages.length * 1500 + 1000);
    }

    displayMessageWithDelay(message, delay) {
        return new Promise(resolve => {
            setTimeout(() => {
                this.addMessage(message.role, message.content);
                resolve();
            }, delay);
        });
    }

    addSystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'text-center py-2';
        messageDiv.innerHTML = `
            <div class="inline-block bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-2">
                <span class="text-yellow-700 text-sm">${content}</span>
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isStreaming) return;

        // 添加用户消息
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.sendButton.disabled = true;
        this.isStreaming = true;
        this.typingIndicator.classList.remove('hidden');

        try {
            // 调用流式API
            await this.sendStreamMessage(message);
        } catch (error) {
            console.error('发送消息失败:', error);
            this.addMessage('assistant', '抱歉，处理消息时出现了错误。请稍后重试。');
        } finally {
            this.isStreaming = false;
            this.sendButton.disabled = false;
            this.typingIndicator.classList.add('hidden');
        }
    }

    async sendStreamMessage(message) {
        const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: this.currentSessionId,
                agent_id: this.currentAgentId,
                stream: true
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessageDiv = null;
        let fullResponse = '';

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            
                            if (data.type === 'chunk') {
                                if (!assistantMessageDiv) {
                                    assistantMessageDiv = this.createMessageElement('assistant', '');
                                    this.chatMessages.appendChild(assistantMessageDiv);
                                }
                                
                                fullResponse += data.content;
                                assistantMessageDiv.querySelector('.message-content').textContent = fullResponse;
                                this.scrollToBottom();
                            }
                        } catch (e) {
                            console.warn('解析流数据失败:', e);
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }

        // 保存到对话历史
        this.conversationHistory.push({
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
        });
        
        this.conversationHistory.push({
            role: 'assistant',
            content: fullResponse,
            timestamp: new Date().toISOString()
        });
    }

    addMessage(role, content) {
        const messageDiv = this.createMessageElement(role, content);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        // 保存到对话历史
        this.conversationHistory.push({
            role: role,
            content: content,
            timestamp: new Date().toISOString()
        });
    }

    createMessageElement(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
        
        const bubbleClass = role === 'user' ? 
            'user-message message-bubble' : 
            'assistant-message message-bubble';
        
        messageDiv.innerHTML = `
            <div class="${bubbleClass} rounded-2xl px-4 py-3 shadow-sm">
                <div class="message-content">${this.formatMessage(content)}</div>
                <div class="text-xs opacity-70 mt-1 text-right">${new Date().toLocaleTimeString()}</div>
            </div>
        `;
        
        return messageDiv;
    }

    formatMessage(content) {
        // 简单的Markdown格式支持
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
            .replace(/\n/g, '<br>');
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    switchAgent(agentId) {
        this.currentAgentId = agentId;
        
        // 更新活跃状态
        document.querySelectorAll('.agent-card').forEach(card => {
            if (card.dataset.agentId === agentId) {
                card.classList.add('active-sidebar-item');
                card.classList.remove('sidebar-item');
            } else {
                card.classList.remove('active-sidebar-item');
                card.classList.add('sidebar-item');
            }
        });

        this.addSystemMessage(`已切换到智能体: ${this.getAgentName(agentId)}`);
    }

    getAgentName(agentId) {
        const agents = {
            'quantum_sales_manager': '量子销售经理'
        };
        return agents[agentId] || agentId;
    }

    exportConversation() {
        if (this.conversationHistory.length === 0) {
            alert('没有对话内容可导出');
            return;
        }

        const exportData = {
            sessionId: this.currentSessionId,
            agentId: this.currentAgentId,
            exportTime: new Date().toISOString(),
            conversation: this.conversationHistory
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
            type: 'application/json' 
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversation_${this.currentSessionId}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.addSystemMessage('对话已导出为JSON文件');
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});