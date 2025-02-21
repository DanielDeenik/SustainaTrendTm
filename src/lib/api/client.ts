import { config } from '$lib/config';

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

async function handleResponse(response: Response) {
  const requestId = response.headers.get('X-Request-ID');

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.message || 'An unexpected error occurred',
      response.status,
      requestId || undefined,
      errorData
    );
  }

  return response.json();
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${config.apiUrl}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
      },
    });

    return handleResponse(response);
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    throw new APIError(
      error instanceof Error ? error.message : 'Failed to connect to the server',
      0,
      undefined,
      { originalError: error }
    );
  }
}