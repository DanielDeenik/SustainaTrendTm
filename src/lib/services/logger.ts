import { dev } from '$app/environment';

type LogLevel = 'info' | 'warn' | 'error' | 'debug';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: any;
  requestId?: string;
  error?: Error;
}

class Logger {
  private static instance: Logger;
  private logLevel: LogLevel = dev ? 'debug' : 'info';

  private formatError(error: Error): any {
    return {
      name: error.name,
      message: error.message,
      stack: dev ? error.stack : undefined,
      ...(error instanceof Error && 'data' in error ? { data: (error as any).data } : {})
    };
  }

  private shouldLog(level: LogLevel): boolean {
    const levels: Record<LogLevel, number> = {
      debug: 0,
      info: 1,
      warn: 2,
      error: 3
    };
    return levels[level] >= levels[this.logLevel];
  }

  private logToConsole(entry: LogEntry) {
    if (!this.shouldLog(entry.level)) return;

    const logFn = entry.level === 'error' ? console.error :
                  entry.level === 'warn' ? console.warn :
                  entry.level === 'debug' ? console.debug :
                  console.log;

    const prefix = `[${entry.timestamp}] [${entry.level.toUpperCase()}]`;
    const message = `${prefix} ${entry.message}`;

    if (entry.requestId) {
      logFn(`${message} | Request ID: ${entry.requestId}`);
    } else {
      logFn(message);
    }

    if (entry.data) {
      logFn(`${prefix} Data:`, entry.data);
    }

    if (entry.error) {
      logFn(`${prefix} Error Details:`, this.formatError(entry.error));
    }
  }

  log(level: LogLevel, message: string, data?: any, requestId?: string, error?: Error) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      data,
      requestId,
      error
    };

    this.logToConsole(entry);

    // In production, we could send logs to a service here
    if (!dev && (level === 'error' || level === 'warn')) {
      // TODO: Implement remote error logging service integration
    }
  }

  debug(message: string, data?: any, requestId?: string) {
    this.log('debug', message, data, requestId);
  }

  info(message: string, data?: any, requestId?: string) {
    this.log('info', message, data, requestId);
  }

  warn(message: string, data?: any, requestId?: string) {
    this.log('warn', message, data, requestId);
  }

  error(message: string, error?: any, requestId?: string) {
    if (error instanceof Error) {
      this.log('error', message, undefined, requestId, error);
    } else {
      this.log('error', message, error, requestId);
    }
  }

  setLogLevel(level: LogLevel) {
    this.logLevel = level;
  }
}

export const logger = new Logger();