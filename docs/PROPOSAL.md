# Multi-Agent Pre-Travel Handbook System Proposal

## 1. Project Title

Voyagent: a risk-aware multi-agent travel planning handbook system.

## 2. Project Sponsor

No sponsors.

## 3. Project Members

| Name | Contact |
| --- | --- |
| JIANG XINYI | e1538027@u.nus.edu |
| SUN SIHAN | e1554454@u.nus.edu |
| XIONG KUN | e1327864@u.nus.edu |
| YAN TIANLI | e1539075@u.nus.edu |
| ZHANG XINYAN | e1554415@u.nus.edu |

## 4. Overview

Voyagent is a risk-aware multi-agent travel planning system designed to generate a structured pre-trip travel handbook for individuals or small groups. Preparing for a trip requires coordinating multiple factors such as traveler preferences, destination information, accommodation choices, dining options, route planning, and overall travel costs. Traditional travel tools or single conversational assistants often provide fragmented suggestions and struggle to organize these elements into a coherent and actionable preparation guide.

To address this challenge, Voyagent adopts a multi-agent architecture composed of five specialized agents that collaborate to transform user travel requirements into a comprehensive travel preparation plan:

- User Preference Agent
- Spot Recommendation Agent
- Dining Recommendation Agent
- Route & Hotel Planning Agent
- Cost Optimization Agent

Through the collaboration of these agents, Voyagent generates a personalized, constraint-aware, and budget-conscious travel handbook that includes recommended attractions, dining options, route and accommodation planning, and estimated travel costs. The system aims to support travelers in organizing their trips more effectively while maintaining transparency in planning decisions and helping users prepare for their journeys with greater confidence.

## 5. Scope of Work

The project will design and implement Voyagent, a multi-agent system that generates a structured pre-trip travel handbook based on user preferences, destination information, and budget constraints. The system demonstrates how multiple specialized agents can collaborate to transform fragmented travel information into a coherent and practical preparation guide.

### 5.1 Agent Design and Responsibilities

Voyagent is composed of five specialized agents, each responsible for a distinct aspect of the travel planning and preparation process:

- **User Preference Agent**: Collects and structures user travel requirements such as travel dates, budget expectations, group composition, travel style, and personal preferences. The agent transforms user inputs into a structured planning profile that guides subsequent agents.
- **Spot Recommendation Agent**: Identifies and recommends attractions, landmarks, and activities that match the traveler's interests and travel objectives. The agent gathers candidate destinations and highlights relevant information such as opening hours, popularity, and suitability for the travel style.
- **Dining Recommendation Agent**: Suggests dining options and local food experiences that complement the travel plan. The agent selects restaurants or food areas that fit the itinerary timing, traveler preferences, and destination context.
- **Route & Hotel Planning Agent**: Organizes attractions and dining recommendations into a feasible day-by-day travel structure. It determines travel routes, daily activity groupings, and accommodation strategy to ensure the itinerary is geographically and temporally practical.
- **Cost Optimization Agent**: Estimates the overall travel expenses, including accommodation, attractions, dining, and transportation. The agent evaluates affordability and proposes adjustments when the travel plan exceeds the user's budget constraints.

### 5.2 Agent Autonomy and Orchestration

The system implements a coordinated workflow in which agents operate semi-autonomously while sharing contextual information. The orchestration layer manages the interaction between agents by:

- Passing structured outputs from one agent to the next
- Maintaining a shared planning context throughout the workflow
- Coordinating the sequential generation of the travel handbook

This design ensures that each agent focuses on a specific responsibility while contributing to the overall travel planning process.

### 5.3 Explainability, Trust, and Accountability

Voyagent incorporates mechanisms to support transparency and user trust in the planning process:

- Recommendations are accompanied by brief explanations describing why attractions, dining options, or accommodations are suggested.
- Planning decisions are recorded to allow users to review the reasoning behind itinerary arrangements.
- Users can clearly see how preferences and constraints influence the final travel handbook.

These practices enhance system assurance, trust, and accountability.

### 5.4 Ethical and Fair AI Considerations

The system is designed to follow responsible AI principles in travel recommendation:

- Avoiding biased recommendations toward only highly commercial or popular locations
- Ensuring diverse attraction and dining suggestions when possible
- Clearly distinguishing between factual information and generated recommendations
- Indicating uncertainty when destination information may change or be incomplete

These measures support ethical and responsible use of AI-generated travel recommendations.

### 5.5 Security and Risk Management

Voyagent considers potential AI-related risks and incorporates safeguards:

- Detecting potentially unreliable or outdated travel information retrieved from external sources
- Preventing prompt injection or malicious instructions from influencing agent outputs
- Applying rule-based checks to validate travel constraints such as opening hours or travel feasibility

These security measures help ensure that the generated travel handbook remains reliable and safe for user decision-making.

### 5.6 MLOps and LLMOps Practices

To support maintainability and operational transparency, the project incorporates basic operational practices:

- Version control for prompts and agent configurations
- Logging of agent outputs and interactions
- Basic testing of agent workflows and system outputs
- Monitoring of potential failures or inconsistencies in the planning process

These practices demonstrate how multi-agent AI systems can be deployed with appropriate LLMOps and operational governance considerations.

## 6. Effort Estimates

| Task | Description | Responsible Member | Estimated Effort (Person-Days) |
| --- | --- | --- | --- |
| System Requirement Analysis | Analyze project objectives, define the scope of the travel handbook generation system, and identify key functional requirements | Team | 3 |
| System Architecture Design | Design overall multi-agent architecture, define agent responsibilities, orchestration workflow, and data flow | Team | 3 |
| User Preference Agent - Design | Design user preference schema, define how user inputs are structured and interpreted | Member 1 | 2 |
| User Preference Agent - Implementation | Implement user input processing and structured preference extraction logic | Member 1 | 5 |
| User Preference Agent - Testing | Test preference extraction accuracy and validate structured outputs | Member 1 | 2 |
| Spot Recommendation Agent - Design | Design attraction discovery and recommendation logic based on user preferences | Member 2 | 2 |
| Spot Recommendation Agent - Implementation | Implement attraction recommendation and candidate spot generation | Member 2 | 5 |
| Spot Recommendation Agent - Testing | Validate attraction recommendations and ensure relevance to user travel profiles | Member 2 | 2 |
| Dining Recommendation Agent - Design | Design dining recommendation logic considering cuisine type, location, and schedule compatibility | Member 3 | 2 |
| Dining Recommendation Agent - Implementation | Implement dining recommendation module and contextual suggestions | Member 3 | 5 |
| Dining Recommendation Agent - Testing | Test dining suggestions and ensure compatibility with itinerary structure | Member 3 | 2 |
| Route & Hotel Planning Agent - Design | Design itinerary construction logic, route planning strategy, and accommodation planning rules | Member 4 | 2 |
| Route & Hotel Planning Agent - Implementation | Implement daily route sequencing, area grouping, and hotel selection logic | Member 4 | 5 |
| Route & Hotel Planning Agent - Testing | Test route feasibility, schedule consistency, and accommodation placement | Member 4 | 2 |
| Cost Optimization Agent - Design | Design cost estimation model and budget constraint logic | Member 5 | 2 |
| Cost Optimization Agent - Implementation | Implement travel cost estimation and budget optimization logic | Member 5 | 5 |
| Cost Optimization Agent - Testing | Validate cost calculations and ensure plans meet budget constraints | Member 5 | 2 |
| Agent Integration & Workflow Orchestration | Integrate all agents into a coordinated workflow and manage data exchange between agents | Team | 3 |
| UI/UX Design | Design simple interface for entering travel preferences and displaying generated travel handbook | Team | 2 |
| Frontend Implementation | Implement web interface for user input and travel handbook visualization | Team | 3 |
| Frontend-Agent Integration | Connect UI with backend agent workflow to trigger travel planning process | Team | 2 |
| CI/CD Pipeline Setup | Set up basic CI/CD pipeline for automated testing and deployment workflow | Team | 2 |
| Automated Testing Integration | Integrate unit tests and workflow tests into CI pipeline | Team | 2 |
| System Monitoring & Logging | Implement logging and monitoring for agent interactions and system outputs | Team | 2 |
| System Testing & Debugging | Conduct end-to-end system testing and resolve integration issues | Team | 3 |
| Documentation & Final Report Preparation | Prepare system documentation, architecture description, and final project report | Team | 5 |
| Total Estimated Effort |  |  | 75 |

*Individual division of labor will be determined during the stage of requirement analysis and architecture design.*
