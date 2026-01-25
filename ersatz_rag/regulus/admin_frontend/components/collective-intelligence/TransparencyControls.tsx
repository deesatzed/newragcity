'use client';

/**
 * Transparency Controls - User controls for transparency and privacy
 * 
 * This implements user controls from Phase 1 Week 1-2:
 * - Transparency level selection (basic/detailed/expert)
 * - Privacy mode toggle for browser-based processing
 * - Streaming and multimodal feature controls
 * - Real-time connection status display
 */

import React from 'react';

interface TransparencyControlsProps {
  config: {
    enableStreaming: boolean;
    privacyMode: boolean;
    transparencyLevel: 'basic' | 'detailed' | 'expert';
    enableVoice: boolean;
    enableCamera: boolean;
    enableDocumentUpload: boolean;
    confidenceThreshold: number;
  };
  onConfigChange: (updates: any) => void;
  connectionStatus: string;
  isProcessing: boolean;
}

export const TransparencyControls: React.FC<TransparencyControlsProps> = ({
  config,
  onConfigChange,
  connectionStatus,
  isProcessing
}) => {
  const transparencyLevels = [
    {
      value: 'basic' as const,
      label: 'Basic',
      description: 'Show final results with basic confidence scores',
      icon: '📊'
    },
    {
      value: 'detailed' as const,
      label: 'Detailed', 
      description: 'Show reasoning steps and calibrated confidence',
      icon: '🔍'
    },
    {
      value: 'expert' as const,
      label: 'Expert',
      description: 'Full transparency with citations and verification',
      icon: '🎯'
    }
  ];

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-600 bg-green-100';
      case 'connecting': return 'text-yellow-600 bg-yellow-100';
      case 'disconnected': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getConnectionStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected': return '🟢';
      case 'connecting': return '🟡';
      case 'disconnected': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Connection Status */}
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">Connection:</span>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${getConnectionStatusColor()}`}>
            {getConnectionStatusIcon()} {connectionStatus}
          </div>
          {isProcessing && (
            <div className="animate-pulse text-blue-600">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            </div>
          )}
        </div>

        {/* Privacy Mode Toggle */}
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Privacy Mode:</label>
          <button
            onClick={() => onConfigChange({ privacyMode: !config.privacyMode })}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              config.privacyMode ? 'bg-green-600' : 'bg-gray-300'
            }`}
            disabled={isProcessing}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                config.privacyMode ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
          <span className="text-xs text-gray-600">
            {config.privacyMode ? '🔒 Local' : '☁️ Cloud'}
          </span>
        </div>

        {/* Streaming Toggle */}
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Streaming:</label>
          <button
            onClick={() => onConfigChange({ enableStreaming: !config.enableStreaming })}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              config.enableStreaming ? 'bg-blue-600' : 'bg-gray-300'
            }`}
            disabled={config.privacyMode || isProcessing}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                config.enableStreaming ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Transparency Level */}
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Transparency:</label>
          <select
            value={config.transparencyLevel}
            onChange={(e) => onConfigChange({ 
              transparencyLevel: e.target.value as 'basic' | 'detailed' | 'expert' 
            })}
            className="text-sm border border-gray-300 rounded px-2 py-1"
            disabled={isProcessing}
          >
            {transparencyLevels.map(level => (
              <option key={level.value} value={level.value}>
                {level.icon} {level.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Advanced Controls (collapsible) */}
      <details className="mt-4">
        <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
          🔧 Advanced Settings
        </summary>
        
        <div className="mt-3 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 bg-gray-50 rounded">
          
          {/* Confidence Threshold */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Confidence Threshold: {(config.confidenceThreshold * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.05"
              value={config.confidenceThreshold}
              onChange={(e) => onConfigChange({ confidenceThreshold: parseFloat(e.target.value) })}
              className="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer slider"
              disabled={isProcessing}
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Low (10%)</span>
              <span>High (100%)</span>
            </div>
          </div>

          {/* Multimodal Features */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Input Methods
            </label>
            <div className="space-y-1">
              <label className="flex items-center text-xs">
                <input
                  type="checkbox"
                  checked={config.enableVoice}
                  onChange={(e) => onConfigChange({ enableVoice: e.target.checked })}
                  className="mr-2 h-3 w-3"
                  disabled={isProcessing}
                />
                🎤 Voice Input
              </label>
              <label className="flex items-center text-xs">
                <input
                  type="checkbox"
                  checked={config.enableCamera}
                  onChange={(e) => onConfigChange({ enableCamera: e.target.checked })}
                  className="mr-2 h-3 w-3"
                  disabled={isProcessing}
                />
                📷 Camera
              </label>
              <label className="flex items-center text-xs">
                <input
                  type="checkbox"
                  checked={config.enableDocumentUpload}
                  onChange={(e) => onConfigChange({ enableDocumentUpload: e.target.checked })}
                  className="mr-2 h-3 w-3"
                  disabled={isProcessing}
                />
                📎 Documents
              </label>
            </div>
          </div>

          {/* Current Settings Info */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Current Configuration
            </label>
            <div className="text-xs text-gray-600 space-y-1">
              <div>Mode: {config.privacyMode ? '🔒 Private' : '☁️ Collective'}</div>
              <div>Transparency: {config.transparencyLevel}</div>
              <div>Features: {[
                config.enableVoice && '🎤',
                config.enableCamera && '📷', 
                config.enableDocumentUpload && '📎'
              ].filter(Boolean).join(' ') || 'Text only'}</div>
            </div>
          </div>
        </div>
      </details>

      {/* Transparency Level Description */}
      {config.transparencyLevel !== 'basic' && (
        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
          <div className="flex items-start space-x-2">
            <span className="text-lg">
              {transparencyLevels.find(l => l.value === config.transparencyLevel)?.icon}
            </span>
            <div>
              <h4 className="font-medium text-blue-900">
                {transparencyLevels.find(l => l.value === config.transparencyLevel)?.label} Transparency
              </h4>
              <p className="text-sm text-blue-700">
                {transparencyLevels.find(l => l.value === config.transparencyLevel)?.description}
              </p>
              {config.transparencyLevel === 'expert' && (
                <p className="text-xs text-blue-600 mt-1">
                  Includes citation verification, uncertainty quantification, and complete reasoning audit trails.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Privacy Mode Warning */}
      {config.privacyMode && (
        <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded">
          <div className="flex items-start space-x-2">
            <span className="text-green-600">🔒</span>
            <div>
              <h4 className="font-medium text-green-900">Privacy Mode Active</h4>
              <p className="text-sm text-green-700">
                All processing happens locally in your browser. No data is sent to external servers.
                Some advanced features may be limited in privacy mode.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};