from backend.agents.assignment_agent import ABAssignmentAgent


def test_assignment_deterministic():
    agent = ABAssignmentAgent(split_ratio={"A": 0.5, "B": 0.5}, seed="test-seed")
    a1 = agent.assign_user("user123", "exp_x")
    a2 = agent.assign_user("user123", "exp_x")
    assert a1["variant_id"] == a2["variant_id"]
    assert a1["experiment_id"] == "exp_x"
    assert 0.0 <= a1["hash_value"] < 1.0


def test_validate_assignment():
    agent = ABAssignmentAgent(split_ratio={"A": 0.7, "B": 0.3})
    assignment = agent.assign_user("u1", "exp1")
    ok, err = agent.validate_assignment(assignment)
    assert ok and err is None
