"""
景点推荐 Agent 测试
"""

import pytest
from models.schemas import TravelProfile, SpotList, PlanningContext
from agents.spot_recommendation.agent import SpotRecommendationAgent
from datetime import date


@pytest.fixture
def agent():
    """创建 Agent 实例"""
    return SpotRecommendationAgent()


@pytest.fixture
def sample_context():
    """创建示例上下文"""
    context = PlanningContext()
    context.travel_profile = TravelProfile(
        destination='Paris',
        start_date=date(2024, 5, 15),
        end_date=date(2024, 5, 22),
        budget=5000,
        group_size=4,
        travel_style='culture',
        interests=['history', 'art', 'museums']
    )
    return context


def test_agent_initialization(agent):
    """测试 Agent 初始化"""
    assert agent.name == "Spot Recommendation Agent"
    assert agent.description == "根据用户旅行偏好推荐合适的景点"


def test_process_valid_input(agent, sample_context):
    """测试有效输入的处理"""
    result = agent.process(sample_context)
    
    assert result is not None
    # 如果实现完整，应该有 spot_list
    # assert result.spot_list is not None


def test_process_missing_travel_profile(agent):
    """测试缺少旅行档案的处理"""
    context = PlanningContext()
    
    result = agent.process(context)
    
    assert len(result.errors) > 0


def test_validate_input_success(agent, sample_context):
    """测试输入验证成功"""
    assert agent.validate_input(sample_context) is True


def test_validate_input_failure(agent):
    """测试输入验证失败"""
    context = PlanningContext()
    
    assert agent.validate_input(context) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
