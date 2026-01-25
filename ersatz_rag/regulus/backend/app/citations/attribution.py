"""
Enhanced Citation Attribution System

This implements the enhanced citation system from Phase 1 Week 1-2:
- Page-level granularity for precise source attribution
- Source relevance scoring and verification
- Citation accuracy validation and quality scoring
- Integration with PageIndex metadata for enhanced precision

Target: 95% citation accuracy with page-level precision
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class CitationSource:
    """Enhanced citation source with page-level precision"""
    node_id: str
    document_title: str
    section_title: Optional[str]
    page_number: int
    page_range: Tuple[int, int]
    content_excerpt: str
    relevance_score: float
    attribution_confidence: float
    citation_text: str
    metadata: Dict[str, Any]

@dataclass
class CitationVerification:
    """Result of citation accuracy verification"""
    citation_id: str
    is_accurate: bool
    accuracy_score: float
    verification_method: str
    issues_found: List[str]
    corrections_suggested: List[str]
    verification_details: Dict[str, Any]

@dataclass
class AttributionResult:
    """Complete attribution result for a query response"""
    query: str
    response_text: str
    citations: List[CitationSource]
    attribution_quality: float
    coverage_score: float
    precision_score: float
    total_sources: int
    verifications: List[CitationVerification]

class EnhancedCitationSystem:
    """
    Enhanced citation system with page-level precision and verification
    
    Provides accurate source attribution for RAG responses with precise
    page-level citations and comprehensive verification capabilities.
    """
    
    def __init__(self, 
                 min_relevance_threshold: float = 0.7,
                 max_excerpt_length: int = 200,
                 enable_verification: bool = True):
        """
        Initialize enhanced citation system
        
        Args:
            min_relevance_threshold: Minimum relevance score for citation inclusion
            max_excerpt_length: Maximum length of content excerpts
            enable_verification: Enable citation accuracy verification
        """
        
        self.min_relevance_threshold = min_relevance_threshold
        self.max_excerpt_length = max_excerpt_length
        self.enable_verification = enable_verification
        
        # Citation formatting patterns
        self.citation_formats = {
            'academic': '[{document_title}, p. {page_number}]',
            'legal': '({document_title} § {section_title}, p. {page_number})',
            'corporate': '[{document_title}, Section {section_title}, Page {page_number}]',
            'simple': '(Page {page_number})'
        }
        
        # Content verification patterns
        self.verification_patterns = {
            'exact_quote': r'"([^"]*)"',
            'paraphrase_indicators': ['according to', 'as stated in', 'the policy indicates'],
            'factual_claims': ['must', 'required', 'prohibited', 'authorized', 'mandatory']
        }
        
        # Source credibility factors
        self.credibility_weights = {
            'official_document': 1.0,
            'policy_document': 0.95,
            'guideline_document': 0.9,
            'draft_document': 0.7,
            'informal_document': 0.5
        }
        
        logger.info(f"📝 Enhanced Citation System initialized")
        logger.info(f"   Relevance threshold: {min_relevance_threshold}")
        logger.info(f"   Max excerpt length: {max_excerpt_length}")
        logger.info(f"   Verification enabled: {enable_verification}")
    
    def generate_attributions(self, 
                            query: str,
                            response_text: str,
                            search_results: List[Dict[str, Any]],
                            citation_format: str = 'corporate') -> AttributionResult:
        """
        Generate enhanced attributions for a query response
        
        Args:
            query: Original query string
            response_text: Generated response text
            search_results: List of search results with metadata
            citation_format: Format for citation display
            
        Returns:
            AttributionResult with comprehensive citation information
        """
        
        logger.debug(f"📝 Generating attributions for query: '{query}'")
        
        # Step 1: Extract and rank citation sources
        citation_sources = self._extract_citation_sources(
            search_results, response_text, query
        )
        
        # Step 2: Filter by relevance threshold
        relevant_citations = [
            cite for cite in citation_sources 
            if cite.relevance_score >= self.min_relevance_threshold
        ]
        
        logger.debug(f"Filtered to {len(relevant_citations)} relevant citations")
        
        # Step 3: Generate formatted citations
        for citation in relevant_citations:
            citation.citation_text = self._format_citation(citation, citation_format)
        
        # Step 4: Calculate attribution quality metrics
        attribution_quality = self._calculate_attribution_quality(relevant_citations, response_text)
        coverage_score = self._calculate_coverage_score(relevant_citations, response_text)
        precision_score = self._calculate_precision_score(relevant_citations, query)
        
        # Step 5: Verify citation accuracy (if enabled)
        verifications = []
        if self.enable_verification:
            verifications = self._verify_citations(relevant_citations, response_text)
        
        result = AttributionResult(
            query=query,
            response_text=response_text,
            citations=relevant_citations,
            attribution_quality=attribution_quality,
            coverage_score=coverage_score,
            precision_score=precision_score,
            total_sources=len(search_results),
            verifications=verifications
        )
        
        logger.info(f"✅ Generated {len(relevant_citations)} attributions "
                   f"(quality: {attribution_quality:.3f})")
        
        return result
    
    def _extract_citation_sources(self, 
                                search_results: List[Dict[str, Any]],
                                response_text: str,
                                query: str) -> List[CitationSource]:
        """Extract and enrich citation sources from search results"""
        
        citation_sources = []
        
        for i, result in enumerate(search_results):
            metadata = result.get('metadata', {})
            
            # Extract page information with enhanced precision
            page_info = self._extract_page_information(metadata)
            
            # Calculate relevance score
            relevance_score = self._calculate_source_relevance(result, response_text, query)
            
            # Calculate attribution confidence
            attribution_confidence = self._calculate_attribution_confidence(
                result, response_text, metadata
            )
            
            # Extract content excerpt
            content_excerpt = self._extract_content_excerpt(
                result.get('content', ''), response_text
            )
            
            # Determine document credibility
            doc_type = self._classify_document_type(metadata)
            credibility_factor = self.credibility_weights.get(doc_type, 0.8)
            
            citation_source = CitationSource(
                node_id=result.get('node_id', f'result_{i}'),
                document_title=metadata.get('document_title', 'Unknown Document'),
                section_title=metadata.get('title', metadata.get('section_title')),
                page_number=page_info['primary_page'],
                page_range=page_info['range'],
                content_excerpt=content_excerpt,
                relevance_score=relevance_score * credibility_factor,
                attribution_confidence=attribution_confidence,
                citation_text='',  # Will be set during formatting
                metadata={
                    **metadata,
                    'document_type': doc_type,
                    'credibility_factor': credibility_factor,
                    'extraction_rank': i
                }
            )
            
            citation_sources.append(citation_source)
        
        # Sort by relevance score (highest first)
        citation_sources.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return citation_sources
    
    def _extract_page_information(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract precise page information from metadata"""
        
        page_ranges = metadata.get('page_ranges', [1, 1])
        
        if isinstance(page_ranges, list) and len(page_ranges) >= 2:
            start_page = page_ranges[0]
            end_page = page_ranges[1]
        else:
            # Fallback extraction from other metadata fields
            start_page = metadata.get('page_number', 1)
            end_page = start_page
        
        return {
            'primary_page': start_page,
            'range': (start_page, end_page),
            'span': end_page - start_page + 1
        }
    
    def _calculate_source_relevance(self, 
                                  result: Dict[str, Any],
                                  response_text: str,
                                  query: str) -> float:
        """Calculate relevance score for citation source"""
        
        content = result.get('content', '')
        
        # Factor 1: Content overlap with response
        response_overlap = self._calculate_text_overlap(content, response_text)
        
        # Factor 2: Query term coverage
        query_coverage = self._calculate_query_coverage(content, query)
        
        # Factor 3: Search ranking (higher ranked = more relevant)
        search_score = result.get('hybrid_score', result.get('semantic_score', result.get('score', 0)))
        normalized_search_score = min(search_score / 1000.0, 1.0) if search_score > 1 else search_score
        
        # Factor 4: Content quality indicators
        quality_score = self._assess_content_quality(content, result.get('metadata', {}))
        
        # Weighted combination
        relevance_score = (
            response_overlap * 0.35 +
            query_coverage * 0.25 +
            normalized_search_score * 0.25 +
            quality_score * 0.15
        )
        
        return min(1.0, relevance_score)
    
    def _calculate_attribution_confidence(self,
                                        result: Dict[str, Any],
                                        response_text: str,
                                        metadata: Dict[str, Any]) -> float:
        """Calculate confidence in attribution accuracy"""
        
        confidence_factors = []
        
        # Factor 1: Source authority (from PageIndex reasoning)
        reasoning_confidence = metadata.get('reasoning_confidence', 0.75)
        confidence_factors.append(reasoning_confidence)
        
        # Factor 2: Content-response alignment
        content = result.get('content', '')
        alignment_score = self._calculate_content_alignment(content, response_text)
        confidence_factors.append(alignment_score)
        
        # Factor 3: Metadata completeness
        metadata_completeness = self._assess_metadata_completeness(metadata)
        confidence_factors.append(metadata_completeness)
        
        # Factor 4: Page precision (more precise = higher confidence)
        page_precision = self._assess_page_precision(metadata)
        confidence_factors.append(page_precision)
        
        # Average with slight bias toward metadata quality
        attribution_confidence = (
            sum(confidence_factors) / len(confidence_factors) * 0.8 +
            metadata_completeness * 0.2
        )
        
        return min(1.0, attribution_confidence)
    
    def _extract_content_excerpt(self, content: str, response_text: str) -> str:
        """Extract most relevant excerpt from source content"""
        
        if not content:
            return ""
        
        # Find the most relevant sentences by overlap with response
        sentences = self._split_into_sentences(content)
        
        if not sentences:
            return content[:self.max_excerpt_length]
        
        # Score sentences by relevance to response
        sentence_scores = []
        for sentence in sentences:
            overlap_score = self._calculate_text_overlap(sentence, response_text)
            sentence_scores.append((sentence, overlap_score))
        
        # Sort by relevance and take top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Build excerpt from top sentences
        excerpt_parts = []
        current_length = 0
        
        for sentence, score in sentence_scores:
            if score > 0.1 and current_length + len(sentence) <= self.max_excerpt_length:
                excerpt_parts.append(sentence.strip())
                current_length += len(sentence)
            elif current_length > self.max_excerpt_length * 0.5:
                break
        
        if not excerpt_parts:
            # Fallback to beginning of content
            return content[:self.max_excerpt_length].strip()
        
        excerpt = " ".join(excerpt_parts)
        
        # Add ellipsis if truncated
        if len(excerpt) >= self.max_excerpt_length * 0.9:
            excerpt = excerpt[:self.max_excerpt_length-3] + "..."
        
        return excerpt
    
    def _format_citation(self, citation: CitationSource, format_type: str) -> str:
        """Format citation according to specified style"""
        
        format_template = self.citation_formats.get(format_type, self.citation_formats['corporate'])
        
        # Prepare formatting variables
        format_vars = {
            'document_title': citation.document_title,
            'section_title': citation.section_title or 'Unknown Section',
            'page_number': citation.page_number,
            'page_range': f"{citation.page_range[0]}-{citation.page_range[1]}" 
                         if citation.page_range[0] != citation.page_range[1] 
                         else str(citation.page_range[0]),
            'node_id': citation.node_id
        }
        
        try:
            formatted_citation = format_template.format(**format_vars)
        except KeyError as e:
            logger.warning(f"Citation formatting error: {e}")
            # Fallback format
            formatted_citation = f"[{citation.document_title}, Page {citation.page_number}]"
        
        return formatted_citation
    
    def _calculate_attribution_quality(self, 
                                     citations: List[CitationSource],
                                     response_text: str) -> float:
        """Calculate overall attribution quality score"""
        
        if not citations:
            return 0.0
        
        quality_factors = []
        
        # Factor 1: Average relevance of citations
        avg_relevance = sum(cite.relevance_score for cite in citations) / len(citations)
        quality_factors.append(avg_relevance)
        
        # Factor 2: Average attribution confidence
        avg_confidence = sum(cite.attribution_confidence for cite in citations) / len(citations)
        quality_factors.append(avg_confidence)
        
        # Factor 3: Citation diversity (different sources)
        unique_documents = len(set(cite.document_title for cite in citations))
        diversity_score = min(unique_documents / max(len(citations), 1), 1.0)
        quality_factors.append(diversity_score)
        
        # Factor 4: Coverage completeness
        coverage_score = self._calculate_coverage_score(citations, response_text)
        quality_factors.append(coverage_score)
        
        # Weighted average
        quality_score = (
            avg_relevance * 0.3 +
            avg_confidence * 0.3 +
            diversity_score * 0.2 +
            coverage_score * 0.2
        )
        
        return min(1.0, quality_score)
    
    def _calculate_coverage_score(self, 
                                citations: List[CitationSource],
                                response_text: str) -> float:
        """Calculate how well citations cover the response content"""
        
        if not citations or not response_text:
            return 0.0
        
        response_sentences = self._split_into_sentences(response_text)
        
        if not response_sentences:
            return 0.5  # Default for very short responses
        
        covered_sentences = 0
        
        for sentence in response_sentences:
            # Check if this sentence is covered by any citation
            for citation in citations:
                overlap = self._calculate_text_overlap(sentence, citation.content_excerpt)
                if overlap > 0.3:  # Reasonable overlap threshold
                    covered_sentences += 1
                    break
        
        coverage_score = covered_sentences / len(response_sentences)
        return min(1.0, coverage_score)
    
    def _calculate_precision_score(self, 
                                 citations: List[CitationSource],
                                 query: str) -> float:
        """Calculate precision of citations relative to query"""
        
        if not citations:
            return 0.0
        
        query_terms = set(query.lower().split())
        precision_scores = []
        
        for citation in citations:
            # Check how well citation content matches query terms
            content_terms = set(citation.content_excerpt.lower().split())
            
            if not content_terms:
                precision_scores.append(0.0)
                continue
            
            # Calculate term overlap precision
            common_terms = query_terms.intersection(content_terms)
            precision = len(common_terms) / len(query_terms) if query_terms else 0.0
            
            precision_scores.append(precision)
        
        return sum(precision_scores) / len(precision_scores)
    
    def _verify_citations(self, 
                        citations: List[CitationSource],
                        response_text: str) -> List[CitationVerification]:
        """Verify citation accuracy and identify issues"""
        
        verifications = []
        
        for i, citation in enumerate(citations):
            verification = self._verify_single_citation(citation, response_text, i)
            verifications.append(verification)
        
        return verifications
    
    def _verify_single_citation(self, 
                              citation: CitationSource,
                              response_text: str,
                              citation_index: int) -> CitationVerification:
        """Verify accuracy of a single citation"""
        
        citation_id = f"cite_{citation_index}_{citation.node_id}"
        issues_found = []
        corrections_suggested = []
        
        # Verification 1: Content alignment check
        alignment_score = self._calculate_content_alignment(
            citation.content_excerpt, response_text
        )
        
        if alignment_score < 0.3:
            issues_found.append("low_content_alignment")
            corrections_suggested.append("Verify content relevance to response")
        
        # Verification 2: Quote accuracy check
        quote_issues = self._verify_quotes(citation.content_excerpt, response_text)
        issues_found.extend(quote_issues)
        
        # Verification 3: Page number validation
        if citation.page_number <= 0:
            issues_found.append("invalid_page_number")
            corrections_suggested.append("Verify page number accuracy")
        
        # Verification 4: Source authority validation
        if citation.attribution_confidence < 0.5:
            issues_found.append("low_attribution_confidence")
            corrections_suggested.append("Review source credibility")
        
        # Calculate overall accuracy score
        accuracy_score = max(0.0, 1.0 - len(issues_found) * 0.2)
        is_accurate = accuracy_score >= 0.7 and alignment_score >= 0.3
        
        verification = CitationVerification(
            citation_id=citation_id,
            is_accurate=is_accurate,
            accuracy_score=accuracy_score,
            verification_method="comprehensive_check",
            issues_found=issues_found,
            corrections_suggested=corrections_suggested,
            verification_details={
                "alignment_score": alignment_score,
                "attribution_confidence": citation.attribution_confidence,
                "relevance_score": citation.relevance_score,
                "content_excerpt_length": len(citation.content_excerpt)
            }
        )
        
        return verification
    
    def _verify_quotes(self, citation_content: str, response_text: str) -> List[str]:
        """Verify accuracy of quoted content"""
        
        issues = []
        
        # Find quoted text in response
        quotes_in_response = re.findall(self.verification_patterns['exact_quote'], response_text)
        
        for quote in quotes_in_response:
            if quote.strip() and quote.lower() not in citation_content.lower():
                issues.append(f"unverified_quote: '{quote[:50]}...'")
        
        return issues
    
    def _calculate_text_overlap(self, text1: str, text2: str) -> float:
        """Calculate semantic overlap between two texts (simplified)"""
        
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_query_coverage(self, content: str, query: str) -> float:
        """Calculate how well content covers query terms"""
        
        query_terms = set(query.lower().split())
        content_terms = set(content.lower().split())
        
        if not query_terms:
            return 1.0
        
        covered_terms = query_terms.intersection(content_terms)
        return len(covered_terms) / len(query_terms)
    
    def _assess_content_quality(self, content: str, metadata: Dict[str, Any]) -> float:
        """Assess quality indicators of content"""
        
        quality_score = 0.5  # Base score
        
        # Length factor (not too short, not too long)
        content_length = len(content.split())
        if 20 <= content_length <= 500:
            quality_score += 0.2
        elif content_length > 10:
            quality_score += 0.1
        
        # Structure indicators
        if any(indicator in content.lower() for indicator in 
               ['section', 'paragraph', 'subsection', 'clause']):
            quality_score += 0.1
        
        # Authority indicators
        if metadata.get('reasoning_confidence', 0) > 0.8:
            quality_score += 0.1
        
        # Document type quality
        doc_type = self._classify_document_type(metadata)
        if doc_type in ['official_document', 'policy_document']:
            quality_score += 0.1
        
        return min(1.0, quality_score)
    
    def _calculate_content_alignment(self, content: str, response_text: str) -> float:
        """Calculate alignment between content and response"""
        
        # This is a simplified implementation
        # In production, would use more sophisticated semantic similarity
        return self._calculate_text_overlap(content, response_text)
    
    def _assess_metadata_completeness(self, metadata: Dict[str, Any]) -> float:
        """Assess completeness of citation metadata"""
        
        required_fields = ['title', 'page_ranges', 'reasoning_confidence']
        optional_fields = ['section_title', 'document_title', 'node_id']
        
        required_score = sum(1 for field in required_fields if field in metadata) / len(required_fields)
        optional_score = sum(1 for field in optional_fields if field in metadata) / len(optional_fields)
        
        return required_score * 0.7 + optional_score * 0.3
    
    def _assess_page_precision(self, metadata: Dict[str, Any]) -> float:
        """Assess precision of page information"""
        
        page_ranges = metadata.get('page_ranges', [])
        
        if not page_ranges:
            return 0.3  # Low precision for missing page info
        
        if isinstance(page_ranges, list) and len(page_ranges) >= 2:
            start, end = page_ranges[0], page_ranges[1]
            
            # Higher precision for specific pages
            if start == end:
                return 1.0  # Exact page
            elif end - start <= 2:
                return 0.8  # Small range
            elif end - start <= 5:
                return 0.6  # Moderate range
            else:
                return 0.4  # Large range
        
        return 0.5  # Default for unclear page info
    
    def _classify_document_type(self, metadata: Dict[str, Any]) -> str:
        """Classify document type for credibility assessment"""
        
        title = metadata.get('document_title', '').lower()
        section_type = metadata.get('section_type', '').lower()
        
        if any(term in title for term in ['policy', 'regulation', 'standard']):
            return 'official_document'
        elif any(term in title for term in ['guideline', 'procedure', 'manual']):
            return 'policy_document'
        elif 'draft' in title:
            return 'draft_document'
        elif section_type in ['scope_definition', 'definitions', 'requirements']:
            return 'policy_document'
        else:
            return 'guideline_document'
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        
        # Simple sentence splitting (could be enhanced with NLP)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def get_citation_stats(self) -> Dict[str, Any]:
        """Get citation system statistics and configuration"""
        
        return {
            'system_type': 'enhanced_citation_with_page_precision',
            'configuration': {
                'min_relevance_threshold': self.min_relevance_threshold,
                'max_excerpt_length': self.max_excerpt_length,
                'verification_enabled': self.enable_verification
            },
            'citation_formats': list(self.citation_formats.keys()),
            'verification_patterns': list(self.verification_patterns.keys()),
            'credibility_weights': self.credibility_weights,
            'target_accuracy': '95% citation accuracy with page-level precision'
        }