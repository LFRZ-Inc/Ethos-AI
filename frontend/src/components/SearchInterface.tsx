import React, { useState, useEffect } from 'react';
import { Search, BarChart3, TrendingUp, Filter, BookOpen, MessageSquare, Calendar, Hash } from 'lucide-react';
import { API_ENDPOINTS } from '../config';
import toast from 'react-hot-toast';

interface SearchResult {
  conversation_id: string;
  conversation_title: string;
  message_id: string;
  user_message: string;
  ai_response: string;
  timestamp: string;
  relevance_score: number;
  context: string;
  topics: string[];
  model_used: string;
}

interface MemoryAnalytics {
  total_conversations: number;
  total_messages: number;
  average_messages_per_conversation: number;
  most_active_day: string;
  most_active_hour: number;
  top_topics: [string, number][];
  conversation_timeline: any[];
  model_usage: Record<string, number>;
  average_response_length: number;
  memory_growth_rate: number;
}

interface ConversationInsights {
  total_messages: number;
  total_length: number;
  average_length: number;
  question_count: number;
  top_topics: [string, number][];
  conversation_flow: any;
  key_insights: string[];
}

const SearchInterface: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [analytics, setAnalytics] = useState<MemoryAnalytics | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingAnalytics, setIsLoadingAnalytics] = useState(false);
  const [activeTab, setActiveTab] = useState<'search' | 'analytics' | 'insights'>('search');
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [conversationInsights, setConversationInsights] = useState<ConversationInsights | null>(null);
  const [filters, setFilters] = useState({
    conversation_filter: '',
    topic_filter: '',
    date_filter: ''
  });

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setIsLoadingAnalytics(true);
    try {
      const response = await fetch(API_ENDPOINTS.analytics || '/api/memory/analytics');
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        throw new Error('Failed to load analytics');
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
      toast.error('Failed to load analytics');
    } finally {
      setIsLoadingAnalytics(false);
    }
  };

  const performSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const params = new URLSearchParams({
        query: searchQuery,
        limit: '20'
      });

      // Add filters if specified
      if (filters.conversation_filter) params.append('conversation_filter', filters.conversation_filter);
      if (filters.topic_filter) params.append('topic_filter', filters.topic_filter);
      if (filters.date_filter) params.append('date_filter', filters.date_filter);

      const response = await fetch(`${API_ENDPOINTS.search || '/api/memory/search'}?${params}`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || []);
      } else {
        throw new Error('Search failed');
      }
    } catch (error) {
      console.error('Error performing search:', error);
      toast.error('Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  const loadConversationInsights = async (conversationId: string) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.conversations}/${conversationId}/insights`);
      if (response.ok) {
        const data = await response.json();
        setConversationInsights(data);
        setSelectedConversation(conversationId);
      } else {
        throw new Error('Failed to load insights');
      }
    } catch (error) {
      console.error('Error loading conversation insights:', error);
      toast.error('Failed to load insights');
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    performSearch();
  };

  const formatRelevanceScore = (score: number) => {
    return Math.round(score * 100);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getTopicColor = (topic: string) => {
    const colors = {
      programming: 'bg-blue-100 text-blue-800',
      analysis: 'bg-green-100 text-green-800',
      content_creation: 'bg-purple-100 text-purple-800',
      visual_analysis: 'bg-pink-100 text-pink-800',
      mathematics: 'bg-orange-100 text-orange-800',
      learning: 'bg-indigo-100 text-indigo-800',
      business: 'bg-gray-100 text-gray-800',
      technology: 'bg-cyan-100 text-cyan-800'
    };
    return colors[topic as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            🧠 Memory Search & Analytics
          </h1>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('search')}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                activeTab === 'search'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              <Search size={16} />
              <span>Search</span>
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                activeTab === 'analytics'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              <BarChart3 size={16} />
              <span>Analytics</span>
            </button>
            <button
              onClick={() => setActiveTab('insights')}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                activeTab === 'insights'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              <TrendingUp size={16} />
              <span>Insights</span>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'search' && (
          <div className="h-full flex flex-col">
            {/* Search Form */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <form onSubmit={handleSearch} className="space-y-4">
                <div className="flex space-x-2">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search conversations by meaning..."
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={isSearching || !searchQuery.trim()}
                    className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {isSearching ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Searching...</span>
                      </>
                    ) : (
                      <>
                        <Search size={16} />
                        <span>Search</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Filters */}
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <Filter size={16} className="text-gray-500" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">Filters:</span>
                  </div>
                  <input
                    type="text"
                    value={filters.conversation_filter}
                    onChange={(e) => setFilters({ ...filters, conversation_filter: e.target.value })}
                    placeholder="Conversation title..."
                    className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm dark:bg-gray-800 dark:text-white"
                  />
                  <input
                    type="text"
                    value={filters.topic_filter}
                    onChange={(e) => setFilters({ ...filters, topic_filter: e.target.value })}
                    placeholder="Topic..."
                    className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </form>
            </div>

            {/* Search Results */}
            <div className="flex-1 overflow-y-auto p-4">
              {searchResults.length > 0 ? (
                <div className="space-y-4">
                  {searchResults.map((result, index) => (
                    <div
                      key={result.message_id}
                      className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                            {result.conversation_title}
                          </span>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(result.timestamp)}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                            {formatRelevanceScore(result.relevance_score)}% match
                          </span>
                          <span className="text-xs text-gray-500">
                            {result.model_used}
                          </span>
                        </div>
                      </div>

                      <div className="space-y-2">
                        {result.user_message && (
                          <div>
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">User:</span>
                            <p className="text-sm text-gray-600 dark:text-gray-400 ml-2">{result.user_message}</p>
                          </div>
                        )}
                        {result.ai_response && (
                          <div>
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Ethos:</span>
                            <p className="text-sm text-gray-600 dark:text-gray-400 ml-2">{result.ai_response}</p>
                          </div>
                        )}
                      </div>

                      {result.topics.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-1">
                          {result.topics.map((topic) => (
                            <span
                              key={topic}
                              className={`text-xs px-2 py-1 rounded ${getTopicColor(topic)}`}
                            >
                              {topic}
                            </span>
                          ))}
                        </div>
                      )}

                      {result.context && (
                        <div className="mt-3 p-2 bg-gray-100 dark:bg-gray-700 rounded text-xs text-gray-600 dark:text-gray-400">
                          <strong>Context:</strong> {result.context}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : searchQuery && !isSearching ? (
                <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                  <Search size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No results found for "{searchQuery}"</p>
                  <p className="text-sm">Try different keywords or check your filters</p>
                </div>
              ) : (
                <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                  <Search size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Search through all your conversations</p>
                  <p className="text-sm">Find anything by meaning, not just keywords</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="h-full overflow-y-auto p-4">
            {isLoadingAnalytics ? (
              <div className="text-center py-8">
                <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p>Loading analytics...</p>
              </div>
            ) : analytics ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Overview Cards */}
                <div className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg">
                  <div className="flex items-center space-x-3 mb-4">
                    <MessageSquare className="text-blue-500" size={24} />
                    <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100">Conversations</h3>
                  </div>
                  <p className="text-3xl font-bold text-blue-900 dark:text-blue-100">{analytics.total_conversations}</p>
                  <p className="text-sm text-blue-600 dark:text-blue-300">Total conversations</p>
                </div>

                <div className="bg-green-50 dark:bg-green-900/20 p-6 rounded-lg">
                  <div className="flex items-center space-x-3 mb-4">
                    <BookOpen className="text-green-500" size={24} />
                    <h3 className="text-lg font-semibold text-green-900 dark:text-green-100">Messages</h3>
                  </div>
                  <p className="text-3xl font-bold text-green-900 dark:text-green-100">{analytics.total_messages}</p>
                  <p className="text-sm text-green-600 dark:text-green-300">Total messages exchanged</p>
                </div>

                <div className="bg-purple-50 dark:bg-purple-900/20 p-6 rounded-lg">
                  <div className="flex items-center space-x-3 mb-4">
                    <TrendingUp className="text-purple-500" size={24} />
                    <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-100">Growth</h3>
                  </div>
                  <p className="text-3xl font-bold text-purple-900 dark:text-purple-100">
                    {analytics.memory_growth_rate.toFixed(1)}
                  </p>
                  <p className="text-sm text-purple-600 dark:text-purple-300">Conversations per day</p>
                </div>

                {/* Top Topics */}
                <div className="md:col-span-2 lg:col-span-3 bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Topics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {analytics.top_topics.map(([topic, count]) => (
                      <div key={topic} className="text-center">
                        <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{count}</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 capitalize">{topic.replace('_', ' ')}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Conversation Timeline */}
                <div className="md:col-span-2 lg:col-span-3 bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Conversations</h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {analytics.conversation_timeline.slice(0, 10).map((conv) => (
                      <div key={conv.id} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                        <span className="text-sm text-gray-700 dark:text-gray-300">{conv.title}</span>
                        <span className="text-xs text-gray-500">{conv.message_count} messages</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                <BarChart3 size={48} className="mx-auto mb-4 opacity-50" />
                <p>No analytics data available</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="h-full overflow-y-auto p-4">
            <div className="text-center text-gray-500 dark:text-gray-400 py-8">
              <TrendingUp size={48} className="mx-auto mb-4 opacity-50" />
              <p>Conversation Insights</p>
              <p className="text-sm">Select a conversation to see detailed insights</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchInterface; 