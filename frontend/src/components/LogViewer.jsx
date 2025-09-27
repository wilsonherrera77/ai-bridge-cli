import React, { useState, useRef, useEffect } from 'react';
import { Filter, Search, Download, Trash2, Eye, AlertCircle, Info, CheckCircle, XCircle } from 'lucide-react';

const LogViewer = ({ logs = [], onClearLogs = () => {} }) => {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isAutoScroll, setIsAutoScroll] = useState(true);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (isAutoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, isAutoScroll]);

  const getLogIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'error':
        return <XCircle className="w-4 h-4 text-red-400" />;
      case 'warning':
      case 'warn':
        return <AlertCircle className="w-4 h-4 text-yellow-400" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'info':
      default:
        return <Info className="w-4 h-4 text-blue-400" />;
    }
  };

  const getLogColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'error':
        return 'text-red-300 border-red-500/30';
      case 'warning':
      case 'warn':
        return 'text-yellow-300 border-yellow-500/30';
      case 'success':
        return 'text-green-300 border-green-500/30';
      case 'info':
      default:
        return 'text-blue-300 border-blue-500/30';
    }
  };

  const filteredLogs = logs.filter(log => {
    const matchesFilter = filter === 'all' || log.level?.toLowerCase() === filter.toLowerCase();
    const matchesSearch = !searchTerm || 
      log.message?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.source?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    return new Date(timestamp).toLocaleTimeString();
  };

  const logLevels = ['all', 'info', 'warning', 'error', 'success'];
  const logCounts = logLevels.reduce((acc, level) => {
    if (level === 'all') {
      acc[level] = logs.length;
    } else {
      acc[level] = logs.filter(log => log.level?.toLowerCase() === level.toLowerCase()).length;
    }
    return acc;
  }, {});

  const downloadLogs = () => {
    const logText = filteredLogs.map(log => 
      `[${formatTimestamp(log.timestamp)}] ${log.level?.toUpperCase() || 'INFO'} - ${log.source || 'SYSTEM'}: ${log.message}`
    ).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-bridge-logs-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg backdrop-blur-sm">
      {/* Header */}
      <div className="p-4 border-b border-slate-700/50">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center">
            <Eye className="w-5 h-5 mr-2 text-green-400" />
            Real-time System Logs
          </h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={downloadLogs}
              className="p-2 hover:bg-slate-700/50 rounded-lg text-slate-400 hover:text-white transition-colors"
              title="Download logs"
            >
              <Download className="w-4 h-4" />
            </button>
            <button
              onClick={onClearLogs}
              className="p-2 hover:bg-slate-700/50 rounded-lg text-slate-400 hover:text-red-400 transition-colors"
              title="Clear logs"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <label className="flex items-center space-x-2 text-sm text-slate-400">
              <input
                type="checkbox"
                checked={isAutoScroll}
                onChange={(e) => setIsAutoScroll(e.target.checked)}
                className="rounded border-slate-600 bg-slate-700 text-blue-500 focus:ring-blue-500"
              />
              <span>Auto-scroll</span>
            </label>
          </div>
        </div>

        {/* Filter and Search */}
        <div className="flex flex-col md:flex-row gap-4">
          {/* Log level filters */}
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-400" />
            {logLevels.map(level => (
              <button
                key={level}
                onClick={() => setFilter(level)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  filter === level
                    ? 'bg-blue-500 text-white'
                    : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700 hover:text-slate-300'
                }`}
              >
                {level} ({logCounts[level] || 0})
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Log entries */}
      <div 
        ref={scrollRef}
        className="h-64 overflow-y-auto p-4 font-mono text-sm"
      >
        {filteredLogs.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-slate-400">
            <div className="text-center">
              <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No logs to display</p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredLogs.map((log, index) => (
              <div key={index} className={`flex items-start space-x-3 p-3 rounded-lg border-l-2 bg-slate-900/30 ${getLogColor(log.level)}`}>
                <div className="flex-shrink-0 mt-0.5">
                  {getLogIcon(log.level)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center space-x-2 text-xs">
                      <span className="text-slate-300 font-medium">
                        {log.source || 'SYSTEM'}
                      </span>
                      <span className="text-slate-500">•</span>
                      <span className="text-slate-400">
                        {formatTimestamp(log.timestamp)}
                      </span>
                      {log.level && (
                        <>
                          <span className="text-slate-500">•</span>
                          <span className={`font-medium ${getLogColor(log.level).split(' ')[0]}`}>
                            {log.level.toUpperCase()}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                  
                  <div className="text-slate-200 leading-relaxed break-words">
                    {log.message || 'No message'}
                  </div>
                  
                  {/* Additional data */}
                  {log.data && (
                    <div className="mt-2 p-2 bg-slate-800/50 rounded text-xs text-slate-400 overflow-x-auto">
                      <pre>{JSON.stringify(log.data, null, 2)}</pre>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Status bar */}
      <div className="p-3 border-t border-slate-700/50 bg-slate-900/30">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>
            Showing {filteredLogs.length} of {logs.length} logs
          </span>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>Live</span>
            </div>
            <span>Updated: {logs.length > 0 ? formatTimestamp(logs[logs.length - 1]?.timestamp) : 'Never'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogViewer;