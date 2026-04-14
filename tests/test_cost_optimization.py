"""
成本优化 Agent 测试
"""

import pytest
from models.schemas import TravelProfile, Itinerary, DayItinerary, PlanningContext
from agents.cost_optimization.agent import CostOptimizationAgent
from datetime import date


@pytest.fixture
def agent():
    """创建 Agent 实例"""
    return CostOptimizationAgent()


@pytest.fixture
def sample_context():
    """创建示例上下文"""
    context = PlanningContext()
    context.travel_profile = TravelProfile(
        destination='Rome',
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 7),
        budget=5000,
        group_size=2,
        travel_style='cultural'
    )
    context.itinerary = Itinerary(
        location='Rome',
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 7),
        days=[]
    )
    return context


def test_agent_initialization(agent):
    """测试 Agent 初始化"""
    assert agent.name == "Cost Optimization Agent"


def test_process_valid_input(agent, sample_context):
    """测试有效输入的处理"""
    result = agent.process(sample_context)
    
    assert result is not None


def test_validate_input_success(agent, sample_context):
    """测试输入验证成功"""
    assert agent.validate_input(sample_context) is True


def test_validate_input_missing_itinerary(agent, sample_context):
    """测试缺少行程的输入验证"""
    sample_context.itinerary = None
    
    assert agent.validate_input(sample_context) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
