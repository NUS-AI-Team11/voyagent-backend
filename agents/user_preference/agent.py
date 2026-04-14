"""
用户偏好 Agent - 收集和解析用户的旅行偏好
"""

import json
from typing import Dict, Any
from datetime import datetime, date

from agents.base_agent import BaseAgent
from models.schemas import TravelProfile, PlanningContext
from agents.user_preference.prompts import (
    SYSTEM_PROMPT,
    USER_PREFERENCE_EXTRACTION_PROMPT,
    CLARIFICATION_PROMPT,
    PROFILE_SUMMARY_PROMPT
)


class UserPreferenceAgent(BaseAgent):
    """收集用户偏好信息的 Agent"""
    
    def __init__(self):
        super().__init__(
            name="User Preference Agent",
            description="收集和解析用户的旅行偏好信息"
        )
        self.required_fields = [
            'destination', 'start_date', 'end_date',
            'budget', 'group_size', 'travel_style'
        ]
    
    def process(self, context: PlanningContext) -> PlanningContext:
        """
        处理用户输入并生成 TravelProfile
        
        Args:
            context: 规划上下文，需包含原始用户输入
            
        Returns:
            包含 TravelProfile 的上下文
        """
        try:
            # 从 context.metadata 中获取用户输入
            user_input = context.metadata.get('user_input', '')
            
            if not user_input:
                context.add_error("用户输入为空")
                return context
            
            # 提取偏好信息
            preference_data = self._extract_preferences(user_input)
            
            # 验证必需字段
            missing_fields = self._validate_required_fields(preference_data)
            if missing_fields:
                context.add_warning(f"缺少字段: {', '.join(missing_fields)}")
            
            # 创建 TravelProfile
            travel_profile = self._create_travel_profile(preference_data)
            context.travel_profile = travel_profile
            
            self.log_execution(f"成功解析用户偏好: {travel_profile.destination}")
            
        except Exception as e:
            context.add_error(f"用户偏好处理失败: {str(e)}")
            self.log_execution(f"错误: {str(e)}", level="error")
        
        return context
    
    def _extract_preferences(self, user_input: str) -> Dict[str, Any]:
        """
        从用户输入中提取偏好信息
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            提取的偏好数据字典
        """
        # 在实际实现中，这里会调用 LLM 来解析用户输入
        # 这里展示一个模拟实现
        
        preference_data = {
            'destination': self._extract_field(user_input, 'destination'),
            'start_date': self._extract_field(user_input, 'start_date'),
            'end_date': self._extract_field(user_input, 'end_date'),
            'budget': self._extract_field(user_input, 'budget'),
            'group_size': self._extract_field(user_input, 'group_size'),
            'travel_style': self._extract_field(user_input, 'travel_style'),
            'interests': self._extract_field(user_input, 'interests', default=[]),
            'dietary_restrictions': self._extract_field(user_input, 'dietary_restrictions', default=[]),
            'hotel_preference': self._extract_field(user_input, 'hotel_preference'),
            'transportation_preference': self._extract_field(user_input, 'transportation_preference'),
            'custom_notes': self._extract_field(user_input, 'custom_notes'),
        }
        
        return preference_data
    
    def _extract_field(self, text: str, field_name: str, default: Any = None) -> Any:
        """
        从文本中提取指定字段
        
        Args:
            text: 输入文本
            field_name: 字段名称
            default: 默认值
            
        Returns:
            提取的值或默认值
        """
        # 这是一个简化的实现，实际应通过 LLM
        return default
    
    def _validate_required_fields(self, preference_data: Dict[str, Any]) -> list:
        """
        验证必需字段是否存在
        
        Args:
            preference_data: 偏好数据
            
        Returns:
            缺少的字段列表
        """
        missing = []
        for field in self.required_fields:
            if not preference_data.get(field):
                missing.append(field)
        return missing
    
    def _create_travel_profile(self, preference_data: Dict[str, Any]) -> TravelProfile:
        """
        根据提取的数据创建 TravelProfile 对象
        
        Args:
            preference_data: 提取的偏好数据
            
        Returns:
            TravelProfile 对象
        """
        return TravelProfile(
            destination=preference_data.get('destination', ''),
            start_date=preference_data.get('start_date') or date.today(),
            end_date=preference_data.get('end_date') or date.today(),
            budget=float(preference_data.get('budget', 0)),
            group_size=int(preference_data.get('group_size', 1)),
            travel_style=preference_data.get('travel_style', ''),
            interests=preference_data.get('interests', []),
            dietary_restrictions=preference_data.get('dietary_restrictions', []),
            hotel_preference=preference_data.get('hotel_preference'),
            transportation_preference=preference_data.get('transportation_preference'),
            custom_notes=preference_data.get('custom_notes'),
        )
