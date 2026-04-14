"""
Prompt templates for the Route & Hotel Planning Agent.
"""

SYSTEM_PROMPT = """You are a professional travel planner. Your tasks are:
1. Plan a daily itinerary based on recommended attractions and restaurants
2. Optimize the visit order for attractions (considering location and transit)
3. Recommend suitable hotels
4. Allocate reasonable time and activities for each day
5. Provide transportation advice

Important: ensure the itinerary is both satisfying and feasible."""

ITINERARY_CREATION_PROMPT = """
Create a detailed schedule based on the following information:

User information:
- Destination: {destination}
- Departure date: {start_date}
- Return date: {end_date}
- Group size: {group_size}
- Transportation preference: {transportation_preference}

Recommended attractions:
{spots}

Recommended restaurants:
{restaurants}

For each day create a detailed itinerary including:
1. Morning activities (time, attraction, estimated duration)
2. Lunch location and time
3. Afternoon activities
4. Dinner location and time
5. Evening activities
6. Estimated transportation cost for the day
7. Estimated entrance fee cost for the day

Return a JSON list of daily itineraries.
"""

HOTEL_RECOMMENDATION_PROMPT = """
Recommend suitable hotels for the user:

Destination: {destination}
Number of nights: {nights}
Group size: {group_size}
Hotel preference: {hotel_preference}
Budget: {budget}

Please recommend 3-5 hotels, each including:
1. Hotel name
2. Location / address
3. Star rating
4. Price per night
5. User rating
6. Key amenities
7. Distance to major attractions

Include options at different price levels.
"""

ROUTE_OPTIMIZATION_PROMPT = """
Optimize the visit route for the following attractions:

Attraction list:
{spots}

Starting point: {starting_point}
Mode of transport: {transportation}

Please provide:
1. Optimal visit order
2. Estimated transit time between each attraction
3. Recommended route description
4. Estimated total travel time
"""

DAILY_SCHEDULE_PROMPT = """
Create a detailed schedule for day {day_number}:

Date: {date}
Assigned attractions: {spots}
Assigned restaurants: {restaurants}
Hotel information: {hotel}

Create a minute-level schedule including:
- Wake-up time
- Breakfast time and location
- Departure time
- Detailed visit windows for each attraction
- Lunch time
- Continued sightseeing
- Dinner time
- Return to hotel time

Ensure the schedule is reasonable and not overly packed.
"""
