"""
Token管理和上下文窗口优化
处理LLM的上下文窗口限制，智能截断和压缩
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import tiktoken

logger = logging.getLogger(__name__)


@dataclass
class TokenBudget:
    """Token预算配置"""
    max_tokens: int
    reserved_for_response: int = 512
    buffer_percentage: float = 0.1  # 10%缓冲
    
    @property
    def available_tokens(self) -> int:
        """可用Token数量"""
        return self.max_tokens - self.reserved_for_response
    
    @property
    def safe_available_tokens(self) -> int:
        """安全可用Token数量（包含缓冲）"""
        return int(self.available_tokens * (1 - self.buffer_percentage))


class TokenManager:
    """Token管理器"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        try:
            self.encoder = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # 如果模型不支持，使用默认编码器
            self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """计算文本的Token数量"""
        return len(self.encoder.encode(text))
    
    def truncate_text(self, text: str, max_tokens: int, strategy: str = "end") -> str:
        """截断文本到指定Token数量"""
        tokens = self.encoder.encode(text)
        
        if len(tokens) <= max_tokens:
            return text
        
        if strategy == "start":
            truncated_tokens = tokens[-max_tokens:]
        elif strategy == "middle":
            # 保留开头和结尾
            start_len = max_tokens // 2
            end_len = max_tokens - start_len
            truncated_tokens = tokens[:start_len] + tokens[-end_len:]
        else:  # end strategy (default)
            truncated_tokens = tokens[:max_tokens]
        
        return self.encoder.decode(truncated_tokens)
    
    def prioritize_content(self, contents: List[str], budget: TokenBudget) -> List[str]:
        """根据优先级选择内容，确保不超过Token预算"""
        prioritized = []
        total_tokens = 0
        
        for content in contents:
            content_tokens = self.count_tokens(content)
            
            if total_tokens + content_tokens <= budget.safe_available_tokens:
                prioritized.append(content)
                total_tokens += content_tokens
            else:
                # 尝试截断当前内容
                remaining_tokens = budget.safe_available_tokens - total_tokens
                if remaining_tokens > 50:  # 至少保留50个token
                    truncated_content = self.truncate_text(content, remaining_tokens)
                    prioritized.append(truncated_content)
                    break
                else:
                    break
        
        logger.info(f"Token usage: {total_tokens}/{budget.safe_available_tokens}")
        return prioritized
    
    def compress_conversation(self, messages: List[Dict[str, str]], budget: TokenBudget) -> List[Dict[str, str]]:
        """压缩对话历史以节省Token"""
        compressed_messages = []
        total_tokens = 0
        
        # 优先保留最近的对话
        for message in reversed(messages):
            message_text = f"{message['role']}: {message['content']}"
            message_tokens = self.count_tokens(message_text)
            
            if total_tokens + message_tokens <= budget.safe_available_tokens:
                compressed_messages.insert(0, message)  # 保持顺序
                total_tokens += message_tokens
            else:
                # 对最旧的消息进行摘要
                oldest_message = compressed_messages.pop(0) if compressed_messages else None
                if oldest_message:
                    # 简单的摘要策略：截断或替换为摘要
                    summary_tokens = min(50, budget.safe_available_tokens - total_tokens)
                    if summary_tokens > 10:
                        summary = self.truncate_text(oldest_message['content'], summary_tokens)
                        compressed_messages.insert(0, {
                            'role': oldest_message['role'],
                            'content': f"[摘要] {summary}"
                        })
                        total_tokens += self.count_tokens(compressed_messages[0]['content'])
                
                # 添加当前消息
                if total_tokens + message_tokens <= budget.safe_available_tokens:
                    compressed_messages.append(message)
                    total_tokens += message_tokens
                break
        
        return compressed_messages