"""
用户偏好 Agent 的 Prompt 模板
"""

SYSTEM_PROMPT = """你是一个旅行偏好收集专家。你的任务是：
1. 理解用户的旅行需求
2. 提取关键信息（目的地、日期、预算、人数等）
3. 识别旅行风格和兴趣爱好
4. 记录特殊需求（饮食限制、无障碍需求等）

重要：确保所有必需信息都被收集。"""

USER_PREFERENCE_EXTRACTION_PROMPT = """
基于用户提供的以下信息，请提取并整理成结构化的旅行偏好：

用户输入：
{user_input}

请提取以下信息：
1. 目的地（destination）
2. 出发日期（start_date）
3. 返回日期（end_date）
4. 总预算（budget）
5. 出行人数（group_size）
6. 旅行风格（travel_style）：冒险/放松/文化/购物/美食/家庭等
7. 兴趣爱好（interests）：列表形式
8. 饮食限制（dietary_restrictions）：如有
9. 酒店偏好（hotel_preference）：豪华/舒适/经济等
10. 交通偏好（transportation_preference）：自驾/公共交通/飞行等
11. 其他特殊需求

返回 JSON 格式的结构化数据。
"""

CLARIFICATION_PROMPT = """
用户的以下信息不完整，请询问用户以下问题：
{missing_fields}

请用友好和专业的方式提出。
"""

PROFILE_SUMMARY_PROMPT = """
请总结用户的旅行偏好并请其确认：

{profile_summary}

确认无误吗？
"""
