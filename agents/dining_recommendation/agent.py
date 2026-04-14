"""
餐饮推荐 Agent - 推荐合适的餐厅和餐饮方案
"""

from agents.base_agent import BaseAgent
from models.schemas import DiningList, Restaurant, TravelProfile, PlanningContext
from agents.dining_recommendation.prompts import (
    SYSTEM_PROMPT,
    DINING_RECOMMENDATION_PROMPT,
    MEAL_PLAN_PROMPT,
    BUDGET_DINING_PROMPT
)
from typing import List
from datetime import datetime


class DiningRecommendationAgent(BaseAgent):
    """根据用户偏好推荐餐饮的 Agent"""
    
    def __init__(self):
        super().__init__(
            name="Dining Recommendation Agent",
            description="根据用户饮食偏好和预算推荐合适的餐厅和餐饮方案"
        )
    
    def process(self, context: PlanningContext) -> PlanningContext:
        """
        处理用户偏好并生成餐饮推荐列表
        
        Args:
            context: 规划上下文，需包含 TravelProfile
            
        Returns:
            包含 DiningList 的上下文
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
            
            # 生成餐饮推荐列表
            restaurants = self._recommend_restaurants(travel_profile)
            
            # 创建 DiningList
            dining_list = DiningList(
                restaurants=restaurants,
                meal_type="all",
                filter_criteria={
                    'destination': travel_profile.destination,
                    'dietary_restrictions': travel_profile.dietary_restrictions,
                    'budget': travel_profile.budget
                },
                total_count=len(restaurants),
                generated_at=datetime.now()
            )
            
            context.dining_list = dining_list
            self.log_execution(f"推荐了 {len(restaurants)} 家餐厅")
            
        except Exception as e:
            context.add_error(f"餐饮推荐失败: {str(e)}")
            self.log_execution(f"错误: {str(e)}", level="error")
        
        return context
    
    def validate_input(self, context: PlanningContext) -> bool:
        """验证必需的输入"""
        return context.travel_profile is not None
    
    def _recommend_restaurants(self, travel_profile: TravelProfile) -> List[Restaurant]:
        """
        根据用户偏好生成餐厅推荐列表
        
        Args:
            travel_profile: 用户旅行信息
            
        Returns:
            推荐的餐厅列表
        """
        # 这里实现餐饮推荐的主要逻辑
        # 在实际实现中，会调用 LLM 或数据库查询
        
        restaurants = []
        
        # 模拟推荐结果
        # 实际实现时会替换为真实的推荐逻辑
        
        return restaurants
