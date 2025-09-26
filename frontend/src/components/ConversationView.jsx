import React, { useEffect, useRef } from 'react';
import { ArrowRight, Clock, User, Bot } from 'lucide-react';

const ConversationView = ({ messages = [], agentA = 'agent_a', agentB = 'agent_b' }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const getMessageStyle = (sender) => {
    if (sender === agentA) {
      return {
        container: 'animate-slide-in-left',
        bubble: 'bg-blue-600/20 border-blue-500/30 text-blue-100',
        avatar: 'bg-gradient-to-br from-blue-500 to-purple-500',
        name: 'AgentA (Claude)',
        icon: '🤖'
      };
    } else if (sender === agentB) {
      return {
        container: 'animate-slide-in-right ml-auto',
        bubble: 'bg-green-600/20 border-green-500/30 text-green-100',
        avatar: 'bg-gradient-to-br from-green-500 to-teal-500',
        name: 'AgentB (GPT-5)',
        icon: '⚡'
      };
    } else {
      return {
        container: 'animate-slide-in-left',
        bubble: 'bg-slate-600/20 border-slate-500/30 text-slate-100',
        avatar: 'bg-gradient-to-br from-gray-500 to-gray-600',
        name: 'System',
        icon: '⚙️'
      };
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    return new Date(timestamp).toLocaleTimeString();
  };

  const getMessageTypeDisplay = (type) => {
    const typeMap = {
      'task': '📋 Task',
      'response': '💬 Response',
      'coordination': '🤝 Coordination',
      'cross_communication': '↔️ Direct Chat',
      'implementation': '⚡ Implementation',
      'review': '👁️ Review',
      'autonomous_request': '🔄 Request',
      'autonomous_response': '✅ Completion',
      'handoff': '🔁 Handoff',
      'progress_update': '📈 Progress'
    };
    return typeMap[type] || `📝 ${type}`;
  };

  return (
    <div className="h-full flex flex-col bg-slate-800/30 rounded-lg border border-slate-700/50">
      {/* Header */}
      <div className="p-4 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white flex items-center">
            <Bot className="w-5 h-5 mr-2 text-blue-400" />
            Agent Conversations
          </h3>
          <div className="flex items-center space-x-2 text-sm text-slate-400">
            <span>🤖 AgentA</span>
            <ArrowRight className="w-4 h-4" />
            <span>⚡ AgentB</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 max-h-96"
      >
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-slate-400">
            <div className="text-center">
              <Bot className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No conversations yet. Waiting for agent communication...</p>
            </div>
          </div>
        ) : (
          messages.map((message, index) => {
            const style = getMessageStyle(message.sender);
            
            return (
              <div key={message.id || index} className={`flex max-w-sm ${style.container}`}>
                <div className="flex space-x-3">
                  {/* Avatar */}
                  <div className={`w-8 h-8 rounded-full ${style.avatar} flex items-center justify-center text-sm font-bold text-white shadow-lg flex-shrink-0`}>
                    {style.icon}
                  </div>
                  
                  {/* Message */}
                  <div className="flex-1">
                    <div className={`rounded-lg border p-3 ${style.bubble}`}>
                      {/* Message header */}
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-xs font-medium opacity-90">
                          {style.name}
                        </div>
                        <div className="text-xs opacity-60 flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {formatTimestamp(message.timestamp)}
                        </div>
                      </div>
                      
                      {/* Message type */}
                      {message.type && (
                        <div className="text-xs opacity-75 mb-2">
                          {getMessageTypeDisplay(message.type)}
                        </div>
                      )}
                      
                      {/* Message content */}
                      <div className="text-sm leading-relaxed">
                        {message.content || message.message || 'No content'}
                      </div>
                      
                      {/* Metadata */}
                      {message.metadata && Object.keys(message.metadata).length > 0 && (
                        <div className="mt-2 text-xs opacity-60 bg-black/20 rounded p-2">
                          <strong>Context:</strong> {JSON.stringify(message.metadata, null, 1)}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Status bar */}
      <div className="p-3 border-t border-slate-700/50 bg-slate-900/30">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Messages: {messages.length}</span>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>Live</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationView;