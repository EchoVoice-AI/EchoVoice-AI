from __future__ import annotations

from typing import Any, Dict, Optional

from .base_node import BaseNode
from agents.assignment_agent import ABAssignmentAgent


class AssignmentNode(BaseNode):
    """
    Thin adapter node to assign a user for an experiment.

    Expected input:
      {
        "user_id": "...",
        "experiment_id": "...",
        "context": {...}  # optional
      }

    Returns:
      assignment dict (see ABAssignmentAgent.assign_user)
    """

    def __init__(self, name: str = "assignment", agent: Optional[ABAssignmentAgent] = None):
        super().__init__(name)
        self.agent = agent or ABAssignmentAgent()

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = data.get("user_id") or data.get("customer", {}).get("id")
        experiment_id = data.get("experiment_id") or data.get("exp_id") or "exp_default"
        context = data.get("context")
        return self.agent.assign_user(user_id, experiment_id, context=context)
