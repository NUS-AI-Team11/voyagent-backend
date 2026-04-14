"""
共享数据模型 - 所有 Agent 依赖的 Schema 定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, date


@dataclass
class TravelProfile:
    """用户旅行偏好信息"""
    destination: str                    # 目的地
    start_date: date                   # 出发日期
    end_date: date                     # 返回日期
    budget: float                      # 总预算
    group_size: int                    # 人数
    travel_style: str                  # 旅行风格（冒险/放松/文化/购物/美食等）
    interests: List[str] = field(default_factory=list)  # 兴趣爱好
    dietary_restrictions: List[str] = field(default_factory=list)  # 饮食限制
    hotel_preference: Optional[str] = None  # 酒店偏好
    transportation_preference: Optional[str] = None  # 交通偏好
    custom_notes: Optional[str] = None  # 其他备注
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Spot:
    """景点信息"""
    name: str                          # 景点名称
    description: str                   # 景点描述
    location: str                      # 位置
    category: str                      # 类别（历史/自然/艺术等）
    opening_hours: Optional[str] = None  # 开放时间
    entrance_fee: Optional[float] = None  # 门票价格
    rating: float = 0.0               # 评分
    duration_hours: float = 2.0        # 建议游览时间（小时）
    best_season: Optional[str] = None  # 最佳游览季节
    accessibility_notes: Optional[str] = None  # 无障碍信息


@dataclass
class SpotList:
    """景点推荐列表"""
    spots: List[Spot] = field(default_factory=list)
    filter_criteria: Dict[str, Any] = field(default_factory=dict)  # 过滤条件
    total_count: int = 0
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Restaurant:
    """餐厅信息"""
    name: str                          # 餐厅名称
    cuisine_type: str                  # 菜系
    location: str                      # 地址
    price_range: str                   # 价格区间（$/$$/$$$/$$$$）
    rating: float = 0.0               # 评分
    average_cost_per_person: Optional[float] = None  # 人均消费
    opening_hours: Optional[str] = None  # 营业时间
    reservations_needed: bool = False  # 是否需要预订
    accessibility_notes: Optional[str] = None  # 特殊需求（过敏等）


@dataclass
class DiningList:
    """餐饮推荐列表"""
    restaurants: List[Restaurant] = field(default_factory=list)
    meal_type: str = "all"  # 餐类型（breakfast/lunch/dinner/all）
    filter_criteria: Dict[str, Any] = field(default_factory=dict)
    total_count: int = 0
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DayItinerary:
    """单日行程"""
    day_number: int                    # 第几天
    date: date                         # 日期
    activities: List[Dict[str, Any]] = field(default_factory=list)  # [{"time": "09:00", "activity": "游览xxx", "duration": 2, "spot": Spot}]
    meals: Dict[str, str] = field(default_factory=dict)  # {"breakfast": "xxx", "lunch": "xxx", "dinner": "xxx"}
    accommodation: Optional[Dict[str, Any]] = None  # 住宿信息
    total_estimated_cost: float = 0.0  # 当日估计费用
    notes: Optional[str] = None


@dataclass
class Itinerary:
    """完整行程安排"""
    location: str
    start_date: date
    end_date: date
    days: List[DayItinerary] = field(default_factory=list)
    estimated_total_cost: float = 0.0
    cost_breakdown: Dict[str, float] = field(default_factory=dict)  # {"transport": 500, "accommodation": 1000, "food": 600, ...}
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostBreakdown:
    """成本明细"""
    accommodation: float = 0.0
    transportation: float = 0.0
    dining: float = 0.0
    attractions: float = 0.0
    shopping: float = 0.0
    miscellaneous: float = 0.0
    contingency: float = 0.0  # 应急预留
    
    @property
    def total(self) -> float:
        return sum([
            self.accommodation, self.transportation, self.dining,
            self.attractions, self.shopping, self.miscellaneous,
            self.contingency
        ])


@dataclass
class OptimizationRecommendation:
    """优化建议"""
    category: str                      # 优化类别
    suggestion: str                    # 建议内容
    potential_savings: float           # 潜在节省金额
    confidence: float                  # 置信度（0-1）


@dataclass
class FinalHandbook:
    """最终旅行手册"""
    title: str
    destination: str
    itinerary: Itinerary
    cost_breakdown: CostBreakdown
    budget: float
    budget_remaining: float
    optimization_recommendations: List[OptimizationRecommendation] = field(default_factory=list)
    emergency_contacts: Dict[str, str] = field(default_factory=dict)
    tips_and_tricks: List[str] = field(default_factory=list)
    packing_list: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_within_budget(self) -> bool:
        return self.cost_breakdown.total <= self.budget


@dataclass
class PlanningContext:
    """贯穿全程的共享上下文"""
    travel_profile: Optional[TravelProfile] = None
    spot_list: Optional[SpotList] = None
    dining_list: Optional[DiningList] = None
    itinerary: Optional[Itinerary] = None
    final_handbook: Optional[FinalHandbook] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, error: str) -> None:
        """添加错误"""
        self.errors.append(error)
    
    def add_warning(self, warning: str) -> None:
        """添加警告"""
        self.warnings.append(warning)
    
    def is_valid(self) -> bool:
        """检查上下文是否有效"""
        return len(self.errors) == 0
