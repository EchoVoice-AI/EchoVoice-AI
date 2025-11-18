# 🚀 EchoVoice: Customer Personalization Orchestrator

**Project Title:** EchoVoice: Customer Personalization Orchestrator  
**Challenge Solved:** Compliant, on-brand personalization and A/B/n experimentation in a regulated domain.

## Overview

EchoVoice is a **multi-agent AI personalization platform** designed for regulated industries (financial services, healthcare, etc.). It delivers safe, on-brand, traceable customer messaging through a coordinated set of specialized agents working together inside a transparent and auditable orchestration pipeline.

**Key Capability:** End-to-end personalized customer messaging with built-in compliance checking, safety gates, and experiment tracking—all auditable and fully traceable for regulatory requirements.

This repository provides a **production-ready scaffold** for local development, including:
- ✅ Multi-agent orchestrator (LangGraph-style)
- ✅ Specialized agents (segmentation, RAG, generation, safety, analytics)
- ✅ Mock RAG data and compliance validation
- ✅ Redis-backed state persistence (optional)
- ✅ Frontend audit dashboard stub
- ✅ Comprehensive test suite

---

## ⚡ Quick Start

### Prerequisites
- Python 3.9+
- Redis (optional, for distributed state)
- API keys for OpenAI, Azure Search (if using real services)

### Backend Setup

**1. Create your environment file:**
```bash
cp .env.template .env
```
Fill in required API keys (OpenAI, Azure Search, delivery provider, etc.).

**2. Create & activate Python virtual environment:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Start the backend orchestrator:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**4. Verify the server is running:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok"
}
```

### Frontend Setup (Optional)
```bash
cd frontend
npm install
npm start  # runs on http://localhost:3000
```

---

## 🔄 How It Works

The orchestrator executes a complete personalization pipeline on each request:

```
Customer Event
    ↓
[1] Segmentation    → Assign segment, intent level, use case
    ↓
[2] RAG Retrieval   → Find relevant knowledge base entries
    ↓
[3] Generation      → Create A/B/n message variants
    ↓
[4] Safety Check    → Validate compliance, brand alignment, factual grounding
    ↓
[5] Analytics       → Score variants, select winner
    ↓
[6] Delivery        → Send selected message (mock or real)
    ↓
Audit Log & Metrics
```

Each step is:
- **Traceable:** Full audit trail with decision rationale
- **Auditable:** Compliance checks logged and inspectable
- **Reversible:** State persisted to memory or Redis

---

## 🔧 Configuration

### Environment Variables

```env
# API Keys
OPENAI_API_KEY=your_openai_key
VECTOR_DB_ENDPOINT=your_vector_db_endpoint
VECTOR_DB_API_KEY=your_vector_db_key
DELIVERY_PROVIDER_API_KEY=your_delivery_key

# Logging
LOG_LEVEL=INFO

# Deployment
ENV=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# State Persistence (optional)
REDIS_URL=redis://localhost:6379/0
```

### Optional: Enable Redis

For multi-process or distributed deployments, configure Redis:

```env
REDIS_URL=redis://localhost:6379/0
```

**Notes:**
- `MemoryStore` is the default (in-process, thread-safe, suitable for single-worker development)
- Use Redis in production or multi-worker setups for cross-process state sharing
- If Redis is unavailable, the app falls back to `MemoryStore` automatically

---

## 📁 Project Structure

```
EchoVoice-AI-2/
├── README.md                 # Project overview (this file)
├── ARCHITECTURE.md           # Detailed architecture & design
├── API_REFERENCE.md          # API endpoints & payloads
├── pytest.ini
├── requirements.txt          # Frontend dependencies
├── .env.template             # Environment template
│
├── data/                     # Sample knowledge base & test data
│   ├── brand-guidelines.md   # Brand compliance rules
│   ├── customers.json        # Mock customer profiles
│   ├── products.json         # Product catalog
│   ├── customer_events.csv   # Sample customer journey events
│   └── irs_tax_knowledge.jsonl  # Sample RAG corpus
│
├── frontend/                 # React audit dashboard (optional)
│   ├── package.json
│   └── src/
│       └── App.js
│
└── backend/                  # FastAPI orchestrator & agents
    ├── requirements.txt      # Python dependencies
    ├── app/
    │   ├── main.py          # FastAPI app & middleware
    │   ├── config.py        # Environment config
    │   ├── graph/
    │   │   └── orchestrator.py       # Orchestrator class
    │   ├── nodes/
    │   │   ├── base_node.py          # Abstract node interface
    │   │   ├── segmenter_node.py     # Segmentation (step 1)
    │   │   ├── retriever_node.py     # RAG retrieval (step 2)
    │   │   ├── generator_node.py     # Message generation (step 3)
    │   │   ├── safety_node.py        # Compliance check (step 4)
    │   │   └── analytics_node.py     # Variant scoring (step 5)
    │   ├── routers/
    │   │   ├── health.py             # /health endpoint
    │   │   └── orchestrator.py       # /personalize endpoint
    │   └── store/
    │       ├── memory_store.py       # In-memory state store
    │       └── redis_store.py        # Redis state store
    │
    ├── agents/               # Agent implementations
    │   ├── segmenter.py      # Segment users by intent & funnel stage
    │   ├── retriever.py      # RAG with PII redaction
    │   ├── generator.py      # A/B/n variant generation
    │   ├── safety_gate.py    # Compliance validation
    │   └── analytics.py      # Variant scoring & selection
    │
    ├── services/             # Shared utilities
    │   ├── logger.py         # Structured logging
    │   ├── delivery.py       # Email delivery (mock)
    │   └── vector_db.py      # Similarity search
    │
    ├── docs/                 # Component documentation
    │   ├── segmenter.md
    │   ├── retriever.md
    │   ├── generator.md
    │   ├── safety_gate.md
    │   └── analytics.md
    │
    └── tests/                # Comprehensive test suite
        ├── conftest.py
        ├── test_health.py
        ├── test_segmenter_node.py
        ├── test_retriever_node.py
        ├── test_generator_node.py
        ├── test_safety_node.py
        ├── test_analytics_node.py
        ├── test_memory_store.py
        ├── test_orchestrator_*.py
        └── ...
```

---

## 🧠 Architecture Overview

### Multi-Agent Orchestrator Pattern

EchoVoice uses a **LangGraph-inspired multi-agent workflow** where:

1. **Specialized Agents** handle discrete tasks (segmentation, retrieval, generation, safety, analytics)
2. **Orchestrator** coordinates data flow between agents
3. **State Store** persists intermediate results (memory or Redis)
4. **Routers** expose HTTP endpoints for client integration

### Key Agents

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **Segmenter** | Classify user intent, funnel stage, use case | Customer profile, event | Segment label, intent level, reasons |
| **Retriever** | Find relevant knowledge base entries via RAG | Segment, query | Ranked citations with PII redaction |
| **Generator** | Create A/B/n message variants | Customer, segment, citations | List of variants (subject, body, metadata) |
| **Safety Gate** | Validate compliance, brand alignment, factual accuracy | Variants, guidelines | Safe variants + blocked reasons |
| **Analytics** | Score variants and select winner | Safe variants, customer | Winner selection + uplift metrics |

### Data Flow

```
1. Segmentation
   Input:  { user_id, email, viewed_page, form_started, scheduled, attended }
   Output: { segment, intent_level, funnel_stage, reasons }

2. Retrieval
   Input:  { segment, use_case }
   Output: [{ id, title, text, redacted_text, url, source }]

3. Generation
   Input:  { customer, segment, citations }
   Output: [{ id, subject, body, meta }]

4. Safety Gate
   Input:  { variants, brand_guidelines, compliance_rules }
   Output: { safe: [...], blocked: [...] }

5. Analytics
   Input:  { variants, customer }
   Output: { winner: { variant_id, reason, score } }

6. Delivery
   Input:  { email, subject, body }
   Output: { status, message_id, timestamp }
```

### State Management

- **Memory Store:** Process-local, thread-safe, ideal for development/testing
- **Redis Store:** Distributed, ideal for multi-worker production
- **Fallback:** Automatic fallback from Redis → Memory if unavailable

---

## 🧪 Testing

Run the test suite:

```bash
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov=agents --cov=services
```

### Test Structure
- `test_health.py` — API health check
- `test_*_node.py` — Individual agent node tests
- `test_orchestrator_*.py` — End-to-end orchestrator scenarios
- `test_memory_store.py` — State persistence tests

---

## 📊 Next Steps & Enhancements

### Phase 1 (MVP - Current)
- ✅ Multi-agent orchestrator scaffold
- ✅ Mock agents with deterministic logic
- ✅ Memory store for state
- ✅ Test coverage for all nodes

### Phase 2 (Production Readiness)
- 🔄 Azure OpenAI integration
- 🔄 Azure Search vector DB integration
- 🔄 Advanced safety checks (brand policy engine)
- 🔄 A/B testing framework
- 🔄 Metrics & analytics dashboard
- 🔄 Docker & Kubernetes deployment

### Phase 3 (Advanced)
- 🔄 Multi-language support
- 🔄 Real-time experiment tracking
- 🔄 Feedback loops for continuous optimization
- 🔄 Compliance audit trails (GDPR, CCPA)

---

## 📖 Documentation

For deeper dives, see:

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** — System design, patterns, and rationale
- **[ARCHITECTURE_SEQUENCE.puml](./ARCHITECTURE_SEQUENCE.puml)** — Sequence diagram of complete personalization flow
- **[API_REFERENCE.md](./API_REFERENCE.md)** — Complete endpoint reference with examples
- **[backend/docs/](./backend/docs/)** — Individual agent documentation

---

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/my-feature`)
2. Write tests for new functionality
3. Ensure all tests pass (`pytest`)
4. Submit a pull request

---

## 📄 License

[Your License Here]

---

## 🎯 Support

For questions or issues, please:
1. Check the documentation in `ARCHITECTURE.md`
2. Review test examples in `backend/tests/`
3. Open an issue with reproduction steps

---

**Happy personalizing! 🎉**
