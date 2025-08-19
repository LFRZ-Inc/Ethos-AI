// API Configuration - Detect the correct backend URL
// Updated for Vercel deployment with TypeScript fixes
// Force Vercel to use latest commit with TypeScript fixes
// Deployment timestamp: 2024-12-19 23:30:00 UTC
// CACHE BUST: 2024-12-19 23:45:00 UTC - Force LocalTunnel for Vercel
const getApiBaseUrl = () => {
  // Check for Vite environment variable first
  if (import.meta.env.VITE_API_BASE_URL) {
    console.log('Using VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Force Railway for Vercel deployment (Railway proxies to LocalTunnel)
  if (window.location.hostname.includes('vercel.app')) {
    console.log('Vercel detected - using Railway proxy to LocalTunnel');
    return 'https://cooking-ethos-ai-production-6bfd.up.railway.app';
  }
  
  // If we're on the same machine, use localhost
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('Using localhost backend');
    return 'http://127.0.0.1:8000';
  }
  

  
  // For Railway deployment, use LocalTunnel backend for full functionality
  if (window.location.hostname.includes('railway.app') || 
      window.location.hostname.includes('ethos-ai-backend')) {
    console.log('Using LocalTunnel backend for Railway deployment');
    return 'https://ethos-ai-test.loca.lt';
  }
  
  // Default fallback to LocalTunnel backend for full functionality
  console.log('Using LocalTunnel backend as fallback');
  return 'https://ethos-ai-test.loca.lt';
};

export const API_BASE_URL = getApiBaseUrl();

// Force LocalTunnel for Vercel deployment - override any cached values
if (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app')) {
  console.log('OVERRIDE: Forcing LocalTunnel URL for Vercel deployment');
  // This will ensure we always use LocalTunnel for Vercel
}

// API Endpoints
export const API_ENDPOINTS = {
  // Legacy endpoints
  chat: `${API_BASE_URL}/api/chat`,
  conversations: `${API_BASE_URL}/api/conversations`,
  models: `${API_BASE_URL}/api/models`,
  config: `${API_BASE_URL}/api/config`,
  upload: `${API_BASE_URL}/api/upload`,
  health: `${API_BASE_URL}/health`,
  search: `${API_BASE_URL}/api/memory/search`,
  analytics: `${API_BASE_URL}/api/memory/analytics`,
  insights: `${API_BASE_URL}/api/conversations`,
  tasks: `${API_BASE_URL}/api/tasks`,
  documents: `${API_BASE_URL}/api/documents`,
  knowledge: `${API_BASE_URL}/api/knowledge`,
  citations: `${API_BASE_URL}/api/citations`,
  
  // New client-side storage endpoints
  clientChat: `${API_BASE_URL}/api/client/chat`,
  clientMemorySave: `${API_BASE_URL}/api/client/memory/save`,
  clientStorageInfo: `${API_BASE_URL}/api/client/storage/info`,
  ramUsage: `${API_BASE_URL}/api/ram/usage`,
  modelsStatus: `${API_BASE_URL}/api/models/status`,
} as const; 