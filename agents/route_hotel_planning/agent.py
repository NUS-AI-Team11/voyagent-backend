"""
路线&酒店规划 Agent - 规划完整的日程和酒店安排
"""

from agents.base_agent import BaseAgent
from models.schemas import (
    Itinerary, DayItinerary, TravelProfile, SpotList, 
    DiningList, PlanningContext
)
from agents.route_hotel_planning.prompts import (
    SYSTEM_PROMPT,
    ITINERARY_CREATION_PROMPT,
    HOTEL_RECOMMENDATION_PROMPT,
    ROUTE_OPTIMIZATION_PROMPT,
    DAILY_SCHEDULE_PROMPT
)
from typing import List
from datetime import datetime, timedelta


class RouteHotelPlanningAgent(BaseAgent):
    """规划路线和酒店的 Agent"""
    
    def __init__(self):
        super().__init__(
            name="Route & Hotel Planning Agent",
            description="根据景点和餐厅推荐规划完整的日程和酒店安排"
        )
    
    def process(self, context: PlanningContext) -> PlanningContext:
        """
        处理景点和餐厅推荐，生成完整的行程和酒店安排
        
        Args:
            context: 规划上下文，需包含 TravelProfile, SpotList, DiningList
            
        Returns:
            包含 Itinerary 的上下文
        """
        try:
            if not self.validate_input(context):
                context.add_error("缺少必需的输入信息")
                return context
            
            travel_profile = context.travel_profile
            spot_list = context.spot_list
            dining_list = context.dining_list
            
            # 创建每日行程
            days = self._create_daily_itineraries(
                travel_profile,
                spot_list,
                dining_list
            )
            
            # 创建完整行程
            itinerary = Itinerary(
                location=travel_profile.destination,
                start_date=travel_profile.start_date,
                end_date=travel_profile.end_date,
                days=days,
                estimated_total_cost=sum(day.total_estimated_cost for day in days),
                cost_breakdown={
                    'transport': 0.0,
                    'accommodation': 0.0,
                    'food': 0.0,
                    'attractions': 0.0,
                },
                generated_at=datetime.now()
            )
            
            context.itinerary = itinerary
            self.log_execution(f"创建了 {len(days)} 天的行程")
            
        except Exception as e:
            context.add_error(f"行程规划失败: {str(e)}")
            self.log_execution(f"错误: {str(e)}", level="error")
        
        return context
    
    def validate_input(self, context: PlanningContext) -> bool:
        """验证必需的输入"""
        return (
            context.travel_profile is not None and
            context.spot_list is not None and
            context.dining_list is not None
        )
    
    def _create_daily_itineraries(
        self,
        travel_profile: TravelProfile,
        spot_list: SpotList,
        dining_list: DiningList
    ) -> List[DayItinerary]:
        """
        为每一天创建详细的行程安排
        
        Args:
            travel_profile: 用户旅行信息
            spot_list: 推荐景点列表
            dining_list: 推荐餐厅列表
            
        Returns:
            每日行程列表
        """
        days = []
        current_date = travel_profile.start_date
        day_number = 1
        
        # 计算旅行天数
        num_days = (travel_profile.end_date - travel_profile.start_date).days + 1
        
        while day_number <= num_days:
            day_itinerary = DayItinerary(
                day_number=day_number,
                date=current_date,
                activities=[],
                meals={},
                accommodation=None,
                total_estimated_cost=0.0,
                notes=""
            )
            
            days.append(day_itinerary)
            current_date += timedelta(days=1)
            day_number += 1
        
        return days
