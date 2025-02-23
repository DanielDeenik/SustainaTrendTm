// Frontend configuration
export const config = {
  apiUrl: import.meta.env.VITE_BACKEND_URL || 'http://0.0.0.0:8000',
  development: import.meta.env.DEV || false,
  version: '1.0.0'
};