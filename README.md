# VoyageAgent - 智能旅行规划系统

一个基于多 Agent 架构的智能旅行规划系统，使用 LLM 为用户生成完整、个性化的旅行手册。

## 🎯 项目特点

- **多 Agent 架构**: 5 个专职 Agent，分别负责不同阶段的规划
- **数据驱动**: 完整的数据模型，支持 Agent 间的无缝协作
- **可扩展设计**: 易于添加新 Agent 或扩展现有功能
- **完整的工作流**: 从用户输入到最终手册全自动生成
- **充分的测试**: 每个 Agent 都有完整的测试覆盖

## 🏗️ 系统架构

```
用户输入
   ↓
User Preference Agent → 提取用户偏好
   ↓
Spot Recommendation Agent → 推荐景点
   ↓
Dining Recommendation Agent → 推荐餐厅  
   ↓
Route & Hotel Planning Agent → 规划行程
   ↓
Cost Optimization Agent → 优化成本
   ↓
最终旅行手册
```

## 📁 目录结构

```
voyagent-backend/
├── models/                          # 数据模型
│   └── schemas.py                  
├── agents/                          # Agent 实现
│   ├── base_agent.py               # 基类
│   ├── user_preference/            
│   ├── spot_recommendation/
│   ├── dining_recommendation/
│   ├── route_hotel_planning/
│   └── cost_optimization/
├── orchestrator/
│   └── workflow.py                 # 工作流编排
├── tests/                          # 单元测试
├── .github/workflows/              # CI/CD
├── docs/                           # 文档
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 快速开始

### 环境准备

```bash
# 克隆仓库
git clone <repo-url>
cd voyagent-backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加你的 API 密钥
```

### 运行示例

```python
from orchestrator.workflow import TravelPlanningWorkflow

# 创建工作流
workflow = TravelPlanningWorkflow()

# 用户输入
user_input = """
我想去巴黎，5月15日出发，5月22日回来。
预算5000美元，4个人。
我们喜欢文化和美食。
"""

# 执行规划
context = workflow.run(user_input)

# 获取最终结果
final_handbook = context.final_handbook
print(f"旅行手册: {final_handbook.title}")
print(f"总成本: ${final_handbook.cost_breakdown.total}")
```

## 👥 分工说明

| 成员 | 负责模块 | 分支 |
|------|--------|------|
| Member 1 | User Preference Agent | feature/agent-user-preference |
| Member 2 | Spot Recommendation Agent | feature/agent-spot |
| Member 3 | Dining Recommendation Agent | feature/agent-dining |
| Member 4 | Route & Hotel Planning Agent | feature/agent-route-hotel |
| Member 5 | Cost Optimization Agent | feature/agent-cost |
| Team Lead | Orchestrator + Schemas | - |

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_user_preference.py -v

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

## 📊 Agent 说明

### User Preference Agent
提取用户的旅行偏好信息（目的地、预算、日期、人数等）

### Spot Recommendation Agent
根据用户偏好推荐合适的景点，包括评分、门票价格等

### Dining Recommendation Agent
推荐符合用户饮食偏好和预算的餐厅

### Route & Hotel Planning Agent
规划详细的每日行程和酒店安排

### Cost Optimization Agent
分析成本、提供优化建议，生成最终旅行手册

## 🔄 Git 工作流

```bash
# 创建特性分支
git checkout -b feature/agent-xxx

# 开发和提交
git add .
git commit -m "feat: 实现 xxx 功能"

# 推送到远程
git push origin feature/agent-xxx

# 创建 PR 到 dev 分支
# 审查通过后合并

# 定期从 dev 合并到 main
```

## 📝 配置

参考 `.env.example` 配置环境变量：

```env
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./data/voyagent.db
```

## 📚 文档

详细架构文档请参考 [docs/architecture.md](docs/architecture.md)

## 🔧 开发指南

- 每个 Agent 位于 `agents/<agent_name>/` 目录
- 每个 Agent 包含 `agent.py`（实现）和 `prompts.py`（LLM Prompt）
- 所有 Schema 定义在 `models/schemas.py`
- 工作流逻辑在 `orchestrator/workflow.py`

## 🚦 CI/CD

项目使用 GitHub Actions 自动进行测试和部署。配置文件：`.github/workflows/ci.yml`

## 📄 许可证

MIT License

## 💬 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交修改 (`git commit -m 'Add xxx'`)
4. 推送到分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

## 📞 联系我们

- 问题报告: GitHub Issues
- 讨论建议: GitHub Discussions
- 邮件: team@voyagent.com
