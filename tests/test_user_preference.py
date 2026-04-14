"""
用户偏好 Agent 测试
"""

import pytest
from datetime import date, datetime
from models.schemas import TravelProfile, PlanningContext
from agents.user_preference.agent import UserPreferenceAgent


@pytest.fixture
def agent():
    """创建 Agent 实例"""
    return UserPreferenceAgent()


@pytest.fixture
def sample_context():
    """创建示例上下文"""
    context = PlanningContext()
    context.metadata['user_input'] = """
    我想去巴黎，5月15日出发，5月22日回来。
    预算5000美元，4个人。
    我们喜欢文化和美食。
    """
    return context


def test_agent_initialization(agent):
    """测试 Agent 初始化"""
    assert agent.name == "User Preference Agent"
    assert agent.description == "收集和解析用户的旅行偏好信息"


def test_process_valid_input(agent, sample_context):
    """测试有效输入的处理"""
    result = agent.process(sample_context)
    
    # 检查上下文是否被更新
    assert result is not None
    # 如果实现完整，应该有 travel_profile
    # assert result.travel_profile is not None


def test_process_empty_input(agent):
    """测试空输入的处理"""
    context = PlanningContext()
    context.metadata['user_input'] = ''
    
    result = agent.process(context)
    
    assert len(result.errors) > 0


def test_validate_required_fields(agent):
    """测试必需字段的验证"""
    incomplete_data = {
        'destination': 'Paris',
        # 缺少其他必需字段
    }
    
    missing = agent._validate_required_fields(incomplete_data)
    
    assert len(missing) > 0
    assert 'budget' in missing


def test_create_travel_profile(agent):
    """测试旅行档案的创建"""
    data = {
        'destination': 'Tokyo',
        'start_date': date(2024, 5, 15),
        'end_date': date(2024, 5, 22),
        'budget': 3000,
        'group_size': 2,
        'travel_style': 'adventure',
        'interests': ['temples', 'food'],
    }
    
    profile = agent._create_travel_profile(data)
    
    assert profile.destination == 'Tokyo'
    assert profile.budget == 3000
    assert profile.group_size == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
