"""
成本优化 Agent 的 Prompt 模板
"""

SYSTEM_PROMPT = """你是一个旅行成本优化专家。你的任务是：
1. 分析当前行程的成本结构
2. 提供成本优化建议
3. 确保总成本在用户预算内
4. 提出替代方案以节省成本
5. 识别可能的隐藏成本

重要：在优化成本的同时，保持旅行质量和用户体验。"""

COST_ANALYSIS_PROMPT = """
分析以下行程的成本结构：

目标目的地：{destination}
旅行日期：{start_date} 至 {end_date}
预算：{budget}

成本明细：
- 住宿：{accommodation_cost}
- 餐饮：{dining_cost}
- 景点门票：{attraction_cost}
- 交通：{transportation_cost}
- 其他：{miscellaneous_cost}

总成本：{total_cost}

请分析：
1. 成本是否超支
2. 各项成本占比
3. 成本趋势
4. 潜在的节省机会
"""

OPTIMIZATION_RECOMMENDATION_PROMPT = """
为以下行程提供成本优化建议：

当前总成本：{current_cost}
预算：{budget}
超支金额：{overage}

行程详情：
{itinerary}

请提提供：
1. 高优先级的优化建议（立即可实施）
2. 中优先级的优化建议（需要调整）
3. 低优先级的优化建议（可选）

对于每个建议，请包括：
- 建议说明
- 预计节省金额
- 对体验的影响（1-5分）
- 实施难度（1-5分）
"""

BUDGET_ALLOCATION_PROMPT = """
为用户重新分配预算以实现最佳价值：

总预算：{budget}
旅行天数：{days}
人数：{group_size}

用户优先级：
1. {priority_1}
2. {priority_2}
3. {priority_3}

请提供推荐的预算分配：
- 住宿：___（建议：__%）
- 餐饮：___（建议：__%）
- 景点：___（建议：__%）
- 交通：___（建议：__%）
- 其他：___（建议：__%）
- 应急：___（建议：__%）

说明您的分配理由。
"""

ALTERNATIVE_ITINERARY_PROMPT = """
创建一个成本更低的行程替代方案：

当前行程成本：{current_cost}
目标成本：{target_cost}
节省目标：{savings_needed}

当前行程亮点：
{current_highlights}

请创建一个：
1. 保留关键景点和体验
2. 考虑免费或低成本替代方案
3. 调整住宿和餐饮选择
4. 优化交通路线

新行程应在目标成本内，同时最大化用户满意度。
"""

FINAL_HANDBOOK_PROMPT = """
创建最终的旅行手册和成本总结：

行程信息：{itinerary_summary}
成本明细：{cost_breakdown}
预算来源：{budget}
节省情况：{savings}

最终手册应包括：
1. 一页行程概览
2. 详细的日程表
3. 成本明细表
4. 预订信息（酒店、餐厅等）
5. 应急联系方式
6. 本地提示和建议
7. 打包清单
8. 天气预报
9. 货币和支付信息
10. 应急预案
"""
