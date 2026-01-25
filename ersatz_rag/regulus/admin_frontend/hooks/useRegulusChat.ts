'use client';

/**
 * Regulus Chat Hook - State management for collective intelligence chat
 * 
 * This implements the React hook from Phase 1 Week 1-2:
 * - Streaming connection management
 * - Real-time confidence tracking  
 * - Citation data handling
 * - Transparency state management
 * - WebSocket and SSE connection handling
 */

import { useState, useEffect, useRef, useCallback } from 'react';

interface UseRegulusChatConfig {
  apiBaseUrl: string;
  enableStreaming: boolean;
  privacyMode: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

interface ChatState {
  isConnected: boolean;
  isProcessing: boolean;
  error: Error | null;
  sessionId: string | null;
}

interface StreamingData {
  step: string;
  status: string;
  message: string;
  progress: number;
  data?: any;
}

interface ConfidenceData {
  originalConfidence: number;
  calibratedConfidence: number;
  uncertaintyEstimate: number;
  confidenceInterval: [number, number];
  calibrationQuality: string;
}

interface CitationData {
  nodeId: string;
  documentTitle: string;
  sectionTitle?: string;
  pageNumber: number;
  contentExcerpt: string;
  relevanceScore: number;
  citationText: string;
}

export const useRegulusChat = (config: UseRegulusChatConfig) => {
  // Core state
  const [chatState, setChatState] = useState<ChatState>({
    isConnected: false,
    isProcessing: false,
    error: null,
    sessionId: null
  });

  // Data state
  const [streamingData, setStreamingData] = useState<StreamingData | null>(null);
  const [confidence, setConfidence] = useState<ConfidenceData | null>(null);
  const [citations, setCitations] = useState<CitationData[]>([]);
  const [reasoningHistory, setReasoningHistory] = useState<StreamingData[]>([]);

  // Connection references
  const eventSourceRef = useRef<EventSource | null>(null);
  const websocketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef<number>(0);

  const maxReconnectAttempts = config.reconnectAttempts || 5;
  const reconnectDelay = config.reconnectDelay || 3000;

  // Generate session ID
  const generateSessionId = useCallback(() => {
    return `chat_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
  }, []);

  // Initialize connection
  const initializeConnection = useCallback(() => {
    const sessionId = generateSessionId();
    
    setChatState(prev => ({
      ...prev,
      sessionId,
      isConnected: false,
      error: null
    }));

    // Initialize based on configuration
    if (config.enableStreaming && !config.privacyMode) {
      if (config.apiBaseUrl.includes('ws://') || config.apiBaseUrl.includes('wss://')) {
        initializeWebSocket(sessionId);
      } else {
        initializeEventSource(sessionId);
      }
    } else {
      // For privacy mode or non-streaming, mark as connected for regular HTTP requests
      setChatState(prev => ({ ...prev, isConnected: true }));
    }
  }, [config]);

  // Initialize Server-Sent Events connection
  const initializeEventSource = useCallback((sessionId: string) => {
    try {
      const sseUrl = `${config.apiBaseUrl}/api/streaming/collective-reasoning-sse`;
      const eventSource = new EventSource(sseUrl);

      eventSource.onopen = () => {
        console.log('🔌 SSE connection established');
        setChatState(prev => ({ ...prev, isConnected: true, error: null }));
        reconnectAttempts.current = 0;
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleStreamingUpdate(data);
        } catch (error) {
          console.error('SSE message parsing error:', error);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        setChatState(prev => ({ ...prev, isConnected: false }));
        
        eventSource.close();
        attemptReconnection(sessionId);
      };

      eventSourceRef.current = eventSource;

    } catch (error) {
      console.error('Failed to initialize SSE:', error);
      setChatState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error('SSE initialization failed') 
      }));
    }
  }, [config.apiBaseUrl]);

  // Initialize WebSocket connection
  const initializeWebSocket = useCallback((sessionId: string) => {
    try {
      const wsUrl = `${config.apiBaseUrl.replace('http', 'ws')}/api/ws/collective-reasoning/${sessionId}`;
      const websocket = new WebSocket(wsUrl);

      websocket.onopen = () => {
        console.log('🔌 WebSocket connection established');
        setChatState(prev => ({ ...prev, isConnected: true, error: null }));
        reconnectAttempts.current = 0;
        
        // Send initial connection message
        websocket.send(JSON.stringify({
          type: 'connection_init',
          session_id: sessionId,
          timestamp: new Date().toISOString(),
          data: { client_type: 'regulus_chat' }
        }));
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('WebSocket message parsing error:', error);
        }
      };

      websocket.onclose = (event) => {
        console.log('🔌 WebSocket connection closed:', event.code, event.reason);
        setChatState(prev => ({ ...prev, isConnected: false }));
        
        if (event.code !== 1000) { // Not a normal closure
          attemptReconnection(sessionId);
        }
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setChatState(prev => ({ 
          ...prev, 
          error: new Error('WebSocket connection error') 
        }));
      };

      websocketRef.current = websocket;

    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
      setChatState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error('WebSocket initialization failed') 
      }));
    }
  }, [config.apiBaseUrl]);

  // Handle streaming updates (SSE)
  const handleStreamingUpdate = useCallback((data: any) => {
    console.log('📡 Streaming update:', data);
    
    setStreamingData(data);
    setReasoningHistory(prev => [...prev, data]);

    // Update processing state
    setChatState(prev => ({
      ...prev,
      isProcessing: data.status === 'processing'
    }));

    // Handle specific update types
    switch (data.step) {
      case 'confidence_calibration':
        if (data.data?.confidence_calibration) {
          setConfidence({
            originalConfidence: data.data.confidence_calibration.original_confidence,
            calibratedConfidence: data.data.confidence_calibration.calibrated_confidence,
            uncertaintyEstimate: data.data.confidence_calibration.uncertainty_estimate,
            confidenceInterval: data.data.confidence_calibration.confidence_interval,
            calibrationQuality: data.data.confidence_calibration.calibration_quality
          });
        }
        break;

      case 'final_results':
        if (data.data?.results) {
          // Extract citations from results
          const extractedCitations: CitationData[] = data.data.results.map((result: any, index: number) => ({
            nodeId: result.node_id || `result_${index}`,
            documentTitle: result.metadata?.document_title || 'Unknown Document',
            sectionTitle: result.metadata?.title || result.metadata?.section_title,
            pageNumber: result.metadata?.page_ranges?.[0] || 1,
            contentExcerpt: result.content?.substring(0, 200) + '...',
            relevanceScore: result.search_scores?.hybrid_score || result.confidence_profile?.composite_confidence || 0.5,
            citationText: `[${result.metadata?.document_title || 'Unknown'}, p. ${result.metadata?.page_ranges?.[0] || 1}]`
          }));
          
          setCitations(extractedCitations);
        }
        break;
    }
  }, []);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((data: any) => {
    console.log('📬 WebSocket message:', data);
    
    switch (data.type) {
      case 'connection_established':
        console.log('✅ WebSocket connection confirmed');
        break;
        
      case 'reasoning_update':
        handleStreamingUpdate(data.data);
        break;
        
      case 'error':
        setChatState(prev => ({ 
          ...prev, 
          error: new Error(data.data?.error || 'WebSocket error') 
        }));
        break;
        
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }, [handleStreamingUpdate]);

  // Attempt reconnection
  const attemptReconnection = useCallback((sessionId: string) => {
    if (reconnectAttempts.current >= maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      setChatState(prev => ({ 
        ...prev, 
        error: new Error('Connection lost - please refresh the page') 
      }));
      return;
    }

    reconnectAttempts.current++;
    console.log(`Attempting reconnection ${reconnectAttempts.current}/${maxReconnectAttempts}`);

    reconnectTimeoutRef.current = setTimeout(() => {
      if (websocketRef.current?.readyState === WebSocket.CLOSED || 
          eventSourceRef.current?.readyState === EventSource.CLOSED) {
        initializeConnection();
      }
    }, reconnectDelay);
  }, [maxReconnectAttempts, reconnectDelay, initializeConnection]);

  // Send message
  const sendMessage = useCallback(async (query: string, options?: any) => {
    if (!chatState.isConnected && !config.privacyMode) {
      throw new Error('Not connected to server');
    }

    setChatState(prev => ({ ...prev, isProcessing: true }));
    setStreamingData(null);
    setReasoningHistory([]);

    try {
      if (config.enableStreaming && websocketRef.current?.readyState === WebSocket.OPEN) {
        // Send via WebSocket
        websocketRef.current.send(JSON.stringify({
          type: 'start_reasoning',
          session_id: chatState.sessionId,
          timestamp: new Date().toISOString(),
          data: {
            query,
            top_k: options?.topK || 10,
            confidence_threshold: options?.confidenceThreshold || 0.8,
            enable_citations: options?.enableCitations !== false,
            streaming_speed: options?.streamingSpeed || 'normal'
          }
        }));
        
        return; // Response will come via WebSocket
      } else {
        // Send via HTTP
        const response = await fetch(`${config.apiBaseUrl}/api/streaming/enhanced-search`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            query,
            top_k: options?.topK || 10,
            enable_streaming: config.enableStreaming && !config.privacyMode,
            confidence_threshold: options?.confidenceThreshold || 0.8,
            include_citations: options?.enableCitations !== false
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        // Process the result as if it came from streaming
        handleStreamingUpdate({
          step: 'final_results',
          status: 'completed',
          message: 'Query completed',
          progress: 1.0,
          data: result
        });

        return result;
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setChatState(prev => ({ 
        ...prev, 
        isProcessing: false,
        error: error instanceof Error ? error : new Error('Failed to send message') 
      }));
      throw error;
    }
  }, [chatState.isConnected, chatState.sessionId, config, handleStreamingUpdate]);

  // Clear error
  const clearError = useCallback(() => {
    setChatState(prev => ({ ...prev, error: null }));
  }, []);

  // Disconnect
  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    setChatState(prev => ({ ...prev, isConnected: false }));
  }, []);

  // Initialize connection on mount
  useEffect(() => {
    initializeConnection();
    
    return () => {
      disconnect();
    };
  }, [initializeConnection, disconnect]);

  // Return hook interface
  return {
    // State
    isConnected: chatState.isConnected,
    isProcessing: chatState.isProcessing,
    error: chatState.error,
    sessionId: chatState.sessionId,
    connectionStatus: chatState.isConnected ? 'connected' : 'disconnected',
    
    // Data
    streamingData,
    confidence,
    citations,
    reasoningHistory,
    
    // Actions
    sendMessage,
    clearError,
    disconnect,
    reconnect: initializeConnection
  };
};