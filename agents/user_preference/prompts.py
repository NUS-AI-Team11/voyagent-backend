"""
Prompt templates for the User Preference Agent.
"""

SYSTEM_PROMPT = """You are a travel preference collection specialist. Your tasks are:
1. Understand the user's travel requirements
2. Extract key information (destination, dates, budget, group size, etc.)
3. Identify travel style and interests
4. Record special requirements (dietary restrictions, accessibility needs, etc.)

Important: ensure all required information is collected."""

USER_PREFERENCE_EXTRACTION_PROMPT = """
Based on the following user input, extract and structure the travel preferences:

User input:
{user_input}

Please extract:
1. Destination
2. Departure date (start_date)
3. Return date (end_date)
4. Total budget
5. Group size
6. Travel style: adventure / relaxation / culture / shopping / food / family / etc.
7. Interests (list)
8. Dietary restrictions (if any)
9. Hotel preference: luxury / comfortable / budget / etc.
10. Transportation preference: self-drive / public transit / flights / etc.
11. Any other special requirements

Return a single JSON object only. Use these types:
- budget: a JSON number only (no currency words), e.g. 4200 for "USD 4,200"
- group_size: integer
- start_date / end_date: "YYYY-MM-DD" strings

Return structured data in JSON format.
"""

CLARIFICATION_PROMPT = """
The following information is incomplete. Please ask the user for the missing details:
{missing_fields}

Ask in a friendly and professional manner.
"""

PROFILE_SUMMARY_PROMPT = """
Please summarize the user's travel preferences and ask them to confirm:

{profile_summary}

Does this look correct?
"""
