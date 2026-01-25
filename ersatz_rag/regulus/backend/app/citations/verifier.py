"""
Citation Verifier - Advanced citation accuracy validation

This implements citation verification from Phase 1 Week 1-2:
- Citation accuracy validation against source materials
- Source attribution verification and cross-checking
- Citation quality scoring and improvement suggestions
- Automated citation correction recommendations
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import difflib
from collections import Counter

logger = logging.getLogger(__name__)

@dataclass
class VerificationResult:
    """Result of citation verification process"""
    citation_id: str
    verification_type: str
    is_verified: bool
    confidence: float
    issues: List[str]
    suggestions: List[str]
    details: Dict[str, Any]

@dataclass
class CrossReferenceCheck:
    """Result of cross-reference verification"""
    source_citation: str
    reference_found: bool
    reference_accuracy: float
    context_match: bool
    page_accuracy: bool
    content_verification: Dict[str, Any]

class CitationVerifier:
    """
    Advanced citation verification system
    
    Validates citation accuracy, checks source attribution, and provides
    quality scoring with improvement suggestions for 95% accuracy target.
    """
    
    def __init__(self, 
                 strict_verification: bool = True,
                 enable_auto_correction: bool = True,
                 min_confidence_threshold: float = 0.8):
        """
        Initialize citation verifier
        
        Args:
            strict_verification: Use strict verification standards
            enable_auto_correction: Enable automatic correction suggestions
            min_confidence_threshold: Minimum confidence for verified citations
        """
        
        self.strict_verification = strict_verification
        self.enable_auto_correction = enable_auto_correction
        self.min_confidence_threshold = min_confidence_threshold
        
        # Verification type weights
        self.verification_weights = {
            'exact_match': 1.0,
            'paraphrase_match': 0.8,
            'contextual_match': 0.6,
            'topical_match': 0.4
        }
        
        # Common citation errors and patterns
        self.error_patterns = {
            'misquoted_text': {
                'pattern': r'"([^"]*)"',
                'description': 'Quoted text not found in source'
            },
            'wrong_page_number': {
                'pattern': r'p\.?\s*(\d+)',
                'description': 'Page number does not match source location'
            },
            'incorrect_section': {
                'pattern': r'[Ss]ection\s+(\d+(?:\.\d+)*)',
                'description': 'Section reference not found in source'
            },
            'outdated_reference': {
                'pattern': r'(\d{4})',
                'description': 'Reference may be to outdated version'
            }
        }
        
        # Quality indicators
        self.quality_indicators = {
            'specificity': ['page', 'paragraph', 'section', 'subsection'],
            'authority': ['official', 'policy', 'regulation', 'standard'],
            'completeness': ['title', 'date', 'version', 'author']
        }
        
        logger.info(f"🔍 Citation Verifier initialized")
        logger.info(f"   Strict verification: {strict_verification}")
        logger.info(f"   Auto-correction: {enable_auto_correction}")
        logger.info(f"   Confidence threshold: {min_confidence_threshold}")
    
    def verify_citations(self, 
                        response_text: str,
                        citations: List[Dict[str, Any]],
                        source_documents: List[Dict[str, Any]]) -> List[VerificationResult]:
        """
        Comprehensive citation verification
        
        Args:
            response_text: The generated response containing citations
            citations: List of citation objects to verify
            source_documents: Original source documents for verification
            
        Returns:
            List of VerificationResult objects with detailed verification status
        """
        
        logger.debug(f"🔍 Verifying {len(citations)} citations")
        
        verification_results = []
        
        for i, citation in enumerate(citations):
            citation_id = citation.get('citation_id', f'citation_{i}')
            
            # Comprehensive verification of this citation
            result = self._verify_single_citation(
                citation_id=citation_id,
                citation=citation,
                response_text=response_text,
                source_documents=source_documents
            )
            
            verification_results.append(result)
        
        logger.info(f"✅ Verified citations: "
                   f"{sum(1 for r in verification_results if r.is_verified)}/{len(verification_results)} passed")
        
        return verification_results
    
    def _verify_single_citation(self, 
                              citation_id: str,
                              citation: Dict[str, Any],
                              response_text: str,
                              source_documents: List[Dict[str, Any]]) -> VerificationResult:
        """Verify a single citation comprehensively"""
        
        issues = []
        suggestions = []
        verification_details = {}
        
        # Step 1: Find the corresponding source document
        source_doc = self._find_source_document(citation, source_documents)
        
        if not source_doc:
            return VerificationResult(
                citation_id=citation_id,
                verification_type='source_lookup',
                is_verified=False,
                confidence=0.0,
                issues=['source_document_not_found'],
                suggestions=['Verify source document availability'],
                details={'error': 'Could not locate source document'}
            )
        
        # Step 2: Verify content accuracy
        content_verification = self._verify_content_accuracy(citation, source_doc, response_text)
        verification_details['content_accuracy'] = content_verification
        
        if content_verification['accuracy_score'] < 0.7:
            issues.append('content_mismatch')
            suggestions.append('Review content alignment with source')
        
        # Step 3: Verify page reference accuracy
        page_verification = self._verify_page_reference(citation, source_doc)
        verification_details['page_accuracy'] = page_verification
        
        if not page_verification['is_accurate']:
            issues.extend(page_verification['issues'])
            suggestions.extend(page_verification['suggestions'])
        
        # Step 4: Verify quote accuracy (if any)
        quote_verification = self._verify_quotes(citation, source_doc, response_text)
        verification_details['quote_accuracy'] = quote_verification
        
        if quote_verification['issues']:
            issues.extend(quote_verification['issues'])
            suggestions.extend(quote_verification['suggestions'])
        
        # Step 5: Check for common citation errors
        error_check = self._check_common_errors(citation, source_doc)
        verification_details['error_check'] = error_check
        
        issues.extend(error_check['errors_found'])
        suggestions.extend(error_check['corrections'])
        
        # Step 6: Calculate overall verification confidence
        confidence = self._calculate_verification_confidence(
            content_verification,
            page_verification,
            quote_verification,
            error_check
        )
        
        is_verified = (
            confidence >= self.min_confidence_threshold and
            len(issues) == 0 and
            content_verification['accuracy_score'] >= 0.7
        )
        
        return VerificationResult(
            citation_id=citation_id,
            verification_type='comprehensive',
            is_verified=is_verified,
            confidence=confidence,
            issues=issues,
            suggestions=suggestions,
            details=verification_details
        )
    
    def _find_source_document(self, 
                            citation: Dict[str, Any],
                            source_documents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the source document corresponding to a citation"""
        
        citation_node_id = citation.get('node_id')
        citation_title = citation.get('document_title', '').lower()
        
        for doc in source_documents:
            # Try to match by node_id first (most reliable)
            if citation_node_id and doc.get('node_id') == citation_node_id:
                return doc
            
            # Try to match by document title
            doc_title = doc.get('metadata', {}).get('document_title', '').lower()
            if citation_title and doc_title and citation_title in doc_title:
                return doc
            
            # Try to match by content similarity (fallback)
            citation_content = citation.get('content_excerpt', '')
            doc_content = doc.get('content', '')
            if citation_content and doc_content:
                similarity = self._calculate_content_similarity(citation_content, doc_content)
                if similarity > 0.8:  # High similarity threshold
                    return doc
        
        return None
    
    def _verify_content_accuracy(self, 
                               citation: Dict[str, Any],
                               source_doc: Dict[str, Any],
                               response_text: str) -> Dict[str, Any]:
        """Verify accuracy of citation content against source"""
        
        citation_excerpt = citation.get('content_excerpt', '')
        source_content = source_doc.get('content', '')
        
        if not citation_excerpt or not source_content:
            return {
                'accuracy_score': 0.0,
                'verification_type': 'no_content',
                'details': 'Insufficient content for verification'
            }
        
        # Check for exact matches
        exact_match_score = self._find_exact_matches(citation_excerpt, source_content)
        
        # Check for paraphrase matches
        paraphrase_score = self._find_paraphrase_matches(citation_excerpt, source_content)
        
        # Check contextual relevance
        context_score = self._assess_contextual_relevance(citation_excerpt, source_content, response_text)
        
        # Calculate weighted accuracy score
        accuracy_score = (
            exact_match_score * self.verification_weights['exact_match'] +
            paraphrase_score * self.verification_weights['paraphrase_match'] +
            context_score * self.verification_weights['contextual_match']
        ) / sum(self.verification_weights.values())
        
        return {
            'accuracy_score': accuracy_score,
            'exact_match_score': exact_match_score,
            'paraphrase_score': paraphrase_score,
            'context_score': context_score,
            'verification_type': self._determine_match_type(exact_match_score, paraphrase_score, context_score)
        }
    
    def _verify_page_reference(self, 
                             citation: Dict[str, Any],
                             source_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Verify accuracy of page references"""
        
        citation_page = citation.get('page_number')
        citation_range = citation.get('page_range', (citation_page, citation_page))
        
        source_metadata = source_doc.get('metadata', {})
        source_page_ranges = source_metadata.get('page_ranges', [])
        
        issues = []
        suggestions = []
        
        if not citation_page:
            issues.append('missing_page_reference')
            suggestions.append('Add page reference to citation')
            return {
                'is_accurate': False,
                'issues': issues,
                'suggestions': suggestions,
                'details': 'No page reference provided'
            }
        
        if not source_page_ranges:
            # Cannot verify without source page info
            return {
                'is_accurate': True,  # Assume correct if can't verify
                'issues': [],
                'suggestions': ['Verify page reference manually'],
                'details': 'Source page information unavailable'
            }
        
        # Check if citation page falls within source page range
        source_start, source_end = source_page_ranges[0], source_page_ranges[-1]
        
        if citation_page < source_start or citation_page > source_end:
            issues.append('page_reference_out_of_range')
            suggestions.append(f'Correct page reference (source spans pages {source_start}-{source_end})')
        
        # Check page range accuracy
        if citation_range:
            cite_start, cite_end = citation_range
            if cite_start < source_start or cite_end > source_end:
                issues.append('page_range_extends_beyond_source')
                suggestions.append('Adjust page range to match source boundaries')
        
        return {
            'is_accurate': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions,
            'details': {
                'citation_page': citation_page,
                'citation_range': citation_range,
                'source_range': (source_start, source_end)
            }
        }
    
    def _verify_quotes(self, 
                      citation: Dict[str, Any],
                      source_doc: Dict[str, Any],
                      response_text: str) -> Dict[str, Any]:
        """Verify accuracy of quoted text"""
        
        issues = []
        suggestions = []
        verified_quotes = []
        
        # Extract quotes from response text
        quotes = re.findall(r'"([^"]*)"', response_text)
        
        if not quotes:
            return {
                'issues': [],
                'suggestions': [],
                'verified_quotes': [],
                'details': 'No quotes found in response'
            }
        
        source_content = source_doc.get('content', '').lower()
        
        for quote in quotes:
            quote_clean = quote.strip().lower()
            
            if len(quote_clean) < 5:  # Skip very short quotes
                continue
            
            # Check if quote exists in source
            if quote_clean in source_content:
                verified_quotes.append({
                    'quote': quote,
                    'verified': True,
                    'match_type': 'exact'
                })
            else:
                # Check for near matches (allowing for minor differences)
                best_match = self._find_best_quote_match(quote_clean, source_content)
                
                if best_match['similarity'] > 0.85:
                    verified_quotes.append({
                        'quote': quote,
                        'verified': True,
                        'match_type': 'near_exact',
                        'source_text': best_match['source_text']
                    })
                else:
                    verified_quotes.append({
                        'quote': quote,
                        'verified': False,
                        'match_type': 'not_found'
                    })
                    issues.append(f'unverified_quote: "{quote[:50]}..."')
                    suggestions.append(f'Verify quote accuracy: "{quote[:30]}..."')
        
        return {
            'issues': issues,
            'suggestions': suggestions,
            'verified_quotes': verified_quotes,
            'total_quotes': len(quotes),
            'verified_count': sum(1 for q in verified_quotes if q['verified'])
        }
    
    def _check_common_errors(self, 
                           citation: Dict[str, Any],
                           source_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Check for common citation errors"""
        
        errors_found = []
        corrections = []
        
        citation_text = citation.get('citation_text', '')
        
        for error_type, pattern_info in self.error_patterns.items():
            pattern = pattern_info['pattern']
            description = pattern_info['description']
            
            if error_type == 'wrong_page_number':
                # Already handled in page verification
                continue
            
            matches = re.findall(pattern, citation_text)
            
            if matches and error_type == 'misquoted_text':
                # Check if quoted text exists in source
                source_content = source_doc.get('content', '')
                for quote in matches:
                    if quote.lower() not in source_content.lower():
                        errors_found.append(f'{error_type}: "{quote[:30]}..."')
                        corrections.append('Verify quote exists in source document')
            
            elif matches and error_type == 'incorrect_section':
                # Check if section reference exists
                source_title = source_doc.get('metadata', {}).get('title', '')
                section_refs = [f'Section {match}' for match in matches]
                for ref in section_refs:
                    if ref not in source_title:
                        errors_found.append(f'{error_type}: {ref}')
                        corrections.append('Verify section number accuracy')
        
        return {
            'errors_found': errors_found,
            'corrections': corrections,
            'patterns_checked': list(self.error_patterns.keys())
        }
    
    def _calculate_verification_confidence(self, 
                                         content_verification: Dict[str, Any],
                                         page_verification: Dict[str, Any],
                                         quote_verification: Dict[str, Any],
                                         error_check: Dict[str, Any]) -> float:
        """Calculate overall verification confidence"""
        
        confidence_factors = []
        
        # Content accuracy factor
        content_score = content_verification.get('accuracy_score', 0.0)
        confidence_factors.append(content_score * 0.4)
        
        # Page accuracy factor
        page_accurate = page_verification.get('is_accurate', False)
        confidence_factors.append((1.0 if page_accurate else 0.3) * 0.3)
        
        # Quote accuracy factor
        quote_stats = quote_verification
        if quote_stats.get('total_quotes', 0) > 0:
            quote_accuracy = quote_stats.get('verified_count', 0) / quote_stats.get('total_quotes', 1)
            confidence_factors.append(quote_accuracy * 0.2)
        else:
            confidence_factors.append(0.2)  # No quotes to verify
        
        # Error check factor
        errors_count = len(error_check.get('errors_found', []))
        error_penalty = min(errors_count * 0.1, 0.3)  # Max 30% penalty
        confidence_factors.append((1.0 - error_penalty) * 0.1)
        
        return min(1.0, sum(confidence_factors))
    
    def _find_exact_matches(self, citation_text: str, source_text: str) -> float:
        """Find exact matches between citation and source"""
        
        citation_sentences = self._split_sentences(citation_text)
        source_text_lower = source_text.lower()
        
        if not citation_sentences:
            return 0.0
        
        exact_matches = 0
        
        for sentence in citation_sentences:
            if len(sentence) > 10 and sentence.lower() in source_text_lower:
                exact_matches += 1
        
        return exact_matches / len(citation_sentences)
    
    def _find_paraphrase_matches(self, citation_text: str, source_text: str) -> float:
        """Find paraphrase matches using similarity scoring"""
        
        citation_sentences = self._split_sentences(citation_text)
        source_sentences = self._split_sentences(source_text)
        
        if not citation_sentences or not source_sentences:
            return 0.0
        
        paraphrase_matches = 0
        
        for cite_sentence in citation_sentences:
            best_similarity = 0.0
            
            for source_sentence in source_sentences:
                similarity = self._calculate_sentence_similarity(cite_sentence, source_sentence)
                best_similarity = max(best_similarity, similarity)
            
            if best_similarity > 0.7:  # Threshold for paraphrase match
                paraphrase_matches += 1
        
        return paraphrase_matches / len(citation_sentences)
    
    def _assess_contextual_relevance(self, 
                                   citation_text: str,
                                   source_text: str,
                                   response_text: str) -> float:
        """Assess contextual relevance of citation to response"""
        
        # Extract key terms from response
        response_terms = set(response_text.lower().split())
        citation_terms = set(citation_text.lower().split())
        source_terms = set(source_text.lower().split())
        
        # Calculate term overlaps
        citation_response_overlap = len(citation_terms.intersection(response_terms))
        citation_source_overlap = len(citation_terms.intersection(source_terms))
        
        # Contextual relevance score
        if len(citation_terms) == 0:
            return 0.0
        
        relevance_score = (
            (citation_response_overlap / len(citation_terms)) * 0.6 +
            (citation_source_overlap / len(citation_terms)) * 0.4
        )
        
        return min(1.0, relevance_score)
    
    def _determine_match_type(self, 
                            exact_score: float,
                            paraphrase_score: float,
                            context_score: float) -> str:
        """Determine the primary type of match found"""
        
        if exact_score > 0.8:
            return 'exact_match'
        elif paraphrase_score > 0.7:
            return 'paraphrase_match'
        elif context_score > 0.6:
            return 'contextual_match'
        else:
            return 'weak_match'
    
    def _find_best_quote_match(self, quote: str, source_text: str) -> Dict[str, Any]:
        """Find the best matching text for a quote in source"""
        
        # Split source into overlapping windows
        quote_length = len(quote)
        best_match = {'similarity': 0.0, 'source_text': ''}
        
        # Search for similar text segments
        source_words = source_text.split()
        quote_word_count = len(quote.split())
        
        for i in range(len(source_words) - quote_word_count + 1):
            segment = ' '.join(source_words[i:i + quote_word_count + 3])  # Slightly longer
            
            similarity = difflib.SequenceMatcher(None, quote, segment).ratio()
            
            if similarity > best_match['similarity']:
                best_match = {
                    'similarity': similarity,
                    'source_text': segment
                }
        
        return best_match
    
    def _calculate_content_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        
        if not text1 or not text2:
            return 0.0
        
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _calculate_sentence_similarity(self, sent1: str, sent2: str) -> float:
        """Calculate similarity between two sentences"""
        
        return self._calculate_content_similarity(sent1, sent2)
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
    
    def cross_reference_citations(self, 
                                citations: List[Dict[str, Any]],
                                source_documents: List[Dict[str, Any]]) -> List[CrossReferenceCheck]:
        """Perform cross-reference verification between citations"""
        
        cross_ref_results = []
        
        for citation in citations:
            cross_ref = self._cross_reference_single_citation(citation, source_documents)
            cross_ref_results.append(cross_ref)
        
        return cross_ref_results
    
    def _cross_reference_single_citation(self, 
                                       citation: Dict[str, Any],
                                       source_documents: List[Dict[str, Any]]) -> CrossReferenceCheck:
        """Cross-reference a single citation against all sources"""
        
        citation_text = citation.get('citation_text', '')
        
        # Find potential references in other documents
        reference_found = False
        reference_accuracy = 0.0
        context_match = False
        page_accuracy = False
        content_verification = {}
        
        for doc in source_documents:
            if doc.get('node_id') != citation.get('node_id'):  # Don't check against itself
                doc_content = doc.get('content', '')
                
                # Check if citation content appears in other documents
                citation_excerpt = citation.get('content_excerpt', '')
                if citation_excerpt and citation_excerpt.lower() in doc_content.lower():
                    reference_found = True
                    reference_accuracy = 0.8  # Good cross-reference
                    
                    # Check if context matches
                    context_similarity = self._calculate_content_similarity(
                        citation_excerpt, doc_content[:500]  # First part of doc
                    )
                    context_match = context_similarity > 0.6
                    break
        
        return CrossReferenceCheck(
            source_citation=citation_text,
            reference_found=reference_found,
            reference_accuracy=reference_accuracy,
            context_match=context_match,
            page_accuracy=page_accuracy,
            content_verification=content_verification
        )
    
    def generate_quality_report(self, 
                              verification_results: List[VerificationResult]) -> Dict[str, Any]:
        """Generate comprehensive citation quality report"""
        
        if not verification_results:
            return {'status': 'no_citations_to_verify'}
        
        total_citations = len(verification_results)
        verified_citations = sum(1 for r in verification_results if r.is_verified)
        
        # Confidence distribution
        confidences = [r.confidence for r in verification_results]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Issue analysis
        all_issues = []
        all_suggestions = []
        
        for result in verification_results:
            all_issues.extend(result.issues)
            all_suggestions.extend(result.suggestions)
        
        issue_counts = Counter(all_issues)
        
        # Quality assessment
        quality_score = verified_citations / total_citations
        
        if quality_score >= 0.95:
            quality_rating = 'excellent'
        elif quality_score >= 0.85:
            quality_rating = 'good'
        elif quality_score >= 0.70:
            quality_rating = 'acceptable'
        else:
            quality_rating = 'needs_improvement'
        
        return {
            'overall_statistics': {
                'total_citations': total_citations,
                'verified_citations': verified_citations,
                'verification_rate': round(quality_score, 3),
                'average_confidence': round(avg_confidence, 3),
                'quality_rating': quality_rating
            },
            'issue_analysis': {
                'most_common_issues': dict(issue_counts.most_common(5)),
                'total_issues_found': len(all_issues),
                'suggestions_generated': len(all_suggestions)
            },
            'confidence_distribution': {
                'high_confidence': sum(1 for c in confidences if c >= 0.8),
                'medium_confidence': sum(1 for c in confidences if 0.6 <= c < 0.8),
                'low_confidence': sum(1 for c in confidences if c < 0.6)
            },
            'target_compliance': {
                'target_accuracy': '95%',
                'current_accuracy': f'{quality_score * 100:.1f}%',
                'meets_target': quality_score >= 0.95
            }
        }
    
    def get_verifier_config(self) -> Dict[str, Any]:
        """Get citation verifier configuration and capabilities"""
        
        return {
            'verification_capabilities': [
                'content_accuracy_verification',
                'page_reference_validation',
                'quote_accuracy_checking',
                'common_error_detection',
                'cross_reference_validation'
            ],
            'configuration': {
                'strict_verification': self.strict_verification,
                'auto_correction_enabled': self.enable_auto_correction,
                'confidence_threshold': self.min_confidence_threshold
            },
            'verification_weights': self.verification_weights,
            'error_patterns_detected': list(self.error_patterns.keys()),
            'quality_indicators': self.quality_indicators,
            'target_metrics': {
                'citation_accuracy': '95%',
                'verification_confidence': f'{self.min_confidence_threshold * 100}%+'
            }
        }