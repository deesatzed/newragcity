# Correct the Gaps: Build Guide and Checklist

## 1. Introduction
This document provides a detailed, step-by-step guide to transform the `Regulus`, `Cognitron`, and `Thalamus` architectural prototypes into fully functional applications. The core task is to replace all simulated components and heuristic-based logic with real, production-grade implementations of the `PageIndex`, `LEANN`, and `deepConf` technologies, and to integrate the required external APIs.

This guide is structured into three parts:
1.  **Core Technology Implementation**: Foundational steps applicable to all three projects.
2.  **Application-Specific Checklists**: Targeted actions to functionalize each application.
3.  **Testing and Validation**: A framework for verifying the completed work.

---

## 2. Universal Core Technology Implementation

These steps are prerequisites for all three applications. The goal is to have centrally managed, fully operational `PageIndex`, `LEANN`, and `deepConf` services.

### 2.1. `deepConf` Service Implementation
**Current State:** Confidence scores are simulated using heuristics on search results, not by analyzing the LLM's generative process.
**Target State:** A standalone microservice that accepts an LLM prompt and returns a calibrated confidence score based on token log-probabilities.

**Checklist:**
- [ ] **Develop `deepConf` Microservice:**
    - [ ] Create a new FastAPI application for the `deepConf` service.
    - [ ] Define an API endpoint (e.g., `/calculate_confidence`) that accepts a prompt, context, and the full log-probability data from an LLM call.
    - [ ] Implement the core logic to analyze log-probabilities. This involves calculating sequence likelihood, identifying low-confidence tokens (potential hallucinations), and normalizing the score.
    - [ ] The service should return a JSON object containing the final confidence score (0.0-1.0), a list of low-confidence tokens, and a justification.
- [ ] **Integrate `deepConf` with LLM Calls:**
    - [ ] Modify the central LLM wrapper (e.g., [regulus/backend/app/llm.py](cci:7://file:///Volumes/WS4TB/ERSATZ_RAG/regulus/backend/app/llm.py:0:0-0:0)) to always request log-probabilities from the underlying model (e.g., OpenAI's `logprobs=True`).
    - [ ] After receiving a response from the LLM, the wrapper must make a subsequent call to the new `deepConf` microservice, passing the required data.
    - [ ] The LLM wrapper should then return both the generated text and the full confidence report from `deepConf`.

### 2.2. `PageIndex` Service Implementation
**Current State:** Document structure analysis is simulated with basic keyword matching.
**Target State:** A robust service that uses real document processing libraries to analyze layout, extract metadata, and build a hierarchical index.

**Checklist:**
- [ ] **Develop `PageIndex` Service:**
    - [ ] Create a new service that accepts a document (e.g., PDF, DOCX).
    - [ ] Integrate a powerful PDF/document analysis library (e.g., `PyMuPDF`, `pdfplumber`, `unstructured-io`).
    - [ ] Implement logic to identify structural elements: headers (H1, H2, etc.), tables, lists, paragraphs, and footers based on font size, style, and position.
    - [ ] The service should output a structured JSON representation of the document, where each text chunk is tagged with its structural role and location (e.g., `page: 5, type: 'table', section_header: '2.1 Results'`).
    - [ ] This structured JSON is the "evidence-based index" that will be used for retrieval.

### 2.3. `LEANN` Service Implementation
**Current State:** `Regulus` uses the library correctly, but `Cognitron` and `Thalamus` use simple keyword searches on hardcoded dictionaries.
**Target State:** All applications use a real, high-performance vector search engine.

**Checklist:**
- [ ] **Deploy a Vector Database:**
    - [ ] Set up and run a dedicated vector database instance (e.g., `Weaviate`, `Pinecone`, `Qdrant`). This will serve as the backend for `LEANN`.
- [ ] **Standardize `LEANN` Integration:**
    - [ ] Ensure the `leann-core` library is configured to connect to the deployed vector database.
    - [ ] Create a standardized client class for interacting with `LEANN` that can be shared across all three projects.
    - [ ] The client must handle embedding text chunks (from `PageIndex`) and querying the vector database.

---

## 3. Application-Specific Implementation Checklists

### 3.1. `Regulus`: Correcting the Gaps
**Overall Goal:** Replace the heuristic confidence calculation with the real `deepConf` service.

- [ ] **File: [regulus/backend/app/three_approach_integration.py](cci:7://file:///Volumes/WS4TB/ERSATZ_RAG/regulus/backend/app/three_approach_integration.py:0:0-0:0)**
    - [ ] **Remove Heuristic Confidence:** Delete the internal functions that calculate confidence based on search result scores.
    - [ ] **Integrate `deepConf` Report:** Modify the `query_and_generate` function to use the confidence report returned by the updated [llm.py](cci:7://file:///Volumes/WS4TB/ERSATZ_RAG/regulus/backend/app/llm.py:0:0-0:0) wrapper. The decision to show an answer should be based on the `deepConf` score, not the search score.
- [ ] **File: [regulus/backend/app/llm.py](cci:7://file:///Volumes/WS4TB/ERSATZ_RAG/regulus/backend/app/llm.py:0:0-0:0)**
    - [ ] **Implement `deepConf` Call:** As described in section 2.1, this file should be updated to call the `deepConf` microservice after getting the LLM response.

### 3.2. `Cognitron`: From Mock-up to Functional Tool
**Overall Goal:** Replace all simulated indexing and confidence logic with the real core services.

- [ ] **File: [cognitron/cognitron/indexing/service.py](cci:7://file:///Volumes/WS4TB/ERSATZ_RAG/cognitron/cognitron/indexing/service.py:0:0-0:0)**
    - [ ] **Remove Simulated Indexing:** Delete the `_chunk_code_heuristically` and `_chunk_document_heuristically` methods.
    - [ ] **Integrate `PageIndex`:** The `process_file` method must now call the real `PageIndex` service to get structured JSON chunks.
    - [ ] **Integrate `LEANN`:** After receiving chunks from `PageIndex`, this service must use the `LEANN` client to embed and store them in the vector database.
- [ ] **File: [cognitron/cognitron/core/confidence.py](cci:7://file:///Volumes/WS4TB/ERSATZ_RAG/cognitron/cognitron/core/confidence.py:0:0-0:0)**
    - [ ] **Gut the Placeholder:** This file should be almost entirely rewritten. Delete all internal calculation logic.
    - [ ] **Wrap `deepConf` Service:** The `DeveloperGradeConfidenceCalculator` class should now be a simple client that calls the `deepConf` microservice. Its `calculate_confidence` method will pass the LLM data to the service and return the result.
- [ ] **File: [cognitron/cognitron/core/llm.py](cci:7://file:///Volumes/WS4TB/ERSATZ_RAG/cognitron/cognitron/core/llm.py:0:0-0:0) (or equivalent)**
    - [ ] **Enable Log-probabilities:** Ensure the LLM interface actually requests log-probabilities, which it currently does not. This is critical for `deepConf` to function.

### 3.3. `Thalamus`: From Blueprint to Prototype
**Overall Goal:** Replace the entire simulated pipeline with real service integrations and add external API clients.

- [ ] **File: [thalamus/mandatory_integrated_medical_pipeline.py](cci:7://file:///Volumes/WS4TB/ERSATZ_RAG/thalamus/mandatory_integrated_medical_pipeline.py:0:0-0:0)**
    - [ ] **Complete Rewrite:** This file must be refactored from a simulation into a real orchestration pipeline.
    - [ ] **Replace [PageIndexMedicalProcessor](cci:2://file:///Volumes/WS4TB/ERSATZ_RAG/thalamus/mandatory_integrated_medical_pipeline.py:22:0-209:57):** Delete the class. All calls to it should be replaced with calls to the real `PageIndex` service.
    - [ ] **Replace [LEANNMedicalEnhancer](cci:2://file:///Volumes/WS4TB/ERSATZ_RAG/thalamus/mandatory_integrated_medical_pipeline.py:212:0-431:31):** Delete the class. Replace hardcoded dictionaries with queries to the `LEANN` service.
    - [ ] **Replace [DeepConfMedicalValidator](cci:2://file:///Volumes/WS4TB/ERSATZ_RAG/thalamus/mandatory_integrated_medical_pipeline.py:434:0-852:36):** Delete the class. Replace heuristic calculations with calls to the real `deepConf` service.
- [ ] **Create `medplum_client.py`**
    - [ ] Implement a client to connect to the Medplum FHIR API using the provided API key.
    - [ ] Create functions to fetch patient data, observations, and other relevant FHIR resources.
    - [ ] Add robust error handling and data validation (e.g., using Pydantic models for FHIR resources).
- [ ] **Create `biomcp_client.py`**
    - [ ] Implement a client to query the BioMCP / PubMed API.
    - [ ] Create functions to search for medical literature based on keywords and retrieve abstracts or full-text articles.
- [ ] **Integrate External APIs:**
    - [ ] In the refactored [mandatory_integrated_medical_pipeline.py](cci:7://file:///Volumes/WS4TB/ERSATZ_RAG/thalamus/mandatory_integrated_medical_pipeline.py:0:0-0:0), add logic to enrich the context for the LLM by calling the `Medplum` and `BioMCP` clients based on the user's query.

---

## 4. Testing and Validation Strategy

- [ ] **Unit Tests:** For each new client and service, write unit tests to verify its functionality in isolation. Mock external API calls.
- [ ] **Integration Tests:**
    - [ ] **Test 1 (Regulus):** Create a test that indexes a policy document using `PageIndex` and `LEANN`, asks a question, and verifies that the `deepConf` score is above a certain threshold.
    - [ ] **Test 2 (Cognitron):** Create a test that indexes a source code file, asks a technical question, and verifies a high `deepConf` score.
    - [ ] **Test 3 (Thalamus):** Create a test that asks a clinical question, verifies that both `Medplum` and `BioMCP` are called, and checks the final `deepConf` score.
- [ ] **End-to-End (E2E) Tests:**
    - [ ] Run the full application stack (e.g., using Docker Compose) and test the flow from a user query to a final, confidence-gated answer.
    - [ ] Use the test suites already present in the projects (e.g., [comprehensive_qa_accuracy_test_suite.py](cci:7://file:///Volumes/WS4TB/ERSATZ_RAG/thalamus/comprehensive_qa_accuracy_test_suite.py:0:0-0:0)) but run them against the fully integrated, non-simulated applications.