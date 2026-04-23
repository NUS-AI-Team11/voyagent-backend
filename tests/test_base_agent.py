from agents.base_agent import BaseAgent
from models.schemas import PlanningContext


class _AgentOK(BaseAgent):
    def __init__(self):
        super().__init__(name="Agent OK", description="ok")

    def process(self, context: PlanningContext) -> PlanningContext:
        context.metadata["ok_ran"] = True
        return context


class _AgentValidationFail(BaseAgent):
    def __init__(self):
        super().__init__(name="Agent Validation Fail", description="bad input")

    def validate_input(self, context: PlanningContext) -> bool:
        return False

    def process(self, context: PlanningContext) -> PlanningContext:
        context.metadata["should_not_run"] = True
        return context


class _AgentAddsError(BaseAgent):
    def __init__(self):
        super().__init__(name="Agent Adds Error", description="adds error")

    def process(self, context: PlanningContext) -> PlanningContext:
        context.add_error("boom")
        return context


class _AgentRaises(BaseAgent):
    def __init__(self):
        super().__init__(name="Agent Raises", description="raises")

    def process(self, context: PlanningContext) -> PlanningContext:
        raise RuntimeError("kaboom")


def test_base_agent_execute_records_success_run_metadata():
    ctx = PlanningContext()
    agent = _AgentOK()
    out = agent.execute(ctx)
    assert out.metadata["ok_ran"] is True
    assert "agent_runs" in out.metadata
    last = out.metadata["agent_runs"][-1]
    assert last["agent"] == "Agent OK"
    assert last["status"] == "success"
    assert last["error"] == ""


def test_base_agent_execute_validation_failure_adds_error_and_does_not_run_process():
    ctx = PlanningContext()
    agent = _AgentValidationFail()
    out = agent.execute(ctx)
    assert any("input validation failed" in e for e in out.errors)
    assert out.metadata.get("should_not_run") is None


def test_base_agent_execute_marks_failed_when_new_errors_added():
    ctx = PlanningContext()
    agent = _AgentAddsError()
    out = agent.execute(ctx)
    assert out.errors
    last = out.metadata["agent_runs"][-1]
    assert last["agent"] == "Agent Adds Error"
    assert last["status"] == "failed"


def test_base_agent_execute_catches_exceptions_and_records_error():
    ctx = PlanningContext()
    agent = _AgentRaises()
    out = agent.execute(ctx)
    assert any("execution failed" in e for e in out.errors)
    last = out.metadata["agent_runs"][-1]
    assert last["agent"] == "Agent Raises"
    assert last["status"] == "failed"
    assert "kaboom" in last["error"]
