# 🚀 **EchoVoice: Customer Personalization Orchestrator**

**Project Title:** `EchoVoice: Customer Personalization Orchestrator`
**Challenge Solved:** *Compliant, on-brand personalization and A/B/n experimentation in a regulated domain.*

EchoVoice is a **multi-agent AI personalization platform** designed for regulated industries. It delivers safe, on-brand, traceable customer messaging through a coordinated set of specialized agents working together inside a transparent and auditable orchestration pipeline.

This repository provides a **prototype scaffold** for local development, including an orchestrator, agent suite, mock RAG data, and a frontend stub for auditability.

---

## ⚙️ Quick Start (Backend)

### **1. Create your environment file**

```bash
cp .env.template .env
```

Fill in the required API keys (Azure OpenAI, Azure Search, etc.).

---

### **2. Create & activate a Python virtual environment**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### **3. Run the backend orchestrator**

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### **3. Check health of server**

GET request:

```bash
GET http://localhost:8000/health
```

Example payload:

```json
{
  "status": "ok",
}
```

This simulates the full end-to-end personalization flow:

* Segmentation
* RAG retrieval
* A/B/n generation
* Safety & compliance filtering
* Variant selection
* Experiment logging

---

## 📁 Repository Layout

```bash
EchoVoice-AI/
├── README.md
├── package.json
├── .env.template
│
├── data/              # sample KB & events for testing
├── frontend/          # React + Tailwind audit dashboard scaffold
└── backend/
    ├── main.py        # FastAPI orchestrator
    ├── agents/        # segmentation, RAG, generation, safety, analytics
    ├── utils/         # logging, validation, configuration
    └── data/          # local mock content for retrieval
    ├── requirements.txt 
```

This scaffold includes **mock/minimal agent logic** so you can quickly validate orchestration before integrating full Azure services.

---

## 🧱 Architecture Overview

EchoVoice uses a **LangGraph-style multi-agent workflow** coordinated by a central orchestrator.

### **Key Components**

* **`agents/`** – individual, modular specialist agents:

  * **SegmentationAgent** – assigns user segment + explainability
  * **RetrievalAgent** – RAG over verified local KB
  * **GenerationAgent** – creates A/B/n personalized messages
  * **SafetyComplianceAgent** – checks brand, legal, factual grounding
  * **DeliveryAgent** – decides auto-send vs. human review
  * **AnalyticsAgent** – logs results + tracks uplift
* **`main.py`** – orchestrator that connects all agents into a decision pipeline
* **`data/`** – mock content and synthetic customer events
* **Frontend Stub** – React/Tailwind dashboard (audit log, experiment view)

This architecture allows:

* experiment-driven personalization
* full auditability
* safe outbound communication
* transparent decision-making for every step

---

If you want, I can also provide:

✅ A polished **project description for Innovation Studio submission**
✅ A **system architecture diagram** (PNG/SVG)
✅ **Agent prompt templates** (Azure OpenAI format)
✅ **Full API documentation**
✅ **A/B/n experiment logic implementation**

Just say: **"Generate the full architecture diagram"** or **"Add agent prompts"**.
