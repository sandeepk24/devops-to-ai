# Path B — real LLM planner (optional stretch)

Path A finishes the phase with `PLANNER_BACKEND=mock`. A real model is optional candy.

## What must stay true

Even with OpenAI/Anthropic:

1. Tool names still pass through `ToolRegistry` allowlist  
2. `execute_rollback` still requires an approved `approval_id`  
3. Log text never becomes authorization  
4. Evals still pass  

## Sketch

1. Add an API key via env (never commit it)  
2. Implement `openai_plan(incident, tool_schemas) -> tool_calls` in `planner.py`  
3. Set `PLANNER_BACKEND=openai` only after the mock path is green  
4. Re-run `./scripts/smoke_test.sh` and `python3 scripts/run_evals.py`  

If the model asks for `delete_namespace` or `execute_rollback` mid-investigate, your allowlist/approval layer should refuse — that's the whole lesson.
