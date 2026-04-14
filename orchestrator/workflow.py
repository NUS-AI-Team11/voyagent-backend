"""
Agent 编排器 - 模型的主要业务逻辑
"""

import logging
from typing import Dict, Any

from models.schemas import PlanningContext
from agents.user_preference.agent import UserPreferenceAgent
from agents.spot_recommendation.agent import SpotRecommendationAgent
from agents.dining_recommendation.agent import DiningRecommendationAgent
from agents.route_hotel_planning.agent import RouteHotelPlanningAgent
from agents.cost_optimization.agent import CostOptimizationAgent


logger = logging.getLogger(__name__)


class TravelPlanningWorkflow:
    """完整的旅行规划工作流"""
    
    def __init__(self):
        """初始化所有 Agent"""
        self.user_preference_agent = UserPreferenceAgent()
        self.spot_recommendation_agent = SpotRecommendationAgent()
        self.dining_recommendation_agent = DiningRecommendationAgent()
        self.route_hotel_planning_agent = RouteHotelPlanningAgent()
        self.cost_optimization_agent = CostOptimizationAgent()
        
        self.agents = [
            self.user_preference_agent,
            self.spot_recommendation_agent,
            self.dining_recommendation_agent,
            self.route_hotel_planning_agent,
            self.cost_optimization_agent,
        ]
        
        logger.info("旅行规划工作流已初始化，共有 5 个 Agent")
    
    def run(self, user_input: str) -> PlanningContext:
        """
        执行完整的旅行规划工作流
        
        Args:
            user_input: 用户的原始输入
            
        Returns:
            包含完整规划结果的 PlanningContext
        """
        # 创建初始上下文，包含用户输入
        context = PlanningContext()
        context.metadata['user_input'] = user_input
        
        logger.info("=" * 50)
        logger.info("开始执行旅行规划工作流")
        logger.info("=" * 50)
        
        try:
            # 步骤 1: 用户偏好
            logger.info("\n[步骤 1] 执行 User Preference Agent...")
            context = self.user_preference_agent.process(context)
            if not context.travel_profile:
                logger.error("用户偏好解析失败，无法继续")
                return context
            logger.info(f"✓ 完成: {context.travel_profile.destination}")
            
            # 步骤 2: 景点推荐
            logger.info("\n[步骤 2] 执行 Spot Recommendation Agent...")
            context = self.spot_recommendation_agent.process(context)
            if context.spot_list:
                logger.info(f"✓ 完成: 推荐 {context.spot_list.total_count} 个景点")
            
            # 步骤 3: 餐饮推荐
            logger.info("\n[步骤 3] 执行 Dining Recommendation Agent...")
            context = self.dining_recommendation_agent.process(context)
            if context.dining_list:
                logger.info(f"✓ 完成: 推荐 {context.dining_list.total_count} 家餐厅")
            
            # 步骤 4: 路线和酒店规划
            logger.info("\n[步骤 4] 执行 Route & Hotel Planning Agent...")
            context = self.route_hotel_planning_agent.process(context)
            if context.itinerary:
                logger.info(f"✓ 完成: 生成 {len(context.itinerary.days)} 天的行程")
            
            # 步骤 5: 成本优化
            logger.info("\n[步骤 5] 执行 Cost Optimization Agent...")
            context = self.cost_optimization_agent.process(context)
            if context.final_handbook:
                logger.info(f"✓ 完成: 生成最终手册")
            
            # 输出最终结果
            self._print_summary(context)
            
        except Exception as e:
            context.add_error(f"工作流执行失败: {str(e)}")
            logger.error(f"工作流错误: {str(e)}", exc_info=True)
        
        logger.info("\n" + "=" * 50)
        logger.info("旅行规划工作流执行完成")
        logger.info("=" * 50)
        
        return context
    
    def _print_summary(self, context: PlanningContext) -> None:
        """打印执行摘要"""
        print("\n" + "=" * 60)
        print("📋 旅行规划执行摘要")
        print("=" * 60)
        
        if context.errors:
            print("\n❌ 错误:")
            for error in context.errors:
                print(f"  - {error}")
        
        if context.warnings:
            print("\n⚠️  警告:")
            for warning in context.warnings:
                print(f"  - {warning}")
        
        if context.final_handbook:
            handbook = context.final_handbook
            print(f"\n✅ 旅行手册: {handbook.title}")
            print(f"   - 目的地: {handbook.destination}")
            print(f"   - 预算: ${handbook.budget}")
            print(f"   - 总成本: ${handbook.cost_breakdown.total:.2f}")
            print(f"   - 剩余预算: ${handbook.budget_remaining:.2f}")
            
            if handbook.optimization_recommendations:
                print(f"\n💡 优化建议 ({len(handbook.optimization_recommendations)} 个):")
                for rec in handbook.optimization_recommendations[:3]:
                    print(f"   - {rec.category}: {rec.suggestion}")
                    print(f"     预计节省: ${rec.potential_savings:.2f}")
        
        print("\n" + "=" * 60 + "\n")
    
    def get_agent_info(self) -> Dict[str, str]:
        """获取所有 Agent 的信息"""
        return {agent.name: agent.description for agent in self.agents}


def main():
    """主函数示例"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建工作流
    workflow = TravelPlanningWorkflow()
    
    # 示例用户输入
    user_input = """
    我想要计划一次去巴黎的 5 天旅行。
    出发日期是 2024 年 6 月 15 日，返回日期是 6 月 20 日。
    我们有 4 个人一起去，总预算是 $4000。
    我们喜欢探索历史文化遗迹，也对美食很感兴趣。
    我们都吃素食。
    希望住在舒适但不过度豪华的酒店。
    """
    
    # 执行工作流
    context = workflow.run(user_input)
    
    # 返回最终结果
    return context


if __name__ == "__main__":
    main()
