'use client';

/**
 * Regulus Collective Chat - Revolutionary Deep Chat Integration
 * 
 * This implements the Deep Chat component from Phase 1 Week 1-2:
 * - Revolutionary multimodal collective intelligence interface
 * - Real-time streaming reasoning transparency  
 * - Voice, camera, and document upload capabilities
 * - Privacy mode with browser-based LLM processing
 * - Live confidence calibration and citation display
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { DeepChat } from 'deep-chat';
import { useRegulusChat } from '../../hooks/useRegulusChat';
import { ConfidenceDisplay } from './ConfidenceDisplay';
import { ReasoningVisualization } from './ReasoningVisualization';
import { CitationPanel } from './CitationPanel';
import { TransparencyControls } from './TransparencyControls';

interface CollectiveIntelligenceConfig {
  enableStreaming: boolean;
  privacyMode: boolean;
  transparencyLevel: 'basic' | 'detailed' | 'expert';
  enableVoice: boolean;
  enableCamera: boolean;
  enableDocumentUpload: boolean;
  confidenceThreshold: number;
}

interface ReasoningStep {
  step: string;
  status: 'processing' | 'completed' | 'error';
  message: string;
  timestamp: string;
  progress: number;
  data?: any;
}

export const RegulusCollectiveChat: React.FC = () => {
  const [config, setConfig] = useState<CollectiveIntelligenceConfig>({
    enableStreaming: true,
    privacyMode: false,
    transparencyLevel: 'detailed',
    enableVoice: true,
    enableCamera: true,
    enableDocumentUpload: true,
    confidenceThreshold: 0.8
  });

  const [currentSession, setCurrentSession] = useState<string | null>(null);
  const [reasoningSteps, setReasoningSteps] = useState<ReasoningStep[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastResponse, setLastResponse] = useState<any>(null);

  // Deep Chat reference
  const chatRef = useRef<any>(null);
  
  // Custom hook for chat state management
  const {
    sendMessage,
    streamingData,
    confidence,
    citations,
    connectionStatus,
    error
  } = useRegulusChat({
    apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    enableStreaming: config.enableStreaming,
    privacyMode: config.privacyMode
  });

  // Deep Chat configuration
  const deepChatConfig = {
    // Core messaging configuration
    textInput: {
      placeholder: {
        text: "Ask me about policies, AI governance, or any corporate questions...",
        style: { color: "#606060", fontStyle: "italic" }
      },
      characterLimit: 2000,
      disabled: isProcessing
    },

    // Multimodal capabilities
    microphone: config.enableVoice ? {
      button: {
        default: {
          container: { default: { backgroundColor: "#2563eb" }},
          svg: { content: '🎤', viewBox: '0 0 24 24' }
        }
      },
      files: { acceptedFormats: ['.mp3', '.wav', '.m4a'] },
      speechToText: {
        webSpeechAPI: { language: 'en-US' }
      }
    } : false,

    camera: config.enableCamera ? {
      button: {
        default: {
          container: { default: { backgroundColor: "#059669" }},
          svg: { content: '📷', viewBox: '0 0 24 24' }
        }
      },
      files: { acceptedFormats: ['.jpg', '.jpeg', '.png', '.pdf'] }
    } : false,

    attachmentFiles: config.enableDocumentUpload ? {
      button: {
        default: {
          container: { default: { backgroundColor: "#7c3aed" }},
          svg: { content: '📎', viewBox: '0 0 24 24' }
        }
      },
      acceptedFormats: ['.pdf', '.doc', '.docx', '.txt', '.csv', '.json'],
      maxNumberOfFiles: 5,
      maxFileSize: 50000000 // 50MB
    } : false,

    // Privacy mode (browser-based LLM)
    ...(config.privacyMode && {
      webModel: {
        worker: true,
        model: 'Xenova/microsoft-DialoGPT-medium',
        config: { temperature: 0.7, max_length: 1000 }
      }
    }),

    // Streaming configuration  
    stream: config.enableStreaming ? {
      url: '/api/streaming/collective-reasoning-sse',
      method: 'GET',
      params: {
        confidence_threshold: config.confidenceThreshold
      }
    } : false,

    // Request configuration
    request: {
      url: config.enableStreaming ? 
        '/api/streaming/collective-reasoning' : 
        '/api/enhanced-search',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      additionalBodyProps: {
        enable_streaming: config.enableStreaming,
        confidence_threshold: config.confidenceThreshold,
        include_citations: true
      }
    },

    // Response processing
    responseInterceptor: (response: any) => {
      return processCollectiveResponse(response);
    },

    // UI customization
    style: {
      borderRadius: '12px',
      border: '2px solid #e5e7eb',
      boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
      backgroundColor: '#ffffff',
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif'
    },

    // Custom avatars
    avatars: {
      ai: {
        src: '/images/regulus-ai-avatar.png',
        styles: {
          avatar: {
            marginTop: '10px',
            width: '36px', 
            height: '36px',
            borderRadius: '50%',
            border: '2px solid #2563eb'
          }
        }
      },
      user: {
        src: '/images/user-avatar.png',
        styles: {
          avatar: {
            marginTop: '10px',
            width: '36px',
            height: '36px', 
            borderRadius: '50%',
            border: '2px solid #059669'
          }
        }
      }
    }
  };

  // Process collective intelligence response
  const processCollectiveResponse = useCallback((response: any) => {
    console.log('🧠 Processing collective response:', response);
    
    // Handle streaming updates
    if (response.step) {
      const reasoningStep: ReasoningStep = {
        step: response.step,
        status: response.status,
        message: response.message,
        timestamp: response.timestamp,
        progress: response.progress || 0,
        data: response.data
      };
      
      setReasoningSteps(prev => {
        const existingIndex = prev.findIndex(s => s.step === reasoningStep.step);
        if (existingIndex >= 0) {
          // Update existing step
          const updated = [...prev];
          updated[existingIndex] = reasoningStep;
          return updated;
        } else {
          // Add new step
          return [...prev, reasoningStep];
        }
      });

      // Update processing state
      setIsProcessing(response.status === 'processing');
      
      // Handle final results
      if (response.step === 'final_results' && response.data) {
        setLastResponse(response.data);
        setIsProcessing(false);
      }
      
      return null; // Don't display streaming updates as regular messages
    }
    
    // Handle regular response
    if (response.results) {
      setLastResponse(response);
      setIsProcessing(false);
      
      // Format response for display
      const formattedResponse = formatCollectiveResponse(response);
      return { text: formattedResponse };
    }
    
    return response;
  }, []);

  // Format response for display
  const formatCollectiveResponse = (response: any) => {
    const { results, confidence_analysis, approach_summary, citations = [] } = response;
    
    if (!results || results.length === 0) {
      return "I couldn't find relevant information for your query. Please try rephrasing or asking about a different topic.";
    }

    const topResult = results[0];
    const content = topResult.content;
    const confidenceScore = topResult.confidence_calibration?.calibrated_confidence || topResult.confidence_profile?.composite_confidence;
    
    let formattedResponse = content;
    
    // Add confidence information
    if (confidenceScore) {
      const confidenceLevel = confidenceScore > 0.8 ? 'High' : confidenceScore > 0.6 ? 'Medium' : 'Low';
      formattedResponse += `\n\n**Confidence:** ${confidenceLevel} (${(confidenceScore * 100).toFixed(1)}%)`;
    }
    
    // Add approach summary
    if (approach_summary) {
      const approaches = approach_summary.hybrid_search_components || ['semantic', 'lexical'];
      formattedResponse += `\n\n**Search Method:** ${approaches.join(' + ')} search`;
      
      if (approach_summary.confidence_calibration === 'enabled') {
        formattedResponse += ' with calibrated confidence';
      }
    }
    
    return formattedResponse;
  };

  // Handle configuration changes
  const updateConfig = (updates: Partial<CollectiveIntelligenceConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }));
  };

  // Handle chat ready event
  const onChatReady = () => {
    console.log('🚀 Regulus Collective Chat ready');
    
    // Send welcome message
    if (chatRef.current) {
      chatRef.current.addMessage({
        role: 'ai',
        text: `Welcome to the Regulus Collective Intelligence System! 🧠\n\nI can help you with:\n• Policy and compliance questions\n• AI governance guidance\n• Document search and analysis\n• Real-time reasoning transparency\n\n${config.privacyMode ? '🔒 Privacy mode enabled - all processing happens locally in your browser.' : '☁️ Connected to cloud-based collective intelligence.'}\n\nHow can I assist you today?`,
        customContent: {
          html: '<div class="welcome-message">Ready for transparent AI assistance!</div>'
        }
      });
    }
  };

  // Error handling
  useEffect(() => {
    if (error) {
      console.error('Chat error:', error);
      
      if (chatRef.current) {
        chatRef.current.addMessage({
          role: 'ai',
          text: `I encountered an error: ${error.message}\n\nPlease try again or contact support if the issue persists.`,
          error: true
        });
      }
    }
  }, [error]);

  return (
    <div className="regulus-collective-chat">
      {/* Transparency Controls */}
      <div className="mb-4">
        <TransparencyControls
          config={config}
          onConfigChange={updateConfig}
          connectionStatus={connectionStatus}
          isProcessing={isProcessing}
        />
      </div>

      {/* Main Chat Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Panel */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-lg p-4">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              🧠 Collective Intelligence Chat
              {config.privacyMode && (
                <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                  🔒 Private
                </span>
              )}
            </h2>
            
            <deep-chat
              ref={chatRef}
              {...deepChatConfig}
              onComponentRender={onChatReady}
              style={{
                height: '500px',
                width: '100%',
                ...deepChatConfig.style
              }}
            />
          </div>
        </div>

        {/* Transparency Panels */}
        <div className="space-y-4">
          {/* Real-time Reasoning Visualization */}
          {(config.transparencyLevel === 'detailed' || config.transparencyLevel === 'expert') && (
            <ReasoningVisualization
              steps={reasoningSteps}
              isProcessing={isProcessing}
              transparencyLevel={config.transparencyLevel}
            />
          )}

          {/* Confidence Display */}
          {lastResponse && (
            <ConfidenceDisplay
              confidence={confidence}
              lastResponse={lastResponse}
              calibrationEnabled={true}
            />
          )}

          {/* Citations Panel */}
          {citations.length > 0 && (
            <CitationPanel
              citations={citations}
              enableVerification={config.transparencyLevel === 'expert'}
            />
          )}
        </div>
      </div>

      {/* Processing Overlay */}
      {isProcessing && (
        <div className="fixed inset-0 bg-black bg-opacity-25 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 shadow-xl">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <div>
                <p className="text-lg font-semibold">🧠 Collective Intelligence Processing</p>
                <p className="text-sm text-gray-600">
                  {reasoningSteps.length > 0 
                    ? reasoningSteps[reasoningSteps.length - 1].message
                    : 'Analyzing your query...'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Development Debug Panel (only in development) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-6 p-4 bg-gray-100 rounded-lg">
          <h3 className="font-semibold mb-2">🔧 Debug Information</h3>
          <div className="text-sm text-gray-600">
            <p>Session: {currentSession}</p>
            <p>Reasoning Steps: {reasoningSteps.length}</p>
            <p>Streaming: {config.enableStreaming ? '✅' : '❌'}</p>
            <p>Privacy Mode: {config.privacyMode ? '🔒' : '☁️'}</p>
            <p>Connection: {connectionStatus}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default RegulusCollectiveChat;