import pytest
from unittest.mock import patch
from agent.loop import run_agent_loop

class MockResponse:
    def __init__(self, output_text: str = "", output: list = None):
        self.output_text = output_text
        self.output = output or []

class MockFunctionCall:
    def __init__(self, item_id: str, call_id: str, name: str, arguments: str):
        self.type = "function_call"
        self.id = item_id
        self.call_id = call_id
        self.name = name
        self.arguments = arguments


@patch("agent.loop.client.get_chat_response")
def test_simple_conversation(mock_get_response):
    mock_get_response.return_value = MockResponse(output_text="Paris is the capital of France.")

    result = run_agent_loop("What is the capital of France?")

    assert result == "Paris is the capital of France."

    mock_get_response.assert_called_once()
    called_args, _ = mock_get_response.call_args
    sent_messages = called_args[0]
    assert len(sent_messages) == 2
    assert sent_messages[0]["role"] == "developer"
    assert sent_messages[1]["role"] == "user"
    assert sent_messages[1]["content"] == "What is the capital of France?"

@patch("agent.loop.client.get_chat_response")
def test_tool_calling_loop(mock_get_chat_response):
    turn_1 = MockResponse(
        output=[
            MockFunctionCall(
                item_id="fc_1",
                call_id="call_1",
                name="web_search",
                arguments='{"query": "population of Paris"}'
            )
        ]
    )
    turn_2 = MockResponse(output_text="The population of Paris is 2.1 million.")

    mock_get_chat_response.side_effect = [turn_1, turn_2]

    result = run_agent_loop("What is the population of Paris?")

    assert result == "The population of Paris is 2.1 million."
    assert mock_get_chat_response.call_count == 2
    second_call_args = mock_get_chat_response.call_args_list[1][0]
    sent_messages = second_call_args[0]

    assert len(sent_messages) == 4
    assert sent_messages[2]["type"] == "function_call"
    assert sent_messages[3]["type"] == "function_call_output"
    assert sent_messages[3]["call_id"] == "call_1"
    assert "2.1 million" in sent_messages[3]["output"]