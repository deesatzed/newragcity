"""
Accuracy Tracker - Historical accuracy data collection and analysis

This implements accuracy tracking for confidence calibration from Phase 1 Week 1-2:
- Ground truth comparison utilities
- Accuracy data collection system  
- Calibration training data pipeline
- Performance monitoring and alerting
"""

import logging
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class AccuracyMeasurement:
    """Single accuracy measurement record"""
    query_id: str
    query_text: str
    query_type: str
    predicted_answer: str
    ground_truth: str
    accuracy_score: float
    confidence_score: float
    timestamp: datetime
    metadata: Dict[str, Any]
    validation_method: str

@dataclass
class GroundTruthComparison:
    """Result of comparing prediction to ground truth"""
    exact_match: bool
    semantic_similarity: float
    key_facts_match: float
    citation_accuracy: float
    overall_accuracy: float
    explanation: str

class AccuracyTracker:
    """
    Tracks prediction accuracy against ground truth for confidence calibration
    
    This system enables the confidence calibrator to learn from historical
    performance and reduce overconfident responses by 30%.
    """
    
    def __init__(self, 
                 retention_days: int = 90,
                 similarity_threshold: float = 0.8,
                 batch_size: int = 100):
        """
        Initialize accuracy tracker
        
        Args:
            retention_days: Days to retain accuracy data
            similarity_threshold: Threshold for semantic similarity matches
            batch_size: Batch size for bulk operations
        """
        
        self.retention_days = retention_days
        self.similarity_threshold = similarity_threshold
        self.batch_size = batch_size
        
        # In-memory storage (would be database in production)
        self.accuracy_data: List[AccuracyMeasurement] = []
        
        # Query type categorization
        self.query_classifiers = {
            'policy_lookup': ['policy', 'guideline', 'procedure', 'rule'],
            'ai_governance': ['ai', 'artificial intelligence', 'machine learning', 'algorithm'],
            'compliance': ['compliance', 'requirement', 'mandatory', 'authorized'],
            'definition': ['what is', 'define', 'definition', 'meaning'],
            'procedure': ['how to', 'process', 'steps', 'procedure']
        }
        
        # Accuracy validation methods
        self.validation_methods = {
            'exact_match': self._validate_exact_match,
            'semantic_similarity': self._validate_semantic_similarity,
            'key_facts': self._validate_key_facts,
            'citation_check': self._validate_citations,
            'expert_review': self._validate_expert_review
        }
        
        # Performance tracking
        self.performance_stats = {
            'total_measurements': 0,
            'avg_accuracy': 0.0,
            'accuracy_by_type': defaultdict(list),
            'confidence_calibration_quality': 0.0
        }
        
        logger.info(f"📊 AccuracyTracker initialized")
        logger.info(f"   Retention: {retention_days} days")
        logger.info(f"   Similarity threshold: {similarity_threshold}")
    
    def track_prediction_accuracy(self,
                                query_id: str,
                                query_text: str,
                                predicted_answer: str,
                                ground_truth: str,
                                confidence_score: float,
                                metadata: Optional[Dict[str, Any]] = None) -> AccuracyMeasurement:
        """
        Track accuracy of a prediction against ground truth
        
        Args:
            query_id: Unique identifier for the query
            query_text: Original query string
            predicted_answer: System's predicted answer
            ground_truth: Known correct answer
            confidence_score: System's confidence in prediction
            metadata: Additional context and metadata
            
        Returns:
            AccuracyMeasurement object with calculated accuracy
        """
        
        logger.debug(f"📊 Tracking accuracy for query: {query_id}")
        
        if metadata is None:
            metadata = {}
        
        # Classify query type
        query_type = self._classify_query_type(query_text)
        
        # Compare prediction to ground truth
        comparison = self._compare_to_ground_truth(predicted_answer, ground_truth, metadata)
        
        # Create accuracy measurement
        measurement = AccuracyMeasurement(
            query_id=query_id,
            query_text=query_text,
            query_type=query_type,
            predicted_answer=predicted_answer,
            ground_truth=ground_truth,
            accuracy_score=comparison.overall_accuracy,
            confidence_score=confidence_score,
            timestamp=datetime.now(),
            metadata={
                **metadata,
                'comparison_details': asdict(comparison)
            },
            validation_method='comprehensive'
        )
        
        # Store measurement
        self.accuracy_data.append(measurement)
        
        # Update performance statistics
        self._update_performance_stats(measurement)
        
        # Cleanup old data
        self._cleanup_old_measurements()
        
        logger.info(f"✅ Tracked accuracy: {comparison.overall_accuracy:.3f} "
                   f"(confidence: {confidence_score:.3f}, type: {query_type})")
        
        return measurement
    
    def _classify_query_type(self, query_text: str) -> str:
        """Classify query into predefined categories"""
        
        query_lower = query_text.lower()
        
        # Check each category
        for query_type, keywords in self.query_classifiers.items():
            if any(keyword in query_lower for keyword in keywords):
                return query_type
        
        return 'general'
    
    def _compare_to_ground_truth(self, 
                               predicted: str,
                               ground_truth: str,
                               metadata: Dict[str, Any]) -> GroundTruthComparison:
        """
        Comprehensive comparison of prediction to ground truth
        
        Uses multiple validation methods for robust accuracy assessment.
        """
        
        # 1. Exact match check
        exact_match = predicted.strip().lower() == ground_truth.strip().lower()
        
        # 2. Semantic similarity
        semantic_sim = self._calculate_semantic_similarity(predicted, ground_truth)
        
        # 3. Key facts matching
        key_facts_match = self._check_key_facts_match(predicted, ground_truth)
        
        # 4. Citation accuracy (if applicable)
        citation_accuracy = self._check_citation_accuracy(predicted, ground_truth, metadata)
        
        # 5. Calculate overall accuracy
        if exact_match:
            overall_accuracy = 1.0
        else:
            # Weighted combination of similarity measures
            overall_accuracy = (
                semantic_sim * 0.4 +
                key_facts_match * 0.4 +
                citation_accuracy * 0.2
            )
        
        # Generate explanation
        explanation = self._generate_accuracy_explanation(
            exact_match, semantic_sim, key_facts_match, citation_accuracy
        )
        
        return GroundTruthComparison(
            exact_match=exact_match,
            semantic_similarity=semantic_sim,
            key_facts_match=key_facts_match,
            citation_accuracy=citation_accuracy,
            overall_accuracy=overall_accuracy,
            explanation=explanation
        )
    
    def _calculate_semantic_similarity(self, predicted: str, ground_truth: str) -> float:
        """
        Calculate semantic similarity between predicted and ground truth answers
        
        This is a simplified implementation - in production would use
        sentence transformers or other embedding-based similarity.
        """
        
        # Simple token-based similarity (Jaccard similarity)
        predicted_tokens = set(predicted.lower().split())
        truth_tokens = set(ground_truth.lower().split())
        
        if not predicted_tokens and not truth_tokens:
            return 1.0
        
        if not predicted_tokens or not truth_tokens:
            return 0.0
        
        intersection = predicted_tokens.intersection(truth_tokens)
        union = predicted_tokens.union(truth_tokens)
        
        jaccard_sim = len(intersection) / len(union) if union else 0.0
        
        # Boost for exact phrase matches
        predicted_lower = predicted.lower()
        truth_lower = ground_truth.lower()
        
        if len(truth_lower) > 10:  # For longer ground truth
            # Check for substring matches
            if truth_lower in predicted_lower or predicted_lower in truth_lower:
                jaccard_sim = max(jaccard_sim, 0.8)
        
        return min(1.0, jaccard_sim)
    
    def _check_key_facts_match(self, predicted: str, ground_truth: str) -> float:
        """
        Check if key facts from ground truth are present in prediction
        
        Focuses on important entities, numbers, and concepts.
        """
        
        # Extract potential key facts (entities, numbers, important terms)
        import re
        
        # Numbers
        truth_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', ground_truth)
        predicted_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', predicted)
        
        # Capitalized words (potential entities)
        truth_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', ground_truth)
        predicted_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', predicted)
        
        # Important policy terms
        policy_terms = ['required', 'mandatory', 'authorized', 'prohibited', 'approved']
        truth_policy = [term for term in policy_terms if term in ground_truth.lower()]
        predicted_policy = [term for term in policy_terms if term in predicted.lower()]
        
        # Calculate matches for each fact type
        number_match = self._calculate_list_overlap(predicted_numbers, truth_numbers)
        entity_match = self._calculate_list_overlap(predicted_entities, truth_entities)
        policy_match = self._calculate_list_overlap(predicted_policy, truth_policy)
        
        # Weighted average (numbers and policy terms more important)
        key_facts_score = (
            number_match * 0.4 +
            policy_match * 0.4 +
            entity_match * 0.2
        )
        
        return min(1.0, key_facts_score)
    
    def _check_citation_accuracy(self, 
                               predicted: str,
                               ground_truth: str,
                               metadata: Dict[str, Any]) -> float:
        """Check accuracy of citations if present"""
        
        # Simple citation extraction (would be more sophisticated in production)
        predicted_citations = self._extract_citations(predicted)
        truth_citations = self._extract_citations(ground_truth)
        
        if not truth_citations and not predicted_citations:
            return 1.0  # No citations needed
        
        if not truth_citations:
            return 0.8 if not predicted_citations else 0.6  # Predicted citations when none needed
        
        if not predicted_citations:
            return 0.3  # Missing citations when needed
        
        # Compare citation accuracy
        citation_overlap = self._calculate_list_overlap(predicted_citations, truth_citations)
        return citation_overlap
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract citations from text (simplified implementation)"""
        
        import re
        
        # Look for common citation patterns
        patterns = [
            r'\(p\.\s*\d+\)',  # (p. 123)
            r'\[.*?\]',        # [Section 1.2]
            r'Section\s+\d+(?:\.\d+)*',  # Section 1.2.3
            r'Page\s+\d+',     # Page 123
        ]
        
        citations = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)
        
        return list(set(citations))  # Remove duplicates
    
    def _calculate_list_overlap(self, list1: List[str], list2: List[str]) -> float:
        """Calculate overlap between two lists"""
        
        if not list1 and not list2:
            return 1.0
        
        if not list1 or not list2:
            return 0.0
        
        set1 = set(item.lower() for item in list1)
        set2 = set(item.lower() for item in list2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _generate_accuracy_explanation(self,
                                     exact_match: bool,
                                     semantic_sim: float,
                                     key_facts: float,
                                     citations: float) -> str:
        """Generate human-readable explanation of accuracy assessment"""
        
        if exact_match:
            return "Perfect match: prediction exactly matches ground truth"
        
        explanations = []
        
        if semantic_sim > 0.8:
            explanations.append(f"High semantic similarity ({semantic_sim:.2f})")
        elif semantic_sim > 0.6:
            explanations.append(f"Moderate semantic similarity ({semantic_sim:.2f})")
        else:
            explanations.append(f"Low semantic similarity ({semantic_sim:.2f})")
        
        if key_facts > 0.8:
            explanations.append("Key facts well preserved")
        elif key_facts > 0.6:
            explanations.append("Most key facts preserved")
        else:
            explanations.append("Key facts missing or incorrect")
        
        if citations > 0.8:
            explanations.append("Citations accurate")
        elif citations > 0.6:
            explanations.append("Citations partially correct")
        elif citations > 0.0:
            explanations.append("Citation issues detected")
        
        return "; ".join(explanations)
    
    def _update_performance_stats(self, measurement: AccuracyMeasurement):
        """Update running performance statistics"""
        
        self.performance_stats['total_measurements'] += 1
        
        # Update overall average accuracy
        total = self.performance_stats['total_measurements']
        old_avg = self.performance_stats['avg_accuracy']
        new_accuracy = measurement.accuracy_score
        
        self.performance_stats['avg_accuracy'] = (old_avg * (total - 1) + new_accuracy) / total
        
        # Update accuracy by query type
        self.performance_stats['accuracy_by_type'][measurement.query_type].append(new_accuracy)
        
        # Update confidence calibration quality (simplified metric)
        confidence_error = abs(measurement.confidence_score - measurement.accuracy_score)
        self.performance_stats['confidence_calibration_quality'] = 1.0 - min(1.0, confidence_error)
    
    def _cleanup_old_measurements(self):
        """Remove measurements older than retention window"""
        
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        original_count = len(self.accuracy_data)
        
        self.accuracy_data = [m for m in self.accuracy_data if m.timestamp >= cutoff_date]
        
        cleaned_count = original_count - len(self.accuracy_data)
        if cleaned_count > 0:
            logger.debug(f"🧹 Cleaned {cleaned_count} old accuracy measurements")
    
    def get_accuracy_insights(self, 
                            query_type: Optional[str] = None,
                            days_back: int = 30) -> Dict[str, Any]:
        """
        Get accuracy insights and trends
        
        Args:
            query_type: Filter by specific query type
            days_back: Number of days to analyze
            
        Returns:
            Dictionary with accuracy insights and recommendations
        """
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_data = [m for m in self.accuracy_data if m.timestamp >= cutoff_date]
        
        if query_type:
            recent_data = [m for m in recent_data if m.query_type == query_type]
        
        if not recent_data:
            return {'status': 'no_data', 'query_type': query_type, 'period_days': days_back}
        
        # Calculate metrics
        accuracies = [m.accuracy_score for m in recent_data]
        confidences = [m.confidence_score for m in recent_data]
        
        avg_accuracy = np.mean(accuracies)
        avg_confidence = np.mean(confidences)
        overconfidence = avg_confidence - avg_accuracy
        
        # Confidence calibration analysis
        calibration_errors = [abs(m.confidence_score - m.accuracy_score) for m in recent_data]
        avg_calibration_error = np.mean(calibration_errors)
        
        # Accuracy trend (simple linear trend over time)
        timestamps = [(m.timestamp - cutoff_date).days for m in recent_data]
        if len(timestamps) > 1:
            trend_slope = np.polyfit(timestamps, accuracies, 1)[0] if len(set(timestamps)) > 1 else 0
        else:
            trend_slope = 0
        
        # Query type breakdown
        type_stats = defaultdict(list)
        for m in recent_data:
            type_stats[m.query_type].append(m.accuracy_score)
        
        type_averages = {qtype: np.mean(scores) for qtype, scores in type_stats.items()}
        
        # Problem areas identification
        problem_areas = []
        if overconfidence > 0.15:
            problem_areas.append("high_overconfidence")
        if avg_calibration_error > 0.2:
            problem_areas.append("poor_confidence_calibration")
        if avg_accuracy < 0.7:
            problem_areas.append("low_overall_accuracy")
        if trend_slope < -0.01:
            problem_areas.append("declining_accuracy_trend")
        
        return {
            'status': 'analyzed',
            'period': f'{days_back} days',
            'query_type': query_type or 'all',
            'sample_size': len(recent_data),
            'accuracy_metrics': {
                'average_accuracy': round(avg_accuracy, 3),
                'average_confidence': round(avg_confidence, 3),
                'overconfidence': round(overconfidence, 3),
                'calibration_error': round(avg_calibration_error, 3),
                'accuracy_trend_slope': round(trend_slope, 4)
            },
            'accuracy_by_type': {qtype: round(avg, 3) for qtype, avg in type_averages.items()},
            'problem_areas': problem_areas,
            'recommendations': self._generate_recommendations(problem_areas, type_averages)
        }
    
    def _generate_recommendations(self, 
                                problem_areas: List[str],
                                type_averages: Dict[str, float]) -> List[str]:
        """Generate recommendations based on accuracy analysis"""
        
        recommendations = []
        
        if "high_overconfidence" in problem_areas:
            recommendations.append("Increase confidence calibration training data")
            recommendations.append("Review and adjust confidence calculation weights")
        
        if "poor_confidence_calibration" in problem_areas:
            recommendations.append("Implement more sophisticated calibration methods")
            recommendations.append("Increase historical accuracy tracking window")
        
        if "low_overall_accuracy" in problem_areas:
            recommendations.append("Review and improve core retrieval algorithms")
            recommendations.append("Expand training data and ground truth coverage")
        
        if "declining_accuracy_trend" in problem_areas:
            recommendations.append("Investigate recent system changes")
            recommendations.append("Perform detailed error analysis on recent queries")
        
        # Type-specific recommendations
        worst_type = min(type_averages.items(), key=lambda x: x[1]) if type_averages else None
        if worst_type and worst_type[1] < 0.6:
            recommendations.append(f"Focus improvement efforts on '{worst_type[0]}' query type")
        
        return recommendations
    
    def export_calibration_data(self, 
                              query_type: Optional[str] = None,
                              days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Export calibration data for external analysis or model training
        
        Returns data in format suitable for confidence calibration training.
        """
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        data_to_export = [m for m in self.accuracy_data if m.timestamp >= cutoff_date]
        
        if query_type:
            data_to_export = [m for m in data_to_export if m.query_type == query_type]
        
        # Convert to training format
        training_data = []
        for measurement in data_to_export:
            training_data.append({
                'predicted_confidence': measurement.confidence_score,
                'actual_accuracy': measurement.accuracy_score,
                'query_type': measurement.query_type,
                'query_length': len(measurement.query_text.split()),
                'answer_length': len(measurement.predicted_answer.split()),
                'timestamp': measurement.timestamp.isoformat(),
                'overconfidence': measurement.confidence_score - measurement.accuracy_score,
                'validation_details': measurement.metadata.get('comparison_details', {})
            })
        
        logger.info(f"📤 Exported {len(training_data)} calibration data points")
        return training_data
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive accuracy tracking system statistics"""
        
        return {
            'total_measurements': len(self.accuracy_data),
            'retention_days': self.retention_days,
            'active_period_measurements': len([
                m for m in self.accuracy_data 
                if m.timestamp >= datetime.now() - timedelta(days=30)
            ]),
            'performance_stats': dict(self.performance_stats),
            'query_type_distribution': dict(Counter(m.query_type for m in self.accuracy_data)),
            'validation_methods': list(self.validation_methods.keys()),
            'latest_measurement': self.accuracy_data[-1].timestamp.isoformat() if self.accuracy_data else None
        }