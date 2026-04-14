"""
Shared data models - schema definitions used by all agents.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, date


@dataclass
class TravelProfile:
    """User travel preference information."""
    destination: str
    start_date: date
    end_date: date
    budget: float
    group_size: int
    travel_style: str                  # adventure / relaxation / culture / shopping / food / etc.
    interests: List[str] = field(default_factory=list)
    dietary_restrictions: List[str] = field(default_factory=list)
    hotel_preference: Optional[str] = None
    transportation_preference: Optional[str] = None
    custom_notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Spot:
    """Attraction information."""
    name: str
    description: str
    location: str
    category: str                      # history / nature / art / etc.
    opening_hours: Optional[str] = None
    entrance_fee: Optional[float] = None
    rating: float = 0.0
    duration_hours: float = 2.0
    best_season: Optional[str] = None
    accessibility_notes: Optional[str] = None


@dataclass
class SpotList:
    """Recommended attractions list."""
    spots: List[Spot] = field(default_factory=list)
    filter_criteria: Dict[str, Any] = field(default_factory=dict)
    total_count: int = 0
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Restaurant:
    """Restaurant information."""
    name: str
    cuisine_type: str
    location: str
    price_range: str                   # $ / $$ / $$$ / $$$$
    rating: float = 0.0
    average_cost_per_person: Optional[float] = None
    opening_hours: Optional[str] = None
    reservations_needed: bool = False
    accessibility_notes: Optional[str] = None


@dataclass
class DiningList:
    """Recommended restaurants list."""
    restaurants: List[Restaurant] = field(default_factory=list)
    meal_type: str = "all"             # breakfast / lunch / dinner / all
    filter_criteria: Dict[str, Any] = field(default_factory=dict)
    total_count: int = 0
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DayItinerary:
    """Single-day itinerary."""
    day_number: int
    date: date
    activities: List[Dict[str, Any]] = field(default_factory=list)
    meals: Dict[str, str] = field(default_factory=dict)
    accommodation: Optional[Dict[str, Any]] = None
    total_estimated_cost: float = 0.0
    notes: Optional[str] = None


@dataclass
class Itinerary:
    """Complete multi-day itinerary."""
    location: str
    start_date: date
    end_date: date
    days: List[DayItinerary] = field(default_factory=list)
    estimated_total_cost: float = 0.0
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostBreakdown:
    """Cost breakdown by category."""
    accommodation: float = 0.0
    transportation: float = 0.0
    dining: float = 0.0
    attractions: float = 0.0
    shopping: float = 0.0
    miscellaneous: float = 0.0
    contingency: float = 0.0

    @property
    def total(self) -> float:
        return sum([
            self.accommodation, self.transportation, self.dining,
            self.attractions, self.shopping, self.miscellaneous,
            self.contingency
        ])


@dataclass
class OptimizationRecommendation:
    """Cost optimization recommendation."""
    category: str
    suggestion: str
    potential_savings: float
    confidence: float                  # 0-1


@dataclass
class FinalHandbook:
    """Final travel handbook."""
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
    """Shared context passed through the entire planning pipeline."""
    travel_profile: Optional[TravelProfile] = None
    spot_list: Optional[SpotList] = None
    dining_list: Optional[DiningList] = None
    itinerary: Optional[Itinerary] = None
    final_handbook: Optional[FinalHandbook] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, error: str) -> None:
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)

    def is_valid(self) -> bool:
        return len(self.errors) == 0
