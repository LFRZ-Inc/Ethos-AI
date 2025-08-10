import React, { useState } from 'react';
import { Wrench, Search, Code, FileText } from 'lucide-react';
import { useAppStore } from '../stores/appStore';

const ToolPanel: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { useTools, setUseTools } = useAppStore();

  const tools = [
    {
      id: 'web_search',
      name: 'Web Search',
      description: 'Search the web for current information',
      icon: Search,
      enabled: useTools,
    },
    {
      id: 'code_execution',
      name: 'Code Execution',
      description: 'Execute Python code in sandboxed environment',
      icon: Code,
      enabled: useTools,
    },
    {
      id: 'file_search',
      name: 'File Search',
      description: 'Search local files for content',
      icon: FileText,
      enabled: useTools,
    },
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        title="Tools"
      >
        <Wrench size={20} />
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-1 w-64 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg z-50">
          <div className="p-4">
            <div className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              AI Tools
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Enable Tools
                </span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useTools}
                    onChange={(e) => setUseTools(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
              
              <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
                <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                  Available Tools
                </div>
                
                {tools.map((tool) => {
                  const Icon = tool.icon;
                  return (
                    <div
                      key={tool.id}
                      className={`flex items-center space-x-3 p-2 rounded ${
                        tool.enabled 
                          ? 'bg-blue-50 dark:bg-blue-900/20' 
                          : 'bg-gray-50 dark:bg-gray-700/50'
                      }`}
                    >
                      <Icon size={16} className="text-gray-500 dark:text-gray-400" />
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {tool.name}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {tool.description}
                        </div>
                      </div>
                      <div className={`w-2 h-2 rounded-full ${
                        tool.enabled 
                          ? 'bg-green-500' 
                          : 'bg-gray-300 dark:bg-gray-600'
                      }`} />
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolPanel; 