## Part 1: Product Requirements Documents (PRDs)
I will create three distinct PRDs, each tailored to a specific application and user persona.

PRD 1: The "Personal Knowledge Assistant" (Project: Cognitron)
1. Introduction
Software engineers and knowledge workers are drowning in a sea of disparate information spread across code repositories, design documents, personal notes, emails, and team chats. Finding specific information is a time-consuming and fragmented process that breaks focus and slows down development. Cognitron will be a privacy-first, local AI assistant that unifies a user's entire digital workspace, allowing them to find, connect, and reason over their information with unprecedented speed and intelligence.

2. User Persona
Primary: The Software Engineer/Developer who lives in the terminal and needs to quickly find code snippets, understand architectural documents, and recall project history.

Secondary: The Power User/Knowledge Worker who manages a large local archive of research papers, articles, and personal projects.

3. Goals and Objectives
Primary Goal: To create the ultimate local knowledge management and retrieval tool that drastically reduces the time spent searching for information.

Objective 1: Build a unified index of a user's entire specified workspace (code, docs, notes).

Objective 2: Provide a single, intelligent interface (CLI) to query this index using natural language.

Objective 3: The system must learn from user interactions to improve its retrieval strategies and tool usage over time.

Objective 4: All operations must be performed locally to guarantee user privacy.

4. Features & Requirements
FR-1: Unified CLI Interface

The primary interface will be a command-line tool (cognitron).

Commands will include index, ask, topics, and status.

FR-2: Hybrid Indexing Engine

The system will use a Hybrid Indexing Strategy.

For code files, it will use LEANN's existing AST-aware chunking to preserve code semantics.

For long-form documents (

.md, .pdf), it will use PageIndex's "Smart Chunking" to create semantically coherent chunks based on the document's natural structure.


FR-3: AI-Powered Topic Discovery

The index command will automatically organize the user's files using AI Topic Clustering.

The topics command will list these AI-generated categories, allowing for browsable discovery.

FR-4: Hybrid RAG Query Engine

The ask command will use a Unified Query Router to intelligently handle queries.

It will leverage the "Broad-then-Deep" retrieval model. LEANN will first identify relevant code files or documents, and then PageIndex's reasoning engine will be invoked for a deep-dive analysis on the top candidates.


FR-5: Confidence-Gated Case Memory

Cognitron will be an agentic system that learns from experience.


Every complex workflow (a sequence of commands or a multi-step query) is a "case".

The agent will store not just the final outcome but a 

Confidence Profile for each case, including the LLM's certainty at each step.



When faced with a new task, the agent will retrieve past cases that were both 

successful and executed with high confidence, allowing it to learn and reuse effective, reliable workflows.

5. Non-Goals
This is not a cloud-based SaaS product. It is a local-first application.

We will not build a graphical user interface (GUI) in the first version.

We will not support real-time collaboration or multi-user features.

6. Success Metrics
Adoption: Number of active weekly users in a beta group of developers.

Performance: p95 latency for ask queries under 2 seconds for broad search, under 10 seconds for deep-dive.

Accuracy: Achieve >90% accuracy on a curated benchmark of code retrieval and documentation Q&A tasks.

PRD 2: The "Clinical & Research Co-Pilot" (Project: Thalamus)
1. Introduction
Medical professionals and researchers face the overwhelming challenge of keeping up with an exponentially growing body of literature across countless specialties. Finding specific, evidence-based answers to complex clinical questions is a manual, slow, and error-prone process. Thalamus will be a web-based AI co-pilot that provides trusted, accurate, and traceable answers by deeply reasoning over a vast and disparate corpus of medical resources.

2. User Persona
Primary: The Medical Researcher who needs to synthesize findings from clinical trials, review articles, and guidelines.

Secondary: The Clinician who needs quick, evidence-based answers to specific questions during patient care.

3. Goals and Objectives
Primary Goal: To provide medical professionals with the most accurate, reliable, and traceable answers to complex questions by synthesizing information from a large medical knowledge base.

Objective 1: Ingest and index a wide range of medical documents (PDFs, clinical guidelines, research papers).

Objective 2: Implement a retrieval system that prioritizes accuracy and evidence above all else.

Objective 3: All answers must be accompanied by direct citations and links to the source documents.

Objective 4: The system must learn which sources and retrieval strategies are most effective for different types of medical queries.

4. Features & Requirements
FR-1: Web-Based User Interface

A clean, intuitive web interface for submitting queries and viewing results.

Results will display the synthesized answer, followed by detailed, citable evidence snippets from source documents.

FR-2: Accuracy-Focused RAG Engine

The core engine will be the 

"Broad-then-Deep" model. LEANN will identify candidate papers, and PageIndex will perform a deep reading to extract the precise information.


The index will be built using 

PageIndex's "Smart Chunking" to ensure medical context is never arbitrarily split.

FR-3: Semantic Caching

Implement a semantic cache to provide instant answers to common or previously asked questions, reducing latency and cost.

FR-4: Confidence-Gated Case Memory

Thalamus will learn which types of documents provide the most reliable answers for specific medical domains.

It will store the 

Confidence Profile of each query-retrieval workflow.

When answering a new question, it will prioritize retrieval strategies and source types that have historically resulted in high-confidence success. For example, it will learn to trust official guidelines for dosage questions and clinical trial results for efficacy questions.

FR-5: Cross-Specialty Topic Discovery

Use AI Topic Clustering to organize the corpus, helping researchers discover connections and relevant literature from adjacent medical specialties.

5. Non-Goals
This is not a tool for providing medical advice to patients. It is a decision-support tool for professionals.

It will not have a CLI.

It will not initially support non-text modalities (e.g., DICOM image analysis).

6. Success Metrics
Accuracy: Outperform existing benchmarks on medical Q&A datasets (e.g., MedQA).

User Trust: High repeat usage and positive feedback from a pilot group of researchers and clinicians.

Traceability: 100% of answers must be backed by accurate, clickable citations to the source document section.

PRD 3: The "Corporate Policy & Compliance Bot" (Project: Regulus)
1. Introduction
In any large organization, accessing clear, accurate, and up-to-date information on internal policies and procedures is a constant challenge. Employees waste time searching for the right document, and HR, Legal, and Compliance teams are burdened with answering repetitive questions. Regulus will be an intelligent chatbot that serves as the single source of truth for all corporate policies, providing instant, accurate, and auditable answers to employee questions.

2. User Persona
Primary: The general employee who needs to ask a question about a policy (e.g., "How do I request parental leave?").

Secondary: HR, Legal, and Compliance officers who manage the knowledge base and need to ensure the accuracy and auditability of the information provided.

3. Goals and Objectives
Primary Goal: To provide every employee with instant, accurate, and easy-to-understand answers to questions about company policies, backed by verifiable sources.

Objective 1: Create a single, trusted knowledge base from all official policy and procedure documents.

Objective 2: Deliver answers through a simple chatbot interface integrated into existing company platforms (e.g., Slack, Microsoft Teams, Intranet).

Objective 3: Ensure all answers are 100% traceable to the specific section of the source document.

Objective 4: The system must learn which documents are the authoritative sources for different types of queries.

4. Features & Requirements
FR-1: Chatbot Interface

An easy-to-use chatbot that can be embedded in various corporate platforms.

FR-2: High-Fidelity RAG Engine

The system will use the "Broad-then-Deep" retrieval model to find the correct policy document and then the exact section.

Indexing will be done using 

PageIndex's "Smart Chunking" to preserve the integrity of policy clauses and procedural steps.

Metadata for versioning and effective dates must be stored and filterable.

FR-3: AI-Powered Knowledge Navigation

AI Topic Clustering will be used to automatically organize policies into categories (e.g., "Leave Policies," "IT Security," "Expense Reporting"), which will be presented to users for browsing.

FR-4: Confidence-Gated Case Memory for Authoritative Sources

Regulus will maintain a 

Confidence-Gated Case Memory to learn which documents are the most authoritative sources for different topics.


When an employee asks a question, the agent retrieves past high-confidence cases to inform its search. It learns, for example, that for questions about vacation, the "Employee Handbook" is a more confident source than a departmental memo. This improves accuracy and reduces the chance of citing an outdated or incorrect policy.

FR-5: Admin Dashboard

A simple backend UI for Compliance Officers to upload, manage, and version documents in the knowledge base.

5. Non-Goals
The system will not handle personal employee data (e.g., "How many vacation days do I have left?"). It only provides general policy information.

It will not write or create new policies.

The first version will not have a CLI.

6. Success Metrics
Case Deflection: A measurable reduction in the number of policy-related support tickets sent to HR and IT.

Employee Satisfaction: High ratings from employees on the usefulness and accuracy of the bot's answers.

Auditability: 100% of answers can be successfully audited and traced back to the correct source document and version.




## Part 1: Product Requirements Documents (PRDs)
PRD 1: The "Personal Knowledge Assistant" (Project: Cognitron)
1. Introduction
Software engineers and knowledge workers operate within a fractured digital environment. Critical information is scattered across code repositories, design documents, personal notes, emails, and team chats. The cognitive overhead of locating, connecting, and utilizing this information results in significant productivity loss. Cognitron is a privacy-first, local AI assistant that creates a unified, intelligent workspace on the user's machine. It transforms a chaotic collection of files into an organized, queryable, and continually learning knowledge base.

2. User Persona
The Architect (SWE): Manages multiple codebases and needs to understand legacy systems, find specific function implementations, and cross-reference architectural design documents with the code.

The Maker (Power User): Manages a large local archive of research papers, project notes, and personal data, and needs to discover connections and synthesize information across their entire corpus.

3. Features & Requirements
Epic 1: Intelligent & Hybrid Indexing

Story 1.1: As an Architect, I want the system to automatically use the best indexing method for each file type, so that code is understood semantically and documents are understood structurally without manual configuration.

Acceptance Criteria:

[ ] When indexing, files with extensions .py, .js, .ts, etc., must be processed using LEANN's AST-aware chunking.

[ ] Documents (.pdf, .md) over 20 pages must be processed using the PageIndex "Smart Chunking" engine.

[ ] All other files must be processed with a standard sentence splitter.

Story 1.2: As a Maker, I want my indexed knowledge base to be automatically organized by topic, so that I can browse and discover information without knowing exactly what to search for.

Acceptance Criteria:

[ ] After indexing, the system must perform embedding-based clustering (HDBSCAN) on all chunks.

[ ] An LLM call must be used to assign a human-readable label to each cluster (e.g., "Python Backend APIs," "Personal Finance," "Machine Learning Research").

[ ] The CLI must have a topics command that displays these generated categories.

Epic 2: Advanced Agentic Retrieval

Story 2.1: As an Architect, I want to ask a complex, multi-step question in natural language, so that I can get a precise answer synthesized from both code and documentation.

Acceptance Criteria:

[ ] The system must implement a Planner-Executor agent model. The Planner decomposes queries like "Find the database connection logic and explain its configuration from the design doc."

[ ] The Executor must use the "Broad-then-Deep" retrieval model, first using LEANN to find relevant files, then PageIndex for deep analysis of any long-form documents.

Story 2.2: As a Maker, I want the assistant to learn from my successful and failed interactions, so that it becomes more effective and reliable over time.

Acceptance Criteria:

[ ] Confidence-Gated Case Memory must be implemented.

[ ] Every completed agentic workflow must be stored as a "case" with a ConfidenceProfile (capturing token-level logprobs for each reasoning step).

[ ] For new tasks, the Planner must retrieve past cases that were both successful AND executed with high confidence.

[ ] The retrieved high-confidence strategies must be included in the Planner's prompt context to guide its approach.

4. Success Metrics
Task Success Rate: >85% successful completion rate for a benchmark of 50 common SWE tasks (e.g., "Find the function that handles user authentication," "Summarize the project's deployment process from the README").

Performance: p95 query latency under 3 seconds for searches not requiring a deep-dive.

PRD 2: The "Clinical & Research Co-Pilot" (Project: Thalamus)
1. Introduction
The pace of medical innovation is relentless, making it impossible for clinicians and researchers to stay fully informed. The risk of missing a critical piece of information from a new clinical trial or an updated guideline is high. Thalamus is a professional-grade AI co-pilot designed to provide medical experts with accurate, evidence-based, and fully traceable answers from a vast corpus of medical literature, empowering better clinical decisions and accelerating research.

2. User Persona
The Researcher: Needs to synthesize findings, identify trends, and discover connections across thousands of clinical trials, review articles, and papers.

The Clinician: Needs fast, reliable answers to specific questions during patient care, with complete trust in the evidence provided.

3. Features & Requirements
Epic 1: High-Fidelity Knowledge Base

Story 1.1: As a Researcher, I want to upload a library of PDFs and have the system index them in a way that respects their scientific structure, so that retrieval is precise and contextually aware.

Acceptance Criteria:

[ ] The system must use PageIndex "Smart Chunking" for all ingested documents to preserve the integrity of sections like "Methodology," "Results," and "Conclusion."

[ ] Metadata such as publication date, authors, journal, and document type (e.g., "Clinical Trial," "Guideline") must be extracted and stored with each chunk.

Epic 2: Trustworthy & Traceable Q&A

Story 2.1: As a Clinician, when I ask a question, I want to receive a direct, synthesized answer along with the exact source snippets that support it, so I can verify the information myself.

Acceptance Criteria:

[ ] The system must use the "Broad-then-Deep" retrieval model.

[ ] Every answer must be accompanied by a list of evidence snippets.

[ ] Each snippet must include the source document title, section, page number, and a direct link to open the source PDF.

[ ] The UI must clearly distinguish between the AI-synthesized answer and the source-of-truth evidence.

Story 2.2: As a Researcher, I want the system to learn which sources are most authoritative for different kinds of questions, so its answers become more reliable over time.

Acceptance Criteria:

[ ] Confidence-Gated Case Memory must be implemented.

[ ] Every query is stored as a case with its answer, evidence, and a detailed ConfidenceProfile. User feedback (thumbs up/down) is used to label the case outcome.

[ ] The agent must learn to prioritize sources based on past high-confidence successes. For example, it should learn to prefer "Clinical Guidelines" for dosage questions over "Review Articles."

[ ] This learned priority must be used to dynamically boost the ranking of certain document types during the initial LEANN search.

4. Success Metrics
Accuracy: Achieve >95% accuracy in retrieving the correct information for a benchmark of 100 clinical questions curated by a panel of experts.

Traceability: 100% of generated answers must be supported by correct, verifiable citations displayed in the UI.

PRD 3: The "Corporate Policy & Compliance Bot" (Project: Regulus)
1. Introduction
Navigating corporate policies is a universal source of friction and uncertainty for employees. Ambiguous or hard-to-find information leads to non-compliance, drains productivity, and creates an administrative burden on HR and Legal teams. Regulus is an intelligent compliance bot that provides instant, accurate, and auditable answers to all policy-related questions, acting as the definitive source of truth for the entire organization.

2. User Persona
The Employee: Needs a quick, clear answer to a policy question without having to read a 50-page document.

The Compliance Officer: Needs to manage the knowledge base, ensure the information provided is always up-to-date and accurate, and maintain an audit trail of queries.

3. Features & Requirements
Epic 1: Ironclad Knowledge Management

Story 1.1: As a Compliance Officer, I want to upload, version, and manage all policy documents from a secure admin dashboard, so I can control the single source of truth.

Acceptance Criteria:

[ ] A web-based admin UI allows for uploading new documents and archiving old ones.

[ ] When a document is uploaded, its version and effective_date must be extracted from the content or entered manually. This metadata is mandatory.

[ ] The indexing process must use PageIndex "Smart Chunking" to ensure policy clauses are never split.

Epic 2: Accurate & Auditable Chatbot

Story 2.1: As an Employee, I want to ask a question in my company's chat tool (Slack/Teams) and get an immediate, direct answer with a link to the official policy document.

Acceptance Criteria:

[ ] The chatbot must be available as an integration for Slack and Microsoft Teams.

[ ] The "Broad-then-Deep" retrieval model must be used.

[ ] The initial LEANN search must be filtered to only include documents whose effective_date is in the past and are not archived.

[ ] The answer must begin with a citation: "According to [Policy Name] (v[X], effective [Date]), ..."

Story 2.2: As a Compliance Officer, I want the system to learn which documents are the authoritative sources for different departments, so that it avoids citing outdated or irrelevant departmental memos.

Acceptance Criteria:

[ ] Confidence-Gated Case Memory is implemented to provide a full audit trail of all questions and answers.

[ ] The case memory stores the ConfidenceProfile of the retrieval workflow.

[ ] The agent uses this memory to learn authoritative sources. It learns that the "Global Code of Conduct" is a higher-confidence source for ethics questions than a regional "Team Best Practices" memo.

[ ] This learned source hierarchy is used to heavily boost authoritative documents during retrieval.

4. Success Metrics
Case Deflection: 50% reduction in policy-related support tickets to HR within 6 months of launch.

Auditability: An external auditor can successfully trace 100% of a random sample of 50 answers back to the correct source document and section via the case memory logs.

## Part 2: Meticulously Detailed Build Checklists
Build Checklist 1: Personal Knowledge Assistant (Cognitron)
Phase 1: Foundation & Environment Setup

[ ] Init Git repo and set up uv with pyproject.toml.

[ ] Add dependencies: leann-core, leann-backend-hnsw, pageindex (as a local module), typer, rich, scikit-learn, sqlite.

[ ] Configure ruff and pytest. Implement a basic CI pipeline on GitHub Actions to run linters and initial tests.

[ ] Define project structure: cognitron/ (for core logic), cli.py, tests/.

Phase 2: Core Technology Integration & Indexing

[ ] Data Models: In cognitron/models.py, define Pydantic or dataclass models for Chunk, DocumentMetadata, and Topic.

[ ] IndexingService:

[ ] In cognitron/indexing.py, create class IndexingService.

[ ] Implement async def run_indexing(self, paths: List[Path]):

[ ] Iterate through paths. For each file, determine strategy using a _get_strategy(file_path) helper.

[ ] Smart Chunking Logic: If strategy is pageindex, call pageindex.page_index.page_index_main, iterate through the resulting tree, and create Chunk objects from each node.

[ ] AST Chunking Logic: If strategy is ast, read file and use astchunk to generate chunks.

[ ] Add all generated chunks to a LeannBuilder instance and call build_index.

[ ] TopicService:

[ ] In cognitron/topics.py, create class TopicService.

[ ] Implement async def generate_topics(self, index_path: str):

[ ] Load all embeddings from the LEANN index.

[ ] Run HDBSCAN on the embedding matrix.

[ ] For each cluster, sample texts, generate a label with an LLM, and save to topics.json.

Phase 3: Agentic Layer & Confidence Memory

[ ] Agent & LLM Backend:

[ ] In cognitron/agent.py, create class CognitronAgent.

[ ] In cognitron/llm.py, create a wrapper around openai.AsyncOpenAI that modifies chat.completions.create to always include logprobs=True and top_logprobs=5. It should parse and return both the message and the logprobs object.

[ ] Confidence Calculation:

[ ] In cognitron/confidence.py, implement calculate_confidence_profile(trace: List[LLMCall]) -> ConfidenceProfile.

[ ] Define the ConfidenceProfile data schema: { "planner_confidence": float, "steps": [ { "step_confidence": float, "tool_confidence": float } ] }. Use the "Lowest Group Confidence" metric.

[ ] ConfidenceGatedCaseMemory:

[ ] In cognitron/memory.py, create class CaseMemory using SQLite.

[ ] DB Schema: cases (id, timestamp, query, outcome, confidence_profile_json).

[ ] Implement async def add_case(...) and async def retrieve_cases(query: str, min_confidence: float). Retrieval uses a simple embedding similarity search on the query column.

Phase 4: CLI Application

[ ] In cli.py, set up Typer application.

[ ] cognitron index: Takes a list of paths, runs IndexingService, then TopicService.

[ ] cognitron ask: Instantiates CognitronAgent, runs the query, and uses rich to print the final answer and any intermediate thoughts.

[ ] cognitron topics: Loads topics.json and displays it in a formatted table.

Phase 5: Testing, Benchmarking, and Hardening

[ ] Create a tests/fixtures directory with sample code and documents.

[ ] Write unit tests for confidence calculation and indexing strategies.

[ ] Write an end-to-end integration test for the ask command that mocks LLM calls but uses a real index.

[ ] Benchmark index command performance on a 1000-file repository.

[ ] Validate that no network traffic occurs during local operations (except for intended LLM calls).

Build Checklist 2: Clinical & Research Co-Pilot (Thalamus)
Phase 1: Foundation & Environment Setup

[ ] Init Git monorepo with backend/ and frontend/ directories.

[ ] Backend: FastAPI project with uv. Dependencies: fastapi, uvicorn, leann-core, pageindex, psycopg2-binary (for PostgreSQL), arq.

[ ] Frontend: Next.js project with TypeScript, Tailwind CSS, and react-query for data fetching.

[ ] Set up docker-compose.yml with services for the backend, frontend, PostgreSQL, and Redis (for the task queue).

Phase 2: Core Technology Integration & Indexing

[ ] Database Schema: Use an ORM (e.g., SQLAlchemy) to define tables for Documents (with metadata like publication_date, document_type), Cases, and background IndexingJobs.

[ ] IndexingService:

[ ] In backend/services/indexing.py, create an arq worker function process_and_index_document(ctx, doc_id: int).

[ ] Logic: Fetch doc from DB -> run PageIndex "Smart Chunking" -> extract metadata -> add chunks to LeannBuilder -> build/update index.

[ ] API Endpoint /upload:

[ ] Create a secure endpoint that accepts a PDF file, saves it to storage (e.g., S3), creates a Documents record in the DB, and enqueues an arq job to index it.

[ ] RetrievalService:

[ ] In backend/services/retrieval.py, implement async def broad_then_deep_query(...).

[ ] Define the API contract for the /query endpoint. Request: { "query": str }. Response: { "answer": str, "evidence": List[EvidenceSnippet] }.

[ ] Logic: Implement the two-stage retrieval. The response must be validated to ensure all evidence snippets are populated correctly.

Phase 3: Agentic Layer & Confidence Memory

[ ] ResearchAgent: The main broad_then_deep_query function will be orchestrated by this agent.

[ ] LLM Backend: Create an LLM service that requests and parses logprobs for all calls.

[ ] ConfidenceGatedCaseMemory:

[ ] Implement CaseMemory service with methods to write cases to the PostgreSQL DB and retrieve them.

[ ] Schema for ConfidenceProfile must include scores for each stage of the "Broad-then-Deep" process: triage_leann_confidence, deepdive_pageindex_confidence, synthesis_confidence.

[ ] Confidence-Based Source Boosting:

[ ] Add a document_type field to the Documents table.

[ ] When the ResearchAgent starts a query, it retrieves past high-confidence cases.

[ ] It performs a simple analysis: "For queries like this, which document_types appeared most often in successful, high-confidence results?"

[ ] It then passes a boost parameter to the LeannSearcher to up-rank results from those document types.

Phase 4: Web Application

[ ] Backend API: Build out the full FastAPI application with endpoints for query, document management, and user feedback.

[ ] Frontend UI:

[ ] Design a search interface and a results view.

[ ] The results view must render the synthesized answer and the interactive "Evidence" cards.

[ ] Clicking an evidence card should highlight the text and provide a link to the source PDF.

[ ] Implement the thumbs up/down feedback buttons and connect them to a /feedback API endpoint.

Phase 5: Testing & Validation

[ ] Write unit tests for all services and API endpoints.

[ ] Create a "golden dataset" of 20 medical PDFs and 50 questions with known answers and source locations.

[ ] Write an end-to-end test that runs through the golden dataset and asserts that accuracy is >90% and all citations are correct.

[ ] Load test the /query endpoint to ensure p95 latency is under 15 seconds.

[ ] Set up a staging environment and conduct a beta test with at least 5 medical professionals.

Build Checklist 3: Corporate Policy & Compliance Bot (Regulus)
Phase 1: Foundation & Environment Setup

[ ] Init Git monorepo with backend/, admin_frontend/, integrations/.

[ ] Backend: FastAPI project. Dependencies are the same as Thalamus.

[ ] Admin Frontend: Simple Vue.js or React single-page application.

[ ] Integrations: Set up boilerplate for a Slack Bot using the slack_bolt library and a Teams bot using botbuilder.

[ ] Dockerize the backend and set up a CI/CD pipeline.

Phase 2: Core Technology Integration & Indexing

[ ] Database Schema: Define tables for PolicyDocuments (with version, effective_date, is_archived boolean), and AuditTrail (to serve as the Case Memory).

[ ] PolicyIndexingService:

[ ] An arq background worker function index_policy_document(doc_id: int).

[ ] Logic must use PageIndex "Smart Chunking".

[ ] It must parse version and effective_date from the document text or use user-provided values and store them as metadata in the LEANN index for every chunk.

[ ] PolicyRetrievalService:

[ ] Implements "Broad-then-Deep".

[ ] Critical Filter: The initial LEANN search MUST include a metadata filter: { "is_archived": { "is_false": True } }. It must also have logic to find the single latest version of a document when multiple exist.

[ ] The final response must be a string formatted with the source citation.

Phase 3: Agentic Layer & Confidence Memory

[ ] ComplianceAgent: Orchestrates the retrieval logic.

[ ] LLM Backend: Must request and parse logprobs.

[ ] ConfidenceGatedCaseMemory (Audit Trail):

[ ] The AuditTrail table in the database will serve this function.

[ ] Schema: (query_id, timestamp, user_id, user_question, bot_answer, confidence_profile_json, source_document_id, source_version).

[ ] After every query, a record is written to this table.

[ ] Confidence for Authoritative Source Boosting:

[ ] Add a source_type (e.g., "Global Policy," "Departmental Memo") to the PolicyDocuments table.

[ ] The agent will query the audit trail to learn that for compliance queries, "Global Policy" documents lead to higher-confidence, successful outcomes.

[ ] This learning is used to boost global policies in the LEANN search.

Phase 4: Application Interfaces

[ ] Backend API:

[ ] /chat: Accepts a question and user ID, returns a formatted string answer.

[ ] /admin/upload: Secure endpoint for admins.

[ ] /admin/audit: Secure endpoint to view the AuditTrail log.

[ ] Admin Frontend:

[ ] A simple UI for uploading/archiving documents and viewing the audit trail.

[ ] Chatbot Integrations:

[ ] Implement the Slack bot logic to listen for mentions, call the /chat API, and post the response.

[ ] Implement the same for the Microsoft Teams bot.

Phase 5: Testing, Security & Audit

[ ] Create a test suite with 50 common HR/IT policy questions.

[ ] Write tests to explicitly check the version filtering logic (i.e., ensure an outdated policy is never cited).

[ ] Perform a security review of the admin dashboard, focusing on access control (RBAC).

[ ] Write an end-to-end test that simulates a user asking a question on Slack and validates the response.

[ ] Ask the legal/compliance team to review 20 sample answers for accuracy and clarity before deploying.