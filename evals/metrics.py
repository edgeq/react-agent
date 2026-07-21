import json
from agent.llm import client
from typing import Any

def evaluate_accuracy(question: str, expected_answer: str, agent_answer: str) -> dict[str, Any]:
    """Evaluates the agent's answer against the ground truth using the LLM as a judge."""

    system_prompt = """You are an independent grading judge.
    Your task is to evaluate the accuracy of an AGENT ANSWER against a GROUND TRUTH answer for a specific QUESTION.

    Provide a score between 0.0 and 1.0:
    - 1.0: The agent's answer is fully accurate and contains all key facts from the ground truth.
    - 0.5: The agent's answer is partially accurate, but missing major details or is incomplete.
    - 0.0: The agent's answer is completely wrong, contradictory, or empty.

    Respond ONLY with a JSON object in this format:
    {
      "score": <float between 0.0 and 1.0>,
      "reason": "<short explanation of your grading>"
    }"""

    eval_prompt = f"""QUESTION: {question}
    GROUND TRUTH: {expected_answer}
    AGENT ANSWER: {agent_answer}"""

    try:
        messages = [
            {"role": "developer", "content": system_prompt},
            {"role": "user", "content": eval_prompt}
        ]
        response = client.get_chat_response(messages)
        result = json.loads(response.output_text)
        return result
    except Exception as e:
        return {
            "score": 0.0,
            "reason": f"Evaluation failed due to error: {str(e)}"
        }

def evaluate_hallucination(agent_answer: str, tool_outputs: list[str]) -> dict[str, Any]:
    combined_sources = ""
    if tool_outputs:
        combined_sources = "\n\n".join(tool_outputs)
    else:
        combined_sources = "No tools were called"

    system_prompt = """You are an independent auditing judge.
    Your task is to detect factual HALLUCINATIONS in an AGENT ANSWER. You will be provided with the AGENT ANSWER and the SOURCE observations representing
  the exact information retrieved by the agent.

    Compare the AGENT ANSWER against the SOURCE text:
    - If the agent makes factual claims (names, numbers, specific stats, events) that are NOT present anywhere in the SOURCE text, this is a hallucination.
    - If the agent states it cannot find the information (for empty or fictional queries), this is NOT a hallucination (score 0.0).
    - Common knowledge (like 'Paris is the capital of France') does not count as a hallucination.

    Provide a score between 0.0 and 1.0:
    - 0.0: No hallucinations. Every claim is supported by the sources.
    - 0.5: Minor hallucination. Most claims are supported, but there are minor unsupported facts.
    - 1.0: Major hallucination. The agent fabricated major facts or numbers not found in the sources.

    Respond ONLY with a JSON object in this format:
    {
      "hallucination_score": <float between 0.0 and 1.0>,
      "reason": "<short explanation>"
    }"""

    eval_prompt = f"""AGENT ANSWER: {agent_answer}
    SOURCE:
    {combined_sources}"""

    try:
        messages = [
            {"role": "developer", "content": system_prompt},
            {"role": "user", "content": eval_prompt}
        ]
        response = client.get_chat_response(messages)
        result = json.loads(response.output_text)
        return result
    except Exception as e:
        return {
            "hallucination_score": 0.0,
            "reason": f"Evaluation failed due to error: {str(e)}"
        }

def evaluate_efficiency(messages: list[Any]) -> dict[str, int]:
    steps = 0
    tool_calls = 0
    for msg in messages:
        if getattr(msg, "type", None) == "function_call":
            tool_calls += 1
        if getattr(msg, "type", None) == "function_call" or getattr(msg, "role", None) == "assistant":
            steps += 1

    return {
        "steps": steps,
        "tool_calls": tool_calls
    }
