import pytest
from unittest.mock import patch, MagicMock
from agent.loop import run_agent_loop

class MockResponse:
    def __init__(self, output_text: str = "", output: list = []):
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
@patch("agent.tools.web_search.DDGS")
def test_tool_calling_loop(mock_ddgs, mock_get_chat_response):
    # Mock the context manager __enter__ to return our fake search object
    mock_ddgs_instance = mock_ddgs.return_value.__enter__.return_value

    # Tell ddgs.text to return our offline mock result
    mock_ddgs_instance.text.return_value = [
        {
            "title": "Population of Paris",
            "href": "https://en.wikipedia.org/wiki/Population_of_Paris",
            "body": "The population of Paris is 2.1 million."
        }
    ]
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

@patch("agent.loop.client.get_chat_response")
@patch("agent.tools.web_search.DDGS")
@patch("agent.tools.read_url.httpx.get")
def test_multi_tool_calling_loop(mock_httpx_get, mock_ddgs, mock_get_chat_response):
    # 1. Mock the DDGS context manager
    mock_ddgs_instance = mock_ddgs.return_value.__enter__.return_value
    mock_ddgs_instance.text.return_value = [
        {
            "title": "Paris - Wikipedia",
            "href": "https://en.wikipedia.org/wiki/Paris",
            "body": "Wikipedia page link"
        }
    ]
    
    # 2. Mock httpx.get response
    mock_response = MagicMock()
    mock_response.text = "<html><body><h1>Paris</h1><p>Paris is the capital of France.</p></body></html>"
    mock_response.status_code = 200
    mock_httpx_get.return_value = mock_response
    
    # 3. Define the three LLM response turns
    turn_1 = MockResponse(
        output=[
            MockFunctionCall(
                item_id="fc_1",
                call_id="call_1",
                name="web_search",
                arguments='{"query": "Paris wikipedia"}'
            )
        ]
    )
    turn_2 = MockResponse(
        output=[
            MockFunctionCall(
                item_id="fc_2",
                call_id="call_2",
                name="read_url",
                arguments='{"url": "https://en.wikipedia.org/wiki/Paris"}'
            )
        ]
    )
    turn_3 = MockResponse(output_text="Paris is the capital of France.")
    
    mock_get_chat_response.side_effect = [turn_1, turn_2, turn_3]
    
    # 4. Run the loop
    result = run_agent_loop("Find information on Paris and summarize its wikipedia page")
    
    # 5. Assertions
    assert result == "Paris is the capital of France."
    assert mock_get_chat_response.call_count == 3
    
    # Verify the messages sent in the final turn (should have 6 messages in history)
    third_call_args = mock_get_chat_response.call_args_list[2][0]
    sent_messages = third_call_args[0]
    assert len(sent_messages) == 6
    assert sent_messages[2]["type"] == "function_call"       # web_search call
    assert sent_messages[3]["type"] == "function_call_output" # web_search output
    assert sent_messages[4]["type"] == "function_call"       # read_url call
    assert sent_messages[5]["type"] == "function_call_output" # read_url output
    assert "capital of France" in sent_messages[5]["output"]