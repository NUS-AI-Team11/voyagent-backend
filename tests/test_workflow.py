"""Tests for workflow baseline behavior."""

from orchestrator.workflow import TravelPlanningWorkflow


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

