'use client';

/**
 * Reasoning Visualization - Live transparency of AI reasoning steps
 * 
 * This implements reasoning visualization from Phase 1 Week 1-2:
 * - Real-time display of reasoning steps during processing
 * - Progress visualization for each step
 * - Expandable details for expert-level transparency
 * - Timeline view of collective intelligence process
 */

import React, { useState, useEffect, useRef } from 'react';

interface ReasoningStep {
  step: string;
  status: 'processing' | 'completed' | 'error';
  message: string;
  timestamp: string;
  progress: number;
  data?: any;
}

interface ReasoningVisualizationProps {
  steps: ReasoningStep[];
  isProcessing: boolean;
  transparencyLevel: 'basic' | 'detailed' | 'expert';
}

export const ReasoningVisualization: React.FC<ReasoningVisualizationProps> = ({
  steps,
  isProcessing,
  transparencyLevel
}) => {
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [autoScroll, setAutoScroll] = useState(true);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest step
  useEffect(() => {
    if (autoScroll && scrollContainerRef.current && steps.length > 0) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [steps, autoScroll]);

  const toggleStepExpansion = (stepName: string) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepName)) {
      newExpanded.delete(stepName);
    } else {
      newExpanded.add(stepName);
    }
    setExpandedSteps(newExpanded);
  };

  const getStepIcon = (step: ReasoningStep) => {
    if (step.status === 'error') return '❌';
    if (step.status === 'completed') return '✅';
    if (step.status === 'processing') return '🔄';
    return '⏳';
  };

  const getStepColor = (step: ReasoningStep) => {
    switch (step.status) {
      case 'completed': return 'text-green-600 border-green-200 bg-green-50';
      case 'processing': return 'text-blue-600 border-blue-200 bg-blue-50';
      case 'error': return 'text-red-600 border-red-200 bg-red-50';
      default: return 'text-gray-600 border-gray-200 bg-gray-50';
    }
  };

  const getStepTitle = (stepName: string) => {
    const titles: { [key: string]: string } = {
      'query_processing': '🔍 Query Processing',
      'query_analysis': '📝 Query Analysis',
      'search_initialization': '⚙️ Search Setup',
      'semantic_search': '🧠 Semantic Search',
      'confidence_calibration': '🎯 Confidence Calibration',
      'final_results': '📊 Final Results'
    };
    return titles[stepName] || stepName.replace('_', ' ').toUpperCase();
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const renderStepData = (step: ReasoningStep) => {
    if (!step.data || transparencyLevel === 'basic') return null;

    const data = step.data;

    switch (step.step) {
      case 'query_analysis':
        return (
          <div className="mt-3 space-y-2 text-sm">
            <div><span className="font-medium">Query Type:</span> {data.query_type}</div>
            <div><span className="font-medium">Complexity:</span> {data.complexity}</div>
            <div><span className="font-medium">Terms:</span> {data.query_length} words</div>
          </div>
        );

      case 'semantic_search':
        return (
          <div className="mt-3 space-y-2 text-sm">
            <div><span className="font-medium">Results Found:</span> {data.results_found}</div>
            <div><span className="font-medium">Components:</span> {data.search_components?.join(', ')}</div>
          </div>
        );

      case 'confidence_calibration':
        return (
          <div className="mt-3 space-y-2 text-sm">
            {data.processed && (
              <div><span className="font-medium">Progress:</span> {data.processed}/{data.total}</div>
            )}
            {data.current_result && (
              <div>
                <span className="font-medium">Current:</span> {data.current_result.node_id}
                <span className="ml-2 text-blue-600">
                  ({(data.current_result.calibrated_confidence * 100).toFixed(1)}% confidence)
                </span>
              </div>
            )}
          </div>
        );

      case 'final_results':
        if (transparencyLevel === 'expert') {
          return (
            <div className="mt-3 space-y-3 text-sm">
              {data.results && (
                <div>
                  <span className="font-medium">Results:</span> {data.results.length} found
                </div>
              )}
              {data.confidence_analysis && (
                <div>
                  <span className="font-medium">Avg Confidence:</span>{' '}
                  {(data.confidence_analysis.calibrated_confidence?.average * 100).toFixed(1)}%
                </div>
              )}
              {data.approach_summary && (
                <div>
                  <span className="font-medium">Approaches Used:</span>{' '}
                  {data.approach_summary.total_approaches_used}/3
                </div>
              )}
            </div>
          );
        }
        return null;

      default:
        // Generic data display for unknown steps
        if (typeof data === 'object' && Object.keys(data).length > 0) {
          return (
            <div className="mt-3 text-sm">
              <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          );
        }
        return null;
    }
  };

  if (steps.length === 0 && !isProcessing) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">
          🧠 Reasoning Process
        </h3>
        <p className="text-gray-600 text-sm">
          Reasoning steps will appear here when processing begins...
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">
          🧠 Reasoning Process
          {isProcessing && (
            <span className="ml-2 inline-flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            </span>
          )}
        </h3>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`text-xs px-2 py-1 rounded ${
              autoScroll ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
            }`}
          >
            {autoScroll ? '📌 Auto-scroll' : '📌 Manual'}
          </button>
          
          {transparencyLevel === 'expert' && (
            <span className="text-xs px-2 py-1 bg-purple-100 text-purple-800 rounded">
              Expert Mode
            </span>
          )}
        </div>
      </div>

      {/* Steps Container */}
      <div 
        ref={scrollContainerRef}
        className="max-h-96 overflow-y-auto p-4"
        onScroll={() => {
          if (scrollContainerRef.current) {
            const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
            const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
            if (!isAtBottom) setAutoScroll(false);
          }
        }}
      >
        <div className="space-y-3">
          {steps.map((step, index) => (
            <div
              key={`${step.step}-${index}`}
              className={`border rounded-lg p-3 transition-all duration-200 ${getStepColor(step)}`}
            >
              {/* Step Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className={step.status === 'processing' ? 'animate-spin' : ''}>
                    {getStepIcon(step)}
                  </span>
                  <div>
                    <h4 className="font-medium">{getStepTitle(step.step)}</h4>
                    <p className="text-sm opacity-90">{step.message}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className="text-xs opacity-75">
                    {formatTimestamp(step.timestamp)}
                  </span>
                  
                  {step.data && transparencyLevel !== 'basic' && (
                    <button
                      onClick={() => toggleStepExpansion(step.step)}
                      className="text-xs px-2 py-1 bg-white bg-opacity-50 rounded hover:bg-opacity-75"
                    >
                      {expandedSteps.has(step.step) ? '▼' : '▶'}
                    </button>
                  )}
                </div>
              </div>

              {/* Progress Bar */}
              {step.status === 'processing' && step.progress > 0 && (
                <div className="mt-2">
                  <div className="w-full bg-white bg-opacity-50 rounded-full h-2">
                    <div
                      className="h-2 bg-current rounded-full transition-all duration-300"
                      style={{ width: `${step.progress * 100}%` }}
                    />
                  </div>
                  <div className="text-xs text-right mt-1 opacity-75">
                    {(step.progress * 100).toFixed(0)}%
                  </div>
                </div>
              )}

              {/* Expanded Data */}
              {expandedSteps.has(step.step) && renderStepData(step)}
            </div>
          ))}
        </div>

        {/* Current Processing Indicator */}
        {isProcessing && steps.length > 0 && (
          <div className="mt-4 flex items-center justify-center text-sm text-gray-600">
            <div className="animate-pulse flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <span>Processing collective intelligence...</span>
            </div>
          </div>
        )}
      </div>

      {/* Footer Summary */}
      {steps.length > 0 && !isProcessing && (
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div>
              <span className="font-medium">{steps.length}</span> reasoning steps completed
            </div>
            <div>
              Duration: {(() => {
                if (steps.length < 2) return 'N/A';
                try {
                  const start = new Date(steps[0].timestamp);
                  const end = new Date(steps[steps.length - 1].timestamp);
                  const diff = end.getTime() - start.getTime();
                  return `${(diff / 1000).toFixed(1)}s`;
                } catch {
                  return 'N/A';
                }
              })()}
            </div>
          </div>
          
          {transparencyLevel === 'expert' && (
            <div className="mt-2 text-xs text-gray-500">
              Full reasoning audit trail available for compliance review
            </div>
          )}
        </div>
      )}
    </div>
  );
};