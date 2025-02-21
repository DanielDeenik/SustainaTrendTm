import { config } from '$lib/config';
import { logger } from '$lib/services/logger';

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public requestId?: string,
    public data?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

const DEFAULT_TIMEOUT = 30000; // 30 seconds

async function handleResponse(response: Response) {
  const requestId = response.headers.get('X-Request-ID');
  const processTime = response.headers.get('X-Process-Time');

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { message: 'Failed to parse error response' };
    }

    const error = new APIError(
      errorData.message || 'An unexpected error occurred',
      response.status,
      requestId || undefined,
      errorData
    );

    logger.error('API request failed', { error, processTime }, requestId);
    throw error;
  }

  return response.json();
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${config.apiUrl}${endpoint}`;
  const requestId = crypto.randomUUID();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);

  try {
    logger.info(`Making API request to ${endpoint}`, {
      method: options.method || 'GET',
      requestId
    });

    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Request-ID': requestId,
        ...options.headers,
      },
    });

    const data = await handleResponse(response);
    logger.info(`API request to ${endpoint} succeeded`, {
      requestId,
      processTime: response.headers.get('X-Process-Time')
    });
    return data;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    if (error instanceof DOMException && error.name === 'AbortError') {
      const apiError = new APIError(
        'Request timed out',
        408,
        requestId,
        { originalError: error }
      );
      logger.error('API request timed out', apiError, requestId);
      throw apiError;
    }

    const apiError = new APIError(
      error instanceof Error ? error.message : 'Failed to connect to the server',
      0,
      requestId,
      { originalError: error }
    );

    logger.error('API request failed', apiError, requestId);
    throw apiError;
  } finally {
    clearTimeout(timeout);
  }
}