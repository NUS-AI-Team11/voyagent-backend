"""
路线&酒店规划 Agent 测试
"""

import pytest
from models.schemas import TravelProfile, SpotList, DiningList, PlanningContext
from agents.route_hotel_planning.agent import RouteHotelPlanningAgent
from datetime import date


@pytest.fixture
def agent():
    """创建 Agent 实例"""
    return RouteHotelPlanningAgent()


@pytest.fixture
def sample_context():
    """创建示例上下文"""
    context = PlanningContext()
    context.travel_profile = TravelProfile(
        destination='Barcelona',
        start_date=date(2024, 7, 1),
        end_date=date(2024, 7, 5),
        budget=6000,
        group_size=3,
        travel_style='mix'
    )
    context.spot_list = SpotList()
    context.dining_list = DiningList()
    return context


def test_agent_initialization(agent):
    """测试 Agent 初始化"""
    assert agent.name == "Route & Hotel Planning Agent"


def test_process_valid_input(agent, sample_context):
    """测试有效输入的处理"""
    result = agent.process(sample_context)
    
    assert result is not None


def test_validate_input_success(agent, sample_context):
    """测试输入验证成功"""
    assert agent.validate_input(sample_context) is True


def test_validate_input_missing_spot_list(agent, sample_context):
    """测试缺少景点列表的输入验证"""
    sample_context.spot_list = None
    
    assert agent.validate_input(sample_context) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
