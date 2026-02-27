def codex_prompt(task_spec: str) -> str:
    return f"Implement the following task spec safely:\n\n{task_spec}"
