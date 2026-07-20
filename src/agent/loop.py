import json
from agent.llm import client
from agent.models.messages import (
    ConversationState,
    TextMessage,
    FunctionCallItem,
    FunctionCallOutputItem,
)
from agent.tools import execute_tool, get_tool_schemas

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
        print(f"\n--- Iteration {_+1}---")
        # 2. Serialize messages for the OpenAI API
        messages_payload = [msg.model_dump(exclude_none=True) for msg in state.messages]
        
        # 3. Get response from LLM
        response = client.get_chat_response(messages_payload, tools=get_tool_schemas())
        
        # 4. Check for tool calls (function_call items in response.output)
        tool_calls = [
            item for item in response.output 
            if getattr(item, "type", None) == "function_call"
        ]
        
        if tool_calls:
            # We have tool calls! Handle them.
            for tool_call in tool_calls:
                print(f"🔧 Tool Call: {tool_call.name}({tool_call.arguments})")
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
                # Print a short preview (e.g., first 150 characters) so it doesn't clutter the terminal
                print(f"👁️  Observation: {output_str[:150]}...")
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
            print("\n🏁 Final Answer Found!")
            state.messages.append(
                TextMessage(role="assistant", content=response.output_text)
            )
            return response.output_text
            
        # If we got no tool calls and no output text, break out of loop
        break

    return ""
