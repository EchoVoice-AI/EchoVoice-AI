# Assignment Agent Quick Reference

## TL;DR

The **A/B Assignment Agent** deterministically assigns users to variants using MD5 hashing.

```python
from agents.generator import ABAssignmentAgent

# Create agent
agent = ABAssignmentAgent(split_ratio={"A": 0.5, "B": 0.5})

# Assign user
assignment = agent.assign_user("U123", "exp_001")

# Result: {"variant_id": "A", "hash_value": 0.234, ...}
```

---

## Key Properties

| Property | Value |
|----------|-------|
| **Deterministic** | ✅ Same user always gets same variant |
| **No External State** | ✅ No database/Redis required |
| **Split Ratio Support** | ✅ 50/50, 70/30, 90/10, custom |
| **Multi-Variant** | ✅ Works with A/B, A/B/C, A/B/C/D, etc. |
| **Auditable** | ✅ Full decision logging |
| **Fast** | ✅ < 0.2ms per assignment |
| **Testable** | ✅ 33 passing tests |

---

## Common Use Cases

### 1. Simple 50/50 Split

```python
agent = ABAssignmentAgent()  # Default is 50/50
assignment = agent.assign_user("U123", "exp_001")
```

### 2. Weighted Split (70/30)

```python
agent = ABAssignmentAgent({"A": 0.7, "B": 0.3})
assignment = agent.assign_user("U123", "exp_001")
```

### 3. Multi-Variant (A/B/C)

```python
agent = ABAssignmentAgent({
    "A": 0.5,  # Control
    "B": 0.3,  # Test 1
    "C": 0.2   # Test 2
})
assignment = agent.assign_user("U123", "exp_001")
```

### 4. With Context (for tracking)

```python
assignment = agent.assign_user(
    "U123", "exp_001",
    context={"email": "user@example.com", "segment": "high_intent"}
)
```

### 5. In Variant Generation

The assignment is already integrated into `generate_variants()`:

```python
variants = generate_variants(customer, segment, citations)
# Each variant includes: variant['assignment']['assigned']
```

---

## Result Structure

```python
{
    "variant_id": "A",                          # Assigned variant
    "hash_value": 0.234567,                     # Hash value [0.0, 1.0]
    "threshold": (0.0, 0.5),                    # Variant's hash range
    "experiment_id": "exp_personalization_001",
    "user_id": "U123",
    "strategy": "md5_hash",
    "deterministic": True,
    "split_ratio": {"A": 0.5, "B": 0.5},
    "context": {}
}
```

---

## Determinism Guarantee

```python
agent = ABAssignmentAgent(seed="echovoice")

# Same inputs = same output
a1 = agent.assign_user("U123", "exp_001")
a2 = agent.assign_user("U123", "exp_001")

assert a1["variant_id"] == a2["variant_id"]  # ✓ Always true
```

---

## Distribution Verification

```python
# Test that split ratio is enforced
assignments = [
    agent.assign_user(f"U{i}", "exp_001")
    for i in range(1000)
]

a_count = sum(1 for a in assignments if a["variant_id"] == "A")
ratio = a_count / 1000

print(f"A ratio: {ratio}")  # ~0.5 for 50/50 split
```

---

## Microsoft Services Hooks

### App Insights (Development Mode)

```python
from agents.generator import MicrosoftServicesAdapter

assignment = agent.assign_user("U123", "exp_001")
MicrosoftServicesAdapter.log_assignment_to_app_insights(assignment)
# Prints: [App Insights Hook] Assignment: {...}
```

### Kusto Logging (Development Mode)

```python
MicrosoftServicesAdapter.log_assignment_to_kusto(assignment)
# Prints: [Kusto Hook] Assignment: {...}
```

### Service Bus (Development Mode)

```python
MicrosoftServicesAdapter.publish_assignment_event(assignment)
# Prints: [Service Bus Hook] Assignment Event: {...}
```

---

## Testing

Run the test suite:

```bash
cd backend
pytest tests/test_assignment_agent.py -v

# Result: 33 passed in 0.07s ✓
```

---

## Validation

```python
# Validate assignment result
is_valid, error = agent.validate_assignment(assignment)

if is_valid:
    print("✓ Assignment is valid")
else:
    print(f"✗ Error: {error}")
```

---

## Performance

| Operation | Time |
|-----------|------|
| Hash computation | < 0.1 ms |
| Assignment | < 0.2 ms |
| Per-request overhead | ~2.5 KB memory |

---

## Integration Points

### 1. In `generate_variants()`

```python
# Already integrated! No additional code needed.
variants = generate_variants(customer, segment, citations)
# Each variant includes assignment info
```

### 2. Custom Usage

```python
from agents.generator import ABAssignmentAgent

agent = ABAssignmentAgent({"A": 0.6, "B": 0.4})
assignment = agent.assign_user(user_id, experiment_id)

# Use assignment.variant_id to select message variant
selected_variant = select_variant_by_id(assignment["variant_id"])
```

---

## Troubleshooting

**Q: All users get same variant?**  
A: Check split_ratio sums to 1.0:
```python
# ❌ Wrong: sums to 0.9
agent = ABAssignmentAgent({"A": 0.5, "B": 0.4})

# ✅ Correct: sums to 1.0
agent = ABAssignmentAgent({"A": 0.5, "B": 0.5})
```

**Q: Assignment not repeatable?**  
A: Use same seed and experiment_id:
```python
# ✓ Will be identical
a1 = agent.assign_user("U123", "exp_001")
a2 = agent.assign_user("U123", "exp_001")

# ✗ Will differ (different experiment)
a3 = agent.assign_user("U123", "exp_002")
```

**Q: How do I get 70/30 split?**  
A:
```python
agent = ABAssignmentAgent({"A": 0.7, "B": 0.3})
```

---

## Documentation

- **Full Docs:** `backend/docs/assignment_agent.md`
- **Tests:** `backend/tests/test_assignment_agent.py`
- **Code:** `backend/agents/generator.py`

---

## Next Steps

1. ✅ Basic MD5 assignment (DONE)
2. 🔄 Azure App Insights integration (hooks ready)
3. 🔄 Kusto telemetry (hooks ready)
4. 🔄 Service Bus event publishing (hooks ready)
5. 🔄 Advanced strategies (ROUND_ROBIN, RANDOM)
6. 🔄 Contextual assignment (by customer attributes)
7. 🔄 Bandit algorithm (adaptive allocation)

---

**Last Updated:** November 2025  
**Status:** Production Ready ✓
