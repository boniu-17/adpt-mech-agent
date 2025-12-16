"""
链路追踪工具
提供Agent系统的完整调用链路可视化追踪
"""

import logging
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
import uuid

logger = logging.getLogger(__name__)


class TraceType(Enum):
    """追踪类型枚举"""
    AGENT_THINKING = "agent_thinking"
    TOOL_CALL = "tool_call" 
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    LLM_CALL = "llm_call"
    MESSAGE_PROCESSING = "message_processing"


@dataclass
class TraceSpan:
    """追踪跨度"""
    span_id: str
    trace_id: str
    type: TraceType
    name: str
    start_time: float
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
    
    @property
    def duration(self) -> Optional[float]:
        """计算持续时间"""
        if self.end_time:
            return self.end_time - self.start_time
        return None


class Tracer:
    """链路追踪器"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.current_trace_id: Optional[str] = None
        self.spans: List[TraceSpan] = []
        
    def start_trace(self, trace_id: Optional[str] = None) -> str:
        """开始新的追踪链路"""
        if not self.enabled:
            return ""
            
        self.current_trace_id = trace_id or str(uuid.uuid4())
        logger.info(f"Starting trace: {self.current_trace_id}")
        return self.current_trace_id
        
    def end_trace(self) -> None:
        """结束当前追踪链路"""
        if not self.enabled:
            return
            
        logger.info(f"Ending trace: {self.current_trace_id}")
        self.current_trace_id = None
        
    @contextmanager
    def span(self, span_type: TraceType, name: str, **metadata):
        """创建追踪跨度的上下文管理器"""
        if not self.enabled or not self.current_trace_id:
            yield
            return
            
        span_id = str(uuid.uuid4())
        span = TraceSpan(
            span_id=span_id,
            trace_id=self.current_trace_id,
            type=span_type,
            name=name,
            start_time=time.time(),
            metadata=metadata
        )
        
        self.spans.append(span)
        
        try:
            yield span
        except Exception as e:
            span.error = str(e)
            raise
        finally:
            span.end_time = time.time()
            logger.debug(f"Span completed: {name} ({span.duration:.3f}s)")
            
    def get_spans_by_trace(self, trace_id: str) -> List[TraceSpan]:
        """获取指定追踪ID的所有跨度"""
        return [span for span in self.spans if span.trace_id == trace_id]
        
    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """获取追踪摘要"""
        spans = self.get_spans_by_trace(trace_id)
        completed_spans = [span for span in spans if span.end_time]
        
        return {
            "trace_id": trace_id,
            "total_spans": len(spans),
            "completed_spans": len(completed_spans),
            "total_duration": sum(span.duration for span in completed_spans if span.duration),
            "spans_by_type": {span_type.value: len([s for s in spans if s.type == span_type]) 
                             for span_type in TraceType},
            "errors": [span for span in spans if span.error]
        }
        
    def export_trace_data(self, trace_id: str) -> Dict[str, Any]:
        """导出追踪数据用于可视化"""
        spans = self.get_spans_by_trace(trace_id)
        
        return {
            "trace_id": trace_id,
            "spans": [
                {
                    "span_id": span.span_id,
                    "type": span.type.value,
                    "name": span.name,
                    "start_time": span.start_time,
                    "end_time": span.end_time,
                    "duration": span.duration,
                    "metadata": span.metadata,
                    "tags": span.tags,
                    "error": span.error
                }
                for span in spans
            ],
            "summary": self.get_trace_summary(trace_id)
        }


# 全局追踪器实例
global_tracer = Tracer(enabled=True)


def enable_tracing():
    """启用追踪"""
    global_tracer.enabled = True
    

def disable_tracing():
    """禁用追踪"""
    global_tracer.enabled = False
    

def get_tracer() -> Tracer:
    """获取全局追踪器"""
    return global_tracer