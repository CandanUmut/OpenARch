from datetime import datetime, timedelta
from repo_agent.executor.loop_controller import LoopController


def test_loop_stop_max_iterations():
    lc = LoopController()
    d = lc.should_continue(3, datetime.utcnow(), hours=None, max_iterations=3)
    assert d.continue_loop is False
    assert d.reason == "max_iterations"


def test_loop_stop_hours():
    lc = LoopController()
    d = lc.should_continue(0, datetime.utcnow() - timedelta(hours=2), hours=1, max_iterations=None)
    assert d.continue_loop is False
