/**
 * Enhanced file-based logging utility for debugging and investigation.
 * Supports File System Access API with download fallback.
 */

interface LogEntry {
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'debug';
  component?: string;
  message: string;
  data?: any;
  stack?: string;
  userId?: string;
  sessionId?: string;
}

class Logger {
  private logs: LogEntry[] = [];
  private maxLogs = 5000; // Keep last 5000 logs in memory
  private logToFile = true;
  private logLevel: 'debug' | 'info' | 'warn' | 'error' = 'info';
  private fileHandle: FileSystemFileHandle | null = null;
  private sessionId: string;
  private logBuffer: string[] = [];
  private bufferFlushInterval: number = 5000; // Flush every 5 seconds
  private bufferTimer: NodeJS.Timeout | null = null;

  constructor() {
    // Generate session ID
    this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Check if we should log to file (only in development or if explicitly enabled)
    const shouldLogToFile = import.meta.env.DEV || import.meta.env.VITE_ENABLE_FILE_LOGGING === 'true';
    this.logToFile = shouldLogToFile;
    
    // Set log level from environment
    const envLevel = import.meta.env.VITE_LOG_LEVEL?.toLowerCase();
    if (envLevel && ['debug', 'info', 'warn', 'error'].includes(envLevel)) {
      this.logLevel = envLevel as typeof this.logLevel;
    }

    // Initialize file logging if available
    if (this.logToFile && 'showSaveFilePicker' in window) {
      this.initializeFileLogging();
    }

    // Start buffer flush timer
    this.startBufferFlush();

    // Log initialization
    this.info('Logger initialized', { 
      logLevel: this.logLevel, 
      logToFile: this.logToFile,
      sessionId: this.sessionId,
      fileSystemAccessAvailable: 'showSaveFilePicker' in window
    });
  }

  private async initializeFileLogging() {
    try {
      // Try to use File System Access API
      if ('showSaveFilePicker' in window) {
        // We'll create the file on first log write
        this.debug('File System Access API available');
      }
    } catch (error) {
      this.warn('Failed to initialize file logging', { error });
    }
  }

  private shouldLog(level: LogEntry['level']): boolean {
    const levels = ['debug', 'info', 'warn', 'error'];
    return levels.indexOf(level) >= levels.indexOf(this.logLevel);
  }

  private addLog(
    level: LogEntry['level'], 
    message: string, 
    component?: string,
    data?: any, 
    error?: Error
  ) {
    if (!this.shouldLog(level)) {
      return;
    }

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      component,
      message,
      data,
      stack: error?.stack,
      sessionId: this.sessionId,
    };

    // Add to memory buffer
    this.logs.push(entry);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift(); // Remove oldest log
    }

    // Log to console
    const consoleMethod = level === 'error' ? 'error' : level === 'warn' ? 'warn' : level === 'debug' ? 'debug' : 'log';
    const prefix = `[${entry.timestamp}] [${level.toUpperCase()}]${component ? ` [${component}]` : ''}`;
    if (error) {
      console[consoleMethod](`${prefix} ${message}`, data, error);
    } else {
      console[consoleMethod](`${prefix} ${message}`, data || '');
    }

    // Add to file buffer
    if (this.logToFile) {
      this.addToFileBuffer(entry);
    }
  }

  private addToFileBuffer(entry: LogEntry) {
    const logLine = JSON.stringify(entry) + '\n';
    this.logBuffer.push(logLine);

    // If buffer gets too large, flush immediately
    if (this.logBuffer.length > 100) {
      this.flushBuffer();
    }
  }

  private startBufferFlush() {
    if (this.bufferTimer) {
      clearInterval(this.bufferTimer);
    }
    
    this.bufferTimer = setInterval(() => {
      this.flushBuffer();
    }, this.bufferFlushInterval);
  }

  private async flushBuffer() {
    if (this.logBuffer.length === 0) {
      return;
    }

    const logsToFlush = [...this.logBuffer];
    this.logBuffer = [];

    try {
      // Try File System Access API first
      if ('showSaveFilePicker' in window && this.fileHandle) {
        await this.writeToFileSystem(logsToFlush.join(''));
      } else {
        // Fallback to localStorage and download mechanism
        this.writeToLocalStorage(logsToFlush.join(''));
      }
    } catch (error) {
      console.warn('Failed to flush logs:', error);
      // Put logs back in buffer if write failed
      this.logBuffer.unshift(...logsToFlush);
    }
  }

  private async writeToFileSystem(content: string) {
    if (!this.fileHandle) {
      // Create file handle on first write
      try {
        this.fileHandle = await (window as any).showSaveFilePicker({
          suggestedName: `ui_frontend_logs_${new Date().toISOString().split('T')[0]}.jsonl`,
          types: [{
            description: 'Log files',
            accept: { 'text/plain': ['.jsonl'] }
          }]
        });
      } catch (error) {
        // User cancelled or error - fallback to localStorage
        this.fileHandle = null;
        this.writeToLocalStorage(content);
        return;
      }
    }

    try {
      const writable = await this.fileHandle.createWritable();
      await writable.write(content);
      await writable.close();
    } catch (error) {
      // If write fails, try to get new file handle
      this.fileHandle = null;
      this.writeToLocalStorage(content);
    }
  }

  private writeToLocalStorage(content: string) {
    try {
      const storageKey = 'ui_frontend_logs';
      const existingLogs = localStorage.getItem(storageKey) || '';
      const newLogs = existingLogs + content;
      
      // Keep only last 5000 lines to avoid storage issues
      const lines = newLogs.split('\n').filter(l => l.trim());
      const recentLines = lines.slice(-5000).join('\n');
      
      localStorage.setItem(storageKey, recentLines);
    } catch (e) {
      // Silently fail if localStorage is not available or full
      console.warn('Failed to write log to localStorage:', e);
    }
  }

  async downloadLogs() {
    try {
      const logs = this.logs.map(log => 
        `${log.timestamp} [${log.level.toUpperCase()}]${log.component ? ` [${log.component}]` : ''} ${log.message}${log.data ? ' ' + JSON.stringify(log.data, null, 2) : ''}${log.stack ? '\n' + log.stack : ''}`
      ).join('\n');
      
      const blob = new Blob([logs], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ui_frontend_logs_${new Date().toISOString().split('T')[0]}_${this.sessionId}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      // Also download JSONL format
      const jsonlLogs = this.logs.map(log => JSON.stringify(log)).join('\n');
      const jsonlBlob = new Blob([jsonlLogs], { type: 'application/jsonl' });
      const jsonlUrl = URL.createObjectURL(jsonlBlob);
      const jsonlA = document.createElement('a');
      jsonlA.href = jsonlUrl;
      jsonlA.download = `ui_frontend_logs_${new Date().toISOString().split('T')[0]}_${this.sessionId}.jsonl`;
      document.body.appendChild(jsonlA);
      jsonlA.click();
      document.body.removeChild(jsonlA);
      URL.revokeObjectURL(jsonlUrl);

      this.info('Logs downloaded', { logCount: this.logs.length });
    } catch (e) {
      this.error('Failed to download logs', undefined, e instanceof Error ? e : new Error(String(e)));
    }
  }

  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  clearLogs() {
    this.logs = [];
    this.logBuffer = [];
    try {
      localStorage.removeItem('ui_frontend_logs');
    } catch (e) {
      // Ignore
    }
    this.info('Logs cleared');
  }

  info(message: string, data?: any, component?: string) {
    this.addLog('info', message, component, data);
  }

  warn(message: string, data?: any, component?: string) {
    this.addLog('warn', message, component, data);
  }

  error(message: string, data?: any, component?: string, error?: Error) {
    this.addLog('error', message, component, data, error);
  }

  debug(message: string, data?: any, component?: string) {
    this.addLog('debug', message, component, data);
  }

  getSessionId(): string {
    return this.sessionId;
  }
}

// Export singleton instance
export const logger = new Logger();

// Also export for API calls
export const apiLogger = {
  logRequest: (method: string, url: string, params?: any) => {
    logger.debug(`API Request: ${method} ${url}`, params, 'API');
  },
  logResponse: (method: string, url: string, status: number, data?: any) => {
    if (status >= 400) {
      logger.error(`API Error: ${method} ${url}`, { status, data }, 'API');
    } else {
      logger.debug(`API Response: ${method} ${url}`, { status, dataLength: data ? JSON.stringify(data).length : 0 }, 'API');
    }
  },
  logError: (method: string, url: string, error: any) => {
    logger.error(`API Error: ${method} ${url}`, error, 'API', error instanceof Error ? error : new Error(String(error)));
  },
};

// Export logger instance for use in components
export default logger;
