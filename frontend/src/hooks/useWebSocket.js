import { useState, useEffect, useRef, useCallback } from 'react';

const useWebSocket = (url, options = {}) => {
  const [socket, setSocket] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [messageHistory, setMessageHistory] = useState([]);
  
  const {
    onOpen = () => {},
    onClose = () => {},
    onMessage = () => {},
    onError = () => {},
    shouldReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10
  } = options;

  const reconnectAttempts = useRef(0);
  const reconnectTimeoutId = useRef(null);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);
      
      ws.onopen = (event) => {
        setConnectionStatus('Connected');
        reconnectAttempts.current = 0;
        onOpen(event);
      };

      ws.onclose = (event) => {
        setConnectionStatus('Disconnected');
        onClose(event);
        
        if (shouldReconnect && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          setConnectionStatus(`Reconnecting... (${reconnectAttempts.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutId.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onmessage = (event) => {
        let message;
        try {
          message = JSON.parse(event.data);
        } catch (e) {
          message = { data: event.data, timestamp: new Date().toISOString() };
        }
        
        setLastMessage(message);
        setMessageHistory(prev => [...prev.slice(-99), message]); // Keep last 100 messages
        onMessage(message);
      };

      ws.onerror = (error) => {
        setConnectionStatus('Error');
        onError(error);
      };

      setSocket(ws);
    } catch (error) {
      setConnectionStatus('Error');
      onError(error);
    }
  }, [url, onOpen, onClose, onMessage, onError, shouldReconnect, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutId.current) {
      clearTimeout(reconnectTimeoutId.current);
    }
    if (socket) {
      socket.close();
    }
  }, [socket]);

  const sendMessage = useCallback((message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const messageToSend = typeof message === 'string' ? message : JSON.stringify(message);
      socket.send(messageToSend);
      return true;
    }
    return false;
  }, [socket]);

  useEffect(() => {
    connect();
    
    return () => {
      if (reconnectTimeoutId.current) {
        clearTimeout(reconnectTimeoutId.current);
      }
      if (socket) {
        socket.close();
      }
    };
  }, []);

  return {
    socket,
    lastMessage,
    connectionStatus,
    messageHistory,
    sendMessage,
    disconnect,
    reconnect: connect
  };
};

export default useWebSocket;