'use client';

/**
 * Confidence Display - Real-time confidence visualization
 * 
 * This implements confidence display from Phase 1 Week 1-2:
 * - Real-time confidence score updates
 * - Calibrated confidence vs original confidence
 * - Uncertainty estimation display
 * - Confidence interval visualization
 * - Historical confidence tracking
 */

import React, { useState, useEffect } from 'react';

interface ConfidenceData {
  originalConfidence: number;
  calibratedConfidence: number;
  uncertaintyEstimate: number;
  confidenceInterval: [number, number];
  calibrationQuality: string;
}

interface ConfidenceDisplayProps {
  confidence: ConfidenceData | null;
  lastResponse: any;
  calibrationEnabled: boolean;
  showDetails?: boolean;
}

export const ConfidenceDisplay: React.FC<ConfidenceDisplayProps> = ({
  confidence,
  lastResponse,
  calibrationEnabled,
  showDetails = true
}) => {
  const [animatedConfidence, setAnimatedConfidence] = useState(0);
  const [showCalibrationDetails, setShowCalibrationDetails] = useState(false);

  // Animate confidence changes
  useEffect(() => {
    if (confidence?.calibratedConfidence) {
      const target = confidence.calibratedConfidence * 100;
      let current = animatedConfidence;
      
      const animate = () => {
        const diff = target - current;
        if (Math.abs(diff) < 0.5) {
          setAnimatedConfidence(target);
          return;
        }
        
        current += diff * 0.1;
        setAnimatedConfidence(current);
        requestAnimationFrame(animate);
      };
      
      animate();
    }
  }, [confidence?.calibratedConfidence]);

  if (!confidence && !lastResponse) {
    return null;
  }

  // Extract confidence from response if direct confidence data not available
  const displayConfidence = confidence || extractConfidenceFromResponse(lastResponse);
  
  if (!displayConfidence) {
    return null;
  }

  const confidenceLevel = getConfidenceLevel(displayConfidence.calibratedConfidence);
  const confidenceColor = getConfidenceColor(displayConfidence.calibratedConfidence);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-800">
          🎯 Confidence Analysis
        </h3>
        {calibrationEnabled && (
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
            📊 Calibrated
          </span>
        )}
      </div>

      {/* Main Confidence Display */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Overall Confidence
          </span>
          <span className={`text-lg font-bold ${confidenceColor}`}>
            {animatedConfidence.toFixed(1)}%
          </span>
        </div>
        
        {/* Confidence Bar */}
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${getConfidenceBarColor(displayConfidence.calibratedConfidence)}`}
            style={{ width: `${animatedConfidence}%` }}
          />
        </div>
        
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>Low</span>
          <span>Medium</span>
          <span>High</span>
        </div>
      </div>

      {/* Confidence Level Badge */}
      <div className="flex items-center space-x-2 mb-4">
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceBadgeStyle(confidenceLevel)}`}>
          {getConfidenceIcon(confidenceLevel)} {confidenceLevel} Confidence
        </div>
        
        {displayConfidence.uncertaintyEstimate > 0.2 && (
          <div className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
            ⚠️ High Uncertainty
          </div>
        )}
      </div>

      {/* Calibration Comparison (if enabled) */}
      {calibrationEnabled && displayConfidence.originalConfidence !== displayConfidence.calibratedConfidence && (
        <div className="mb-4 p-3 bg-gray-50 rounded">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Calibration Impact</span>
            <button
              onClick={() => setShowCalibrationDetails(!showCalibrationDetails)}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              {showCalibrationDetails ? 'Hide' : 'Show'} Details
            </button>
          </div>
          
          <div className="flex items-center space-x-4 text-sm">
            <div>
              <span className="text-gray-600">Original:</span>
              <span className="ml-1 font-medium">
                {(displayConfidence.originalConfidence * 100).toFixed(1)}%
              </span>
            </div>
            <span className="text-gray-400">→</span>
            <div>
              <span className="text-gray-600">Calibrated:</span>
              <span className="ml-1 font-medium text-blue-600">
                {(displayConfidence.calibratedConfidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>
          
          {showCalibrationDetails && (
            <div className="mt-3 space-y-2 text-xs text-gray-600">
              <div>
                <span className="font-medium">Uncertainty Estimate:</span>
                <span className="ml-1">{(displayConfidence.uncertaintyEstimate * 100).toFixed(1)}%</span>
              </div>
              <div>
                <span className="font-medium">Confidence Interval:</span>
                <span className="ml-1">
                  [{(displayConfidence.confidenceInterval[0] * 100).toFixed(1)}% - {(displayConfidence.confidenceInterval[1] * 100).toFixed(1)}%]
                </span>
              </div>
              <div>
                <span className="font-medium">Calibration Quality:</span>
                <span className="ml-1 capitalize">{displayConfidence.calibrationQuality.replace('_', ' ')}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Confidence Breakdown (if detailed data available) */}
      {showDetails && lastResponse?.confidence_analysis && (
        <details className="mb-4">
          <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
            📊 Detailed Breakdown
          </summary>
          
          <div className="mt-3 space-y-2">
            {Object.entries(lastResponse.confidence_analysis.calibrated_confidence || {}).map(([key, value]) => (
              <div key={key} className="flex justify-between text-sm">
                <span className="text-gray-600 capitalize">{key.replace('_', ' ')}:</span>
                <span className="font-medium">
                  {typeof value === 'number' ? (value * 100).toFixed(1) + '%' : String(value)}
                </span>
              </div>
            ))}
          </div>
        </details>
      )}

      {/* Confidence Explanation */}
      <div className="text-xs text-gray-500 border-t pt-3">
        <p>
          {getConfidenceExplanation(displayConfidence.calibratedConfidence, calibrationEnabled)}
        </p>
        
        {displayConfidence.uncertaintyEstimate > 0.2 && (
          <p className="mt-1 text-yellow-700">
            High uncertainty detected. Consider asking for clarification or more specific information.
          </p>
        )}
      </div>
    </div>
  );
};

// Helper functions
function extractConfidenceFromResponse(response: any): ConfidenceData | null {
  if (!response) return null;

  const result = response.results?.[0];
  if (!result) return null;

  // Try to extract from calibrated confidence
  if (result.confidence_calibration) {
    return {
      originalConfidence: result.confidence_calibration.original_confidence,
      calibratedConfidence: result.confidence_calibration.calibrated_confidence,
      uncertaintyEstimate: result.confidence_calibration.uncertainty_estimate,
      confidenceInterval: result.confidence_calibration.confidence_interval,
      calibrationQuality: result.confidence_calibration.calibration_quality
    };
  }

  // Fallback to confidence profile
  if (result.confidence_profile) {
    const composite = result.confidence_profile.composite_confidence;
    return {
      originalConfidence: composite,
      calibratedConfidence: composite,
      uncertaintyEstimate: 0.1, // Default uncertainty
      confidenceInterval: [composite - 0.1, composite + 0.1],
      calibrationQuality: 'standard'
    };
  }

  return null;
}

function getConfidenceLevel(confidence: number): 'Low' | 'Medium' | 'High' {
  if (confidence >= 0.8) return 'High';
  if (confidence >= 0.6) return 'Medium';
  return 'Low';
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-600';
  if (confidence >= 0.6) return 'text-yellow-600';
  return 'text-red-600';
}

function getConfidenceBarColor(confidence: number): string {
  if (confidence >= 0.8) return 'bg-green-500';
  if (confidence >= 0.6) return 'bg-yellow-500';
  return 'bg-red-500';
}

function getConfidenceBadgeStyle(level: string): string {
  switch (level) {
    case 'High':
      return 'bg-green-100 text-green-800';
    case 'Medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'Low':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

function getConfidenceIcon(level: string): string {
  switch (level) {
    case 'High':
      return '✅';
    case 'Medium':
      return '⚠️';
    case 'Low':
      return '❌';
    default:
      return '❓';
  }
}

function getConfidenceExplanation(confidence: number, calibrationEnabled: boolean): string {
  const baseExplanation = confidence >= 0.8 
    ? "High confidence indicates strong evidence and reliable sources."
    : confidence >= 0.6
    ? "Medium confidence suggests good evidence but with some uncertainty."
    : "Low confidence indicates limited or conflicting evidence.";

  if (calibrationEnabled) {
    return baseExplanation + " This score has been calibrated based on historical accuracy data.";
  }

  return baseExplanation;
}