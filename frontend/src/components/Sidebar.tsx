import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Plus, MessageSquare, Settings, Trash2, Edit2, Check, X, Search, BarChart3, Bot, BookOpen } from 'lucide-react';
import { useConversationStore, Conversation } from '../stores/appStore';
import toast from 'react-hot-toast';
import DeleteConfirmationModal from './DeleteConfirmationModal';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const { conversations, isLoading, loadConversations, deleteConversation, updateConversation } = useConversationStore();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState<Conversation | null>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  const handleNewConversation = () => {
    window.location.href = '/';
  };

    const handleDeleteConversation = async (conversation: Conversation, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setConversationToDelete(conversation);
    setDeleteModalOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!conversationToDelete) return;
    
    try {
      const response = await fetch(`http://localhost:8003/api/conversations/${conversationToDelete.id}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        deleteConversation(conversationToDelete.id);
        toast.success('Conversation permanently deleted from Ethos AI memory');
      } else {
        throw new Error('Failed to delete conversation');
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
      toast.error('Failed to delete conversation');
      throw error;
    }
  };

  const handleEditConversation = (conversation: Conversation, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setEditingId(conversation.id);
    setEditTitle(conversation.title);
  };

  const handleSaveEdit = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8003/api/conversations/${id}/title`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: editTitle }),
      });
      
      if (response.ok) {
        updateConversation(id, { title: editTitle });
        setEditingId(null);
        setEditTitle('');
        toast.success('Conversation title updated');
      } else {
        throw new Error('Failed to update conversation title');
      }
    } catch (error) {
      console.error('Error updating conversation title:', error);
      toast.error('Failed to update conversation title');
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
  };

  return (
    <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 space-y-2">
        <button
          onClick={handleNewConversation}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Plus size={16} />
          <span>New Chat</span>
        </button>
        
        {/* Search, Analytics, and Automation Buttons */}
        <div className="flex space-x-2">
          <button
            onClick={() => window.open('/search', '_blank')}
            className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            <Search size={14} />
            <span className="text-xs">Search</span>
          </button>
          <button
            onClick={() => window.open('/analytics', '_blank')}
            className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            <BarChart3 size={14} />
            <span className="text-xs">Analytics</span>
          </button>
        </div>
        
                         {/* Task Automation Button */}
                 <button
                   onClick={() => window.open('/automation', '_blank')}
                   className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-900/40 transition-colors"
                 >
                   <Bot size={14} />
                   <span className="text-xs">Task Automation</span>
                 </button>
                 
                 {/* Knowledge Base Button */}
                 <button
                   onClick={() => window.open('/knowledge', '_blank')}
                   className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-200 dark:hover:bg-green-900/40 transition-colors"
                 >
                   <BookOpen size={14} />
                   <span className="text-xs">Knowledge Base</span>
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
                    {editingId === conversation.id ? (
                      <div className="flex items-center space-x-1">
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          className="flex-1 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded px-2 py-1"
                          onKeyPress={(e) => e.key === 'Enter' && handleSaveEdit(conversation.id)}
                          autoFocus
                        />
                        <button
                          onClick={() => handleSaveEdit(conversation.id)}
                          className="p-1 text-green-500 hover:text-green-600"
                          title="Save"
                        >
                          <Check size={12} />
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="p-1 text-gray-500 hover:text-gray-600"
                          title="Cancel"
                        >
                          <X size={12} />
                        </button>
                      </div>
                    ) : (
                      <div className="text-sm font-medium truncate">
                        {conversation.title}
                      </div>
                    )}
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {conversation.message_count} messages • {conversation.updated_at}
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    {editingId !== conversation.id && (
                      <button
                        onClick={(e) => handleEditConversation(conversation, e)}
                        className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                        title="Edit conversation title"
                      >
                        <Edit2 size={14} />
                      </button>
                    )}
                    <button
                      onClick={(e) => handleDeleteConversation(conversation, e)}
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      title="Delete conversation"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
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

      {/* Delete Confirmation Modal */}
      {conversationToDelete && (
        <DeleteConfirmationModal
          isOpen={deleteModalOpen}
          onClose={() => {
            setDeleteModalOpen(false);
            setConversationToDelete(null);
          }}
          onConfirm={handleConfirmDelete}
          conversation={conversationToDelete}
        />
      )}
    </div>
  );
};

export default Sidebar; 