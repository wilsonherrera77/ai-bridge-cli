import React, { useState, useEffect } from 'react';
import AgentPanel from './components/AgentPanel';
import ConversationView from './components/ConversationView';
import SystemMetrics from './components/SystemMetrics';
import LogViewer from './components/LogViewer';
import useWebSocket from './hooks/useWebSocket';
import { Brain, Settings, PlayCircle, PauseCircle, RotateCw } from 'lucide-react';

function App() {
  // State management
  const [systemData, setSystemData] = useState({
    agents: {
      agent_a: {
        status: 'idle',
        lastActivity: null,
        messagesCount: 0,
        isActive: false
      },
      agent_b: {
        status: 'idle', 
        lastActivity: null,
        messagesCount: 0,
        isActive: false
      }
    },
    orchestrator: {
      status: 'idle',
      totalMessages: 0,
      handoffs: 0,
      avgResponseTime: 0,
      activeSession: null,
      projectProgress: 0,
      systemHealth: 100
    },
    conversations: [],
    logs: []
  });

  // WebSocket connection to backend
  const {
    lastMessage,
    connectionStatus,
    sendMessage,
    messageHistory
  } = useWebSocket('ws://localhost:8000/ws', {
    onMessage: (message) => {
      handleWebSocketMessage(message);
    },
    onOpen: () => {
      console.log('Connected to AI-Bridge backend');
      // Request initial system state
      sendMessage({ type: 'get_system_state' });
    },
    shouldReconnect: true,
    reconnectInterval: 3000
  });

  const handleWebSocketMessage = (message) => {
    console.log('WebSocket message received:', message);
    
    switch (message.type) {
      case 'system_state':
        setSystemData(prev => ({
          ...prev,
          ...message.data
        }));
        break;
        
      case 'agent_status_update':
        setSystemData(prev => ({
          ...prev,
          agents: {
            ...prev.agents,
            [message.agent]: {
              ...prev.agents[message.agent],
              ...message.data
            }
          }
        }));
        break;
        
      case 'new_message':
        setSystemData(prev => ({
          ...prev,
          conversations: [...prev.conversations, message.data]
        }));
        break;
        
      case 'log_entry':
        setSystemData(prev => ({
          ...prev,
          logs: [...prev.logs.slice(-999), message.data] // Keep last 1000 logs
        }));
        break;
        
      case 'orchestrator_update':
        setSystemData(prev => ({
          ...prev,
          orchestrator: {
            ...prev.orchestrator,
            ...message.data
          }
        }));
        break;
    }
  };

  // Control functions
  const handleStartSystem = () => {
    sendMessage({ type: 'start_orchestration', objective: 'Begin autonomous development session' });
  };

  const handlePauseSystem = () => {
    sendMessage({ type: 'pause_orchestration' });
  };

  const handleAgentPause = (agentId) => {
    sendMessage({ type: 'pause_agent', agent: agentId });
  };

  const handleAgentResume = (agentId) => {
    sendMessage({ type: 'resume_agent', agent: agentId });
  };

  const handleClearLogs = () => {
    setSystemData(prev => ({
      ...prev,
      logs: []
    }));
  };

  // Simulate some data if WebSocket is not connected (development mode)
  useEffect(() => {
    if (connectionStatus === 'Disconnected') {
      // Simulate some development data
      const interval = setInterval(() => {
        const mockMessage = {
          id: Date.now(),
          type: 'cross_communication',
          sender: Math.random() > 0.5 ? 'agent_a' : 'agent_b',
          recipient: Math.random() > 0.5 ? 'agent_a' : 'agent_b',
          content: [
            'Analyzing frontend requirements...',
            'Setting up API endpoints...',
            'Implementing authentication flow...',
            'Creating responsive components...',
            'Optimizing database queries...',
            'Testing integration points...'
          ][Math.floor(Math.random() * 6)],
          timestamp: new Date().toISOString(),
          metadata: { session_id: 'dev-session' }
        };

        const mockLog = {
          level: ['info', 'warning', 'success', 'error'][Math.floor(Math.random() * 4)],
          message: [
            'Agent communication established',
            'Processing user request',
            'Database connection successful',
            'Component rendering optimized',
            'API response time: 245ms'
          ][Math.floor(Math.random() * 5)],
          timestamp: new Date().toISOString(),
          source: ['AI-Bridge', 'AgentA', 'AgentB', 'Orchestrator'][Math.floor(Math.random() * 4)]
        };

        setSystemData(prev => ({
          ...prev,
          conversations: [...prev.conversations.slice(-19), mockMessage],
          logs: [...prev.logs.slice(-99), mockLog],
          orchestrator: {
            ...prev.orchestrator,
            totalMessages: prev.orchestrator.totalMessages + 1,
            projectProgress: Math.min(prev.orchestrator.projectProgress + Math.random() * 2, 100)
          }
        }));
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [connectionStatus]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-slate-700/50 bg-slate-800/30 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  AI-Bridge Control Cabin
                </h1>
                <p className="text-sm text-slate-400">Real-time supervision of autonomous AI development team</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-xs font-medium flex items-center space-x-2 ${
                connectionStatus === 'Connected' 
                  ? 'bg-green-500/20 text-green-300 border border-green-500/30' 
                  : 'bg-red-500/20 text-red-300 border border-red-500/30'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  connectionStatus === 'Connected' ? 'bg-green-400 animate-pulse' : 'bg-red-400'
                }`}></div>
                <span>{connectionStatus}</span>
              </div>
              
              <button
                onClick={systemData.orchestrator.status === 'running' ? handlePauseSystem : handleStartSystem}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  systemData.orchestrator.status === 'running'
                    ? 'bg-yellow-600/20 hover:bg-yellow-600/30 border border-yellow-600/30 text-yellow-300'
                    : 'bg-green-600/20 hover:bg-green-600/30 border border-green-600/30 text-green-300'
                }`}
              >
                {systemData.orchestrator.status === 'running' ? (
                  <>
                    <PauseCircle className="w-4 h-4" />
                    <span>Pause System</span>
                  </>
                ) : (
                  <>
                    <PlayCircle className="w-4 h-4" />
                    <span>Start System</span>
                  </>
                )}
              </button>
              
              <button className="p-2 hover:bg-slate-700/50 rounded-lg text-slate-400 hover:text-white transition-colors">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Layout */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Agent A Panel */}
          <div className="space-y-6">
            <AgentPanel
              agent="agent_a"
              status={systemData.agents.agent_a.status}
              lastActivity={systemData.agents.agent_a.lastActivity}
              messagesCount={systemData.agents.agent_a.messagesCount}
              isActive={systemData.agents.agent_a.isActive}
              onPause={() => handleAgentPause('agent_a')}
              onResume={() => handleAgentResume('agent_a')}
            />
          </div>

          {/* Central Orchestrator */}
          <div className="space-y-6">
            <SystemMetrics
              orchestratorStatus={systemData.orchestrator.status}
              totalMessages={systemData.orchestrator.totalMessages}
              handoffs={systemData.orchestrator.handoffs}
              avgResponseTime={systemData.orchestrator.avgResponseTime}
              activeSession={systemData.orchestrator.activeSession}
              projectProgress={systemData.orchestrator.projectProgress}
              systemHealth={systemData.orchestrator.systemHealth}
            />
          </div>

          {/* Agent B Panel */}
          <div className="space-y-6">
            <AgentPanel
              agent="agent_b"
              status={systemData.agents.agent_b.status}
              lastActivity={systemData.agents.agent_b.lastActivity}
              messagesCount={systemData.agents.agent_b.messagesCount}
              isActive={systemData.agents.agent_b.isActive}
              onPause={() => handleAgentPause('agent_b')}
              onResume={() => handleAgentResume('agent_b')}
            />
          </div>
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* Conversation View */}
          <ConversationView
            messages={systemData.conversations}
            agentA="agent_a"
            agentB="agent_b"
          />

          {/* Log Viewer */}
          <LogViewer
            logs={systemData.logs}
            onClearLogs={handleClearLogs}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
