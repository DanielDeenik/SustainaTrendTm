// Environment stub for application
export const browser = typeof window !== 'undefined';
export const dev = process.env.NODE_ENV === 'development';
export const building = false;

// Match SvelteKit's env handling
export const platform = browser ? 'browser' : 'server';
export const version = '1.0.0';