import time
from unittest.mock import MagicMock, patch

from agent.memory import AgentSession
from agent.tools import TOOL_REGISTRY, execute_tool_with_retry, validate_args


def response(content=None, calls=None):
    msg = MagicMock(content=content, tool_calls=calls or [])
    return MagicMock(choices=[MagicMock(message=msg)])


def call(call_id, name, arguments):
    tc = MagicMock()
    tc.id = call_id
    tc.function.name = name
    tc.function.arguments = arguments
    return tc


def test_multiple_tools_then_final_answer():
    from agent.loop import run_agent
    first = response(calls=[
        call("1", "query_city_info", '{"city":"北京"}'),
        call("2", "get_user_city", '{"user_id":"1001"}'),
    ])
    client = MagicMock()
    client.chat.completions.create.side_effect = [first, response("组合完成")]
    with patch("agent.loop.get_client", return_value=client), patch(
        "agent.loop.execute_tool_with_retry", side_effect=["城市结果", "用户结果"]
    ):
        result = run_agent("组合查询")
    assert result.success and result.steps == 2
    assert [x.name for x in result.tool_calls] == ["query_city_info", "get_user_city"]


def test_tool_failure_can_recover_to_answer():
    from agent.loop import run_agent
    client = MagicMock()
    client.chat.completions.create.side_effect = [
        response(calls=[call("1", "get_weather", '{"city":"北京"}')]),
        response("天气工具失败，已向用户说明"),
    ]
    with patch("agent.loop.get_client", return_value=client), patch(
        "agent.loop.execute_tool_with_retry", return_value="工具 get_weather 执行失败（已重试 2 次）：offline"
    ):
        result = run_agent("天气")
    assert result.success
    assert result.tool_calls[0].error is not None


def test_illegal_and_dangerous_arguments_are_blocked():
    assert validate_args("get_weather", {"city": 1})[0] is False
    ok, error = validate_args("delete_file", {"path": "x"})
    assert ok is False and "危险操作已拦截" in error


def test_agent_records_dangerous_call_and_recovers():
    from agent.loop import run_agent
    client = MagicMock()
    client.chat.completions.create.side_effect = [
        response(calls=[call("danger", "delete_file", '{"path":"important.db"}')]),
        response("该危险操作已被拦截"),
    ]
    with patch("agent.loop.get_client", return_value=client):
        result = run_agent("删除数据库")
    assert result.success
    assert "危险操作已拦截" in (result.tool_calls[0].error or "")


def test_tool_timeout():
    TOOL_REGISTRY["slow_test"] = lambda: time.sleep(0.1)
    from agent import tools
    tools.TOOL_SCHEMAS["slow_test"] = {"required": [], "types": {}}
    try:
        assert "执行超时" in execute_tool_with_retry("slow_test", {}, timeout=0.01)
    finally:
        TOOL_REGISTRY.pop("slow_test", None)
        tools.TOOL_SCHEMAS.pop("slow_test", None)


def test_empty_tool_result_is_returned_safely():
    TOOL_REGISTRY["empty_test"] = lambda: ""
    from agent import tools
    tools.TOOL_SCHEMAS["empty_test"] = {"required": [], "types": {}}
    try:
        assert execute_tool_with_retry("empty_test", {}) == ""
    finally:
        TOOL_REGISTRY.pop("empty_test", None)
        tools.TOOL_SCHEMAS.pop("empty_test", None)


def test_multi_turn_context_is_preserved():
    from agent.loop import run_agent
    session = AgentSession()
    client = MagicMock()
    client.chat.completions.create.side_effect = [response("第一轮"), response("第二轮")]
    with patch("agent.loop.get_client", return_value=client):
        assert run_agent("问题一", session).success
        assert run_agent("问题二", session).success
    second_messages = client.chat.completions.create.call_args_list[1].kwargs["messages"]
    assert any(m.get("content") == "问题一" for m in second_messages)
    assert any(m.get("content") == "第一轮" for m in second_messages)
