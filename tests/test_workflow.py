"""Tests for workflow baseline behavior."""

from typing import Optional

from orchestrator.workflow import TravelPlanningWorkflow
from models.schemas import PlanningContext


def test_workflow_run_stores_basic_metadata():
    workflow = TravelPlanningWorkflow(print_summary=False)
    workflow.steps = []
    context = workflow.run("test input")

    assert context.metadata.get("user_input") == "test input"
    assert "workflow_started_at" in context.metadata
    assert "workflow_finished_at" in context.metadata
    assert isinstance(context.metadata.get("workflow_steps"), list)


def test_workflow_run_calls_hooks_for_each_step():
    workflow = TravelPlanningWorkflow(print_summary=False)
    events = []

    def _before(step_index, label, output_field, _ctx):
        events.append(("before", step_index, label, output_field))

    def _after(step_index, label, output_field, _ctx):
        events.append(("after", step_index, label, output_field))

    workflow.run("Plan a trip to Tokyo", before_step=_before, after_step=_after)

    assert any(item[0] == "before" for item in events)
    assert any(item[0] == "after" for item in events)


class _DummyExecuteAgent:
    def __init__(self, name: str, output_field: Optional[str] = None, add_error: bool = False):
        self.name = name
        self.description = ""
        self._output_field = output_field
        self._add_error = add_error

    def execute(self, context: PlanningContext) -> PlanningContext:
        if self._output_field:
            setattr(context, self._output_field, {"ok": True})
        if self._add_error:
            context.add_error(f"{self.name}: boom")
        return context


class _DummyProcessAgent:
    def __init__(self, name: str, output_field: Optional[str] = None):
        self.name = name
        self.description = ""
        self._output_field = output_field

    def process(self, context: PlanningContext) -> PlanningContext:
        if self._output_field:
            setattr(context, self._output_field, {"ok": True})
        return context


def test_workflow_run_step_adds_error_when_required_output_missing():
    workflow = TravelPlanningWorkflow(print_summary=False)
    agent = _DummyExecuteAgent("A1", output_field=None)
    ctx = PlanningContext()
    ctx.metadata["workflow_steps"] = []

    out = workflow._run_step(ctx, agent, "travel_profile", required=True)
    assert out.errors
    assert any("expected output" in e for e in out.errors)
    assert out.metadata["workflow_steps"][-1]["has_output"] is False


def test_workflow_run_step_supports_agents_without_execute_method():
    workflow = TravelPlanningWorkflow(print_summary=False)
    agent = _DummyProcessAgent("A2", output_field="travel_profile")
    ctx = PlanningContext()
    ctx.metadata["workflow_steps"] = []

    out = workflow._run_step(ctx, agent, "travel_profile", required=True)
    assert out.travel_profile == {"ok": True}
    assert out.metadata["workflow_steps"][-1]["has_output"] is True


def test_workflow_fail_fast_stops_after_first_error():
    workflow = TravelPlanningWorkflow(print_summary=False, fail_fast=True)
    ran = {"second": False}

    class _Second(_DummyExecuteAgent):
        def execute(self, context: PlanningContext) -> PlanningContext:
            ran["second"] = True
            return super().execute(context)

    workflow.steps = [
        ("Step1", _DummyExecuteAgent("S1", output_field=None, add_error=True), "travel_profile", True),
        ("Step2", _Second("S2", output_field="spot_list"), "spot_list", True),
    ]
    ctx = workflow.run("x")
    assert ctx.errors
    assert ran["second"] is False
