"""
Agent 抽象基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from datetime import datetime

from models.schemas import PlanningContext


class BaseAgent(ABC):
    """所有 Agent 的抽象基类"""
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化 Agent
        
        Args:
            name: Agent 名称
            description: Agent 描述
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(self.__class__.__name__)
        self.created_at = datetime.now()
    
    @abstractmethod
    def process(self, context: PlanningContext) -> PlanningContext:
        """
        处理规划上下文的主方法
        
        Args:
            context: 共享的规划上下文
            
        Returns:
            更新后的规划上下文
        """
        pass
    
    def validate_input(self, context: PlanningContext) -> bool:
        """
        验证输入数据的有效性
        
        Args:
            context: 规划上下文
            
        Returns:
            是否有效
        """
        return True
    
    def log_execution(self, message: str, level: str = "info") -> None:
        """
        记录执行日志
        
        Args:
            message: 日志信息
            level: 日志级别
        """
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(f"[{self.name}] {message}")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
