"""
景点推荐 Agent - 根据用户偏好推荐景点
"""

from agents.base_agent import BaseAgent
from models.schemas import SpotList, Spot, TravelProfile, PlanningContext
from agents.spot_recommendation.prompts import (
    SYSTEM_PROMPT,
    SPOT_RECOMMENDATION_PROMPT,
    SPOT_FILTERING_PROMPT,
    SPOT_RANKING_PROMPT
)
from typing import List
from datetime import datetime


class SpotRecommendationAgent(BaseAgent):
    """根据用户偏好推荐景点的 Agent"""
    
    def __init__(self):
        super().__init__(
            name="Spot Recommendation Agent",
            description="根据用户旅行偏好推荐合适的景点"
        )
    
    def process(self, context: PlanningContext) -> PlanningContext:
        """
        处理用户偏好并生成景点推荐列表
        
        Args:
            context: 规划上下文，需包含 TravelProfile
            
        Returns:
            包含 SpotList 的上下文
        """
        try:
            if not context.travel_profile:
                context.add_error("缺少旅行偏好信息")
                return context
            
            # 验证输入
            if not self.validate_input(context):
                context.add_error("输入验证失败")
                return context
            
            travel_profile = context.travel_profile
            
            # 生成景点推荐列表
            spots = self._recommend_spots(travel_profile)
            
            # 创建 SpotList
            spot_list = SpotList(
                spots=spots,
                filter_criteria={
                    'destination': travel_profile.destination,
                    'travel_style': travel_profile.travel_style,
                    'interests': travel_profile.interests
                },
                total_count=len(spots),
                generated_at=datetime.now()
            )
            
            context.spot_list = spot_list
            self.log_execution(f"推荐了 {len(spots)} 个景点")
            
        except Exception as e:
            context.add_error(f"景点推荐失败: {str(e)}")
            self.log_execution(f"错误: {str(e)}", level="error")
        
        return context
    
    def validate_input(self, context: PlanningContext) -> bool:
        """验证必需的输入"""
        return context.travel_profile is not None
    
    def _recommend_spots(self, travel_profile: TravelProfile) -> List[Spot]:
        """
        根据用户偏好生成景点推荐列表
        
        Args:
            travel_profile: 用户旅行信息
            
        Returns:
            推荐的景点列表
        """
        # 这里实现景点推荐的主要逻辑
        # 在实际实现中，会调用 LLM 或数据库查询
        
        spots = []
        
        # 模拟推荐结果
        # 实际实现时会替换为真实的推荐逻辑
        
        return spots
