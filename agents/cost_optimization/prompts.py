"""
Prompt templates for the Cost Optimization Agent.
"""

SYSTEM_PROMPT = """You are a travel cost optimization expert. Your tasks are:
1. Analyze the cost structure of the current itinerary
2. Provide cost optimization suggestions
3. Ensure total cost stays within the user's budget
4. Propose alternatives to reduce costs
5. Identify potential hidden costs

Important: optimize costs while maintaining travel quality and user experience."""

COST_ANALYSIS_PROMPT = """
Analyze the cost structure of the following itinerary:

Destination: {destination}
Travel dates: {start_date} to {end_date}
Budget: {budget}

Cost breakdown:
- Accommodation: {accommodation_cost}
- Dining: {dining_cost}
- Attraction fees: {attraction_cost}
- Transportation: {transportation_cost}
- Other: {miscellaneous_cost}

Total cost: {total_cost}

Please analyze:
1. Whether costs are over budget
2. Cost proportion by category
3. Cost trends
4. Potential savings opportunities
"""

OPTIMIZATION_RECOMMENDATION_PROMPT = """
Provide cost optimization suggestions for the following itinerary:

Current total cost: {current_cost}
Budget: {budget}
Overage: {overage}

Itinerary details:
{itinerary}

Please provide:
1. High-priority suggestions (immediately actionable)
2. Medium-priority suggestions (require adjustments)
3. Low-priority suggestions (optional)

For each suggestion include:
- Description
- Estimated savings
- Impact on experience (1-5)
- Implementation difficulty (1-5)
"""

BUDGET_ALLOCATION_PROMPT = """
Reallocate the budget to maximize value for the user:

Total budget: {budget}
Duration (days): {days}
Group size: {group_size}

User priorities:
1. {priority_1}
2. {priority_2}
3. {priority_3}

Provide a recommended budget allocation:
- Accommodation: ___ (suggested: __%)
- Dining: ___ (suggested: __%)
- Attractions: ___ (suggested: __%)
- Transportation: ___ (suggested: __%)
- Other: ___ (suggested: __%)
- Contingency: ___ (suggested: __%)

Explain your allocation rationale.
"""

ALTERNATIVE_ITINERARY_PROMPT = """
Create a lower-cost alternative itinerary:

Current itinerary cost: {current_cost}
Target cost: {target_cost}
Savings needed: {savings_needed}

Current itinerary highlights:
{current_highlights}

Please create an alternative that:
1. Retains key attractions and experiences
2. Considers free or low-cost alternatives
3. Adjusts accommodation and dining choices
4. Optimizes transportation routes

The new itinerary should stay within the target cost while maximizing user satisfaction.
"""

FINAL_HANDBOOK_PROMPT = """
Create the final travel handbook and cost summary:

Itinerary information: {itinerary_summary}
Cost breakdown: {cost_breakdown}
Budget: {budget}
Savings: {savings}

The final handbook should include:
1. One-page itinerary overview
2. Detailed day-by-day schedule
3. Cost breakdown table
4. Booking information (hotels, restaurants, etc.)
5. Emergency contacts
6. Local tips and recommendations
7. Packing list
8. Weather forecast
9. Currency and payment information
10. Contingency plans
"""
