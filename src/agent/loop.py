import json
from agent.llm import client
from agent.models.messages import (
    ConversationState,
    TextMessage,
    FunctionCallItem,
    FunctionCallOutputItem,
)

# A temporary tool registry for stubbing out tools during development
def stub_web_search(query: str) -> str:
    if "Paris" in query or "paris" in query:
        return "The population of Paris is 2.1 million."
    return "No search results found."

STUB_TOOLS = {
    "web_search": stub_web_search,
}

def execute_tool(name: str, arguments_json: str) -> str:
    """Parses JSON arguments and routes tool execution.
    
    Rather than raising exceptions and crashing the program, we return error
    messages as strings so the LLM receives the feedback as an observation 
    and has a chance to correct itself.
    """
    try:
        args = json.loads(arguments_json)
    except Exception as e:
        return f"Error: Invalid JSON arguments: {str(e)}"
        
    tool_func = STUB_TOOLS.get(name)
    if not tool_func:
        return f"Error: Tool '{name}' not found."
        
    try:
        return tool_func(**args)
    except Exception as e:
        return f"Error executing tool: {str(e)}"

def run_agent_loop(user_prompt: str, max_iterations: int = 5) -> str:
    # 1. Initialize state before entering the loop
    state = ConversationState()
    state.messages.append(
        TextMessage(role="developer", content="You are a helpful research assistant.")
    )
    state.messages.append(
        TextMessage(role="user", content=user_prompt)
    )

    for _ in range(max_iterations):
        # 2. Serialize messages for the OpenAI API
        messages_payload = [msg.model_dump(exclude_none=True) for msg in state.messages]
        
        # 3. Get response from LLM
        response = client.get_chat_response(messages_payload)
        
        # 4. Check for tool calls (function_call items in response.output)
        tool_calls = [
            item for item in response.output 
            if getattr(item, "type", None) == "function_call"
        ]
        
        if tool_calls:
            # We have tool calls! Handle them.
            for tool_call in tool_calls:
                # Add the tool call item to history
                state.messages.append(
                    FunctionCallItem(
                        id=tool_call.id,
                        call_id=tool_call.call_id,
                        name=tool_call.name,
                        arguments=tool_call.arguments
                    )
                )
                
                # Execute the tool
                output_str = execute_tool(tool_call.name, tool_call.arguments)
                
                # Add the output (observation) to history
                state.messages.append(
                    FunctionCallOutputItem(
                        call_id=tool_call.call_id,
                        output=output_str
                    )
                )
            # Loop again (continue to next iteration of for-loop)
            continue
            
        # 5. If no tool calls, check for final text answer
        if response.output_text:
            state.messages.append(
                TextMessage(role="assistant", content=response.output_text)
            )
            return response.output_text
            
        # If we got no tool calls and no output text, break out of loop
        break

    return ""
