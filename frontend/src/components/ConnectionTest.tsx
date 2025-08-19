import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config';

const ConnectionTest: React.FC = () => {
  const [backendUrl, setBackendUrl] = useState<string>('');
  const [healthStatus, setHealthStatus] = useState<string>('Testing...');
  const [modelsStatus, setModelsStatus] = useState<string>('Testing...');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    // Get the backend URL being used
    setBackendUrl(API_ENDPOINTS.health.replace('/health', ''));
    
    // Test health endpoint
    fetch(API_ENDPOINTS.health)
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error(`Health check failed: ${response.status}`);
      })
      .then(data => {
        setHealthStatus(`✅ Health: ${data.status} (${data.version})`);
      })
      .catch(err => {
        setHealthStatus(`❌ Health: ${err.message}`);
        setError(err.message);
      });

    // Test models status endpoint
    fetch(API_ENDPOINTS.modelsStatus)
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error(`Models status failed: ${response.status}`);
      })
      .then(data => {
        const availableModels = Object.values(data.models).filter((model: any) => model.available).length;
        const totalModels = Object.keys(data.models).length;
        setModelsStatus(`✅ Models: ${availableModels}/${totalModels} available`);
      })
      .catch(err => {
        setModelsStatus(`❌ Models: ${err.message}`);
      });
  }, []);

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Connection Test
      </h3>
      
      <div className="space-y-3">
        <div>
          <span className="text-sm text-gray-500 dark:text-gray-400">Backend URL:</span>
          <span className="ml-2 text-sm font-mono text-blue-600 dark:text-blue-400">
            {backendUrl}
          </span>
        </div>
        
        <div>
          <span className="text-sm text-gray-500 dark:text-gray-400">Health Check:</span>
          <span className="ml-2 text-sm">{healthStatus}</span>
        </div>
        
        <div>
          <span className="text-sm text-gray-500 dark:text-gray-400">Models Status:</span>
          <span className="ml-2 text-sm">{modelsStatus}</span>
        </div>
        
        {error && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
            <p className="text-sm text-red-700 dark:text-red-300">
              Error: {error}
            </p>
            <p className="text-xs text-red-600 dark:text-red-400 mt-1">
              Make sure LocalTunnel is running: lt --port 8000 --subdomain ethos-ai-test
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConnectionTest;
