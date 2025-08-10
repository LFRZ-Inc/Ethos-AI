import React, { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Plus, MessageSquare, Settings, Trash2 } from 'lucide-react';
import { useConversationStore, Conversation } from '../stores/appStore';
import toast from 'react-hot-toast';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const { conversations, isLoading, loadConversations, deleteConversation } = useConversationStore();

  useEffect(() => {
    loadConversations();
  }, []);

  const handleNewConversation = () => {
    window.location.href = '/';
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (confirm('Are you sure you want to delete this conversation?')) {
      try {
        const response = await fetch(`http://localhost:8000/api/conversations/${id}`, {
          method: 'DELETE',
        });
        
        if (response.ok) {
          deleteConversation(id);
          toast.success('Conversation deleted');
        } else {
          throw new Error('Failed to delete conversation');
        }
      } catch (error) {
        console.error('Error deleting conversation:', error);
        toast.error('Failed to delete conversation');
      }
    }
  };

  return (
    <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={handleNewConversation}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Plus size={16} />
          <span>New Chat</span>
        </button>
      </div>

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">
            Loading conversations...
          </div>
        ) : conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">
            <MessageSquare size={32} className="mx-auto mb-2" />
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs">Start a new chat to begin</p>
          </div>
        ) : (
          <div className="p-2">
            {conversations.map((conversation) => (
              <Link
                key={conversation.id}
                to={`/chat/${conversation.id}`}
                className={`block p-3 rounded-lg mb-1 transition-colors ${
                  location.pathname === `/chat/${conversation.id}`
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">
                      {conversation.title}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {conversation.message_count} messages • {conversation.updated_at}
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(conversation.id, e)}
                    className="ml-2 p-1 text-gray-400 hover:text-red-500 transition-colors"
                    title="Delete conversation"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <Link
          to="/settings"
          className="flex items-center space-x-2 px-3 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg transition-colors"
        >
          <Settings size={16} />
          <span className="text-sm">Settings</span>
        </Link>
      </div>
    </div>
  );
};

export default Sidebar; 