/**
 * AI-Bridge Control Cabin - Frontend Application
 * Real-time WebSocket communication with FastAPI backend
 */

class AIBridgeApp {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.currentSession = null;
        this.agents = {
            agent_a: { status: 'idle', messages: 0, lastActivity: null },
            agent_b: { status: 'idle', messages: 0, lastActivity: null }
        };

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadSystemStatus();
        this.startPeriodicUpdates();
    }

    setupEventListeners() {
        // Control buttons
        document.getElementById('startOrchestration').addEventListener('click', () => this.startOrchestration());
        document.getElementById('pauseOrchestration').addEventListener('click', () => this.pauseOrchestration());
        document.getElementById('stopOrchestration').addEventListener('click', () => this.stopOrchestration());

        // Configuration changes
        document.getElementById('reflectionMode').addEventListener('change', () => this.saveConfiguration());
        document.getElementById('maxIterations').addEventListener('change', () => this.saveConfiguration());
        document.getElementById('autoApprove').addEventListener('change', () => this.saveConfiguration());
        document.getElementById('saveConversations').addEventListener('change', () => this.saveConfiguration());

        // Auto-resize textarea
        const textarea = document.getElementById('objectiveInput');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }

    connectWebSocket() {
        try {
            const wsUrl = `ws://${window.location.host}/ws`;
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('🟢 WebSocket connected');
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.addSystemMessage('WebSocket connection established');

                // Request initial system state
                this.sendWebSocketMessage({ type: 'get_system_state' });
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onclose = () => {
                console.log('🔴 WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.addSystemMessage('WebSocket connection lost - attempting to reconnect...');

                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.connectWebSocket(), 3000);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.addSystemMessage('WebSocket error occurred');
            };

        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }

    sendWebSocketMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected, cannot send message');
        }
    }

    handleWebSocketMessage(data) {
        console.log('📨 WebSocket message received:', data);

        switch (data.type) {
            case 'system_state':
            case 'system_state_update':
                this.updateSystemState(data.data);
                break;

            case 'orchestration_started':
                this.handleOrchestrationStarted(data);
                break;

            case 'orchestration_update':
            case 'orchestrator_update':
                this.handleOrchestrationUpdate(data);
                break;

            case 'agent_status_update':
                this.updateAgentStatus(data.agent, data.data);
                break;

            case 'new_conversation':
                this.addConversationMessage(data.data);
                break;

            case 'orchestration_error':
                this.handleOrchestrationError(data.data);
                break;

            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }

    updateSystemState(systemData) {
        if (!systemData) return;

        // Update agents
        if (systemData.agents) {
            this.updateAgentStatus('agent_a', systemData.agents.agent_a);
            this.updateAgentStatus('agent_b', systemData.agents.agent_b);
        }

        // Update orchestrator metrics
        if (systemData.orchestrator) {
            this.updateMetrics(systemData.orchestrator);
            this.updateSystemStatus(systemData.orchestrator.status);
        }

        // Update conversations
        if (systemData.conversations && Array.isArray(systemData.conversations)) {
            systemData.conversations.forEach(conv => this.addConversationMessage(conv));
        }
    }

    updateAgentStatus(agentId, agentData) {
        if (!agentData) return;

        this.agents[agentId] = { ...this.agents[agentId], ...agentData };

        // Update UI elements
        const statusElement = document.getElementById(`${agentId}Status`);
        const detailStatusElement = document.getElementById(`${agentId}DetailStatus`);
        const messagesElement = document.getElementById(`${agentId}Messages`);
        const lastActivityElement = document.getElementById(`${agentId}LastActivity`);
        const cardElement = document.getElementById(agentId);

        if (statusElement) {
            statusElement.textContent = agentData.status || 'idle';
            statusElement.className = `agent-status ${agentData.status || 'idle'}`;
        }

        if (detailStatusElement) {
            const statusText = agentData.isActive ? 'Working actively' : 'Waiting for tasks';
            detailStatusElement.textContent = statusText;
        }

        if (messagesElement) {
            messagesElement.textContent = agentData.messagesCount || 0;
        }

        if (lastActivityElement && agentData.lastActivity) {
            const date = new Date(agentData.lastActivity);
            lastActivityElement.textContent = date.toLocaleTimeString();
        }

        if (cardElement) {
            cardElement.classList.toggle('active', agentData.isActive || false);
        }
    }

    updateMetrics(orchestratorData) {
        const totalMessagesEl = document.getElementById('totalMessages');
        const totalHandoffsEl = document.getElementById('totalHandoffs');
        const projectProgressEl = document.getElementById('projectProgress');
        const systemHealthEl = document.getElementById('systemHealth');

        if (totalMessagesEl) totalMessagesEl.textContent = orchestratorData.totalMessages || 0;
        if (totalHandoffsEl) totalHandoffsEl.textContent = orchestratorData.handoffs || 0;
        if (projectProgressEl) projectProgressEl.textContent = `${orchestratorData.projectProgress || 0}%`;
        if (systemHealthEl) systemHealthEl.textContent = `${orchestratorData.systemHealth || 100}%`;
    }

    updateSystemStatus(status) {
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');

        if (statusIndicator && statusText) {
            statusText.textContent = status ? status.charAt(0).toUpperCase() + status.slice(1) : 'Idle';

            statusIndicator.className = 'status-indicator';
            if (status === 'running') {
                statusIndicator.classList.add('online');
            } else if (status === 'failed' || status === 'error') {
                statusIndicator.classList.add('offline');
            } else {
                statusIndicator.classList.add('warning');
            }
        }
    }

    updateConnectionStatus(connected) {
        const wsStatus = document.getElementById('wsStatus');
        if (wsStatus) {
            wsStatus.textContent = connected ? '🟢 Connected' : '🔴 Disconnected';
            wsStatus.className = `ws-status ${connected ? 'connected' : ''}`;
        }
    }

    addSystemMessage(message) {
        this.addMessage('System', message, 'system-message');
    }

    addConversationMessage(messageData) {
        const sender = messageData.sender || messageData.type || 'Unknown';
        const content = messageData.content || messageData.message || JSON.stringify(messageData);
        const className = sender.includes('agent_a') ? 'agent-a' : sender.includes('agent_b') ? 'agent-b' : 'system-message';

        this.addMessage(sender, content, className);
    }

    addMessage(sender, content, className = '') {
        const feed = document.getElementById('conversationFeed');
        if (!feed) return;

        const messageEl = document.createElement('div');
        messageEl.className = `message ${className}`;

        const timestamp = new Date().toLocaleTimeString();
        messageEl.innerHTML = `
            <span class="timestamp">[${timestamp}] ${sender}:</span>
            <span class="content">${content}</span>
        `;

        feed.appendChild(messageEl);
        feed.scrollTop = feed.scrollHeight;

        // Limit messages to prevent memory issues
        const messages = feed.querySelectorAll('.message');
        if (messages.length > 100) {
            messages[0].remove();
        }
    }

    async startOrchestration() {
        const objective = document.getElementById('objectiveInput').value.trim();
        if (!objective) {
            alert('Please enter a development objective before starting');
            return;
        }

        this.addSystemMessage(`Starting orchestration: ${objective}`);

        try {
            // Send via WebSocket for real-time response
            this.sendWebSocketMessage({
                type: 'start_orchestration',
                objective: objective,
                config: this.getConfiguration()
            });

            // Also call REST API for backup
            const response = await fetch('/api/orchestration/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    objective: objective,
                    config: this.getConfiguration()
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to start orchestration');
            }

            const result = await response.json();
            this.currentSession = result.session_id;
            this.updateControlButtons(true);

        } catch (error) {
            console.error('Error starting orchestration:', error);
            this.addSystemMessage(`Error: ${error.message}`);
        }
    }

    async pauseOrchestration() {
        if (!this.currentSession) return;

        try {
            this.sendWebSocketMessage({ type: 'pause_orchestration' });

            const response = await fetch('/api/orchestration/pause', { method: 'POST' });
            if (response.ok) {
                this.addSystemMessage('Orchestration paused');
            }
        } catch (error) {
            console.error('Error pausing orchestration:', error);
        }
    }

    async stopOrchestration() {
        if (!this.currentSession) return;

        try {
            this.sendWebSocketMessage({ type: 'stop_orchestration' });

            const response = await fetch('/api/orchestration/stop', { method: 'POST' });
            if (response.ok) {
                this.addSystemMessage('Orchestration stopped');
                this.currentSession = null;
                this.updateControlButtons(false);
            }
        } catch (error) {
            console.error('Error stopping orchestration:', error);
        }
    }

    updateControlButtons(isRunning) {
        const startBtn = document.getElementById('startOrchestration');
        const pauseBtn = document.getElementById('pauseOrchestration');
        const stopBtn = document.getElementById('stopOrchestration');

        if (startBtn) startBtn.disabled = isRunning;
        if (pauseBtn) pauseBtn.disabled = !isRunning;
        if (stopBtn) stopBtn.disabled = !isRunning;
    }

    getConfiguration() {
        return {
            reflection_mode: document.getElementById('reflectionMode').value,
            max_iterations: parseInt(document.getElementById('maxIterations').value),
            auto_approve: document.getElementById('autoApprove').checked,
            save_conversations: document.getElementById('saveConversations').checked
        };
    }

    saveConfiguration() {
        const config = this.getConfiguration();
        localStorage.setItem('aibridge_config', JSON.stringify(config));
        console.log('Configuration saved:', config);
    }

    loadConfiguration() {
        try {
            const saved = localStorage.getItem('aibridge_config');
            if (saved) {
                const config = JSON.parse(saved);
                document.getElementById('reflectionMode').value = config.reflection_mode || 'expert';
                document.getElementById('maxIterations').value = config.max_iterations || 50;
                document.getElementById('autoApprove').checked = config.auto_approve !== false;
                document.getElementById('saveConversations').checked = config.save_conversations !== false;
            }
        } catch (error) {
            console.error('Error loading configuration:', error);
        }
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/health');
            const health = await response.json();

            this.updateSystemStatus(health.status);
            this.addSystemMessage(`System health check: ${health.status}`);

        } catch (error) {
            console.error('Error loading system status:', error);
            this.updateSystemStatus('error');
        }
    }

    startPeriodicUpdates() {
        // Update system state every 5 seconds
        setInterval(() => {
            if (this.isConnected) {
                this.sendWebSocketMessage({ type: 'get_system_state' });
            }
        }, 5000);
    }

    handleOrchestrationStarted(data) {
        this.currentSession = data.session_id || data.data?.session_id;
        this.updateControlButtons(true);
        this.addSystemMessage(`✅ Orchestration started - Session: ${this.currentSession}`);
    }

    handleOrchestrationUpdate(data) {
        if (data.data) {
            const status = data.data.status;
            const message = data.data.message || `Orchestration status: ${status}`;

            this.updateSystemStatus(status);
            this.addSystemMessage(message);

            if (status === 'completed' || status === 'stopped' || status === 'failed') {
                this.updateControlButtons(false);
                this.currentSession = null;
            }
        }
    }

    handleOrchestrationError(errorData) {
        const errorMessage = errorData.error || 'Unknown orchestration error';
        this.addSystemMessage(`❌ Error: ${errorMessage}`);
        console.error('Orchestration error:', errorData);
    }
}

// Agent control functions (global scope for button onclick)
window.pauseAgent = function(agentId) {
    if (window.app) {
        window.app.sendWebSocketMessage({
            type: 'pause_agent',
            agent: agentId
        });
        window.app.addSystemMessage(`Pausing ${agentId}`);
    }
};

window.resumeAgent = function(agentId) {
    if (window.app) {
        window.app.sendWebSocketMessage({
            type: 'resume_agent',
            agent: agentId
        });
        window.app.addSystemMessage(`Resuming ${agentId}`);
    }
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AIBridgeApp();
    window.app.loadConfiguration();
});

// Handle page visibility changes to manage WebSocket connection
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Page hidden - maintaining WebSocket connection');
    } else {
        console.log('Page visible - refreshing system state');
        if (window.app && window.app.isConnected) {
            window.app.sendWebSocketMessage({ type: 'get_system_state' });
        }
    }
});