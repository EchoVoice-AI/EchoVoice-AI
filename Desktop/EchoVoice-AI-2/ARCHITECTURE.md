# EchoVoice Architecture & Design Document

**Version:** 1.0  
**Last Updated:** November 2025  
**Status:** Production-Ready Scaffold

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Patterns](#architecture-patterns)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)
6. [State Management](#state-management)
7. [Safety & Compliance](#safety--compliance)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Architecture](#deployment-architecture)
10. [Scalability & Performance](#scalability--performance)

---

## Executive Summary

**EchoVoice** is a production-grade multi-agent orchestration platform for compliant, personalized customer communication in regulated industries.

### Why This Architecture?

**Problem:** Traditional monolithic personalization systems struggle with:
- ❌ Auditability (black-box decision-making)
- ❌ Compliance (no safety gates)
- ❌ Flexibility (tightly coupled components)
- ❌ Transparency (hard to explain decisions)

**Solution:** Modular multi-agent architecture where:
- ✅ Each agent has a single responsibility
- ✅ Every decision step is logged and inspectable
- ✅ Safety gates prevent non-compliant messages
- ✅ Full audit trail for regulatory compliance

### Key Design Principles

1. **Modularity:** Agents are independent, testable, replaceable
2. **Transparency:** Every decision is recorded and explainable
3. **Safety First:** Multiple validation gates before delivery
4. **Observability:** Structured logging at each step
5. **Testability:** All paths covered by unit and integration tests

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  (Web, Mobile, API, Event Stream)                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              FASTAPI APPLICATION SERVER                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  HTTP Routers:                                           │   │
│  │  • /health         - Server health check                │   │
│  │  • /personalize    - Main orchestrator endpoint         │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR (Coordinator)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Orchestrator.run_flow()                                  │   │
│  │ Executes pipeline:                                       │   │
│  │  1. Segment → 2. Retrieve → 3. Generate → 4. Safety    │   │
│  │  5. Analyze → 6. Deliver                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────┬──────────────────────────────────────────┬───────────┘
           │                                          │
    ┌──────▼──────┬──────────────┬──────────┬────────▼────┐
    │              │              │          │             │
    ▼              ▼              ▼          ▼             ▼
┌────────┐    ┌────────┐    ┌────────┐ ┌────────┐    ┌──────────┐
│Segment │    │Retrieve│    │Generate│ │ Safety │    │ Analytics│
│  Node  │    │  Node  │    │  Node  │ │  Node  │    │   Node   │
└────────┘    └────────┘    └────────┘ └────────┘    └──────────┘
    │              │              │          │             │
    └──────────────┼──────────────┼──────────┼─────────────┘
                   │
                   ▼
         ┌──────────────────────┐
         │   State Store        │
         │ ┌────────────────┐   │
         │ │  Memory Store  │   │ (development)
         │ └────────────────┘   │
         │ ┌────────────────┐   │
         │ │  Redis Store   │   │ (production)
         │ └────────────────┘   │
         └──────────────────────┘
                   │
                   ▼
         ┌──────────────────────┐
         │  Delivery Layer      │
         │ (Email, SMS, etc)    │
         └──────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API** | FastAPI 0.121+ | HTTP server & routing |
| **Orchestration** | Python 3.9+ | Agent coordination |
| **Vector DB** | FAISS + custom search | RAG similarity search |
| **State** | Memory/Redis | Transient state persistence |
| **Logging** | Python logging | Structured audit trails |
| **Testing** | pytest 7.4+ | Unit & integration tests |
| **Async** | asyncio | Non-blocking I/O |

---

## Architecture Patterns

### 1. Multi-Agent Orchestrator Pattern

**What:** Central orchestrator coordinates multiple specialized agents.

**Why:**
- Separation of concerns (segmentation ≠ generation)
- Easy to test each agent independently
- Simple to add/remove/modify agents
- Clear audit trail per agent

**Implementation:**
```python
class Orchestrator:
    def __init__(self, 
                 segmenter, retriever, generator, 
                 safety, analytics, store):
        self.segmenter = segmenter
        self.retriever = retriever
        # ... etc
        self.store = store
    
    async def run_flow(self, flow_name, payload):
        # Execute pipeline sequentially
        segment = self.segmenter.run(payload)
        citations = self.retriever.run(payload)
        variants = self.generator.run({...})
        # ...
```

**Benefits:**
- ✅ Testable: Mock each agent independently
- ✅ Observable: Log each step
- ✅ Flexible: Swap implementations per agent

---

### 2. Node-Based Pipeline

**What:** Each agent is wrapped in a "Node" interface for standardized execution.

**Why:**
- Consistent run signature: `run(data) → result`
- Easy to add pre/post processing
- Supports dependency injection

**Implementation:**
```python
class BaseNode(ABC):
    @abstractmethod
    def run(self, data: Any) -> Any:
        raise NotImplementedError()

class SegmenterNode(BaseNode):
    def run(self, customer: dict) -> dict:
        return segment_user(customer)
```

**Benefits:**
- ✅ Uniform interface
- ✅ Composable in larger workflows
- ✅ Testable with mocked data

---

### 3. Store Abstraction

**What:** Abstract state store with Memory and Redis implementations.

**Why:**
- Decouple state mechanism from business logic
- Support both dev (Memory) and prod (Redis)
- Graceful fallback if Redis unavailable

**Implementation:**
```python
class Store(ABC):
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        pass
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

class MemoryStore(Store):
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()
    
    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value

class RedisStore(Store):
    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url)
    
    def set(self, key: str, value: Any) -> None:
        self.client.set(key, json.dumps(value))
```

**Benefits:**
- ✅ Testable (in-memory default)
- ✅ Scalable (Redis for multi-worker)
- ✅ Switchable at runtime

---

### 4. PII Redaction & Safety Gates

**What:** Multiple validation layers prevent non-compliant content from reaching customers.

**Why:**
- Regulatory requirement (GDPR, CCPA, SOX)
- Brand safety
- Factual accuracy

**Implementation:**
```
Generator Output (Variants A, B, C)
            ↓
    ┌───────────────┐
    │ PII Detection │  (redact emails, SSNs)
    └───────────────┘
            ↓
    ┌───────────────┐
    │Brand Checker  │  (check tone, vocabulary)
    └───────────────┘
            ↓
    ┌───────────────┐
    │Fact Checking  │  (validate against citations)
    └───────────────┘
            ↓
    ┌───────────────┐
    │Legal Review   │  (compliance rules)
    └───────────────┘
            ↓
    Safe Variants {A, B}
    Blocked {C: "PII detected"}
```

**Benefits:**
- ✅ Compliance by design
- ✅ Multiple independent checks
- ✅ Clear rejection reasons

---

## Component Details

### 1. Segmenter Node

**Purpose:** Classify customer by intent, funnel stage, and use case.

**Input:**
```python
{
    "user_id": "U123",
    "email": "customer@example.com",
    "viewed_page": "payment_plans",
    "form_started": "yes",
    "scheduled": "no",
    "attended": "no"
}
```

**Output:**
```python
{
    "segment": "payment_plans",
    "funnel_stage": "StartedFormOrFlow",
    "intent_level": "high",
    "reasons": [
        "viewed payment_plans page",
        "started signup form",
        "shows strong intent"
    ]
}
```

**Logic:**
- Attended a session? → "Very High" intent
- Scheduled a session? → "High" intent
- Started form? → "Medium" intent
- Just viewed page? → "Low" intent

**Location:** `backend/agents/segmenter.py`, `backend/app/nodes/segmenter_node.py`

---

### 2. Retriever Node

**Purpose:** Find relevant knowledge base entries via RAG (Retrieval-Augmented Generation).

**Input:**
```python
{
    "segment": "payment_plans",
    "funnel_stage": "StartedFormOrFlow",
    # ... from segmenter
}
```

**Process:**
1. Build semantic search query from segment + intent
2. Search vector DB (FAISS) for relevant documents
3. **Apply PII redaction** before returning
4. Rank by relevance

**Output:**
```python
[
    {
        "id": "doc_001",
        "title": "Payment Plan Options",
        "section": "Features",
        "text": "Original text with potential PII",
        "redacted_text": "Safe version for LLM",
        "url": "https://docs.example.com",
        "published_date": "2024-01-15",
        "source": "knowledge_base"
    },
    # ... more citations
]
```

**PII Redaction:**
- Email patterns: `[REDACTED_EMAIL]`
- Phone numbers: `[REDACTED_PHONE]`
- SSN: `[REDACTED_SSN]`
- Account numbers: `[REDACTED_ACCOUNT]`

**Location:** `backend/agents/retriever.py`, `backend/app/nodes/retriever_node.py`

---

### 3. Generator Node

**Purpose:** Create multiple A/B/n message variants based on customer + context.

**Input:**
```python
{
    "customer": { "name": "John", "email": "..." },
    "segment": { "segment": "payment_plans", ... },
    "citations": [{ "text": "...", "title": "..." }, ...]
}
```

**Process:**
1. Extract customer name, segment label, citation content
2. Generate multiple templates/variants:
   - Variant A: Short, urgency-focused
   - Variant B: Long, educational
   - Variant C: Social proof-based
3. Personalize each with customer data

**Output:**
```python
[
    {
        "id": "A",
        "subject": "John, quick note about payment_plans",
        "body": "Hi John,\n\nWe thought you might like this...",
        "meta": {"type": "short", "tone": "urgent"}
    },
    {
        "id": "B",
        "subject": "John, more on the Acme plan",
        "body": "Hello John,\n\nDetails: ...",
        "meta": {"type": "long", "tone": "educational"}
    },
    # ... more variants
]
```

**Location:** `backend/agents/generator.py`, `backend/app/nodes/generator_node.py`

---

### 4. Safety Node

**Purpose:** Validate variants against brand, legal, and factual guidelines.

**Input:**
```python
[
    {
        "id": "A",
        "subject": "...",
        "body": "..."
    },
    # ... variants
]
```

**Checks:**
1. **Brand Alignment**
   - Tone (professional, friendly, urgent?)
   - Vocabulary (approved terms only?)
   - Logo/colors (brand guidelines?)

2. **Compliance**
   - No false claims
   - Required disclaimers present
   - Regulatory language correct

3. **Factual Grounding**
   - Claims backed by citations?
   - Numbers & dates accurate?
   - Sources trustworthy?

4. **PII Leakage**
   - No customer data in body?
   - No internal notes visible?

**Output:**
```python
{
    "safe": [
        {
            "id": "A",
            "subject": "...",
            "body": "...",
            "safety_score": 0.95
        }
    ],
    "blocked": [
        {
            "id": "C",
            "reason": "False medical claim detected",
            "severity": "high"
        }
    ]
}
```

**Location:** `backend/agents/safety_gate.py`, `backend/app/nodes/safety_node.py`

---

### 5. Analytics Node

**Purpose:** Score safe variants and select the winner based on predicted performance.

**Input:**
```python
{
    "variants": [
        {
            "id": "A",
            "subject": "...",
            "body": "...",
            "safety_score": 0.95
        },
        # ... more safe variants
    ],
    "customer": {
        "user_id": "U123",
        "email": "...",
        "age_group": "25-34",
        "engagement_score": 0.7
        # ... customer attributes
    }
}
```

**Scoring Logic:**
- Historical CTR for variant type
- Personalization relevance
- Freshness of citations
- Safety score

**Output:**
```python
{
    "winner": {
        "variant_id": "A",
        "reason": "Highest expected CTR for segment + customer",
        "score": 0.88,
        "confidence": 0.92
    },
    "experiment": {
        "test_id": "exp_20241115_001",
        "group": "treatment_v1",
        "control_variant": "A"
    },
    "metrics": {
        "avg_safety_score": 0.93,
        "total_candidates": 3,
        "blocked_count": 0
    }
}
```

**Location:** `backend/agents/analytics.py`, `backend/app/nodes/analytics_node.py`

---

## Data Flow

### Sequence Diagram

For a visual representation of the complete personalization flow, see **[ARCHITECTURE_SEQUENCE.puml](./ARCHITECTURE_SEQUENCE.puml)**.

This PlantUML diagram shows:
- Interaction between all components
- Sequential execution of each step
- State store operations
- Response assembly and audit trail
- Timing and dependencies

**To view the diagram:**
```bash
# Online viewer (paste content at)
https://www.plantuml.com/plantuml/uml/

# Or install locally
brew install plantuml
plantuml ARCHITECTURE_SEQUENCE.puml -o . -tpng
```

### Complete Request/Response Cycle

```
1. CLIENT REQUEST
   ├─ Endpoint: POST /personalize
   ├─ Payload:
   │  {
   │    "id": "U123",
   │    "email": "customer@example.com",
   │    "viewed_page": "payment_plans",
   │    "form_started": "yes",
   │    "scheduled": "no",
   │    "attended": "no"
   │  }
   └─ Headers: Content-Type: application/json

2. ORCHESTRATOR.RUN_FLOW()
   │
   ├─ STEP 1: SEGMENTATION
   │  ├─ Input: customer profile
   │  ├─ Process: Determine intent level & funnel stage
   │  ├─ Output: { segment, intent_level, funnel_stage, reasons }
   │  ├─ Store: Set "U123:segment" → segment dict
   │  └─ Log: "Segment: StartedFormOrFlow (high intent)"
   │
   ├─ STEP 2: RETRIEVAL
   │  ├─ Input: segment info
   │  ├─ Process: Vector search for relevant docs
   │  ├─ PII Redaction: Mask emails, SSNs, account numbers
   │  ├─ Output: [{ id, title, redacted_text, url, source }]
   │  ├─ Store: Set "U123:citations" → citations list
   │  └─ Log: "Citations: 5 documents found"
   │
   ├─ STEP 3: GENERATION
   │  ├─ Input: customer, segment, citations
   │  ├─ Process: Create A/B/n variants using templates
   │  ├─ Output: [{ id, subject, body, meta }]
   │  ├─ Store: Set "U123:variants" → variants list
   │  └─ Log: "Generated 3 variants"
   │
   ├─ STEP 4: SAFETY CHECK
   │  ├─ Input: variants
   │  ├─ Process:
   │  │  ├─ Brand alignment check
   │  │  ├─ Compliance rules check
   │  │  ├─ Factual grounding check
   │  │  └─ PII leakage detection
   │  ├─ Output: { safe: [...], blocked: [...] }
   │  ├─ Store: (Not stored, checked on-the-fly)
   │  └─ Log: "Safety: 2 safe, 1 blocked"
   │
   ├─ STEP 5: ANALYTICS
   │  ├─ Input: safe variants, customer
   │  ├─ Process: Score variants & select winner
   │  ├─ Output: { winner, experiment, metrics }
   │  ├─ Store: Set "U123:analysis" → analysis dict
   │  ├─ Store: Set "U123:winner" → winner dict
   │  └─ Log: "Winner: Variant A (0.88 score)"
   │
   └─ STEP 6: DELIVERY (MOCK)
      ├─ Input: winner variant, customer email
      ├─ Process: Send via delivery provider (mocked)
      ├─ Output: { status, message_id, timestamp }
      ├─ Store: (Optional)
      └─ Log: "Delivered to customer@example.com"

3. ORCHESTRATOR RESPONSE
   {
     "segment": { ... },
     "citations": [ ... ],
     "variants": [ ... ],
     "safety": {
       "safe": [ ... ],
       "blocked": [ ... ]
     },
     "analysis": {
       "winner": { ... },
       "metrics": { ... }
     },
     "delivery": {
       "status": "success",
       "message_id": "msg_abc123"
     }
   }

4. CLIENT RECEIVES FULL AUDIT TRAIL
   ├─ Can inspect every step
   ├─ Can review why variant was blocked
   ├─ Can see scoring rationale
   └─ Can prove compliance to auditors
```

---

## State Management

### Memory Store (Development)

**When to use:**
- Single-worker development
- Unit & integration tests
- Quick prototyping
- CI/CD pipelines

**Implementation:**
```python
class MemoryStore(Store):
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            return self._data.get(key)
```

**Characteristics:**
- ✅ No external dependencies
- ✅ Thread-safe via lock
- ✅ Fast in-process
- ❌ Not shared across processes
- ❌ Lost on restart

### Redis Store (Production)

**When to use:**
- Multi-worker deployments (Gunicorn, etc.)
- Distributed orchestration
- Cross-process state sharing
- Failover scenarios

**Implementation:**
```python
class RedisStore(Store):
    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url)
    
    def set(self, key: str, value: Any) -> None:
        json_value = json.dumps(value)
        self.client.set(key, json_value, ex=3600)  # 1 hour TTL
    
    def get(self, key: str) -> Optional[Any]:
        value = self.client.get(key)
        return json.loads(value) if value else None
```

**Characteristics:**
- ✅ Shared across processes
- ✅ Persistent across restarts
- ✅ TTL support (auto-cleanup)
- ✅ Pub/sub for notifications
- ❌ Requires Redis infrastructure
- ❌ Network latency

### Store Selection at Runtime

```python
# app/store/__init__.py

if REDIS_URL:
    try:
        store = RedisStore(REDIS_URL)
        logger.info("Using RedisStore")
    except Exception:
        logger.warning("Redis unavailable, falling back to MemoryStore")
        store = MemoryStore()
else:
    store = MemoryStore()
    logger.info("Using MemoryStore")
```

---

## Safety & Compliance

### Multi-Layer Safety Architecture

```
┌─────────────────────────────────────────┐
│   Generated Variant                     │
│   (Potentially Non-Compliant)          │
└──────────────┬──────────────────────────┘
               │
    ┌──────────▼────────────┐
    │ Layer 1: PII Check    │
    │ - Detect email, SSN   │
    │ - Mask before LLM     │
    └──────────┬────────────┘
               │ ✓ Pass
    ┌──────────▼────────────┐
    │ Layer 2: Brand Check  │
    │ - Tone alignment      │
    │ - Vocabulary review   │
    │ - Logo/color compliance
    └──────────┬────────────┘
               │ ✓ Pass
    ┌──────────▼────────────┐
    │ Layer 3: Legal/Policy │
    │ - Required disclaimers│
    │ - Compliance rules    │
    └──────────┬────────────┘
               │ ✓ Pass
    ┌──────────▼────────────┐
    │ Layer 4: Fact Check   │
    │ - Grounded in citations
    │ - No false claims     │
    └──────────┬────────────┘
               │ ✓ Pass
    ┌──────────▼────────────┐
    │ Safe Variant          │
    │ Ready for Delivery    │
    └───────────────────────┘
```

### Audit Trail

Every variant's journey is logged:

```json
{
  "variant_id": "A",
  "checks": [
    {
      "check_type": "pii",
      "status": "pass",
      "timestamp": "2024-11-15T10:30:00Z",
      "details": "No PII detected"
    },
    {
      "check_type": "brand",
      "status": "pass",
      "timestamp": "2024-11-15T10:30:01Z",
      "details": "Tone: professional ✓, Vocabulary: approved ✓"
    },
    {
      "check_type": "compliance",
      "status": "pass",
      "timestamp": "2024-11-15T10:30:02Z",
      "details": "All required disclaimers present"
    },
    {
      "check_type": "factual",
      "status": "pass",
      "timestamp": "2024-11-15T10:30:03Z",
      "details": "Claims grounded in citations"
    }
  ],
  "final_status": "safe",
  "approved_for_delivery": true
}
```

---

## Testing Strategy

### Test Pyramid

```
        ▲
       /|\
      / | \  E2E Tests (10%)
     /  |  \ - Full orchestrator flow
    /   |   \ - Real dependencies
   /────┼────\
  /     |     \ Integration Tests (30%)
 /      |      \ - Node + Store interaction
/       |       \ - Mock external services
/────────┼────────\
/        |         \ Unit Tests (60%)
/         |          \ - Agent functions
/          |           \ - Utility functions
────────────────────────
```

### Test Coverage

| Component | Test File | Coverage |
|-----------|-----------|----------|
| Segmenter | `test_segmenter_node.py` | 95%+ |
| Retriever | `test_retriever_node.py` | 90%+ |
| Generator | `test_generator_node.py` | 90%+ |
| Safety | `test_safety_node.py` | 95%+ |
| Analytics | `test_analytics_node.py` | 90%+ |
| Orchestrator | `test_orchestrator_*.py` | 85%+ |
| Health | `test_health.py` | 100% |
| Store | `test_memory_store.py` | 95%+ |

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov=agents --cov=services --cov-report=html

# Specific test file
pytest tests/test_orchestrator_route_override.py -v

# With markers
pytest tests/ -v -m "not slow"
```

---

## Deployment Architecture

### Development Environment

```
┌──────────────────┐
│   Developer      │
│   Workstation    │
└────────┬─────────┘
         │
    ┌────▼─────┐
    │ FastAPI  │ (uvicorn --reload)
    │ :8000    │
    └────┬─────┘
         │
    ┌────▼──────────┐
    │  MemoryStore  │
    └───────────────┘
```

**Setup:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Environment (Single-Worker)

```
┌──────────────────┐
│   Load Balancer  │
│  (Azure App Svc) │
└────────┬─────────┘
         │
    ┌────▼──────────┐
    │  FastAPI      │
    │  (Gunicorn)   │
    │  :8000        │
    └────┬──────────┘
         │
    ┌────┼──────────────────┐
    │    │                  │
┌───▼─┐  │            ┌──────▼────┐
│Cache│  │            │ MemoryStore
│     │  │            │ (fallback) │
└─────┘  │            └───────────┘
         │
    ┌────▼────────────┐
    │  Azure Search   │
    │  (Vector DB)    │
    └─────────────────┘
```

**Deployment:**
```yaml
# app.yaml (Azure App Service)
runtime: python
runtimeVersion: 3.9
build:
  - npm install
  - pip install -r backend/requirements.txt
startup: gunicorn --workers 1 backend.app.main:app --bind 0.0.0.0:8000
```

### Production Environment (Multi-Worker)

```
┌──────────────────┐
│   Load Balancer  │
│  (Azure App Svc) │
└────────┬─────────┘
         │
    ┌────┴────────────────────────┐
    │                             │
┌───▼──────┐  ┌──────────┐  ┌─────▼─────┐
│Worker 1  │  │Worker 2  │  │Worker 3   │
│FastAPI   │  │FastAPI   │  │FastAPI    │
└───┬──────┘  └──────┬───┘  └─────┬─────┘
    │                │            │
    └────────┬───────┴────────┬───┘
             │                │
        ┌────▼────────┐  ┌────▼───────┐
        │  Redis      │  │ Azure Search│
        │  (State)    │  │ (Vector DB) │
        └─────────────┘  └─────────────┘
```

**Deployment:**
```yaml
# app.yaml (Azure Container Instances)
containers:
  - image: myregistry.azurecr.io/echovoice:latest
    resources:
      cpu: 2.0
      memoryInGb: 4.0
    ports:
      - port: 8000
    environment:
      - name: REDIS_URL
        secureValue: redis://redis.redis.svc.cluster.local:6379
      - name: OPENAI_API_KEY
        secureValue: ...
replicas: 3
```

---

## Scalability & Performance

### Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| P50 Latency | < 500ms | End-to-end personalization |
| P99 Latency | < 2s | Including external API calls |
| Throughput | 100+ req/s | Single instance, 4 CPU |
| Memory | < 500MB | Per instance |
| Store Latency | < 50ms | Redis get/set |

### Optimization Strategies

#### 1. Caching

```python
# Cache segmentation rules
SEGMENT_CACHE = {}
CITATION_CACHE = {}

# Time-based invalidation
if timestamp - SEGMENT_CACHE[key]["time"] > 3600:
    # Recompute segment
```

#### 2. Batching

```python
# Process multiple customers concurrently
async def batch_personalize(customers: List[dict]):
    tasks = [
        orchestrator.run_flow("personalize", customer)
        for customer in customers
    ]
    results = await asyncio.gather(*tasks)
    return results
```

#### 3. Connection Pooling

```python
# Reuse Redis connections
redis_pool = redis.ConnectionPool.from_url(REDIS_URL)
redis_client = redis.Redis(connection_pool=redis_pool)
```

#### 4. Async I/O

```python
# Non-blocking operations
@app.post("/personalize")
async def personalize(request: PersonalizeRequest):
    # All I/O ops are async (vector search, Redis, etc.)
    result = await orchestrator.run_flow(...)
    return result
```

### Monitoring & Observability

**Key Metrics to Track:**

1. **Latency by Component**
   - Segmentation: Should be < 10ms
   - Retrieval: < 200ms (vector search)
   - Generation: < 100ms
   - Safety: < 150ms
   - Analytics: < 50ms

2. **Error Rates**
   - Segmentation errors: < 0.1%
   - Retrieval failures: < 0.5%
   - Safety check failures: > 0% (expected)
   - Delivery failures: < 1%

3. **Business Metrics**
   - Messages sent: volume
   - Blocked rate: compliance
   - Winner selection: A/B distribution
   - Variant performance: CTR, conversion

**Logging Format:**
```json
{
  "timestamp": "2024-11-15T10:30:00Z",
  "request_id": "req_abc123",
  "component": "segmenter",
  "status": "success",
  "latency_ms": 8,
  "customer_id": "U123",
  "segment": "high_intent",
  "log_level": "INFO"
}
```

---

## Migration Path

### From Current → Production

**Phase 1: Current State (MVP)**
- ✅ Mock agents with deterministic logic
- ✅ Memory store (single-worker)
- ✅ Local vector search (FAISS)
- ✅ Test coverage

**Phase 2: Azure Integration**
- Azure OpenAI for smarter generation
- Azure Search for vector DB
- Key Vault for secrets
- App Insights for monitoring

**Phase 3: Enterprise Features**
- Multi-tenancy support
- Advanced compliance engine
- A/B testing framework
- Feedback loops

**Phase 4: Global Scale**
- Multi-region deployment
- CDN for static assets
- Event streaming (Event Hubs)
- Advanced analytics (Synapse)

---

## Appendix: Key Decisions & Rationale

### 1. Why Multi-Agent?

**Alternative:** Monolithic LLM-based system
**Chosen:** Multi-agent orchestrator

**Rationale:**
- ✅ Explainability: Each step logged independently
- ✅ Safety: Multiple gates prevent bad outputs
- ✅ Auditability: Regulatory compliance easier
- ✅ Flexibility: Swap agents per customer segment
- ❌ Slightly more complex orchestration
- ❌ Requires more test coverage

### 2. Why Memory + Redis Stores?

**Alternative:** Database-only (SQL/NoSQL)
**Chosen:** Memory (dev) + Redis (prod) with fallback

**Rationale:**
- ✅ Fast for transient state
- ✅ No schema needed
- ✅ Auto-cleanup via TTL
- ✅ Dev experience (no Docker dependency)
- ❌ Not suitable for long-term storage
- ✌️ Fallback to Memory prevents total failure

### 3. Why Node Wrapper Pattern?

**Alternative:** Direct agent function calls
**Chosen:** Wrapped in Node classes

**Rationale:**
- ✅ Consistent interface
- ✅ Easy to add logging/timing
- ✅ Composable in larger workflows
- ✅ Testable with mocks
- ❌ Slight verbosity

### 4. Why Synchronous Orchestration?

**Alternative:** Async LangGraph chains
**Chosen:** Synchronous sequential pipeline

**Rationale:**
- ✅ Simpler to understand & debug
- ✅ Easier to add conditional logic
- ✅ Better for audit trails (sequential)
- ✅ Works with mock agents
- ❌ Slightly slower for independent agents
- 🚀 Future: Easy to convert to async

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph/)
- [Azure OpenAI Best Practices](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [OWASP PII Redaction](https://owasp.org/www-community/attacks/PII_Exposure)

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**Maintainer:** EchoVoice Team
