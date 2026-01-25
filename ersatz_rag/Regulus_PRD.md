# Regulus: Corporate Policy & Compliance Bot - Product Requirements Document (PRD)

## 1. Introduction
In large organizations, accessing accurate, up-to-date corporate policies is a major friction point. Employees struggle with finding relevant information, leading to non-compliance risks and HR burden. Regulus is an intelligent, web-based chatbot that serves as the definitive source of truth for all company policies, providing instant, traceable answers with 100% auditability. This implementation follows Option 1: Full-Featured Implementation, integrating LEANN for efficient indexing, PageIndex for reasoning-based document structuring, and deepConf for confidence-based early stopping in LLM responses.

## 2. User Persona
- **Primary**: General employees needing quick, clear answers to policy questions (e.g., "How do I request parental leave?").
- **Secondary**: Compliance officers managing the knowledge base, uploading documents, and ensuring auditability.

## 3. Goals and Objectives
- **Primary Goal**: Deliver instant, accurate, auditable answers to policy questions, backed by authoritative sources.
- **Objectives**:
  - Index and retrieve from a single source of truth using advanced RAG technologies.
  - Ensure all answers are traceable with citations and version control.
  - Learn from interactions to prioritize authoritative sources.
  - Achieve >90% accuracy and 100% auditability.

## 4. Features & Requirements
### FR-1: Web-Based Chatbot Interface
- Clean UI for submitting questions and viewing answers with evidence snippets.
- No Slack/Teams integration for this phase.

### FR-2: Advanced Retrieval Engine
- **Broad-then-Deep Model**: Use LEANN's LeannSearcher for initial broad search with metadata filters (e.g., effective_date > current, is_archived=false), then PageIndex's reasoning engine for deep analysis on top candidates.
- PageIndex Smart Chunking: Generate tree structure from PDFs using page_index_main, preserving policy integrity through hierarchical nodes.
- Metadata filtering for version and effective dates.

### FR-3: Confidence-Gated Case Memory
- Store interaction history with confidence profiles from deepConf's sliding window calculation (confidence = -avg(logprobs of alternative tokens)).
- Learn authoritative sources (e.g., boost global policies over departmental memos) by analyzing past high-confidence cases.
- Early stopping when confidence drops below threshold.

### FR-4: Admin Dashboard
- Upload, version, and manage policy documents.
- View audit trail of queries and answers.

### FR-5: Integration of Core Technologies
- LEANN: Use LeannBuilder for efficient indexing with selective recomputation, LeannSearcher for vector retrieval with metadata support.
- PageIndex: Call page_index_main on PDFs to generate tree structures (nodes with node_id, title, summary, page ranges), integrate as chunks for LEANN.
- deepConf: Patch vLLM's LogprobsProcessor for confidence tracking, enable via SamplingParams.extra_args (enable_conf=true, window_size=2048, threshold=17).

## 5. Non-Goals
- No real-time collaboration or multi-user editing.
- No patient data handling (this is for corporate policies only).
- No GUI beyond web interface.

## 6. Success Metrics
- Case Deflection: 50% reduction in policy-related support tickets.
- Employee Satisfaction: High ratings on accuracy and ease of use.
- Auditability: 100% traceable answers with citations to node_id, page ranges, and document versions.
- Accuracy: >90% correct retrieval in benchmark tests using PageIndex's reasoning capabilities.

## 7. Dependencies & Prerequisites
- LEANN: leann-core, leann-backend-hnsw packages from PyPI or local install.
- PageIndex: Local module with OpenAI API key for LLM reasoning (set CHATGPT_API_KEY).
- deepConf: Patched vLLM installation (apply changes to vllm/v1/engine/logprobs.py and output_processor.py).
- Database: PostgreSQL for documents and audit trail storage.
