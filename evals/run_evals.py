import json
from agent.loop import run_agent_loop
from metrics import evaluate_accuracy, evaluate_efficiency, evaluate_hallucination

with open("evals/dataset.json") as f:
    dataset = json.load(f)

def run_evals():
    test_subset = dataset[:10]
    reports = []
    for i, item in enumerate(test_subset):
            print(f"\n[{i+1}/{len(test_subset)}] Running {item['category']}: {item['question']}")

            # Run agent loop
            result = run_agent_loop(item["question"], return_metadata=True)

            # Print results
            if isinstance(result, dict):
                accuracy_res = evaluate_accuracy(item["question"], item["expected_answer"], result["output"])
                hallucination_res = evaluate_hallucination(result["output"], result["tool_outputs"])
                efficiency_res = evaluate_efficiency(result["messages"])

                print(f"Accuracy: {accuracy_res['score']} - Reason: {accuracy_res['reason']}")
                print(f"Hallucination: {hallucination_res['hallucination_score']} - Reason: {hallucination_res['reason']}")
                print(f"Efficiency: {efficiency_res['steps']} steps, {efficiency_res['tool_calls']} tool calls")
                reports.append({
                    "id": item["id"],
                    "category": item["category"],
                    "question": item["question"],
                    "expected_answer": item["expected_answer"],
                    "agent_answer": result["output"],
                    "accuracy": accuracy_res["score"],
                    "accuracy_reason": accuracy_res["reason"],
                    "hallucination": hallucination_res["hallucination_score"],
                    "hallucination_reason": hallucination_res["reason"],
                    "steps": efficiency_res["steps"],
                    "tool_calls": efficiency_res["tool_calls"]
                })
    num_cases = len(reports)
    avg_accuracy = sum(r["accuracy"] for r in reports) / num_cases
    avg_hallucinations = sum(r["hallucination"] for r in reports) / num_cases
    avg_steps = sum(r["steps"] for r in reports) / num_cases
    avg_tool_calls = sum(r["tool_calls"] for r in reports) / num_cases

    print("\n" + "="*40)
    print("EVALUATION COMPLETED SUMMARY")
    print("="*40)
    print(f"Total test Cases: {num_cases}")
    print(f"Average Accuracy: {avg_accuracy:.2%}")
    print(f"Average Hallucination Rate: {avg_hallucinations:.2%}")
    print(f"Average Steps: {avg_steps:.1f}")
    print(f"Average Tool Calls: {avg_tool_calls:.1f}")
    print("="*40)

     # --- WRITE MARKDOWN REPORT ---
    markdown_content = f"""# ReAct Agent Evaluation Report

    ## Summary Metrics
    | Metric | Value |
    |--------|-------|
    | **Total Test Cases** | {num_cases} |
    | **Average Accuracy** | {avg_accuracy:.2%} |
    | **Average Hallucination Rate** | {avg_hallucinations:.2%} |
    | **Average Steps** | {avg_steps:.1f} |
    | **Average Tool Calls** | {avg_tool_calls:.1f} |

    ## Detailed Results
    """

    for r in reports:
        markdown_content += f"""
    ### Test Case {r['id']} ({r['category']})
    * **Question**: {r['question']}
    * **Ground Truth**: {r['expected_answer']}
    * **Agent Answer**: {r['agent_answer']}
    * **Scores**:
      * **Accuracy**: {r['accuracy']} - *Reason: {r['accuracy_reason']}*
      * **Hallucination**: {r['hallucination']} - *Reason: {r['hallucination_reason']}*
      * **Efficiency**: {r['steps']} steps, {r['tool_calls']} tool calls
    ---
    """

        with open("evals/report.md", "w") as report_file:
            report_file.write(markdown_content)

        print("Saved detailed report to evals/report.md")
    
    return reports

if __name__ == "__main__":
    run_evals()