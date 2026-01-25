"""
Fallback FastAPI service that exposes the deterministic AJ Pack produced by
`run_ingestion_workflow`. This keeps the repository usable even when optional
agent frameworks are unavailable.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import json
import logging
import re
from pydantic import BaseModel
from typing import Any, Dict, Iterable, List, Sequence, Tuple
from .ingestion_workflow import run_ingestion_with_metadata
from .pydantic_schemas import TOC, SectionSummary, QueryResponse, QueryRequest
from .policy_enforcer import PolicyEnforcer
from .agents.toc_agent import TOCAgent
from .agents.loader_agent import LoaderAgent, estimate_tokens
from .agents.answer_verifier_agent import AnswerVerifierAgent
from .agents.confidence_validator import create_confidence_validator
from fastapi import FastAPI, Request


from .llm_providers import create_provider

# Initialize LLM provider (will use mock if none available)
llm_provider = None
try:
    # Try to load LLM provider from environment or default to mock
    provider_type = os.getenv("LLM_PROVIDER", "mock")
    llm_provider = create_provider(provider_type)
except Exception as e:
    # Log error but continue with mock provider
    print(f"Warning: Could not initialize LLM provider '{provider_type}': {e}")
    llm_provider = create_provider("mock")




def build_fallback_app() -> FastAPI:
    # Run ingestion workflow to build AJ Pack from JSON files in project root
    aj_pack, warnings = run_ingestion_with_metadata()

    if warnings:
        logger = logging.getLogger('doc_mcp.service')
        for warning in warnings:
            logger.warning(json.dumps({'event': 'ingestion_warning', 'detail': warning}))

    sections: List[Dict[str, object]] = []
    toc_by_section: Dict[str, Dict[str, object]] = {}
    for file_content in aj_pack.content:
        for section in file_content.content:
            metadata = {
                'file_id': file_content.file_id,
                'section_id': section.section_id,
                'label': section.label,
                'text': section.text_or_data,
                'entities': section.entities,
                'aliases': [],
            }
            sections.append(metadata)

    for file_entry in aj_pack.toc.index:
        for node in file_entry.sections:
            toc_by_section[node.section_id] = {
                'aliases': node.aliases,
                'entities': node.entities,
                'token_estimate': node.token_estimate,
            }

    for section in sections:
        toc_meta = toc_by_section.get(section['section_id'])
        if toc_meta:
            section['aliases'] = toc_meta['aliases']
            section['entities'] = section.get('entities', []) or toc_meta['entities']
            section['token_estimate'] = toc_meta['token_estimate']

    # Initialize all agents
    policy_enforcer = PolicyEnforcer(aj_pack.toc.security)
    toc_agent = TOCAgent(aj_pack.toc, sections)
    loader_agent = LoaderAgent(budget_tokens=4000)
    answer_agent = AnswerVerifierAgent(llm_provider) if llm_provider else None
    confidence_validator = create_confidence_validator()  # Reads ENABLE_SEMANTIC_VALIDATION env var
    
    app = FastAPI(
        title='Doc-MCP Fallback Service',
        version=aj_pack.manifest.version,
        description='Lightweight retrieval service powered by the deterministic AJ Pack.',
    )

    @app.get('/meta')
    def get_meta() -> Dict[str, Any]:
        return {
            'dataset_id': aj_pack.manifest.dataset_id,
            'version': aj_pack.manifest.version,
            'sections': str(len(sections)),
            'warnings': warnings,
        }

    @app.get('/sections', response_model=List[SectionSummary])
    def list_sections() -> List[SectionSummary]:
        return [
            SectionSummary(
                section_id=section['section_id'],
                label=section['label'],
                file_id=section['file_id'],
                aliases=list(section.get('aliases', [])),
                entities=list(section.get('entities', [])),
            )
            for section in sections
        ]

    @app.post('/query', response_model=QueryResponse)
    def query(request: QueryRequest, http_request: Request) -> QueryResponse:
        # AJrag.txt §7: Enforce security policies before processing query
        user_region = http_request.headers.get('X-User-Region', 'UNKNOWN')
        user_has_phi = http_request.headers.get('X-PHI-Clearance', '').lower() == 'true'
        user_has_pii = http_request.headers.get('X-PII-Clearance', '').lower() == 'true'
        
        allowed, reason = policy_enforcer.enforce(
            user_region=user_region,
            user_has_phi_clearance=user_has_phi,
            user_has_pii_clearance=user_has_pii
        )
        
        if not allowed:
            return QueryResponse(
                answer=f"Access denied: {reason}",
                citations=[],
                confidence=0.0,
                section_id='',
                label='POLICY_VIOLATION'
            )
        
        # AJrag.txt §3.1: Delegate to TOC Agent for routing
        best_score, best_section = toc_agent.get_top_section(request.question)

        if best_score == 0:
            return QueryResponse(
                answer='No matching section found in the reference dataset.',
                citations=[],
                confidence=0.0,
                section_id='',
                label='',
            )

        # Validate routing confidence with optional semantic similarity
        routing_confidence, validation_metadata = confidence_validator.validate_routing(
            query=request.question,
            section_text=best_section['text'],
            deterministic_score=best_score,
            section_label=best_section.get('label', '')
        )
        
        # AJrag.txt §3.1: Use Loader Agent to manage context
        loader_agent.clear()  # Clear previous context
        
        # Load the best section into context
        token_estimate = best_section.get('token_estimate', estimate_tokens(best_section['text']))
        success, reason = loader_agent.request_load(
            file_id=best_section['file_id'],
            section_id=best_section['section_id'],
            content=best_section['text'],
            token_estimate=token_estimate,
            metadata={'label': best_section.get('label', '')}
        )
        
        if not success:
            # Budget exceeded - this shouldn't happen with a single section
            # but we handle it gracefully
            answer = best_section['text']
            confidence = routing_confidence
        elif answer_agent:
            # agnoMCPnanobot.txt lines 461-469: Use Answer/Verifier Agent
            context = loader_agent.get_context()
            result = answer_agent.synthesize_with_verification(
                query=request.question,
                context=context,
                citations=loader_agent.get_loaded_section_ids(),
                routing_confidence=routing_confidence,
                max_tokens=500
            )
            answer = result['answer']
            confidence = result['confidence']
        else:
            # No LLM provider - return raw text
            answer = best_section['text']
            confidence = routing_confidence
        
        return QueryResponse(
            answer=answer,
            citations=[best_section['section_id']],
            confidence=confidence,
            section_id=best_section['section_id'],
            label=best_section['label'],
        )

    @app.get('/health')
    def health() -> Dict[str, Any]:
        status = 'ok' if not warnings else 'degraded'
        return {
            'status': status,
            'warnings': warnings,
            'sections': len(sections),
            'dataset_id': aj_pack.manifest.dataset_id,
            'version': aj_pack.manifest.version,
        }
    
    return app

