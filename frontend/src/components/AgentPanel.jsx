import React from 'react';
import { Activity, Bot, CheckCircle, Clock, AlertCircle } from 'lucide-react';

const AgentPanel = ({ 
  agent, 
  status = 'idle', 
  lastActivity = null, 
  messagesCount = 0, 
  isActive = false,
  onPause = () => {},
  onResume = () => {} 
}) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'active':
      case 'working':
        return <Activity className="w-4 h-4 text-green-400 animate-pulse" />;
      case 'thinking':
        return <Clock className="w-4 h-4 text-yellow-400 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Bot className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'active':
      case 'working':
        return 'bg-green-500/20 border-green-500/30 text-green-300';
      case 'thinking':
        return 'bg-yellow-500/20 border-yellow-500/30 text-yellow-300';
      case 'completed':
        return 'bg-green-500/20 border-green-500/30 text-green-300';
      case 'error':
        return 'bg-red-500/20 border-red-500/30 text-red-300';
      default:
        return 'bg-gray-500/20 border-gray-500/30 text-gray-300';
    }
  };

  const agentInfo = {
    agent_a: {
      name: 'AgentA (Claude)',
      role: 'Frontend Specialist',
      color: 'from-blue-500 to-purple-500',
      avatar: '🤖'
    },
    agent_b: {
      name: 'AgentB (GPT-5)',
      role: 'Backend Specialist', 
      color: 'from-green-500 to-teal-500',
      avatar: '⚡'
    }
  }[agent] || {
    name: 'Unknown Agent',
    role: 'Specialist',
    color: 'from-gray-500 to-gray-600',
    avatar: '❓'
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4 backdrop-blur-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${agentInfo.color} flex items-center justify-center text-xl font-bold text-white shadow-lg`}>
            {agentInfo.avatar}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">{agentInfo.name}</h3>
            <p className="text-sm text-slate-400">{agentInfo.role}</p>
          </div>
        </div>
        
        {/* Status indicator */}
        <div className={`px-3 py-1 rounded-full border flex items-center space-x-2 ${getStatusColor()}`}>
          {getStatusIcon()}
          <span className="text-xs font-medium capitalize">{status}</span>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-slate-900/50 rounded-lg p-3">
          <div className="text-2xl font-bold text-white">{messagesCount}</div>
          <div className="text-xs text-slate-400">Messages</div>
        </div>
        <div className="bg-slate-900/50 rounded-lg p-3">
          <div className="text-2xl font-bold text-white">
            {lastActivity ? new Date(lastActivity).toLocaleTimeString() : '--:--'}
          </div>
          <div className="text-xs text-slate-400">Last Activity</div>
        </div>
      </div>

      {/* Activity Indicator */}
      {isActive && (
        <div className="relative">
          <div className="flex items-center space-x-2 text-green-400">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse-dot"></div>
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse-dot" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse-dot" style={{ animationDelay: '0.4s' }}></div>
            <span className="text-xs ml-2">Processing...</span>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex space-x-2 mt-4">
        {status === 'active' || status === 'working' ? (
          <button
            onClick={onPause}
            className="flex-1 px-3 py-2 bg-yellow-600/20 hover:bg-yellow-600/30 border border-yellow-600/30 text-yellow-300 rounded-lg text-sm font-medium transition-colors"
          >
            Pause
          </button>
        ) : (
          <button
            onClick={onResume}
            className="flex-1 px-3 py-2 bg-green-600/20 hover:bg-green-600/30 border border-green-600/30 text-green-300 rounded-lg text-sm font-medium transition-colors"
          >
            Resume
          </button>
        )}
        <button className="px-3 py-2 bg-slate-700/50 hover:bg-slate-700/70 border border-slate-600/50 text-slate-300 rounded-lg text-sm font-medium transition-colors">
          View Details
        </button>
      </div>
    </div>
  );
};

export default AgentPanel;