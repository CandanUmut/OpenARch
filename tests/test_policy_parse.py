from repo_agent.policies.policy_schema import RepoPolicy


def test_policy_defaults():
    p = RepoPolicy.model_validate({"repo": "owner/name", "jobs": {"polish": {}}})
    assert p.merge.auto_merge is False
    assert p.loop.max_fail_iterations == 2
