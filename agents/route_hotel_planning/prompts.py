"""
路线&酒店规划 Agent 的 Prompt 模板
"""

SYSTEM_PROMPT = """你是一个专业的旅行规划师。你的任务是：
1. 根据推荐的景点和餐厅规划每日行程
2. 优化景点访问顺序（考虑地理位置和交通）
3. 推荐合适的酒店
4. 为每天分配合理的时间和活动
5. 提供交通建议

重要：确保行程既滿足用户兴趣又具有可行性。"""

ITINERARY_CREATION_PROMPT = """
根据以下信息创建详细的日程安排：

用户信息：
- 目的地：{destination}
- 出发日期：{start_date}
- 返回日期：{end_date}
- 人数：{group_size}
- 交通偏好：{transportation_preference}

推荐景点：
{spots}

推荐餐厅：
{restaurants}

请为每一天创建详细的行程，包括：
1. 早上活动（时间、景点、预计耗时）
2. 午餐地点和时间
3. 下午活动
4. 晚餐地点和时间
5. 晚上活动
6. 预计该天交通成本
7. 预计该天门票成本

返回 JSON 格式的每日行程列表。
"""

HOTEL_RECOMMENDATION_PROMPT = """
为用户推荐合适的酒店：

目的地：{destination}
停留天数：{nights}
人数：{group_size}
酒店偏好：{hotel_preference}
预算限制：{budget}

请推荐3-5家酒店，包括：
1. 酒店名称
2. 位置/地址
3. 星级
4. 价格（每晚）
5. 评分
6. 关键特色设施
7. 到主要景点的距离

考虑不同等级的酒店，让用户可以选择。
"""

ROUTE_OPTIMIZATION_PROMPT = """
优化以下景点的访问路线：

景点列表：
{spots}

出发点：{starting_point}
交通方式：{transportation}

请提供：
1. 最优访问顺序
2. 景点之间的预计交通时间
3. 推荐路线说明
4. 预计总旅行时间
"""

DAILY_SCHEDULE_PROMPT = """
为第 {day_number} 天创建详细的时间表：

日期：{date}
分配的景点：{spots}
分配的餐厅：{restaurants}
酒店信息：{hotel}

请创建分钟级别的时间表，包括：
- 起床时间
- 早餐时间和地点
- 出发时间
- 每个景点的详细访问时段
- 午餐时间
- 继续游览
- 晚餐时间
- 返回酒店时间

确保行程合理且不过于紧凑。
"""
