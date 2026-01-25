# Cognitron: Personal Knowledge Assistant - Product Requirements Document (PRD)

## 1. Introduction
Software engineers and knowledge workers are drowning in a sea of disparate information spread across code repositories, design documents, personal notes, emails, and team chats. Finding specific information is a time-consuming and fragmented process that breaks focus and slows down development. Cognitron will be a privacy-first, local AI assistant that unifies a user's entire digital workspace, allowing them to find, connect, and reason over their information with unprecedented speed and intelligence.

## 2. User Persona
- **Primary**: The Software Engineer/Developer who lives in the terminal and needs to quickly find code snippets, understand architectural documents, and recall project history.
- **Secondary**: The Power User/Knowledge Worker who manages a large local archive of research papers, articles, and personal projects.

## 3. Goals and Objectives
- **Primary Goal**: To create the ultimate local knowledge management and retrieval tool that drastically reduces the time spent searching for information.
- **Objectives**:
  - Index and retrieve from a user's entire specified workspace (code, docs, notes).
  - Provide a single, intelligent interface (CLI) to query this index using natural language.
  - Learn from user interactions to improve its retrieval strategies and tool usage over time.
  - Ensure all operations are performed locally to guarantee user privacy.

## 4. Features & Requirements
### FR-1: Unified CLI Interface
The primary interface will be a command-line tool (cognitron). Commands will include index, ask, topics, and status.

### FR-2: Hybrid Indexing Engine
The system will use a Hybrid Indexing Strategy. For code files, it will use LEANN's existing AST-aware chunking to preserve code semantics. For long-form documents (.md, .pdf), it will use PageIndex's "Smart Chunking" to create semantically coherent chunks based on the document's natural structure.

### FR-3: AI-Powered Topic Discovery
The index command will automatically organize the user's files using AI Topic Clustering. The topics command will list these AI-generated categories, allowing for browsable discovery.

### FR-4: Hybrid RAG Query Engine
The ask command will use a Unified Query Router to intelligently handle queries. It will leverage the "Broad-then-Deep" retrieval model. LEANN will first identify relevant code files or documents, and then PageIndex's reasoning engine will be invoked for a deep-dive analysis on the top candidates.

### FR-5: Confidence-Gated Case Memory
Cognitron will be an agentic system that learns from experience. Every complex workflow (a sequence of commands or a multi-step query) is a "case". The agent will store not just the final outcome but a Confidence Profile for each case, including the LLM's certainty at each step. When faced with a new task, the agent will retrieve past cases that were both successful and executed with high confidence, allowing it to learn and reuse effective, reliable workflows.

## 5. Non-Goals
This is not a cloud-based SaaS product. It is a local-first application. We will not build a graphical user interface (GUI) in the first version. We will not support real-time collaboration or multi-user features.

## 6. Success Metrics
Adoption: Number of active weekly users in a beta group of developers. Performance: p95 latency for ask queries under 2 seconds for broad search, under 10 seconds for deep-dive. Accuracy: Achieve >90% accuracy on a curated benchmark of code retrieval and documentation Q&A tasks.

## 7. Dependencies & Prerequisites
- LEANN: leann-core, leann-backend-hnsw packages.
- PageIndex: Local module with OpenAI API key for LLM reasoning (set CHATGPT_API_KEY).
- deepConf: Patched vLLM installation (apply changes to vllm/v1/engine/logprobs.py and output_processor.py).
- Database: SQLite for case memory.
