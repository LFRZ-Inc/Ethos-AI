// API Configuration
export const API_BASE_URL = 'http://localhost:8002';

// API Endpoints
export const API_ENDPOINTS = {
  chat: `${API_BASE_URL}/api/chat`,
  conversations: `${API_BASE_URL}/api/conversations`,
  models: `${API_BASE_URL}/api/models`,
  config: `${API_BASE_URL}/api/config`,
  upload: `${API_BASE_URL}/api/upload`,
  health: `${API_BASE_URL}/health`,
} as const; 