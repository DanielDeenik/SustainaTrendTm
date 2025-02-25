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

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { 
        message: response.status === 404 ? 
          'The requested resource was not found' : 
          'An unexpected error occurred'
      };
    }

    const errorMessage = errorData.message || errorData.detail || 'An unexpected error occurred';
    throw new APIError(
      errorMessage,
      response.status,
      requestId,
      errorData
    );
  }

  try {
    const data = await response.json();
    return data;
  } catch (error) {
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
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);

  try {
    const response = await fetch(`/api${endpoint}`, {
      ...options,
      signal: controller.signal,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
      },
    });

    return await handleResponse(response);
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new APIError('Request timed out', 408);
    }

    throw new APIError(
      error instanceof Error ? error.message : 'Failed to connect to the server',
      0,
      undefined,
      { originalError: error }
    );
  } finally {
    clearTimeout(timeout);
  }
}