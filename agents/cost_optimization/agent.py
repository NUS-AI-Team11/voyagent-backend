"""
成本优化 Agent - 分析和优化行程成本
"""

from agents.base_agent import BaseAgent
from models.schemas import (
    Itinerary, FinalHandbook, CostBreakdown, PlanningContext,
    OptimizationRecommendation
)
from agents.cost_optimization.prompts import (
    SYSTEM_PROMPT,
    COST_ANALYSIS_PROMPT,
    OPTIMIZATION_RECOMMENDATION_PROMPT,
    BUDGET_ALLOCATION_PROMPT,
    ALTERNATIVE_ITINERARY_PROMPT,
    FINAL_HANDBOOK_PROMPT
)
from datetime import datetime


class CostOptimizationAgent(BaseAgent):
    """分析和优化成本的 Agent"""
    
    def __init__(self):
        super().__init__(
            name="Cost Optimization Agent",
            description="分析行程成本并提供优化建议以确保符合预算"
        )
    
    def process(self, context: PlanningContext) -> PlanningContext:
        """
        分析行程成本并生成最终手册
        
        Args:
            context: 规划上下文，需包含 Itinerary
            
        Returns:
            包含 FinalHandbook 的上下文
        """
        try:
            if not self.validate_input(context):
                context.add_error("缺少必需的输入信息")
                return context
            
            itinerary = context.itinerary
            travel_profile = context.travel_profile
            
            # 分析成本
            cost_breakdown = self._analyze_costs(itinerary)
            
            # 生成优化建议
            recommendations = self._generate_recommendations(
                cost_breakdown,
                travel_profile.budget,
                itinerary
            )
            
            # 检查是否超预算
            if cost_breakdown.total > travel_profile.budget:
                context.add_warning(
                    f"总成本 {cost_breakdown.total} 超过预算 {travel_profile.budget}"
                )
            
            # 创建最终手册
            final_handbook = FinalHandbook(
                title=f"{travel_profile.destination} 旅行手册",
                destination=travel_profile.destination,
                itinerary=itinerary,
                cost_breakdown=cost_breakdown,
                budget=travel_profile.budget,
                budget_remaining=travel_profile.budget - cost_breakdown.total,
                optimization_recommendations=recommendations,
                generated_at=datetime.now()
            )
            
            context.final_handbook = final_handbook
            self.log_execution(f"完成成本分析，总成本: {cost_breakdown.total}")
            
        except Exception as e:
            context.add_error(f"成本优化失败: {str(e)}")
            self.log_execution(f"错误: {str(e)}", level="error")
        
        return context
    
    def validate_input(self, context: PlanningContext) -> bool:
        """验证必需的输入"""
        return (
            context.itinerary is not None and
            context.travel_profile is not None
        )
    
    def _analyze_costs(self, itinerary: Itinerary) -> CostBreakdown:
        """
        分析行程的成本结构
        
        Args:
            itinerary: 完整行程
            
        Returns:
            成本明细
        """
        cost_breakdown = CostBreakdown()
        
        # 从每日行程中累计成本
        for day in itinerary.days:
            # 这里会从 day 的活动中提取成本信息
            pass
        
        return cost_breakdown
    
    def _generate_recommendations(
        self,
        cost_breakdown: CostBreakdown,
        budget: float,
        itinerary: Itinerary
    ) -> list:
        """
        根据成本分析生成优化建议
        
        Args:
            cost_breakdown: 成本明细
            budget: 用户预算
            itinerary: 完整行程
            
        Returns:
            优化建议列表
        """
        recommendations = []
        
        overage = cost_breakdown.total - budget
        
        if overage > 0:
            # 如果超预算，生成节省建议
            recommend = OptimizationRecommendation(
                category="accommodation",
                suggestion="考虑降级酒店等级",
                potential_savings=overage * 0.3,
                confidence=0.7
            )
            recommendations.append(recommend)
        
        return recommendations
