import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class AssignmentStrategy(Enum):
    """Enum for different assignment strategies."""
    MD5_HASH = "md5_hash"
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"


class ABAssignmentAgent:
    """
    Deterministic A/B assignment agent using MD5 hashing.
    
    Features:
    - Deterministic assignment (same user always gets same variant)
    - Configurable split ratios (50/50, 70/30, custom)
    - Support for multi-variant assignment (A/B/C/etc.)
    - Microsoft Services integration hooks
    - Audit logging for assignment decisions
    
    Example:
        agent = ABAssignmentAgent(split_ratio={"A": 0.5, "B": 0.5})
        assignment = agent.assign_user("U123", "experiment_001")
        # Returns: {"variant_id": "A", "hash_value": 0.234, "ratio": 0.5, ...}
    """
    
    def __init__(
        self,
        split_ratio: Optional[Dict[str, float]] = None,
        strategy: AssignmentStrategy = AssignmentStrategy.MD5_HASH,
        seed: str = "echovoice",
    ):
        """
        Initialize the assignment agent.
        
        Args:
            split_ratio: Dict mapping variant IDs to split ratios.
                         Must sum to 1.0. Default: {"A": 0.5, "B": 0.5}
            strategy: Assignment strategy (MD5_HASH, ROUND_ROBIN, RANDOM)
            seed: Seed value for hashing (default: "echovoice")
        
        Raises:
            ValueError: If split_ratio doesn't sum to 1.0
        """
        self.strategy = strategy
        self.seed = seed
        
        # Set default split ratio if not provided
        if split_ratio is None:
            self.split_ratio = {"A": 0.5, "B": 0.5}
        else:
            self.split_ratio = split_ratio
        
        # Validate split ratio sums to 1.0
        total = sum(self.split_ratio.values())
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ValueError(
                f"Split ratios must sum to 1.0, got {total}. "
                f"Provided: {self.split_ratio}"
            )
        
        # Sort variant IDs for consistent ordering
        self.variant_ids = sorted(self.split_ratio.keys())
        
        # Compute cumulative thresholds for assignment
        self.thresholds = self._compute_thresholds()
    
    def _compute_thresholds(self) -> Dict[str, Tuple[float, float]]:
        """
        Compute cumulative thresholds for each variant.
        
        Returns:
            Dict mapping variant_id to (lower_bound, upper_bound) tuple.
            
        Example:
            split_ratio: {"A": 0.5, "B": 0.3, "C": 0.2}
            thresholds: {"A": (0.0, 0.5), "B": (0.5, 0.8), "C": (0.8, 1.0)}
        """
        thresholds = {}
        lower_bound = 0.0
        
        for variant_id in self.variant_ids:
            ratio = self.split_ratio[variant_id]
            upper_bound = lower_bound + ratio
            thresholds[variant_id] = (lower_bound, upper_bound)
            lower_bound = upper_bound
        
        return thresholds
    
    def _compute_hash_value(self, user_id: str, experiment_id: str) -> float:
        """
        Compute deterministic hash value for user assignment.
        
        Uses MD5 hash of (seed + experiment_id + user_id) to generate
        a deterministic float between 0.0 and 1.0.
        
        Args:
            user_id: Unique user identifier
            experiment_id: Experiment identifier
        
        Returns:
            Float between 0.0 and 1.0
        """
        # Combine seed, experiment_id, and user_id for hashing
        hash_input = f"{self.seed}:{experiment_id}:{user_id}"
        
        # Create MD5 hash
        md5_hash = hashlib.md5(hash_input.encode()).hexdigest()
        
        # Convert first 8 chars of hex to integer, then normalize to 0-1
        hash_int = int(md5_hash[:8], 16)
        hash_value = (hash_int % 1000000) / 1000000.0
        
        return hash_value
    
    def assign_user(
        self,
        user_id: str,
        experiment_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Assign a user to a variant deterministically.
        
        Args:
            user_id: Unique user identifier
            experiment_id: Experiment identifier
            context: Optional context dict for logging (customer, segment, etc.)
        
        Returns:
            Dict with assignment details:
            {
                "variant_id": "A",
                "hash_value": 0.234,
                "threshold": (0.0, 0.5),
                "experiment_id": "exp_001",
                "user_id": "U123",
                "strategy": "md5_hash",
                "deterministic": True,
                "context": {...}
            }
        """
        # Compute hash value
        hash_value = self._compute_hash_value(user_id, experiment_id)
        
        # Determine assigned variant based on hash value
        assigned_variant = None
        for variant_id, (lower, upper) in self.thresholds.items():
            if lower <= hash_value < upper:
                assigned_variant = variant_id
                break
        
        # Fallback to last variant if rounding error occurs
        if assigned_variant is None:
            assigned_variant = self.variant_ids[-1]
        
        return {
            "variant_id": assigned_variant,
            "hash_value": round(hash_value, 6),
            "threshold": self.thresholds[assigned_variant],
            "experiment_id": experiment_id,
            "user_id": user_id,
            "strategy": self.strategy.value,
            "deterministic": True,
            "split_ratio": self.split_ratio.copy(),
            "context": context or {},
        }
    
    def validate_assignment(
        self,
        assignment: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an assignment result.
        
        Args:
            assignment: Assignment dict from assign_user()
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ["variant_id", "hash_value", "experiment_id", "user_id"]
        for field in required_fields:
            if field not in assignment:
                return False, f"Missing required field: {field}"
        
        if assignment["variant_id"] not in self.variant_ids:
            return False, f"Invalid variant_id: {assignment['variant_id']}"
        
        if not (0.0 <= assignment["hash_value"] <= 1.0):
            return False, f"Hash value out of range: {assignment['hash_value']}"
        
        return True, None


# Microsoft Services Integration Hooks
class MicrosoftServicesAdapter:
    """
    Adapter for integrating with Microsoft services.
    
    Currently provides hooks for:
    - Azure Application Insights (tracking)
    - Azure Data Explorer (Kusto) (logging)
    - Azure Service Bus (event streaming)
    
    Future implementations will replace these hooks.
    """
    
    @staticmethod
    def log_assignment_to_app_insights(
        assignment: Dict[str, Any],
        instrumentation_key: Optional[str] = None,
    ) -> bool:
        """
        Log assignment to Azure Application Insights.
        
        Args:
            assignment: Assignment dict from ABAssignmentAgent.assign_user()
            instrumentation_key: App Insights instrumentation key
        
        Returns:
            True if logging successful, False otherwise
        
        Future:
            from azure.monitor.opentelemetry import AzureMonitorTraceExporter
            tracer.add_span_processor(...)
        """
        if instrumentation_key is None:
            # Development mode: just print
            print(f"[App Insights Hook] Assignment: {assignment}")
            return True
        
        # TODO: Implement real Azure App Insights logging
        # from applicationinsights import TelemetryClient
        # tc = TelemetryClient(instrumentation_key)
        # tc.track_event('assignment', assignment)
        
        return True
    
    @staticmethod
    def log_assignment_to_kusto(
        assignment: Dict[str, Any],
        cluster_uri: Optional[str] = None,
        database: str = "echovoice",
    ) -> bool:
        """
        Log assignment to Azure Data Explorer (Kusto).
        
        Args:
            assignment: Assignment dict from ABAssignmentAgent.assign_user()
            cluster_uri: Kusto cluster URI
            database: Database name
        
        Returns:
            True if logging successful, False otherwise
        
        Future:
            from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
            kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(...)
            client = KustoClient(kcsb)
            client.execute_query(database, "insert_assignment_table", ...)
        """
        if cluster_uri is None:
            # Development mode: just print
            print(f"[Kusto Hook] Assignment: {assignment}")
            return True
        
        # TODO: Implement real Azure Data Explorer logging
        
        return True
    
    @staticmethod
    def publish_assignment_event(
        assignment: Dict[str, Any],
        connection_string: Optional[str] = None,
        queue_name: str = "assignment-events",
    ) -> bool:
        """
        Publish assignment event to Azure Service Bus.
        
        Args:
            assignment: Assignment dict from ABAssignmentAgent.assign_user()
            connection_string: Service Bus connection string
            queue_name: Queue name
        
        Returns:
            True if published successfully, False otherwise
        
        Future:
            from azure.servicebus import ServiceBusClient
            with ServiceBusClient.from_connection_string(connection_string) as client:
                sender = client.get_queue_sender(queue_name)
                sender.send_messages(...)
        """
        if connection_string is None:
            # Development mode: just print
            print(f"[Service Bus Hook] Assignment Event: {assignment}")
            return True
        
        # TODO: Implement real Azure Service Bus publishing
        
        return True


def generate_variants(customer: dict, segment: dict, citations: list) -> list:
    """
    Generate A/B/n message variants for a customer.
    
    Uses deterministic MD5-based assignment to ensure consistent variant
    assignment across requests for the same customer in the same experiment.
    
    Args:
        customer: Customer profile dict with keys: id, email, name, etc.
        segment: Segment info dict with keys: segment, intent_level, etc.
        citations: List of citation dicts from retriever
    
    Returns:
        List of variant dicts with keys: id, subject, body, meta, assignment
    """
    # Extract customer info
    name = customer.get('name', 'Customer')
    user_id = customer.get('id') or customer.get('user_id') or 'unknown'
    seg_label = segment.get('segment', 'our offering')
    
    # Extract citation text
    citation_text = ''
    if citations:
        first = citations[0]
        citation_text = first.get('content') or first.get('text') or first.get('redacted_text') or ''
    
    # Initialize assignment agent with 50/50 split
    assignment_agent = ABAssignmentAgent(
        split_ratio={"A": 0.5, "B": 0.5},
        strategy=AssignmentStrategy.MD5_HASH,
        seed="echovoice",
    )
    
    # Assign user to variant
    assignment = assignment_agent.assign_user(
        user_id=user_id,
        experiment_id="exp_personalization_001",
        context={
            "customer_id": user_id,
            "email": customer.get('email'),
            "segment": seg_label,
        }
    )
    
    # Log to Microsoft services (hooks for future integration)
    MicrosoftServicesAdapter.log_assignment_to_app_insights(assignment)
    MicrosoftServicesAdapter.publish_assignment_event(assignment)
    
    # Generate variants
    variants = []
    variants.append({
        'id': 'A',
        'subject': f"Hi {name}, quick note about {seg_label}",
        'body': f"Hi {name},\n\nWe thought you might like this: {citation_text}\n\n— Team",
        'meta': {
            'type': 'short',
            'tone': 'friendly',
            'length_words': 45,
        },
        'assignment': {
            'assigned': assignment['variant_id'] == 'A',
            'hash_value': assignment['hash_value'],
            'experiment_id': assignment['experiment_id'],
        }
    })
    variants.append({
        'id': 'B',
        'subject': f"{name}, more on the {seg_label}",
        'body': f"Hello {name},\n\nDetails: {citation_text}\nLearn more on our site.",
        'meta': {
            'type': 'long',
            'tone': 'professional',
            'length_words': 120,
        },
        'assignment': {
            'assigned': assignment['variant_id'] == 'B',
            'hash_value': assignment['hash_value'],
            'experiment_id': assignment['experiment_id'],
        }
    })
    
    return variants

