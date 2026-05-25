"""Tests for ``decepticon.telemetry.otel`` — opt-in OTLP trace export.

When ``OTEL_ENABLED`` is unset the helpers must produce zero spans. When
set, they must emit the engagement -> agent_run -> (tool_call | llm_call)
hierarchy with the documented Decepticon attributes. Tests install an
``InMemorySpanExporter`` directly on the global TracerProvider so we
exercise the real OpenTelemetry SDK without hitting the network.
"""

from __future__ import annotations

import pytest

opentelemetry = pytest.importorskip("opentelemetry")

from opentelemetry import trace  # noqa: E402
from opentelemetry.sdk.resources import Resource  # noqa: E402
from opentelemetry.sdk.trace import TracerProvider  # noqa: E402
from opentelemetry.sdk.trace.export import SimpleSpanProcessor  # noqa: E402
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (  # noqa: E402
    InMemorySpanExporter,
)

from decepticon.telemetry import otel as otel_module  # noqa: E402
from decepticon.telemetry.otel import (  # noqa: E402
    record_llm_cost,
    record_llm_token_usage,
    reset_current_objective_id,
    set_current_objective_id,
    start_agent_span,
    start_engagement_span,
    start_llm_span,
    start_tool_span,
)

_SHARED_EXPORTER = InMemorySpanExporter()
_SHARED_PROVIDER = TracerProvider(
    resource=Resource.create({"service.name": "decepticon-test"})
)
_SHARED_PROVIDER.add_span_processor(SimpleSpanProcessor(_SHARED_EXPORTER))
trace.set_tracer_provider(_SHARED_PROVIDER)


@pytest.fixture
def memory_exporter(monkeypatch: pytest.MonkeyPatch) -> InMemorySpanExporter:
    """Reuse the module-level TracerProvider; OTel refuses post-init swaps."""
    monkeypatch.setenv("OTEL_ENABLED", "1")
    _SHARED_EXPORTER.clear()
    otel_module._INITIALIZED = True
    otel_module._TRACER = trace.get_tracer("decepticon")
    yield _SHARED_EXPORTER
    _SHARED_EXPORTER.clear()


def test_disabled_by_default_emits_no_spans(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OTEL_ENABLED", raising=False)
    _SHARED_EXPORTER.clear()
    otel_module._reset_for_tests()

    with start_engagement_span("eng-x"):
        with start_agent_span("decepticon"):
            with start_tool_span("update_objective"):
                pass
            with start_llm_span("anthropic/claude-haiku-4-5"):
                record_llm_cost(0.42)

    assert _SHARED_EXPORTER.get_finished_spans() == ()


def test_engagement_agent_tool_llm_hierarchy(memory_exporter: InMemorySpanExporter) -> None:
    with start_engagement_span("eng-1"):
        with start_agent_span("decepticon"):
            with start_tool_span("update_objective"):
                pass
            with start_llm_span("anthropic/claude-haiku-4-5"):
                pass

    spans = {span.name: span for span in memory_exporter.get_finished_spans()}
    assert "decepticon.engagement" in spans
    assert "decepticon.agent_run" in spans
    assert "decepticon.tool_call" in spans
    assert "decepticon.llm_call" in spans
    engagement = spans["decepticon.engagement"]
    agent = spans["decepticon.agent_run"]
    tool = spans["decepticon.tool_call"]
    llm = spans["decepticon.llm_call"]
    assert agent.parent.span_id == engagement.context.span_id
    assert tool.parent.span_id == agent.context.span_id
    assert llm.parent.span_id == agent.context.span_id


def test_attributes_are_set(memory_exporter: InMemorySpanExporter) -> None:
    with start_engagement_span("eng-1"):
        with start_agent_span("decepticon"):
            token = set_current_objective_id("OBJ-001")
            try:
                with start_tool_span("update_objective"):
                    pass
                with start_llm_span("anthropic/claude-haiku-4-5"):
                    record_llm_token_usage(prompt_tokens=120, completion_tokens=45)
                    record_llm_cost(0.123456)
            finally:
                reset_current_objective_id(token)

    spans = {span.name: span for span in memory_exporter.get_finished_spans()}
    engagement = spans["decepticon.engagement"]
    agent = spans["decepticon.agent_run"]
    tool = spans["decepticon.tool_call"]
    llm = spans["decepticon.llm_call"]
    assert engagement.attributes["decepticon.engagement_id"] == "eng-1"
    assert agent.attributes["decepticon.agent"] == "decepticon"
    assert agent.attributes["decepticon.engagement_id"] == "eng-1"
    assert tool.attributes["decepticon.tool"] == "update_objective"
    assert tool.attributes["decepticon.opplan.objective_id"] == "OBJ-001"
    assert tool.attributes["decepticon.engagement_id"] == "eng-1"
    assert llm.attributes["decepticon.llm.model"] == "anthropic/claude-haiku-4-5"
    assert llm.attributes["decepticon.llm.prompt_tokens"] == 120
    assert llm.attributes["decepticon.llm.completion_tokens"] == 45
    assert llm.attributes["decepticon.llm.cost_usd"] == pytest.approx(0.123456)
    assert llm.attributes["decepticon.opplan.objective_id"] == "OBJ-001"


def test_record_llm_cost_falls_back_to_engagement_span(
    memory_exporter: InMemorySpanExporter,
) -> None:
    with start_engagement_span("eng-2"):
        record_llm_cost(2.5)
    eng = next(
        s for s in memory_exporter.get_finished_spans() if s.name == "decepticon.engagement"
    )
    assert eng.attributes["decepticon.llm.cost_usd"] == pytest.approx(2.5)


def test_record_llm_cost_ignores_none(memory_exporter: InMemorySpanExporter) -> None:
    with start_engagement_span("eng-3"):
        with start_llm_span("model-x"):
            record_llm_cost(None)
    llm = next(
        s for s in memory_exporter.get_finished_spans() if s.name == "decepticon.llm_call"
    )
    assert "decepticon.llm.cost_usd" not in llm.attributes


def test_set_current_objective_id_returns_none_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OTEL_ENABLED", raising=False)
    assert set_current_objective_id("OBJ-1") is None
    reset_current_objective_id(None)


def test_init_otel_returns_false_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OTEL_ENABLED", raising=False)
    otel_module._reset_for_tests()
    assert otel_module.init_otel() is False


def test_init_otel_is_idempotent(memory_exporter: InMemorySpanExporter) -> None:
    assert otel_module.init_otel() is True
    assert otel_module.init_otel() is True


def test_helpers_are_safe_when_otel_packages_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Simulate missing optional packages by forcing the import path to fail."""
    monkeypatch.setenv("OTEL_ENABLED", "1")
    otel_module._reset_for_tests()

    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def _no_otel_imports(name: str, *args: object, **kwargs: object) -> object:
        if name.startswith("opentelemetry."):
            raise ImportError("simulated missing otel extra")
        return real_import(name, *args, **kwargs)

    monkeypatch.setitem(__builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__, "__import__", _no_otel_imports)

    assert otel_module.init_otel() is False
    with start_engagement_span("eng-no-otel"):
        with start_agent_span("decepticon"):
            with start_tool_span("update_objective"):
                pass
            with start_llm_span("model-x"):
                record_llm_cost(1.0)
                record_llm_token_usage(prompt_tokens=10, completion_tokens=5)
