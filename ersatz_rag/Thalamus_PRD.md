# Thalamus: Clinical & Research Co-Pilot - Product Requirements Document (PRD)

## 1. Introduction
Medical professionals and researchers face the overwhelming challenge of keeping up with an exponentially growing body of literature across countless specialties. Finding specific, evidence-based answers to complex clinical questions is a manual, slow, and error-prone process. Thalamus will be a web-based AI co-pilot that provides trusted, accurate, and traceable answers by deeply reasoning over a vast and disparate corpus of medical resources.

## 2. User Persona
- **Primary**: The Medical Researcher who needs to synthesize findings from clinical trials, review articles, and guidelines.
- **Secondary**: The Clinician who needs quick, evidence-based answers to specific questions during patient care.

## 3. Goals and Objectives
- **Primary Goal**: To provide medical professionals with the most accurate, reliable, and traceable answers to complex questions by synthesizing information from a large medical knowledge base.
- **Objectives**:
  - Ingest and index a wide range of medical documents (PDFs, clinical guidelines, research papers).
  - Implement a retrieval system that prioritizes accuracy and evidence above all else.
  - All answers must be accompanied by direct citations and links to the source documents.
  - The system must learn which sources and retrieval strategies are most effective for different types of medical queries.

## 4. Features & Requirements
### FR-1: Web-Based User Interface
A clean, intuitive web interface for submitting queries and viewing results. Results will display the synthesized answer, followed by detailed, citable evidence snippets from source documents.

### FR-2: Accuracy-Focused RAG Engine
The core engine will be the "Broad-then-Deep" model. LEANN will identify candidate papers, and PageIndex will perform a deep reading to extract the precise information. The index will be built using PageIndex's "Smart Chunking" to ensure medical context is never arbitrarily split. Use LEANN's LeannSearcher for broad retrieval with metadata filters (e.g., document_type, publication_date). PageIndex generates tree structures from PDFs using page_index_main, preserving medical context through hierarchical nodes.

### FR-3: Semantic Caching
Implement a semantic cache to provide instant answers to common or previously asked questions, reducing latency and cost.

### FR-4: Confidence-Gated Case Memory
Thalamus will learn which types of documents provide the most reliable answers for specific medical domains. It will store the Confidence Profile of each query-retrieval workflow. When answering a new question, it will prioritize retrieval strategies and source types that have historically resulted in high-confidence success. For example, it will learn to trust official guidelines for dosage questions and clinical trial results for efficacy questions. Confidence calculated as -avg(logprobs of alternative tokens) in sliding window. Early stopping when confidence drops below threshold.

### FR-5: Cross-Specialty Topic Discovery
Use AI Topic Clustering to organize the corpus, helping researchers discover connections and relevant literature from adjacent medical specialties.

## 5. Non-Goals
This is not a tool for providing medical advice to patients. It is a decision-support tool for professionals. It will not have a CLI. It will not initially support non-text modalities (e.g., DICOM image analysis).

## 6. Success Metrics
Accuracy: Outperform existing benchmarks on medical Q&A datasets (e.g., MedQA). User Trust: High repeat usage and positive feedback from a pilot group of researchers and clinicians. Traceability: 100% of answers must be backed by accurate, clickable citations to the source document section.

## 7. Dependencies & Prerequisites
- LEANN: leann-core, leann-backend-hnsw packages.
- PageIndex: Local module with OpenAI API key for LLM reasoning (set CHATGPT_API_KEY).
- deepConf: Patched vLLM installation (apply changes to vllm/v1/engine/logprobs.py and output_processor.py).
- Database: PostgreSQL for documents and cases.
