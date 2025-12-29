/**
 * Frontend logging utility for debugging and investigation.
 */

interface LogEntry {
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'debug';
  message: string;
  data?: any;
  stack?: string;
}

class Logger {
  private logs: LogEntry[] = [];
  private maxLogs = 1000; // Keep last 1000 logs in memory
  private logToFile = true;
  private logLevel: 'debug' | 'info' | 'warn' | 'error' = 'info';

  constructor() {
    // Check if we should log to file (only in development or if explicitly enabled)
    const shouldLogToFile = import.meta.env.DEV || import.meta.env.VITE_ENABLE_FILE_LOGGING === 'true';
    this.logToFile = shouldLogToFile;
    
    // Set log level from environment
    const envLevel = import.meta.env.VITE_LOG_LEVEL?.toLowerCase();
    if (envLevel && ['debug', 'info', 'warn', 'error'].includes(envLevel)) {
      this.logLevel = envLevel as typeof this.logLevel;
    }

    // Log initialization
    this.info('Logger initialized', { logLevel: this.logLevel, logToFile: this.logToFile });
  }

  private shouldLog(level: LogEntry['level']): boolean {
    const levels = ['debug', 'info', 'warn', 'error'];
    return levels.indexOf(level) >= levels.indexOf(this.logLevel);
  }

  private addLog(level: LogEntry['level'], message: string, data?: any, error?: Error) {
    if (!this.shouldLog(level)) {
      return;
    }

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      data,
      stack: error?.stack,
    };

    // Add to memory buffer
    this.logs.push(entry);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift(); // Remove oldest log
    }

    // Log to console
    const consoleMethod = level === 'error' ? 'error' : level === 'warn' ? 'warn' : level === 'debug' ? 'debug' : 'log';
    if (error) {
      console[consoleMethod](`[${entry.timestamp}] ${level.toUpperCase()}: ${message}`, data, error);
    } else {
      console[consoleMethod](`[${entry.timestamp}] ${level.toUpperCase()}: ${message}`, data || '');
    }

    // Log to file if enabled
    if (this.logToFile) {
      this.writeToFile(entry);
    }
  }

  private writeToFile(entry: LogEntry) {
    try {
      // Create log entry as JSON string
      const logLine = JSON.stringify(entry) + '\n';
      
      // Use localStorage as a simple file-like storage (limited to ~5-10MB)
      const storageKey = 'ui_frontend_logs';
      const existingLogs = localStorage.getItem(storageKey) || '';
      const newLogs = existingLogs + logLine;
      
      // Keep only last 1000 lines to avoid storage issues
      const lines = newLogs.split('\n').filter(l => l.trim());
      const recentLines = lines.slice(-1000).join('\n');
      
      localStorage.setItem(storageKey, recentLines);
      
      // Also try to download logs periodically (every 100 logs)
      if (this.logs.length % 100 === 0) {
        this.downloadLogs();
      }
    } catch (e) {
      // Silently fail if localStorage is not available or full
      console.warn('Failed to write log to storage:', e);
    }
  }

  downloadLogs() {
    try {
      const logs = this.logs.map(log => 
        `${log.timestamp} [${log.level.toUpperCase()}] ${log.message}${log.data ? ' ' + JSON.stringify(log.data) : ''}${log.stack ? '\n' + log.stack : ''}`
      ).join('\n');
      
      const blob = new Blob([logs], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ui_frontend_logs_${new Date().toISOString().split('T')[0]}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Failed to download logs:', e);
    }
  }

  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  clearLogs() {
    this.logs = [];
    try {
      localStorage.removeItem('ui_frontend_logs');
    } catch (e) {
      // Ignore
    }
  }

  info(message: string, data?: any) {
    this.addLog('info', message, data);
  }

  warn(message: string, data?: any) {
    this.addLog('warn', message, data);
  }

  error(message: string, data?: any, error?: Error) {
    this.addLog('error', message, data, error);
  }

  debug(message: string, data?: any) {
    this.addLog('debug', message, data);
  }
}

// Export singleton instance
export const logger = new Logger();

// Also export for API calls
export const apiLogger = {
  logRequest: (method: string, url: string, params?: any) => {
    logger.debug(`API Request: ${method} ${url}`, params);
  },
  logResponse: (method: string, url: string, status: number, data?: any) => {
    if (status >= 400) {
      logger.error(`API Error: ${method} ${url}`, { status, data });
    } else {
      logger.debug(`API Response: ${method} ${url}`, { status, dataLength: data ? JSON.stringify(data).length : 0 });
    }
  },
  logError: (method: string, url: string, error: any) => {
    logger.error(`API Error: ${method} ${url}`, error, error instanceof Error ? error : new Error(String(error)));
  },
};

