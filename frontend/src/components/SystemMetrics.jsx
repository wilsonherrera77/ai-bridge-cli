import React from 'react';
import { Activity, Users, MessageSquare, ArrowRightLeft, Clock, Zap, Target, TrendingUp } from 'lucide-react';

const SystemMetrics = ({ 
  orchestratorStatus = 'idle',
  totalMessages = 0,
  handoffs = 0,
  avgResponseTime = 0,
  activeSession = null,
  projectProgress = 0,
  systemHealth = 100
}) => {
  const getHealthColor = (health) => {
    if (health >= 90) return 'text-green-400 bg-green-400/20';
    if (health >= 70) return 'text-yellow-400 bg-yellow-400/20';
    return 'text-red-400 bg-red-400/20';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <Activity className="w-5 h-5 text-green-400 animate-pulse" />;
      case 'paused':
        return <Clock className="w-5 h-5 text-yellow-400" />;
      case 'completed':
        return <Target className="w-5 h-5 text-green-400" />;
      case 'failed':
        return <Activity className="w-5 h-5 text-red-400" />;
      default:
        return <Activity className="w-5 h-5 text-gray-400" />;
    }
  };

  const metrics = [
    {
      label: 'Total Messages',
      value: totalMessages,
      icon: MessageSquare,
      color: 'text-blue-400',
      bg: 'bg-blue-400/20'
    },
    {
      label: 'Handoffs',
      value: handoffs,
      icon: ArrowRightLeft,
      color: 'text-purple-400',
      bg: 'bg-purple-400/20'
    },
    {
      label: 'Avg Response',
      value: `${avgResponseTime}ms`,
      icon: Zap,
      color: 'text-green-400',
      bg: 'bg-green-400/20'
    },
    {
      label: 'System Health',
      value: `${systemHealth}%`,
      icon: TrendingUp,
      color: 'text-emerald-400',
      bg: 'bg-emerald-400/20'
    }
  ];

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6 backdrop-blur-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xl shadow-lg">
            ⚡
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white">AI-Bridge Orchestrator</h3>
            <p className="text-sm text-slate-400">Central coordination system</p>
          </div>
        </div>
        
        {/* Status */}
        <div className="flex items-center space-x-2 bg-slate-900/50 px-4 py-2 rounded-full">
          {getStatusIcon(orchestratorStatus)}
          <span className="text-sm font-medium text-white capitalize">
            {orchestratorStatus}
          </span>
        </div>
      </div>

      {/* Current Session */}
      {activeSession && (
        <div className="mb-6 p-4 bg-slate-900/50 rounded-lg border border-slate-700/30">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-lg font-medium text-white">Active Session</h4>
            <span className="text-xs text-slate-400">ID: {activeSession.id?.slice(0, 8)}...</span>
          </div>
          
          <div className="space-y-2">
            <div>
              <div className="text-sm text-slate-300 mb-1">Objective:</div>
              <div className="text-sm text-slate-400 leading-relaxed">{activeSession.objective || 'No objective set'}</div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-300">Progress:</div>
                <div className="text-2xl font-bold text-white">{projectProgress}%</div>
              </div>
              
              <div className="w-32">
                <div className="bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${projectProgress}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/30">
            <div className="flex items-center justify-between">
              <div className={`w-10 h-10 rounded-full ${metric.bg} flex items-center justify-center`}>
                <metric.icon className={`w-5 h-5 ${metric.color}`} />
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-white">{metric.value}</div>
                <div className="text-xs text-slate-400">{metric.label}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Real-time Activity */}
      <div className="border-t border-slate-700/50 pt-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-300 font-medium">Real-time Activity</span>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${getHealthColor(systemHealth)} animate-pulse`}></div>
            <span className="text-xs text-slate-400">System Online</span>
          </div>
        </div>
        
        <div className="mt-3 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Agent Communication</span>
            <span className="text-green-400">● Active</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Message Bus</span>
            <span className="text-green-400">● Connected</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Workflow Engine</span>
            <span className="text-green-400">● Running</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemMetrics;