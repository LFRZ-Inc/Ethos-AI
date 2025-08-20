import React, { useState, useEffect } from 'react';
import { Search, Globe, Settings } from 'lucide-react';
import toast from 'react-hot-toast';

interface WebSearchConfig {
  auto_search_enabled: boolean;
  show_search_indicator: boolean;
  manual_search_available: boolean;
  sources_available: {
    duckduckgo: boolean;
    wikipedia: boolean;
    news: boolean;
  };
}

interface WebSearchButtonProps {
  onWebSearch: (forceSearch: boolean) => void;
  isSearching?: boolean;
  searchPerformed?: boolean;
  sourcesUsed?: {
    duckduckgo?: boolean;
    wikipedia?: boolean;
    news?: boolean;
  };
}

const WebSearchButton: React.FC<WebSearchButtonProps> = ({
  onWebSearch,
  isSearching = false,
  searchPerformed = false,
  sourcesUsed = {}
}) => {
  const [config, setConfig] = useState<WebSearchConfig | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [autoSearchEnabled, setAutoSearchEnabled] = useState(true);
  const [buttonClicked, setButtonClicked] = useState(false);

  useEffect(() => {
    loadWebSearchConfig();
  }, []);

  const loadWebSearchConfig = async () => {
    try {
      const response = await fetch('/api/web-search/config');
      const data = await response.json();
      setConfig(data);
      setAutoSearchEnabled(data.auto_search_enabled);
    } catch (error) {
      console.error('Failed to load web search config:', error);
    }
  };

  const updateConfig = async (updates: Partial<WebSearchConfig>) => {
    try {
      const response = await fetch('/api/web-search/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });
      const data = await response.json();
      if (data.success) {
        setConfig(data.config);
        setAutoSearchEnabled(data.config.auto_search_enabled);
      }
    } catch (error) {
      console.error('Failed to update web search config:', error);
    }
  };

  const handleWebSearch = () => {
    setButtonClicked(true);
    onWebSearch(true);
    toast.success('🌐 Web search activated! Click send to use it.');
    
    // Reset button state after a short delay
    setTimeout(() => {
      setButtonClicked(false);
    }, 3000);
  };

  const toggleAutoSearch = () => {
    const newValue = !autoSearchEnabled;
    setAutoSearchEnabled(newValue);
    updateConfig({ auto_search_enabled: newValue });
  };

  const getSearchIndicator = () => {
    if (!searchPerformed || !config?.show_search_indicator) return null;

    const sources = [];
    if (sourcesUsed.duckduckgo) sources.push('DuckDuckGo');
    if (sourcesUsed.wikipedia) sources.push('Wikipedia');
    if (sourcesUsed.news) sources.push('News');

    return (
      <div className="flex items-center gap-2 text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded-md">
        <Globe size={12} />
        <span>Web search used: {sources.join(', ')}</span>
      </div>
    );
  };

  return (
    <div className="flex items-center gap-2">
      {/* Web Search Button */}
      <button
        onClick={handleWebSearch}
        disabled={isSearching}
        className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
          isSearching
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
            : buttonClicked
            ? 'bg-green-100 text-green-700 border-2 border-green-300 shadow-md'
            : 'bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200'
        }`}
        title={buttonClicked ? "Web search activated! Click send to use it." : "Search the web for current information"}
      >
        <Search size={16} className={buttonClicked ? 'animate-pulse' : ''} />
        {isSearching ? 'Searching...' : buttonClicked ? 'Web Search ✓' : 'Web Search'}
      </button>

      {/* Settings Button */}
      <button
        onClick={() => setShowSettings(!showSettings)}
        className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
        title="Web search settings"
      >
        <Settings size={16} />
      </button>

      {/* Search Indicator */}
      {getSearchIndicator()}
      
      {/* Active Web Search Indicator */}
      {buttonClicked && (
        <div className="flex items-center gap-1 text-xs text-green-600 bg-green-50 px-2 py-1 rounded-md border border-green-200 animate-pulse">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-ping"></div>
          <span>Web search active</span>
        </div>
      )}

      {/* Settings Panel */}
      {showSettings && (
        <div className="absolute top-full right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg p-4 min-w-64 z-50">
          <h3 className="font-medium text-gray-900 mb-3">Web Search Settings</h3>
          
          {/* Auto Search Toggle */}
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-sm font-medium text-gray-700">Auto Search</p>
              <p className="text-xs text-gray-500">Automatically search for current information</p>
            </div>
            <button
              onClick={toggleAutoSearch}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                autoSearchEnabled ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  autoSearchEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Available Sources */}
          <div className="mb-3">
            <p className="text-sm font-medium text-gray-700 mb-2">Available Sources</p>
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-xs">
                <div className={`w-2 h-2 rounded-full ${config?.sources_available.duckduckgo ? 'bg-green-500' : 'bg-red-500'}`} />
                <span>DuckDuckGo</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className={`w-2 h-2 rounded-full ${config?.sources_available.wikipedia ? 'bg-green-500' : 'bg-red-500'}`} />
                <span>Wikipedia</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className={`w-2 h-2 rounded-full ${config?.sources_available.news ? 'bg-green-500' : 'bg-red-500'}`} />
                <span>News API</span>
              </div>
            </div>
          </div>

          {/* Info */}
          <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
            <p>• Auto search triggers for current events, news, and factual queries</p>
            <p>• Manual search available anytime via the Web Search button</p>
            <p>• All searches are privacy-focused and not tracked</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default WebSearchButton;
