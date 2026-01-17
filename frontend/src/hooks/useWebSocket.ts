import { useEffect, useRef } from 'react';
import { useFormStore } from '../store/formStore';
import { WSMessage } from '../types/form';

const WS_URL = 'ws://localhost:8001/api/session/ws';

export function useWebSocket(sessionId: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const { setWebSocket, updateFromWSEvent, setRecording } = useFormStore();
  const reconnectTimeoutRef = useRef<number>();

  useEffect(() => {
    if (!sessionId) return;

    const connect = () => {
      const ws = new WebSocket(`${WS_URL}/${sessionId}`);
      wsRef.current = ws;
      setWebSocket(ws);

      ws.onopen = () => {
        console.log('[WS] Connected to session:', sessionId);
      };

      ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);
          console.log('[WS] Received:', message.type, message.data);
          updateFromWSEvent(message.type, message.data);

          // Update recording status based on transcript events
          if (message.type === 'transcript') {
            if (message.data.speaker === 'assistant') {
              setRecording(false);
            }
          }
        } catch (error) {
          console.error('[WS] Failed to parse message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('[WS] Error:', error);
      };

      ws.onclose = () => {
        console.log('[WS] Disconnected from session:', sessionId);
        setWebSocket(null);

        // Attempt reconnection after 3 seconds
        reconnectTimeoutRef.current = window.setTimeout(() => {
          console.log('Attempting to reconnect...');
          connect();
        }, 3000);
      };
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        setWebSocket(null);
      }
    };
  }, [sessionId, setWebSocket, updateFromWSEvent, setRecording]);

  return wsRef.current;
}
