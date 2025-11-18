# EchoVoice API Reference

**API Version:** 1.0  
**Base URL:** `http://localhost:8000` (development) | `https://api.echovoice.example.com` (production)  
**Content-Type:** `application/json`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Base Response Format](#base-response-format)
3. [Error Handling](#error-handling)
4. [Endpoints](#endpoints)
   - [Health Check](#health-check)
   - [Personalization](#personalization)
5. [Data Models](#data-models)
6. [Examples](#examples)
7. [Rate Limiting](#rate-limiting)

---

## Authentication

Currently, the API uses **no authentication** for development. In production, implement:

```bash
# With API Key (Bearer token)
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8000/health
```

**Future:** Azure AD (Microsoft Entra ID) or API key management.

---

## Base Response Format

All responses follow a standard envelope:

### Success Response (2xx)
```json
{
  "status": "success",
  "data": {
    // ... endpoint-specific data
  },
  "timestamp": "2024-11-15T10:30:00Z",
  "request_id": "req_abc123def456"
}
```

### Error Response (4xx, 5xx)
```json
{
  "status": "error",
  "error": {
    "code": "SEGMENTATION_FAILED",
    "message": "Failed to segment customer: invalid funnel_stage",
    "details": {
      "field": "viewed_page",
      "reason": "Expected one of: [payment_plans, account_features, ...]"
    }
  },
  "timestamp": "2024-11-15T10:30:00Z",
  "request_id": "req_abc123def456"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| **200** | Success | Personalization completed |
| **400** | Bad Request | Missing required field |
| **401** | Unauthorized | Invalid API key |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Server Error | Unexpected error |
| **503** | Service Unavailable | Dependency down (Redis, Vector DB) |

### Error Codes

| Code | Description | Retry? |
|------|-------------|--------|
| `VALIDATION_ERROR` | Input validation failed | No |
| `SEGMENTATION_FAILED` | Segmentation logic error | No |
| `RETRIEVAL_FAILED` | Vector DB search failed | Yes (with backoff) |
| `GENERATION_FAILED` | Variant generation error | No |
| `SAFETY_CHECK_FAILED` | Safety validation error | No |
| `ANALYTICS_FAILED` | Winner selection error | No |
| `DELIVERY_FAILED` | Message delivery failed | Yes (with backoff) |
| `STORE_ERROR` | State persistence error | Yes (with backoff) |
| `INTERNAL_ERROR` | Unexpected server error | Yes (with backoff) |

### Retry Strategy

For retryable errors (marked above):

```bash
# Exponential backoff: 2^attempt seconds, max 30s
Attempt 1: Wait 2s
Attempt 2: Wait 4s
Attempt 3: Wait 8s
Attempt 4: Wait 16s
Attempt 5: Wait 30s (capped)
```

---

## Endpoints

### Health Check

**Endpoint:** `GET /health`

**Purpose:** Verify server is running and dependencies are healthy.

**Request:**
```bash
curl -X GET http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "timestamp": "2024-11-15T10:30:00Z",
  "version": "1.0.0",
  "dependencies": {
    "redis": "connected",
    "vector_db": "connected"
  }
}
```

**Response (503 Unavailable):**
```json
{
  "status": "error",
  "error": {
    "code": "REDIS_UNAVAILABLE",
    "message": "Redis connection failed (using fallback MemoryStore)"
  },
  "timestamp": "2024-11-15T10:30:00Z"
}
```

---

### Personalization

**Endpoint:** `POST /personalize`

**Purpose:** Execute the full personalization pipeline for a customer.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "flow_name": "standard_personalization",
  "id": "U123",
  "email": "customer@example.com",
  "name": "John Doe",
  "viewed_page": "payment_plans",
  "form_started": "yes",
  "scheduled": "no",
  "attended": "no",
  "metadata": {
    "campaign_id": "camp_001",
    "utm_source": "email",
    "device": "mobile"
  }
}
```

**Query Parameters:** (None)

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "segment": {
      "segment": "payment_plans",
      "funnel_stage": "StartedFormOrFlow",
      "intent_level": "high",
      "reasons": [
        "viewed payment_plans page",
        "started signup form",
        "shows strong intent"
      ]
    },
    "citations": [
      {
        "id": "doc_001",
        "title": "Payment Plan Options",
        "section": "Features",
        "text": "Original KB text with potential PII",
        "redacted_text": "Plan options include: Basic ($9/mo), Pro ($19/mo), Enterprise (custom)",
        "url": "https://docs.example.com/plans",
        "published_date": "2024-01-15",
        "source": "knowledge_base"
      },
      {
        "id": "doc_002",
        "title": "Early Adopter Benefits",
        "section": "Promotions",
        "text": "Early adopters get 20% off for life",
        "redacted_text": "Early adopters get 20% off for life",
        "url": "https://docs.example.com/promos",
        "published_date": "2024-11-01",
        "source": "knowledge_base"
      }
    ],
    "variants": [
      {
        "id": "A",
        "subject": "John, quick note about payment_plans",
        "body": "Hi John,\n\nWe noticed you started exploring our payment plans. Here's a quick overview...",
        "meta": {
          "type": "short",
          "tone": "friendly",
          "length_words": 45
        }
      },
      {
        "id": "B",
        "subject": "John, more on the Acme plan",
        "body": "Hello John,\n\nThanks for your interest! Here's more detail about our plans...",
        "meta": {
          "type": "long",
          "tone": "professional",
          "length_words": 120
        }
      },
      {
        "id": "C",
        "subject": "Join 10k+ happy customers",
        "body": "John, over 10,000 customers trust our plans. Here's why...",
        "meta": {
          "type": "social_proof",
          "tone": "persuasive",
          "length_words": 85
        }
      }
    ],
    "safety": {
      "safe": [
        {
          "id": "A",
          "subject": "John, quick note about payment_plans",
          "body": "Hi John,\n\nWe noticed you started exploring our payment plans. Here's a quick overview...",
          "safety_score": 0.98,
          "checks_passed": [
            "pii_detection",
            "brand_alignment",
            "compliance",
            "factual_grounding"
          ]
        },
        {
          "id": "B",
          "subject": "John, more on the Acme plan",
          "body": "Hello John,\n\nThanks for your interest! Here's more detail about our plans...",
          "safety_score": 0.95,
          "checks_passed": [
            "pii_detection",
            "brand_alignment",
            "compliance",
            "factual_grounding"
          ]
        }
      ],
      "blocked": [
        {
          "id": "C",
          "reason": "Brand tone mismatch: 'Join 10k+ customers' uses implied pressure, conflicts with brand guidelines (friendly, no pressure)",
          "severity": "medium",
          "checks_failed": [
            "brand_alignment"
          ]
        }
      ]
    },
    "analysis": {
      "winner": {
        "variant_id": "A",
        "reason": "Highest expected CTR for high-intent customers in payment_plans segment",
        "score": 0.89,
        "confidence": 0.92,
        "rationale": [
          "Historical CTR for short variants: 0.15",
          "Historical CTR for long variants: 0.08",
          "Customer engagement score: 0.75 (matches short content)",
          "Freshness bonus for recent citations: +0.05"
        ]
      },
      "experiment": {
        "test_id": "exp_20241115_001",
        "group": "treatment_v1",
        "control_variant": "A",
        "hypothesis": "Short, friendly variant performs best for high-intent customers"
      },
      "metrics": {
        "avg_safety_score": 0.96,
        "total_candidates": 3,
        "safe_count": 2,
        "blocked_count": 1,
        "generation_latency_ms": 87,
        "retrieval_latency_ms": 203,
        "safety_latency_ms": 142
      }
    },
    "delivery": {
      "status": "success",
      "message_id": "msg_abc123xyz789",
      "timestamp": "2024-11-15T10:30:05Z",
      "recipient": "customer@example.com",
      "channel": "email"
    }
  },
  "timestamp": "2024-11-15T10:30:05Z",
  "request_id": "req_abc123def456"
}
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request payload",
    "details": {
      "field": "viewed_page",
      "reason": "Unknown value. Expected one of: [payment_plans, account_features, pricing, support]"
    }
  },
  "timestamp": "2024-11-15T10:30:00Z",
  "request_id": "req_abc123def456"
}
```

**Response (500 Internal Server Error):**
```json
{
  "status": "error",
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Unexpected error during personalization",
    "details": {
      "component": "retriever",
      "error": "Vector DB connection timeout"
    }
  },
  "timestamp": "2024-11-15T10:30:00Z",
  "request_id": "req_abc123def456"
}
```

---

## Data Models

### Customer Profile

**Description:** Input customer data for personalization.

```typescript
interface CustomerProfile {
  // Required
  id: string;                    // Unique customer ID
  email: string;                 // Email address (must be valid)
  
  // Optional
  name?: string;                 // Customer name
  viewed_page?: string;          // Page viewed (enum: payment_plans, account_features, pricing, support)
  form_started?: string;         // Form started? (yes/no)
  scheduled?: string;            // Scheduled meeting? (yes/no)
  attended?: string;             // Attended meeting? (yes/no)
  
  // Custom metadata
  metadata?: {
    [key: string]: any;
  }
}
```

**Validation Rules:**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `id` | string | ✓ | 1-256 chars, alphanumeric + underscore |
| `email` | string | ✓ | Valid email format |
| `name` | string | | 1-256 chars |
| `viewed_page` | string | | One of: payment_plans, account_features, pricing, support |
| `form_started` | string | | One of: yes, no, y, n, true, false, 1, 0 |
| `scheduled` | string | | One of: yes, no, y, n, true, false, 1, 0 |
| `attended` | string | | One of: yes, no, y, n, true, false, 1, 0 |

### Segment

**Description:** Customer segment with intent level.

```typescript
interface Segment {
  segment: string;              // Segment label (e.g., "payment_plans")
  funnel_stage: string;         // One of: CompletedScheduledStep, ScheduledNextStep, StartedFormOrFlow, JustViewed, Unknown
  intent_level: string;         // One of: very_high, high, medium, low
  reasons: string[];            // Explanation of segmentation
}
```

### Citation

**Description:** Retrieved knowledge base entry.

```typescript
interface Citation {
  id: string;                    // Document ID
  title: string;                 // Document title
  section: string;               // Section/heading
  text: string;                  // Original text (may contain PII)
  redacted_text: string;         // PII-safe version for LLM
  url: string;                   // Source URL
  published_date: string;        // ISO 8601 date (YYYY-MM-DD)
  source: string;                // Source identifier (knowledge_base, etc.)
}
```

### Variant

**Description:** Message variant (A/B/n candidate).

```typescript
interface Variant {
  id: string;                    // Variant ID (A, B, C, etc.)
  subject: string;               // Email subject line
  body: string;                  // Email body
  meta: {
    type: string;                // Content type (short, long, social_proof, etc.)
    tone: string;                // Tone (friendly, professional, urgent, etc.)
    length_words?: number;        // Approximate word count
  }
}
```

### Safety Result

**Description:** Safety validation output.

```typescript
interface SafetyResult {
  safe: VariantWithScore[];      // Variants that passed all checks
  blocked: BlockedVariant[];     // Variants rejected
}

interface VariantWithScore extends Variant {
  safety_score: number;          // 0.0 - 1.0, higher is safer
  checks_passed: string[];       // List of passed checks
}

interface BlockedVariant {
  id: string;                    // Variant ID
  reason: string;                // Explanation of rejection
  severity: string;              // low, medium, high, critical
  checks_failed: string[];       // List of failed checks
}
```

### Analysis Result

**Description:** Winner selection and metrics.

```typescript
interface AnalysisResult {
  winner: {
    variant_id: string;          // ID of selected variant
    reason: string;               // Why this variant won
    score: number;                // 0.0 - 1.0, confidence score
    confidence: number;           // 0.0 - 1.0, prediction confidence
    rationale: string[];          // Detailed scoring explanation
  };
  experiment: {
    test_id: string;              // Experiment ID
    group: string;                // Treatment group
    control_variant: string;      // Control variant ID
    hypothesis: string;           // Hypothesis being tested
  };
  metrics: {
    avg_safety_score: number;     // Average safety score of safe variants
    total_candidates: number;     // Total variants generated
    safe_count: number;           // Passed safety checks
    blocked_count: number;        // Failed safety checks
    generation_latency_ms: number;
    retrieval_latency_ms: number;
    safety_latency_ms: number;
  }
}
```

### Delivery Result

**Description:** Message delivery outcome.

```typescript
interface DeliveryResult {
  status: string;                // success, failed, queued
  message_id: string;            // Provider message ID
  timestamp: string;             // ISO 8601 timestamp
  recipient: string;             // Recipient email
  channel: string;               // Channel used (email, sms, etc.)
  error?: {
    code: string;
    message: string;
  }
}
```

---

## Examples

### Example 1: Basic Personalization Request

```bash
curl -X POST http://localhost:8000/personalize \
  -H "Content-Type: application/json" \
  -d '{
    "flow_name": "standard_personalization",
    "id": "U001",
    "email": "alice@example.com",
    "name": "Alice",
    "viewed_page": "payment_plans",
    "form_started": "yes",
    "scheduled": "no",
    "attended": "no"
  }'
```

### Example 2: Handling a Blocked Variant

```bash
# Request with 3 variants
# Response shows Variant C blocked due to brand tone violation
# Winner selected from safe variants (A, B)

{
  "safety": {
    "safe": [
      { "id": "A", "safety_score": 0.98 },
      { "id": "B", "safety_score": 0.95 }
    ],
    "blocked": [
      {
        "id": "C",
        "reason": "Brand tone: 'limited time offer' conflicts with friendly brand voice",
        "severity": "medium"
      }
    ]
  },
  "analysis": {
    "winner": {
      "variant_id": "A",
      "reason": "Highest expected CTR after safety check"
    }
  }
}
```

### Example 3: Handling Retrieval Failure

```bash
# Vector DB unavailable during retrieval
# Orchestrator continues with empty citations
# Generator creates variants without KB grounding
# Safety check catches factual grounding issue

{
  "citations": [],
  "variants": [...],
  "safety": {
    "safe": [...],
    "blocked": [
      {
        "id": "D",
        "reason": "Factual claim not grounded in citations",
        "severity": "high"
      }
    ]
  }
}
```

### Example 4: Accessing Audit Trail

```bash
# After personalization, inspect decision at each step

GET /audit?customer_id=U001&request_id=req_abc123

{
  "steps": [
    {
      "step": 1,
      "component": "segmenter",
      "status": "success",
      "output": { "segment": "payment_plans", "intent_level": "high" },
      "latency_ms": 8,
      "timestamp": "2024-11-15T10:30:00Z"
    },
    {
      "step": 2,
      "component": "retriever",
      "status": "success",
      "output": { "citations": [...] },
      "latency_ms": 203,
      "timestamp": "2024-11-15T10:30:01Z"
    },
    // ... etc
  ]
}
```

---

## Rate Limiting

### Current Implementation

**Rate limits are NOT currently enforced** in development.

### Production Implementation (Future)

```
Tier        | Requests/Min | Requests/Hour | Burst
------------|--------------|---------------|-------
Free        | 10           | 300           | 15
Professional| 100          | 10,000        | 150
Enterprise  | 1000         | 100,000       | 2000
```

### Headers

**Request:**
```
X-RateLimit-Request-ID: req_abc123
```

**Response:**
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 287
X-RateLimit-Reset: 1731654660
```

**When exceeded (429 Too Many Requests):**
```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded: 300 requests/hour",
    "retry_after_seconds": 3600
  }
}
```

---

## Webhooks (Future)

Subscribe to async events:

```bash
POST /webhooks/subscribe
{
  "event": "personalization.completed",
  "url": "https://your-service.com/webhook",
  "secret": "your_webhook_secret"
}
```

**Events:**
- `personalization.started` - Personalization request initiated
- `personalization.completed` - Personalization finished successfully
- `personalization.failed` - Personalization failed
- `variant_blocked` - Variant rejected by safety gate
- `message_delivered` - Message successfully sent

---

## Changelog

### Version 1.0 (November 2025)
- ✅ Initial API release
- ✅ Health check endpoint
- ✅ Personalization endpoint
- 🔄 Authentication (coming)
- 🔄 Audit trail endpoint (coming)
- 🔄 Rate limiting (coming)
- 🔄 Webhooks (coming)

---

**For questions, see [ARCHITECTURE.md](./ARCHITECTURE.md) or the [backend tests](./backend/tests/).**
