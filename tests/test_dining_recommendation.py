"""
餐饮推荐 Agent 测试
"""

import pytest
from models.schemas import TravelProfile, DiningList, PlanningContext
from agents.dining_recommendation.agent import DiningRecommendationAgent
from datetime import date


@pytest.fixture
def agent():
    """创建 Agent 实例"""
    return DiningRecommendationAgent()


@pytest.fixture
def sample_context():
    """创建示例上下文"""
    context = PlanningContext()
    context.travel_profile = TravelProfile(
        destination='Tokyo',
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 7),
        budget=4000,
        group_size=2,
        travel_style='food',
        dietary_restrictions=['vegetarian']
    )
    return context


def test_agent_initialization(agent):
    """测试 Agent 初始化"""
    assert agent.name == "Dining Recommendation Agent"


def test_process_valid_input(agent, sample_context):
    """测试有效输入的处理"""
    result = agent.process(sample_context)
    
    assert result is not None


def test_process_missing_travel_profile(agent):
    """测试缺少旅行档案的处理"""
    context = PlanningContext()
    
    result = agent.process(context)
    
    assert len(result.errors) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
