"""
Confidence Calibrator - Advanced confidence scoring and calibration

This implements the confidence calibration system from Phase 1 Week 1-2:
- Historical accuracy tracking for confidence calibration
- Multi-factor confidence scoring enhancement
- Overconfidence detection and reduction
- Uncertainty quantification

Target: 30% reduction in overconfident responses
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

@dataclass
class ConfidenceFactors:
    """Individual confidence scoring factors"""
    semantic_confidence: float
    source_authority: float
    content_relevance: float
    structure_confidence: float
    model_confidence: float
    historical_accuracy: float
    uncertainty_penalty: float

@dataclass
class CalibrationDataPoint:
    """Single data point for confidence calibration"""
    predicted_confidence: float
    actual_accuracy: float
    query_type: str
    timestamp: datetime
    factors: ConfidenceFactors
    metadata: Dict[str, Any]

@dataclass
class ConfidenceCalibration:
    """Calibrated confidence result"""
    original_confidence: float
    calibrated_confidence: float
    uncertainty_estimate: float
    confidence_interval: Tuple[float, float]
    calibration_quality: str
    explanation: Dict[str, Any]

class ConfidenceCalibrator:
    """
    Advanced confidence calibration system
    
    Implements multi-factor confidence scoring with historical accuracy tracking
    to reduce overconfident responses and improve reliability assessment.
    """
    
    def __init__(self, 
                 calibration_window_days: int = 30,
                 min_data_points: int = 10,
                 overconfidence_threshold: float = 0.2):
        """
        Initialize confidence calibrator
        
        Args:
            calibration_window_days: Days of historical data for calibration
            min_data_points: Minimum data points needed for calibration
            overconfidence_threshold: Threshold for detecting overconfidence
        """
        
        self.calibration_window_days = calibration_window_days
        self.min_data_points = min_data_points
        self.overconfidence_threshold = overconfidence_threshold
        
        # Historical data storage
        self.calibration_data: List[CalibrationDataPoint] = []
        
        # Calibration models (binned accuracy by confidence level)
        self.confidence_bins = {}
        self.bin_size = 0.1  # 10% bins
        
        # Factor weights for confidence calculation
        self.factor_weights = {
            'semantic_confidence': 0.25,
            'source_authority': 0.20,
            'content_relevance': 0.15,
            'structure_confidence': 0.15,
            'model_confidence': 0.10,
            'historical_accuracy': 0.10,
            'uncertainty_penalty': 0.05
        }
        
        # Overconfidence detection patterns
        self.overconfidence_patterns = {
            'high_confidence_low_accuracy': [],  # Confidence >0.8, Accuracy <0.6
            'consistent_overestimation': [],    # Consistent >20% overestimation
            'domain_specific_issues': defaultdict(list)  # Issues by query type
        }
        
        logger.info(f"🎯 ConfidenceCalibrator initialized")
        logger.info(f"   Calibration window: {calibration_window_days} days")
        logger.info(f"   Min data points: {min_data_points}")
        logger.info(f"   Overconfidence threshold: {overconfidence_threshold}")
    
    def calculate_calibrated_confidence(self, 
                                      result: Dict[str, Any],
                                      query: str,
                                      query_type: str = "general") -> ConfidenceCalibration:
        """
        Calculate calibrated confidence score with uncertainty estimation
        
        Args:
            result: Search result with metadata and scores
            query: Original query string
            query_type: Type of query for domain-specific calibration
            
        Returns:
            ConfidenceCalibration object with calibrated scores and explanations
        """
        
        logger.debug(f"🎯 Calculating calibrated confidence for query: '{query}'")
        
        # Step 1: Extract and calculate confidence factors
        factors = self._extract_confidence_factors(result, query)
        
        # Step 2: Calculate raw composite confidence
        raw_confidence = self._calculate_composite_confidence(factors)
        
        # Step 3: Apply historical calibration if available
        calibrated_confidence = self._apply_historical_calibration(
            raw_confidence, query_type, factors
        )
        
        # Step 4: Calculate uncertainty estimate
        uncertainty = self._estimate_uncertainty(calibrated_confidence, factors, query_type)
        
        # Step 5: Generate confidence interval
        conf_interval = self._calculate_confidence_interval(calibrated_confidence, uncertainty)
        
        # Step 6: Assess calibration quality
        quality = self._assess_calibration_quality(calibrated_confidence, uncertainty)
        
        # Step 7: Generate explanation
        explanation = self._generate_explanation(factors, raw_confidence, calibrated_confidence)
        
        calibration = ConfidenceCalibration(
            original_confidence=raw_confidence,
            calibrated_confidence=calibrated_confidence,
            uncertainty_estimate=uncertainty,
            confidence_interval=conf_interval,
            calibration_quality=quality,
            explanation=explanation
        )
        
        logger.debug(f"✅ Confidence calibrated: {raw_confidence:.3f} -> {calibrated_confidence:.3f} "
                    f"(uncertainty: {uncertainty:.3f})")
        
        return calibration
    
    def _extract_confidence_factors(self, result: Dict[str, Any], query: str) -> ConfidenceFactors:
        """Extract individual confidence factors from search result"""
        
        metadata = result.get('metadata', {})
        
        # Extract existing confidence factors from result
        semantic_confidence = self._normalize_score(result.get('semantic_score', 0.0))
        source_authority = metadata.get('reasoning_confidence', 0.70)
        structure_confidence = metadata.get('reasoning_confidence', 0.70)
        model_confidence = 0.92  # IBM Granite enterprise confidence
        
        # Calculate content relevance based on query-content matching
        content_relevance = self._calculate_content_relevance(result.get('content', ''), query)
        
        # Calculate historical accuracy for similar queries
        historical_accuracy = self._get_historical_accuracy(query, result)
        
        # Calculate uncertainty penalty based on various factors
        uncertainty_penalty = self._calculate_uncertainty_penalty(result, query)
        
        return ConfidenceFactors(
            semantic_confidence=semantic_confidence,
            source_authority=source_authority,
            content_relevance=content_relevance,
            structure_confidence=structure_confidence,
            model_confidence=model_confidence,
            historical_accuracy=historical_accuracy,
            uncertainty_penalty=uncertainty_penalty
        )
    
    def _calculate_composite_confidence(self, factors: ConfidenceFactors) -> float:
        """Calculate weighted composite confidence score"""
        
        factor_dict = asdict(factors)
        
        composite_score = sum(
            factor_dict[factor_name] * weight
            for factor_name, weight in self.factor_weights.items()
        )
        
        # Apply uncertainty penalty (multiplicative)
        composite_score *= (1.0 - factors.uncertainty_penalty * 0.1)
        
        return max(0.0, min(1.0, composite_score))
    
    def _apply_historical_calibration(self, 
                                    raw_confidence: float,
                                    query_type: str,
                                    factors: ConfidenceFactors) -> float:
        """Apply historical calibration to adjust confidence based on past accuracy"""
        
        # Get recent calibration data within window
        cutoff_date = datetime.now() - timedelta(days=self.calibration_window_days)
        recent_data = [dp for dp in self.calibration_data 
                      if dp.timestamp >= cutoff_date and dp.query_type == query_type]
        
        if len(recent_data) < self.min_data_points:
            logger.debug(f"Insufficient calibration data ({len(recent_data)} points), using raw confidence")
            return raw_confidence
        
        # Find the appropriate confidence bin
        confidence_bin = int(raw_confidence / self.bin_size) * self.bin_size
        
        # Get data points in this confidence bin
        bin_data = [dp for dp in recent_data 
                   if abs(dp.predicted_confidence - confidence_bin) < self.bin_size/2]
        
        if not bin_data:
            logger.debug(f"No calibration data for confidence bin {confidence_bin}")
            return raw_confidence
        
        # Calculate actual accuracy in this bin
        actual_accuracies = [dp.actual_accuracy for dp in bin_data]
        avg_accuracy = np.mean(actual_accuracies)
        
        # Calculate calibration adjustment
        # If historical accuracy is lower than predicted confidence, adjust downward
        calibration_factor = avg_accuracy / max(confidence_bin, 0.1)
        calibrated_confidence = raw_confidence * calibration_factor
        
        # Apply conservative adjustment to prevent overcorrection
        adjustment = calibrated_confidence - raw_confidence
        conservative_adjustment = adjustment * 0.7  # 70% of full adjustment
        final_confidence = raw_confidence + conservative_adjustment
        
        logger.debug(f"Historical calibration: bin={confidence_bin}, "
                    f"avg_accuracy={avg_accuracy:.3f}, factor={calibration_factor:.3f}")
        
        return max(0.1, min(0.95, final_confidence))
    
    def _estimate_uncertainty(self, 
                            confidence: float,
                            factors: ConfidenceFactors, 
                            query_type: str) -> float:
        """Estimate uncertainty in the confidence prediction"""
        
        # Base uncertainty increases at confidence extremes (U-shaped)
        base_uncertainty = 2 * confidence * (1 - confidence)  # Maximum at 0.5
        
        # Factor-based uncertainty
        factor_variances = []
        factor_dict = asdict(factors)
        
        for factor_name, value in factor_dict.items():
            # Higher variance for factors close to decision boundaries
            if factor_name != 'uncertainty_penalty':
                variance = 4 * value * (1 - value)  # U-shaped variance
                factor_variances.append(variance)
        
        factor_uncertainty = np.mean(factor_variances) if factor_variances else 0.2
        
        # Historical variance in similar queries
        historical_uncertainty = self._get_historical_uncertainty(query_type)
        
        # Combine uncertainty sources
        total_uncertainty = (
            base_uncertainty * 0.4 +
            factor_uncertainty * 0.4 +
            historical_uncertainty * 0.2
        )
        
        return max(0.05, min(0.4, total_uncertainty))  # Bounded uncertainty
    
    def _calculate_confidence_interval(self, 
                                     confidence: float,
                                     uncertainty: float) -> Tuple[float, float]:
        """Calculate confidence interval around the calibrated confidence"""
        
        # Use uncertainty to define interval width (roughly 1 standard deviation)
        interval_width = uncertainty * 1.96  # 95% confidence interval
        
        lower_bound = max(0.0, confidence - interval_width/2)
        upper_bound = min(1.0, confidence + interval_width/2)
        
        return (lower_bound, upper_bound)
    
    def _assess_calibration_quality(self, confidence: float, uncertainty: float) -> str:
        """Assess the quality of calibration based on confidence and uncertainty"""
        
        if uncertainty < 0.1:
            if confidence > 0.8:
                return "high_quality_confident"
            elif confidence > 0.6:
                return "high_quality_moderate"
            else:
                return "high_quality_uncertain"
        elif uncertainty < 0.2:
            return "moderate_quality"
        else:
            return "low_quality_high_uncertainty"
    
    def _calculate_content_relevance(self, content: str, query: str) -> float:
        """Calculate content relevance factor"""
        
        if not content or not query:
            return 0.5
        
        content_lower = content.lower()
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        # Term overlap
        matches = sum(1 for term in query_terms if term in content_lower)
        term_relevance = matches / max(len(query_terms), 1)
        
        # Length-adjusted relevance (prefer focused content)
        content_length = len(content.split())
        if content_length < 50:
            length_factor = 0.8  # Too short
        elif content_length > 1000:
            length_factor = 0.9  # Too long
        else:
            length_factor = 1.0  # Good length
        
        return min(1.0, term_relevance * length_factor)
    
    def _get_historical_accuracy(self, query: str, result: Dict[str, Any]) -> float:
        """Get historical accuracy for similar queries/results"""
        
        # Simple implementation - in production would use more sophisticated similarity
        similar_data = [dp for dp in self.calibration_data[-50:]  # Last 50 points
                       if any(term in dp.metadata.get('query', '') 
                             for term in query.lower().split())]
        
        if not similar_data:
            return 0.75  # Default historical accuracy
        
        return np.mean([dp.actual_accuracy for dp in similar_data])
    
    def _calculate_uncertainty_penalty(self, result: Dict[str, Any], query: str) -> float:
        """Calculate uncertainty penalty based on various risk factors"""
        
        penalty = 0.0
        
        # Low semantic score increases uncertainty
        semantic_score = result.get('semantic_score', 0.0)
        if semantic_score < 0.7:
            penalty += 0.3
        
        # Very short or very long content increases uncertainty
        content_length = len(result.get('content', '').split())
        if content_length < 20 or content_length > 2000:
            penalty += 0.2
        
        # Ambiguous queries increase uncertainty
        if len(query.split()) < 3:
            penalty += 0.1
        
        # Missing metadata increases uncertainty
        metadata = result.get('metadata', {})
        if not metadata.get('node_id') or not metadata.get('reasoning_confidence'):
            penalty += 0.15
        
        return min(1.0, penalty)
    
    def _get_historical_uncertainty(self, query_type: str) -> float:
        """Get historical uncertainty for query type"""
        
        recent_data = [dp for dp in self.calibration_data[-100:]  # Last 100 points
                      if dp.query_type == query_type]
        
        if not recent_data:
            return 0.2  # Default uncertainty
        
        # Calculate variance in confidence vs accuracy
        confidence_accuracy_pairs = [(dp.predicted_confidence, dp.actual_accuracy) 
                                   for dp in recent_data]
        
        if len(confidence_accuracy_pairs) < 5:
            return 0.2
        
        differences = [abs(conf - acc) for conf, acc in confidence_accuracy_pairs]
        return min(0.4, np.std(differences))
    
    def _generate_explanation(self, 
                            factors: ConfidenceFactors,
                            raw_confidence: float,
                            calibrated_confidence: float) -> Dict[str, Any]:
        """Generate explanation of confidence calculation"""
        
        factor_dict = asdict(factors)
        
        # Find most influential factors
        weighted_factors = {name: value * self.factor_weights[name] 
                          for name, value in factor_dict.items()}
        
        top_factors = sorted(weighted_factors.items(), key=lambda x: x[1], reverse=True)[:3]
        
        explanation = {
            'confidence_factors': {
                name: {
                    'value': round(factor_dict[name], 3),
                    'weight': self.factor_weights[name],
                    'contribution': round(weighted_factors[name], 3)
                }
                for name in factor_dict.keys()
            },
            'top_contributing_factors': [
                {'factor': name, 'contribution': round(contrib, 3)} 
                for name, contrib in top_factors
            ],
            'calibration_adjustment': round(calibrated_confidence - raw_confidence, 3),
            'adjustment_reason': self._get_adjustment_reason(raw_confidence, calibrated_confidence)
        }
        
        return explanation
    
    def _get_adjustment_reason(self, raw_confidence: float, calibrated_confidence: float) -> str:
        """Explain why calibration adjustment was made"""
        
        diff = calibrated_confidence - raw_confidence
        
        if abs(diff) < 0.05:
            return "minimal_adjustment_high_calibration_quality"
        elif diff > 0.05:
            return "confidence_increased_based_on_historical_underestimation"
        else:
            return "confidence_decreased_to_correct_historical_overconfidence"
    
    def add_feedback(self, 
                    query: str,
                    predicted_confidence: float,
                    actual_accuracy: float,
                    query_type: str = "general",
                    metadata: Optional[Dict[str, Any]] = None):
        """
        Add feedback for confidence calibration learning
        
        This is critical for the 30% overconfidence reduction target.
        """
        
        if metadata is None:
            metadata = {}
        
        # Create placeholder factors (would be extracted from original prediction)
        factors = ConfidenceFactors(
            semantic_confidence=predicted_confidence,
            source_authority=0.75,
            content_relevance=0.70,
            structure_confidence=0.75,
            model_confidence=0.92,
            historical_accuracy=0.75,
            uncertainty_penalty=0.1
        )
        
        data_point = CalibrationDataPoint(
            predicted_confidence=predicted_confidence,
            actual_accuracy=actual_accuracy,
            query_type=query_type,
            timestamp=datetime.now(),
            factors=factors,
            metadata={'query': query, **metadata}
        )
        
        self.calibration_data.append(data_point)
        
        # Update overconfidence patterns
        self._update_overconfidence_patterns(data_point)
        
        # Maintain data window
        self._cleanup_old_data()
        
        logger.info(f"📊 Added calibration feedback: confidence={predicted_confidence:.3f}, "
                   f"accuracy={actual_accuracy:.3f}, type={query_type}")
    
    def _update_overconfidence_patterns(self, data_point: CalibrationDataPoint):
        """Update overconfidence pattern tracking"""
        
        confidence = data_point.predicted_confidence
        accuracy = data_point.actual_accuracy
        overconfidence = confidence - accuracy
        
        # Track high confidence, low accuracy cases
        if confidence > 0.8 and accuracy < 0.6:
            self.overconfidence_patterns['high_confidence_low_accuracy'].append(data_point)
        
        # Track consistent overestimation
        if overconfidence > self.overconfidence_threshold:
            self.overconfidence_patterns['consistent_overestimation'].append(data_point)
        
        # Track domain-specific issues
        query_type = data_point.query_type
        if overconfidence > self.overconfidence_threshold:
            self.overconfidence_patterns['domain_specific_issues'][query_type].append(data_point)
    
    def _cleanup_old_data(self):
        """Remove calibration data outside the window"""
        
        cutoff_date = datetime.now() - timedelta(days=self.calibration_window_days * 2)
        
        original_count = len(self.calibration_data)
        self.calibration_data = [dp for dp in self.calibration_data if dp.timestamp >= cutoff_date]
        
        cleaned_count = original_count - len(self.calibration_data)
        if cleaned_count > 0:
            logger.debug(f"🧹 Cleaned {cleaned_count} old calibration data points")
    
    def get_calibration_stats(self) -> Dict[str, Any]:
        """Get comprehensive calibration statistics"""
        
        if not self.calibration_data:
            return {'status': 'no_data'}
        
        recent_data = self.calibration_data[-100:]  # Last 100 points
        
        # Calculate overall calibration metrics
        confidences = [dp.predicted_confidence for dp in recent_data]
        accuracies = [dp.actual_accuracy for dp in recent_data]
        
        # Overconfidence statistics
        overconfidences = [c - a for c, a in zip(confidences, accuracies)]
        avg_overconfidence = np.mean(overconfidences)
        overconfident_rate = sum(1 for oc in overconfidences if oc > self.overconfidence_threshold) / len(overconfidences)
        
        # Calibration quality
        calibration_error = np.mean(np.abs(overconfidences))
        
        return {
            'status': 'active',
            'data_points': len(self.calibration_data),
            'recent_data_points': len(recent_data),
            'calibration_metrics': {
                'average_overconfidence': round(avg_overconfidence, 3),
                'overconfident_rate': round(overconfident_rate, 3),
                'calibration_error': round(calibration_error, 3),
                'target_overconfident_reduction': f"{100 - overconfident_rate*100:.1f}% vs 30% target"
            },
            'pattern_detection': {
                'high_conf_low_acc_cases': len(self.overconfidence_patterns['high_confidence_low_accuracy']),
                'consistent_overestimation_cases': len(self.overconfidence_patterns['consistent_overestimation']),
                'domain_issues': {k: len(v) for k, v in self.overconfidence_patterns['domain_specific_issues'].items()}
            },
            'factor_weights': self.factor_weights
        }
    
    def _normalize_score(self, score: float, score_range: Tuple[float, float] = (0.0, 1000.0)) -> float:
        """Normalize score to 0-1 range"""
        min_score, max_score = score_range
        if max_score > min_score:
            return max(0.0, min(1.0, (score - min_score) / (max_score - min_score)))
        return 0.5