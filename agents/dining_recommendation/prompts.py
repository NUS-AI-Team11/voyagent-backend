"""
Prompt templates for the Dining Recommendation Agent.
"""

SYSTEM_PROMPT = """You are a food and restaurant recommendation expert. Your tasks are:
1. Recommend restaurants that match the user's dietary preferences and budget
2. Provide detailed information for each restaurant (address, cuisine, price, rating, etc.)
3. Account for special dietary requirements (allergies, vegetarian, etc.)
4. Recommend options across different meal types (breakfast, lunch, dinner)

Important: ensure recommendations are diverse and within the user's budget."""

DINING_RECOMMENDATION_PROMPT = """
Recommend restaurants based on the user's travel preferences:

Destination: {destination}
Travel style: {travel_style}
Budget: {budget}
Group size: {group_size}
Duration (days): {duration_days}
Dietary restrictions: {dietary_restrictions}

Please recommend 10-15 restaurants, each including:
1. Name
2. Cuisine type
3. Address / location
4. Price range ($ / $$ / $$$ / $$$$)
5. Average cost per person
6. User rating (1-5)
7. Opening hours
8. Whether reservations are required
9. Special notes (suitable for specific dietary needs, etc.)

Provide separate recommendations suitable across breakfast, lunch, and dinner.
Return valid JSON in this exact shape:
{{
  "restaurants": [
    {{
      "name": "string",
      "cuisine_type": "string",
      "address": "string",
      "price_range": "$|$$|$$$|$$$$",
      "average_cost_per_person": 0,
      "rating": 0,
      "opening_hours": "string",
      "reservations_needed": false,
      "special_notes": "string"
    }}
  ]
}}
"""

MEAL_PLAN_PROMPT = """
Plan dining for the following day:

Date: {date}
Activities that day: {activities}

Recommend suitable options for:
1. Breakfast location and time
2. Lunch location and time
3. Dinner location and time

Account for attraction locations and visit duration.
"""

BUDGET_DINING_PROMPT = """
Recommend a dining plan for the user based on the following budget:

Total budget: {total_budget}
Allocated dining budget: {dining_budget}
Duration (days): {days}
Meals per day: {meals_per_day}

Recommend a balanced plan including:
1. High-end restaurants (per visit)
2. Mid-range restaurants (per visit)
3. Budget restaurants (per visit)
4. Local street food options
"""
