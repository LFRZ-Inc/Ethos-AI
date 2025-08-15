import React, { useState, useEffect } from 'react';
import { Zap, Loader, CheckCircle, XCircle, Play } from 'lucide-react';
import { API_ENDPOINTS } from '../config';

interface Model70BStatus {
  available: boolean;
  initialized: boolean;
  loading: boolean;
  status: string;
  model_info?: {
    model_name: string;
    device: string;
    cuda_available: boolean;
    parameters: string;
    quantization: string;
  };
}

const Model70BStatus: React.FC = () => {
  const [status, setStatus] = useState<Model70BStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(false);

  useEffect(() => {
    loadStatus();
    // Poll status every 5 seconds
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    try {
      const response = await fetch(`${API_ENDPOINTS.models}/70b/status`);
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Failed to load 70B model status:', error);
    }
  };

  const initializeModel = async () => {
    setInitializing(true);
    try {
      const response = await fetch(`${API_ENDPOINTS.models}/70b/initialize`, {
        method: 'POST',
      });
      if (response.ok) {
        const data = await response.json();
        console.log('70B model initialization response:', data);
        // Reload status after a short delay
        setTimeout(loadStatus, 2000);
      } else {
        const error = await response.json();
        console.error('Failed to initialize 70B model:', error);
      }
    } catch (error) {
      console.error('Error initializing 70B model:', error);
    } finally {
      setInitializing(false);
    }
  };

  if (!status) {
    return (
      <div className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-100 dark:bg-gray-800 rounded-lg">
        <Loader size={16} className="animate-spin" />
        <span className="text-gray-600 dark:text-gray-400">Loading 70B status...</span>
      </div>
    );
  }

  if (!status.available) {
    return (
      <div className="flex items-center space-x-2 px-3 py-2 text-sm bg-red-100 dark:bg-red-900 rounded-lg">
        <XCircle size={16} className="text-red-600 dark:text-red-400" />
        <span className="text-red-700 dark:text-red-300">70B Model Unavailable</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2 px-3 py-2 text-sm bg-blue-100 dark:bg-blue-900 rounded-lg">
      <Zap size={16} className="text-blue-600 dark:text-blue-400" />
      
      {status.loading || initializing ? (
        <>
          <Loader size={16} className="animate-spin text-blue-600 dark:text-blue-400" />
          <span className="text-blue-700 dark:text-blue-300">
            {initializing ? 'Initializing 70B...' : 'Loading 70B...'}
          </span>
        </>
      ) : status.initialized ? (
        <>
          <CheckCircle size={16} className="text-green-600 dark:text-green-400" />
          <span className="text-green-700 dark:text-green-300">70B Ready</span>
          {status.model_info && (
            <span className="text-xs text-blue-600 dark:text-blue-400">
              ({status.model_info.parameters}, {status.model_info.quantization})
            </span>
          )}
        </>
      ) : (
        <>
          <span className="text-blue-700 dark:text-blue-300">70B Available</span>
          <button
            onClick={initializeModel}
            disabled={initializing}
            className="flex items-center space-x-1 px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded transition-colors"
          >
            <Play size={12} />
            <span>Initialize</span>
          </button>
        </>
      )}
    </div>
  );
};

export default Model70BStatus;
