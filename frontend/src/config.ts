// API Configuration - Detect the correct backend URL
// Updated for Vercel deployment with TypeScript fixes
// Force Vercel to use latest commit with TypeScript fixes
// Deployment timestamp: 2024-12-19 23:30:00 UTC
const getApiBaseUrl = () => {
  // Check for Vite environment variable first
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // If we're on the same machine, use localhost
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8003';
  }
  
  // For Vercel deployment, use the same domain
  if (window.location.hostname.includes('vercel.app')) {
    return `https://${window.location.hostname}`;
  }
  
  // For Railway deployment, use the Railway backend URL
  if (window.location.hostname.includes('railway.app') || 
      window.location.hostname.includes('ethos-ai-backend')) {
    return 'https://ethos-ai-backend-production.up.railway.app';
  }
  
  // If accessed from phone/other device, use the PC's IP address
  // Extract the IP from the current URL and use port 8003
  const currentHost = window.location.hostname;
  return `http://${currentHost}:8003`;
};

export const API_BASE_URL = getApiBaseUrl();

// API Endpoints
export const API_ENDPOINTS = {
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
} as const; 