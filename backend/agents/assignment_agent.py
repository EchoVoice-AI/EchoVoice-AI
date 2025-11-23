from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class AssignmentStrategy(Enum):
    MD5_HASH = "md5_hash"
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"


class ABAssignmentAgent:
    """
    Deterministic A/B (multi-variant) assignment agent using MD5 hashing.

    Example:
        agent = ABAssignmentAgent(split_ratio={"A":0.5,"B":0.5}, seed="echovoice")
        assignment = agent.assign_user("U123", "exp_001", context={"email": "x@x.com"})
    """

    def __init__(
        self,
        split_ratio: Optional[Dict[str, float]] = None,
        seed: str = "echovoice",
        strategy: AssignmentStrategy = AssignmentStrategy.MD5_HASH,
    ):
        if split_ratio is None:
            split_ratio = {"A": 0.5, "B": 0.5}
        self.split_ratio = dict(split_ratio)
        self._validate_split_ratio()
        self.variant_ids = list(self.split_ratio.keys())
        self.thresholds = self._compute_thresholds()
        self.seed = seed
        self.strategy = strategy

    def _validate_split_ratio(self) -> None:
        total = sum(self.split_ratio.values())
        if not (0.999 <= total <= 1.001):
            raise ValueError("split_ratio values must sum to 1.0")
        for k, v in self.split_ratio.items():
            if v <= 0 or v > 1:
                raise ValueError(f"Invalid split fraction for {k}: {v}")

    def _compute_thresholds(self) -> List[Tuple[str, float]]:
        thresholds: List[Tuple[str, float]] = []
        cum = 0.0
        for vid in self.variant_ids:
            cum += float(self.split_ratio[vid])
            thresholds.append((vid, cum))
        return thresholds

    def _compute_hash_value(self, user_id: str, experiment_id: str) -> float:
        """
        Deterministic hash in [0.0, 1.0).

        Uses md5(seed + experiment_id + user_id) normalized to [0,1).
        """
        key = f"{self.seed}:{experiment_id}:{user_id}"
        digest = hashlib.md5(key.encode("utf-8")).hexdigest()
        truncated = int(digest[:15], 16)
        max_val = float(int("f" * 15, 16))
        return truncated / max_val

    def assign_user(
        self,
        user_id: str,
        experiment_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if self.strategy != AssignmentStrategy.MD5_HASH:
            raise NotImplementedError(f"Strategy {self.strategy} not implemented")

        hash_value = self._compute_hash_value(user_id, experiment_id)
        chosen_variant = None
        for vid, upper in self.thresholds:
            if hash_value < upper:
                chosen_variant = vid
                break
        if chosen_variant is None:
            chosen_variant = self.variant_ids[-1]

        assignment = {
            "variant_id": chosen_variant,
            "hash_value": hash_value,
            "experiment_id": experiment_id,
            "user_id": user_id,
            "context": context,
            "deterministic": True,
        }

        return assignment

    def validate_assignment(self, assignment: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        required = {"variant_id", "hash_value", "experiment_id", "user_id"}
        missing = required - set(assignment.keys())
        if missing:
            return False, f"Missing required field(s): {', '.join(sorted(missing))}"
        if assignment["variant_id"] not in self.variant_ids:
            return False, "Invalid variant_id"
        hv = assignment["hash_value"]
        if not isinstance(hv, (int, float)) or not (0.0 <= hv < 1.0):
            return False, "hash_value out of range [0.0, 1.0)"
        return True, None


class MicrosoftServicesAdapter:
    """
    Development-friendly hooks for Azure integrations (App Insights, Kusto, Service Bus).
    Replace prints with real SDK calls when deploying to Azure.
    """

    @staticmethod
    def log_assignment_to_app_insights(
        assignment: Dict[str, Any],
        instrumentation_key: Optional[str] = None,
    ) -> bool:
        if instrumentation_key is None:
            print(f"[App Insights Hook] Assignment: {json.dumps(assignment)}")
            return True
        return True

    @staticmethod
    def log_assignment_to_kusto(
        assignment: Dict[str, Any],
        cluster_uri: Optional[str] = None,
        database: str = "echovoice",
    ) -> bool:
        if cluster_uri is None:
            print(f"[Kusto Hook] Assignment: {json.dumps(assignment)}")
            return True
        return True

    @staticmethod
    def publish_assignment_event(
        assignment: Dict[str, Any],
        connection_string: Optional[str] = None,
        queue_name: str = "assignment-events",
    ) -> bool:
        if connection_string is None:
            print(f"[Service Bus Hook] Assignment Event: {json.dumps(assignment)}")
            return True
        return True
