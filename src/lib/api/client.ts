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
  const requestId = response.headers.get('X-Request-ID') || undefined;
  const processTime = response.headers.get('X-Process-Time') || undefined;

  logger.debug('API Response received', {
    status: response.status,
    requestId,
    processTime
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
      if (errorData.detail && typeof errorData.detail === 'object') {
        errorData = errorData.detail;
      }
    } catch {
      errorData = { 
        message: response.status === 404 ? 
          'The requested resource was not found' : 
          'An unexpected error occurred'
      };
    }

    const errorMessage = errorData.message || errorData.detail || 'An unexpected error occurred';
    const error = new APIError(
      errorMessage,
      response.status,
      requestId,
      errorData
    );

    logger.error('API request failed', { error, processTime }, requestId);
    throw error;
  }

  try {
    const data = await response.json();
    logger.debug('API Response parsed successfully', { requestId });
    return data;
  } catch (error) {
    logger.error('Failed to parse JSON response', { error, processTime }, requestId);
    throw new APIError(
      'Invalid response format from server',
      response.status,
      requestId
    );
  }
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${config.apiUrl}${endpoint}`;
  const requestId = crypto.randomUUID();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);

  logger.debug(`Making API request`, {
    url,
    method: options.method || 'GET',
    requestId
  });

  try {
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
    logger.info(`API request succeeded`, {
      url,
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
        requestId
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