def judge_run(test_ok: bool, codex_code: int) -> dict:
    passed = test_ok and codex_code == 0
    return {"passed": passed, "reason": "all checks passed" if passed else "execution or tests failed"}
