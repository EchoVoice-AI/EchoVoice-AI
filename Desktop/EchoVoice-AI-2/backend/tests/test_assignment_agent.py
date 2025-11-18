"""
Tests for the A/B Assignment Agent.

Tests deterministic assignment using MD5 hashing, split ratios,
and Microsoft Services integration hooks.
"""

import pytest
from agents.generator import (
    ABAssignmentAgent,
    AssignmentStrategy,
    MicrosoftServicesAdapter,
    generate_variants,
)


class TestABAssignmentAgent:
    """Test suite for ABAssignmentAgent."""

    def test_init_default_split_ratio(self):
        """Test initialization with default 50/50 split."""
        agent = ABAssignmentAgent()
        assert agent.split_ratio == {"A": 0.5, "B": 0.5}
        assert agent.variant_ids == ["A", "B"]

    def test_init_custom_split_ratio(self):
        """Test initialization with custom split ratio."""
        agent = ABAssignmentAgent(split_ratio={"A": 0.7, "B": 0.3})
        assert agent.split_ratio == {"A": 0.7, "B": 0.3}

    def test_init_multi_variant(self):
        """Test initialization with 3+ variants."""
        agent = ABAssignmentAgent(
            split_ratio={"A": 0.5, "B": 0.3, "C": 0.2}
        )
        assert len(agent.variant_ids) == 3
        assert agent.variant_ids == ["A", "B", "C"]

    def test_init_invalid_split_ratio(self):
        """Test that invalid split ratios raise ValueError."""
        with pytest.raises(ValueError, match="must sum to 1.0"):
            ABAssignmentAgent(split_ratio={"A": 0.5, "B": 0.3})

    def test_compute_thresholds(self):
        """Test threshold computation."""
        agent = ABAssignmentAgent(
            split_ratio={"A": 0.5, "B": 0.3, "C": 0.2}
        )
        thresholds = agent.thresholds
        
        assert thresholds["A"] == (0.0, 0.5)
        assert thresholds["B"] == (0.5, 0.8)
        assert thresholds["C"] == (0.8, 1.0)

    def test_compute_hash_value_deterministic(self):
        """Test that hash computation is deterministic."""
        agent = ABAssignmentAgent()
        
        hash1 = agent._compute_hash_value("U123", "exp_001")
        hash2 = agent._compute_hash_value("U123", "exp_001")
        
        assert hash1 == hash2
        assert 0.0 <= hash1 <= 1.0

    def test_compute_hash_value_different_users(self):
        """Test that different users get different hash values."""
        agent = ABAssignmentAgent()
        
        hash1 = agent._compute_hash_value("U123", "exp_001")
        hash2 = agent._compute_hash_value("U456", "exp_001")
        
        assert hash1 != hash2

    def test_compute_hash_value_different_experiments(self):
        """Test that different experiments produce different hashes for same user."""
        agent = ABAssignmentAgent()
        
        hash1 = agent._compute_hash_value("U123", "exp_001")
        hash2 = agent._compute_hash_value("U123", "exp_002")
        
        assert hash1 != hash2

    def test_assign_user_returns_dict(self):
        """Test that assign_user returns a proper dict."""
        agent = ABAssignmentAgent()
        assignment = agent.assign_user("U123", "exp_001")
        
        assert isinstance(assignment, dict)
        assert "variant_id" in assignment
        assert "hash_value" in assignment
        assert "experiment_id" in assignment
        assert "user_id" in assignment

    def test_assign_user_deterministic(self):
        """Test that same user always gets same variant in same experiment."""
        agent = ABAssignmentAgent()
        
        assignment1 = agent.assign_user("U123", "exp_001")
        assignment2 = agent.assign_user("U123", "exp_001")
        
        assert assignment1["variant_id"] == assignment2["variant_id"]
        assert assignment1["hash_value"] == assignment2["hash_value"]

    def test_assign_user_respects_split_ratio(self):
        """Test that assignments roughly follow split ratio."""
        agent = ABAssignmentAgent(split_ratio={"A": 0.7, "B": 0.3})
        
        # Generate 1000 assignments for different users
        assignments = [
            agent.assign_user(f"U{i}", "exp_001")
            for i in range(1000)
        ]
        
        a_count = sum(1 for a in assignments if a["variant_id"] == "A")
        b_count = sum(1 for a in assignments if a["variant_id"] == "B")
        
        # Check that split is roughly 70/30 (with 5% tolerance)
        a_ratio = a_count / len(assignments)
        assert 0.65 <= a_ratio <= 0.75, f"A ratio {a_ratio} not near 0.7"

    def test_assign_user_with_context(self):
        """Test that context is included in assignment."""
        agent = ABAssignmentAgent()
        context = {
            "customer_id": "U123",
            "email": "user@example.com",
            "segment": "high_intent",
        }
        
        assignment = agent.assign_user(
            "U123", "exp_001",
            context=context
        )
        
        assert assignment["context"] == context

    def test_validate_assignment_valid(self):
        """Test validation of valid assignment."""
        agent = ABAssignmentAgent()
        assignment = agent.assign_user("U123", "exp_001")
        
        is_valid, error = agent.validate_assignment(assignment)
        assert is_valid is True
        assert error is None

    def test_validate_assignment_missing_field(self):
        """Test validation fails for missing field."""
        agent = ABAssignmentAgent()
        assignment = {
            "variant_id": "A",
            "hash_value": 0.5,
            # Missing experiment_id and user_id
        }
        
        is_valid, error = agent.validate_assignment(assignment)
        assert is_valid is False
        assert "Missing required field" in error

    def test_validate_assignment_invalid_variant(self):
        """Test validation fails for invalid variant ID."""
        agent = ABAssignmentAgent()
        assignment = {
            "variant_id": "Z",  # Invalid
            "hash_value": 0.5,
            "experiment_id": "exp_001",
            "user_id": "U123",
        }
        
        is_valid, error = agent.validate_assignment(assignment)
        assert is_valid is False
        assert "Invalid variant_id" in error

    def test_validate_assignment_out_of_range_hash(self):
        """Test validation fails for hash value out of range."""
        agent = ABAssignmentAgent()
        assignment = {
            "variant_id": "A",
            "hash_value": 1.5,  # Out of range
            "experiment_id": "exp_001",
            "user_id": "U123",
        }
        
        is_valid, error = agent.validate_assignment(assignment)
        assert is_valid is False
        assert "out of range" in error

    def test_strategy_enum(self):
        """Test that AssignmentStrategy enum works."""
        assert AssignmentStrategy.MD5_HASH.value == "md5_hash"
        assert AssignmentStrategy.ROUND_ROBIN.value == "round_robin"
        assert AssignmentStrategy.RANDOM.value == "random"

    def test_custom_seed(self):
        """Test that custom seed produces different hashes."""
        agent1 = ABAssignmentAgent(seed="seed1")
        agent2 = ABAssignmentAgent(seed="seed2")
        
        hash1 = agent1._compute_hash_value("U123", "exp_001")
        hash2 = agent2._compute_hash_value("U123", "exp_001")
        
        assert hash1 != hash2


class TestMicrosoftServicesAdapter:
    """Test suite for MicrosoftServicesAdapter."""

    def test_log_assignment_to_app_insights_no_key(self, capsys):
        """Test logging to App Insights without key (dev mode)."""
        assignment = {"variant_id": "A", "hash_value": 0.5}
        
        result = MicrosoftServicesAdapter.log_assignment_to_app_insights(
            assignment
        )
        
        assert result is True
        captured = capsys.readouterr()
        assert "[App Insights Hook]" in captured.out

    def test_log_assignment_to_kusto_no_uri(self, capsys):
        """Test logging to Kusto without URI (dev mode)."""
        assignment = {"variant_id": "A", "hash_value": 0.5}
        
        result = MicrosoftServicesAdapter.log_assignment_to_kusto(assignment)
        
        assert result is True
        captured = capsys.readouterr()
        assert "[Kusto Hook]" in captured.out

    def test_publish_assignment_event_no_connection(self, capsys):
        """Test publishing event without connection string (dev mode)."""
        assignment = {"variant_id": "A", "hash_value": 0.5}
        
        result = MicrosoftServicesAdapter.publish_assignment_event(assignment)
        
        assert result is True
        captured = capsys.readouterr()
        assert "[Service Bus Hook]" in captured.out


class TestGenerateVariantsWithAssignment:
    """Test suite for generate_variants with A/B assignment."""

    def test_generate_variants_returns_list(self):
        """Test that generate_variants returns a list."""
        customer = {"id": "U123", "name": "John"}
        segment = {"segment": "payment_plans"}
        citations = []
        
        variants = generate_variants(customer, segment, citations)
        
        assert isinstance(variants, list)
        assert len(variants) == 2

    def test_generate_variants_has_assignment_info(self):
        """Test that variants include assignment information."""
        customer = {"id": "U123", "name": "John"}
        segment = {"segment": "payment_plans"}
        citations = []
        
        variants = generate_variants(customer, segment, citations)
        
        for variant in variants:
            assert "assignment" in variant
            assert "assigned" in variant["assignment"]
            assert "hash_value" in variant["assignment"]
            assert "experiment_id" in variant["assignment"]

    def test_generate_variants_exactly_one_assigned(self):
        """Test that exactly one variant is marked as assigned."""
        customer = {"id": "U123", "name": "John"}
        segment = {"segment": "payment_plans"}
        citations = []
        
        variants = generate_variants(customer, segment, citations)
        
        assigned_count = sum(
            1 for v in variants if v["assignment"]["assigned"]
        )
        assert assigned_count == 1

    def test_generate_variants_deterministic_assignment(self):
        """Test that same customer gets same assignment twice."""
        customer = {"id": "U123", "name": "John"}
        segment = {"segment": "payment_plans"}
        citations = []
        
        variants1 = generate_variants(customer, segment, citations)
        variants2 = generate_variants(customer, segment, citations)
        
        # Find assigned variants
        assigned1 = next(v for v in variants1 if v["assignment"]["assigned"])
        assigned2 = next(v for v in variants2 if v["assignment"]["assigned"])
        
        assert assigned1["id"] == assigned2["id"]
        assert assigned1["assignment"]["hash_value"] == assigned2["assignment"]["hash_value"]

    def test_generate_variants_different_users(self):
        """Test that different users may get different assignments."""
        segment = {"segment": "payment_plans"}
        citations = []
        
        customer1 = {"id": "U123", "name": "John"}
        customer2 = {"id": "U456", "name": "Jane"}
        
        variants1 = generate_variants(customer1, segment, citations)
        variants2 = generate_variants(customer2, segment, citations)
        
        assigned1 = next(v for v in variants1 if v["assignment"]["assigned"])
        assigned2 = next(v for v in variants2 if v["assignment"]["assigned"])
        
        # Different users may get different variants (probabilistically)
        # Just ensure both are valid
        assert assigned1["id"] in ["A", "B"]
        assert assigned2["id"] in ["A", "B"]

    def test_generate_variants_with_citations(self):
        """Test variant generation with citations included."""
        customer = {"id": "U123", "name": "John"}
        segment = {"segment": "payment_plans"}
        citations = [
            {
                "text": "Plan options include Basic ($9/mo), Pro ($19/mo)",
                "title": "Payment Plans",
            }
        ]
        
        variants = generate_variants(customer, segment, citations)
        
        assert len(variants) == 2
        for variant in variants:
            assert "Plan options" in variant["body"]

    def test_generate_variants_missing_customer_id(self):
        """Test variant generation when customer ID is missing."""
        customer = {"name": "John"}  # No id field
        segment = {"segment": "payment_plans"}
        citations = []
        
        # Should not raise, should use 'unknown' as fallback
        variants = generate_variants(customer, segment, citations)
        
        assert len(variants) == 2

    def test_generate_variants_metadata(self):
        """Test that variants include proper metadata."""
        customer = {"id": "U123", "name": "John"}
        segment = {"segment": "payment_plans"}
        citations = []
        
        variants = generate_variants(customer, segment, citations)
        
        # Variant A should be short
        variant_a = next(v for v in variants if v["id"] == "A")
        assert variant_a["meta"]["type"] == "short"
        assert variant_a["meta"]["tone"] == "friendly"
        
        # Variant B should be long
        variant_b = next(v for v in variants if v["id"] == "B")
        assert variant_b["meta"]["type"] == "long"
        assert variant_b["meta"]["tone"] == "professional"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_split_ratio_rounding_tolerance(self):
        """Test that small floating point errors in split ratio are tolerated."""
        # This should not raise due to floating point arithmetic
        agent = ABAssignmentAgent(
            split_ratio={"A": 0.333333, "B": 0.333334, "C": 0.333333}
        )
        assert agent is not None

    def test_empty_citation_handling(self):
        """Test that empty citations are handled gracefully."""
        customer = {"id": "U123", "name": "John"}
        segment = {"segment": "payment_plans"}
        citations = []
        
        variants = generate_variants(customer, segment, citations)
        
        # Should still generate variants even with no citations
        assert len(variants) == 2
        assert all("subject" in v for v in variants)
        assert all("body" in v for v in variants)

    def test_special_characters_in_user_id(self):
        """Test that special characters in user ID are handled."""
        agent = ABAssignmentAgent()
        
        assignment = agent.assign_user(
            "user@example.com:U123!",
            "exp_001"
        )
        
        assert assignment["variant_id"] in ["A", "B"]
        assert assignment["hash_value"] is not None

    def test_very_long_user_id(self):
        """Test that very long user IDs are handled."""
        agent = ABAssignmentAgent()
        long_user_id = "U" * 10000
        
        assignment = agent.assign_user(long_user_id, "exp_001")
        
        assert assignment["variant_id"] in ["A", "B"]
