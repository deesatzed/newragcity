"""
Cognitron Agent: Developer-grade personal knowledge assistant
Combines PageIndex + LEANN + DeepConf architecture for local AI with production-level reliability
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from ..models import (
    CaseMemoryEntry, ConfidenceLevel, QueryResult, 
    WorkflowStep, WorkflowTrace
)
from .confidence import (
    ConfidenceCalculator, ConfidenceProfile, LLMCall, 
    calculate_confidence_profile
)
from .memory import CaseMemory
from .llm import DeveloperGradeLLM
from .router import QueryRouter
from ..indexing.service import IndexingService
from ..topics.service import TopicService


class CognitronAgent:
    """
    Developer-grade personal knowledge assistant
    
    Breakthrough features:
    - Developer AI confidence calibration applied to personal knowledge
    - Self-improving case memory with confidence-based learning
    - Multi-domain intelligence: code + documents + quality validation
    - Local-first processing with privacy guarantees
    """
    
    def __init__(
        self,
        index_path: Path,
        memory_path: Path,
        confidence_threshold: float = 0.85,
        developer_threshold: float = 0.95
    ):
        self.index_path = index_path
        self.memory_path = memory_path
        self.confidence_threshold = confidence_threshold
        self.developer_threshold = developer_threshold
        
        # Core components (enterprise-grade architecture)
        self.llm = DeveloperGradeLLM()
        self.confidence_calculator = ConfidenceCalculator(developer_threshold, confidence_threshold)
        self.case_memory = CaseMemory(memory_path)
        self.indexing_service = IndexingService(index_path)
        self.topic_service = TopicService()
        
        # Query routing intelligence
        self.query_router = QueryRouter(self)
        
        print("🧠 Cognitron Agent Initialized")
        print(f"   Developer-grade confidence threshold: {developer_threshold:.1%}")
        print(f"   Production confidence threshold: {confidence_threshold:.1%}")
        print("   Multi-domain intelligence: Code + Documents + Quality Validation")
        
    async def ask(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        require_high_confidence: bool = True
    ) -> QueryResult:
        """
        Process a knowledge query with enterprise-grade quality assurance
        
        Args:
            query: Natural language question
            context: Optional context information
            require_high_confidence: Whether to require high confidence for display
            
        Returns:
            QueryResult with confidence metrics and quality validation
        """
        query_start_time = time.time()
        
        # Step 1: Check case memory for similar high-confidence solutions
        print(f"🔍 Processing query: {query}")
        memory_cases = await self._check_case_memory(query)
        
        # Step 2: Route query through appropriate retrieval strategy
        workflow_trace = await self.query_router.route_query(query, context, memory_cases)
        
        # Step 3: Calculate enterprise-grade confidence profile
        confidence_profile = self._calculate_workflow_confidence(workflow_trace)
        
        # Step 4: Generate final answer with confidence validation
        final_answer, supporting_chunks = await self._synthesize_answer(
            query, workflow_trace, confidence_profile
        )
        
        processing_time = time.time() - query_start_time
        
        # Step 5: Create query result with enterprise-grade validation
        result = QueryResult(
            query_text=query,
            answer=final_answer,
            retrieval_confidence=confidence_profile.overall_confidence,
            reasoning_confidence=confidence_profile.planner_confidence,
            factual_confidence=min([step["step_confidence"] for step in confidence_profile.steps]) if confidence_profile.steps else 0.5,
            overall_confidence=confidence_profile.overall_confidence,
            relevant_chunks=supporting_chunks,
            confidence_explanation=confidence_profile.confidence_explanation,
            uncertainty_factors=confidence_profile.uncertainty_factors,
            processing_time=processing_time
        )
        
        # Step 6: Store successful high-confidence cases in memory
        if result.overall_confidence >= self.confidence_threshold and result.should_display:
            await self.case_memory._ensure_db_initialized()
            await self.case_memory.add_case(
                query=query,
                outcome=final_answer,
                workflow_trace=workflow_trace,
                confidence_profile=confidence_profile,
                success=True,
                execution_time=processing_time
            )
            
        print(f"✅ Query completed: {result.confidence_level.value} confidence ({result.overall_confidence:.1%})")
        
        return result
        
    async def _check_case_memory(self, query: str) -> List[CaseMemoryEntry]:
        """Check case memory for similar high-confidence solutions"""
        # Ensure database is initialized before retrieving cases
        await self.case_memory._ensure_db_initialized()
        similar_cases = await self.case_memory.retrieve_cases(
            query=query,
            min_confidence=self.confidence_threshold,
            max_cases=3,
            similarity_threshold=0.8
        )
        
        if similar_cases:
            print(f"💭 Found {len(similar_cases)} similar high-confidence cases")
        
        return similar_cases
        
    def _calculate_workflow_confidence(self, workflow_trace: WorkflowTrace) -> ConfidenceProfile:
        """Calculate enterprise-grade confidence profile for workflow"""
        # Extract LLM calls from workflow trace (simplified for this implementation)
        llm_calls_by_step = {}
        
        confidence_profile = calculate_confidence_profile(workflow_trace, llm_calls_by_step)
        return confidence_profile
        
    async def _synthesize_answer(
        self,
        query: str,
        workflow_trace: WorkflowTrace,
        confidence_profile: ConfidenceProfile
    ) -> Tuple[str, List[Any]]:
        """
        Synthesize final answer with enterprise-grade quality validation
        """
        if not workflow_trace.steps:
            return "I don't have sufficient information to answer this query with confidence.", []
            
        # Extract information from workflow steps
        retrieved_information = []
        supporting_chunks = []
        
        for step in workflow_trace.steps:
            if "retrieval_results" in step.output_data:
                retrieved_info = step.output_data["retrieval_results"]
                retrieved_information.extend(retrieved_info.get("chunks", []))
                supporting_chunks.extend(retrieved_info.get("supporting_evidence", []))
                
        if not retrieved_information:
            return "No relevant information found to answer your query.", []
            
        # Synthesize answer using enterprise-grade LLM with confidence tracking
        synthesis_prompt = self._create_synthesis_prompt(query, retrieved_information, confidence_profile)
        
        synthesis_response = await self.llm.generate_with_confidence(
            prompt=synthesis_prompt,
            max_tokens=500,
            temperature=0.1  # Low temperature for more deterministic, reliable answers
        )
        
        # Validate answer quality
        if synthesis_response.confidence < 0.70:
            return (
                "I found some information but cannot provide a confident answer. "
                f"The available information has {synthesis_response.confidence:.1%} confidence. "
                "You may want to refine your query or consult additional sources.",
                supporting_chunks
            )
            
        return synthesis_response.text, supporting_chunks
        
    def _create_synthesis_prompt(self, query: str, information: List[str], confidence_profile: ConfidenceProfile) -> str:
        """Create synthesis prompt with enterprise-grade instructions"""
        
        info_text = "\n\n".join([f"Source {i+1}: {info}" for i, info in enumerate(information)])
        
        return f"""You are a enterprise-grade AI assistant that provides highly reliable answers. 
Your responses must meet production-level accuracy standards.

QUERY: {query}

RETRIEVED INFORMATION:
{info_text}

CONFIDENCE CONTEXT: 
- Information retrieval confidence: {confidence_profile.overall_confidence:.1%}
- Uncertainty factors: {'; '.join(confidence_profile.uncertainty_factors)}

INSTRUCTIONS:
1. Provide a direct, accurate answer based only on the retrieved information
2. If confidence is below 95%, explicitly state uncertainty levels
3. Do not speculate or add information not present in sources
4. If information is insufficient, clearly state this rather than guessing
5. Maintain enterprise-grade accuracy standards throughout

ANSWER:"""

    async def index_content(self, paths: List[Path], force_rebuild: bool = False) -> Dict[str, Any]:
        """
        Index content with enterprise-grade quality validation
        
        Args:
            paths: List of paths to index (files or directories)
            force_rebuild: Whether to force complete index rebuild
            
        Returns:
            Indexing results with quality metrics
        """
        print("📚 Starting enterprise-grade content indexing...")
        
        start_time = time.time()
        
        # Run indexing with quality validation
        indexing_results = await self.indexing_service.run_indexing(
            paths=paths,
            force_rebuild=force_rebuild,
            confidence_threshold=self.confidence_threshold
        )
        
        # Generate AI topics with confidence validation
        if indexing_results.get("success", False):
            print("🏷️  Generating AI-powered topic clusters...")
            topic_results = await self.topic_service.generate_topics(
                index_path=str(self.index_path),
                min_confidence=self.confidence_threshold
            )
            indexing_results.update(topic_results)
            
        indexing_time = time.time() - start_time
        indexing_results["total_indexing_time"] = indexing_time
        
        print(f"✅ Indexing completed in {indexing_time:.2f}s")
        if "indexed_documents" in indexing_results:
            print(f"   Documents indexed: {indexing_results['indexed_documents']}")
        if "chunks_created" in indexing_results:
            print(f"   Chunks created: {indexing_results['chunks_created']}")
        if "topics_generated" in indexing_results:
            print(f"   AI topics generated: {indexing_results['topics_generated']}")
            
        return indexing_results
        
    async def get_topics(self) -> List[Dict[str, Any]]:
        """Get AI-generated topics with confidence metrics"""
        return await self.topic_service.get_topics_with_confidence()
        
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status with enterprise-grade metrics"""
        
        # Memory statistics (ensure database is initialized)
        await self.case_memory._ensure_db_initialized()
        memory_stats = await self.case_memory.get_memory_stats()
        
        # Index statistics
        index_stats = await self.indexing_service.get_index_stats()
        
        # System health metrics
        health_metrics = {
            "developer_threshold_compliance": {
                "cases_meeting_critical": memory_stats.get("critical_cases", 0),
                "total_cases": memory_stats.get("total_cases", 0),
                "critical_percentage": (memory_stats.get("critical_cases", 0) / max(memory_stats.get("total_cases", 1), 1)) * 100
            },
            "confidence_distribution": memory_stats.get("confidence_distribution", {}),
            "average_confidence": memory_stats.get("average_confidence", 0.0),
            "recent_activity": {
                "cases_added_last_week": memory_stats.get("cases_added_last_week", 0),
                "retrievals_last_week": memory_stats.get("retrievals_last_week", 0)
            }
        }
        
        return {
            "system_status": "operational",
            "developer_grade_thresholds": {
                "critical_threshold": self.developer_threshold,
                "production_threshold": self.confidence_threshold
            },
            "memory_system": memory_stats,
            "index_system": index_stats,
            "health_metrics": health_metrics,
            "timestamp": datetime.now().isoformat()
        }


class QueryRouter:
    """
    Intelligent query routing system that learns optimal retrieval strategies
    """
    
    def __init__(self, agent: CognitronAgent):
        self.agent = agent
        
    async def route_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        memory_cases: List[CaseMemoryEntry] = None
    ) -> WorkflowTrace:
        """
        Route query through optimal retrieval strategy
        
        Returns complete workflow trace with confidence tracking
        """
        
        trace_id = uuid4()
        start_time = time.time()
        
        # Analyze query to determine optimal strategy
        query_analysis = await self._analyze_query(query, context)
        
        # Create workflow steps based on analysis
        workflow_steps = []
        
        # Step 1: Memory retrieval (if similar cases found)
        if memory_cases:
            memory_step = await self._execute_memory_retrieval(memory_cases, query)
            workflow_steps.append(memory_step)
            
        # Step 2: Primary retrieval strategy
        if query_analysis["requires_code_search"]:
            code_step = await self._execute_code_retrieval(query, context)
            workflow_steps.append(code_step)
            
        if query_analysis["requires_document_search"]:
            doc_step = await self._execute_document_retrieval(query, context)
            workflow_steps.append(doc_step)
            
        # Step 3: Cross-domain synthesis (if multiple sources)
        if len(workflow_steps) > 1:
            synthesis_step = await self._execute_synthesis(workflow_steps, query)
            workflow_steps.append(synthesis_step)
            
        total_time = time.time() - start_time
        
        # Create workflow trace
        workflow_trace = WorkflowTrace(
            trace_id=trace_id,
            query=query,
            outcome="completed",
            steps=workflow_steps,
            total_execution_time=total_time
        )
        
        return workflow_trace
        
    async def _analyze_query(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze query to determine optimal retrieval strategy"""
        
        query_lower = query.lower()
        
        # Simple heuristics for query classification (could be enhanced with ML)
        code_indicators = ["function", "class", "method", "variable", "import", "error", "bug", "implementation", "code"]
        doc_indicators = ["policy", "documentation", "guide", "process", "procedure", "requirement", "specification"]
        
        requires_code_search = any(indicator in query_lower for indicator in code_indicators)
        requires_document_search = any(indicator in query_lower for indicator in doc_indicators)
        
        # Default to both if unclear
        if not requires_code_search and not requires_document_search:
            requires_code_search = True
            requires_document_search = True
            
        return {
            "requires_code_search": requires_code_search,
            "requires_document_search": requires_document_search,
            "query_complexity": len(query.split()),
            "estimated_difficulty": "medium"  # Could be ML-based
        }
        
    async def _execute_memory_retrieval(self, memory_cases: List[CaseMemoryEntry], query: str) -> WorkflowStep:
        """Execute memory-based retrieval"""
        
        start_time = time.time()
        
        # Extract relevant information from memory cases
        memory_info = []
        for case in memory_cases:
            memory_info.append({
                "previous_query": case.query,
                "previous_outcome": case.outcome,
                "confidence": case.storage_confidence,
                "success_rate": case.success_rate
            })
            
        execution_time = time.time() - start_time
        
        return WorkflowStep(
            step_name="memory_retrieval",
            input_data={"query": query, "similar_cases": len(memory_cases)},
            output_data={"memory_results": memory_info},
            step_confidence=0.9 if memory_cases else 0.5,
            tool_confidence=0.95,  # Memory system is highly reliable
            execution_time=execution_time
        )
        
    async def _execute_code_retrieval(self, query: str, context: Optional[Dict[str, Any]]) -> WorkflowStep:
        """Execute LEANN-based code retrieval"""
        
        start_time = time.time()
        
        # Use LEANN for AST-aware code search
        try:
            search_results = await self.agent.indexing_service.search_code(
                query=query,
                max_results=10,
                confidence_threshold=0.7
            )
            
            step_confidence = 0.85 if search_results else 0.4
            execution_time = time.time() - start_time
            
            return WorkflowStep(
                step_name="code_retrieval",
                input_data={"query": query},
                output_data={"retrieval_results": search_results},
                step_confidence=step_confidence,
                tool_confidence=0.9,  # LEANN is highly reliable for code
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return WorkflowStep(
                step_name="code_retrieval",
                input_data={"query": query},
                output_data={"error": str(e)},
                step_confidence=0.0,
                tool_confidence=0.0,
                execution_time=execution_time,
                errors=[str(e)]
            )
            
    async def _execute_document_retrieval(self, query: str, context: Optional[Dict[str, Any]]) -> WorkflowStep:
        """Execute PageIndex-based document retrieval"""
        
        start_time = time.time()
        
        # Use PageIndex for structure-aware document search
        try:
            search_results = await self.agent.indexing_service.search_documents(
                query=query,
                max_results=10,
                confidence_threshold=0.7
            )
            
            step_confidence = 0.85 if search_results else 0.4
            execution_time = time.time() - start_time
            
            return WorkflowStep(
                step_name="document_retrieval",
                input_data={"query": query},
                output_data={"retrieval_results": search_results},
                step_confidence=step_confidence,
                tool_confidence=0.85,  # PageIndex is reliable for documents
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return WorkflowStep(
                step_name="document_retrieval",
                input_data={"query": query},
                output_data={"error": str(e)},
                step_confidence=0.0,
                tool_confidence=0.0,
                execution_time=execution_time,
                errors=[str(e)]
            )
            
    async def _execute_synthesis(self, workflow_steps: List[WorkflowStep], query: str) -> WorkflowStep:
        """Execute cross-domain information synthesis"""
        
        start_time = time.time()
        
        # Combine information from multiple retrieval steps
        all_results = []
        for step in workflow_steps:
            if "retrieval_results" in step.output_data:
                all_results.extend(step.output_data["retrieval_results"].get("chunks", []))
                
        # Simple synthesis (could be enhanced with LLM-based synthesis)
        synthesis_confidence = min([step.step_confidence for step in workflow_steps]) if workflow_steps else 0.5
        
        execution_time = time.time() - start_time
        
        return WorkflowStep(
            step_name="information_synthesis",
            input_data={"query": query, "source_count": len(workflow_steps)},
            output_data={"synthesized_results": {"chunks": all_results}},
            step_confidence=synthesis_confidence,
            tool_confidence=0.8,
            execution_time=execution_time
        )