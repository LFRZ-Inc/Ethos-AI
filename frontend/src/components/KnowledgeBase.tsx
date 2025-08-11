import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, 
  Search, 
  BookOpen, 
  FileText, 
  Tag, 
  Plus, 
  Edit, 
  Trash2, 
  Download,
  Eye,
  Filter,
  SortAsc,
  SortDesc,
  File,
  Image,
  FileSpreadsheet,
  FileCode,
  X
} from 'lucide-react';
import { API_ENDPOINTS } from '../config';
import toast from 'react-hot-toast';

interface DocumentMetadata {
  filename: string;
  file_type: string;
  file_size: number;
  pages: number;
  word_count: number;
  processing_time: number;
  summary: string;
  keywords: string[];
  topics: string[];
  language: string;
  confidence: number;
  extracted_text: string;
  error?: string;
}

interface KnowledgeEntry {
  id: string;
  title: string;
  content: string;
  source: string;
  document_id?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  metadata?: any;
}

interface SupportedFormats {
  [key: string]: boolean;
}

const KnowledgeBase: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'documents' | 'knowledge' | 'citations'>('documents');
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [knowledgeEntries, setKnowledgeEntries] = useState<KnowledgeEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [supportedFormats, setSupportedFormats] = useState<SupportedFormats>({});
  const [selectedEntry, setSelectedEntry] = useState<KnowledgeEntry | null>(null);
  const [showAddEntry, setShowAddEntry] = useState(false);
  const [newEntry, setNewEntry] = useState({
    title: '',
    content: '',
    source: '',
    tags: [] as string[]
  });
  const [sortBy, setSortBy] = useState<'date' | 'title' | 'type'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [filterTag, setFilterTag] = useState<string>('');
  const [allTags, setAllTags] = useState<string[]>([]);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadSupportedFormats();
    loadKnowledgeEntries();
    loadTags();
  }, []);

  const loadSupportedFormats = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.documents + '/supported-formats');
      if (response.ok) {
        const data = await response.json();
        setSupportedFormats(data.supported_formats);
      }
    } catch (error) {
      console.error('Error loading supported formats:', error);
    }
  };

  const loadKnowledgeEntries = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.knowledge + '/entries');
      if (response.ok) {
        const data = await response.json();
        setKnowledgeEntries(data.entries);
      }
    } catch (error) {
      console.error('Error loading knowledge entries:', error);
      toast.error('Failed to load knowledge entries');
    } finally {
      setIsLoading(false);
    }
  };

  const loadTags = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.knowledge + '/tags');
      if (response.ok) {
        const data = await response.json();
        setAllTags(data.tags);
      }
    } catch (error) {
      console.error('Error loading tags:', error);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const fileType = file.name.split('.').pop()?.toLowerCase();
      if (fileType && supportedFormats[fileType]) {
        setSelectedFile(file);
      } else {
        toast.error(`Unsupported file type: ${fileType}`);
      }
    }
  };

  const processDocument = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(API_ENDPOINTS.documents + '/process', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const metadata: DocumentMetadata = await response.json();
        setDocuments(prev => [metadata, ...prev]);
        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        toast.success(`Document processed: ${metadata.filename}`);
      } else {
        throw new Error('Failed to process document');
      }
    } catch (error) {
      console.error('Error processing document:', error);
      toast.error('Failed to process document');
    } finally {
      setIsProcessing(false);
    }
  };

  const searchKnowledge = async () => {
    if (!searchQuery.trim()) {
      loadKnowledgeEntries();
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_ENDPOINTS.knowledge}/entries?query=${encodeURIComponent(searchQuery)}`);
      if (response.ok) {
        const data = await response.json();
        setKnowledgeEntries(data.entries);
      }
    } catch (error) {
      console.error('Error searching knowledge:', error);
      toast.error('Failed to search knowledge base');
    } finally {
      setIsLoading(false);
    }
  };

  const addKnowledgeEntry = async () => {
    if (!newEntry.title || !newEntry.content) {
      toast.error('Please fill in title and content');
      return;
    }

    try {
      const response = await fetch(API_ENDPOINTS.knowledge + '/entries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newEntry)
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        setShowAddEntry(false);
        setNewEntry({ title: '', content: '', source: '', tags: [] });
        loadKnowledgeEntries();
      } else {
        throw new Error('Failed to add knowledge entry');
      }
    } catch (error) {
      console.error('Error adding knowledge entry:', error);
      toast.error('Failed to add knowledge entry');
    }
  };

  const deleteKnowledgeEntry = async (entryId: string) => {
    if (!confirm('Are you sure you want to delete this knowledge entry?')) return;

    try {
      const response = await fetch(`${API_ENDPOINTS.knowledge}/entries/${entryId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        toast.success('Knowledge entry deleted');
        loadKnowledgeEntries();
      } else {
        throw new Error('Failed to delete knowledge entry');
      }
    } catch (error) {
      console.error('Error deleting knowledge entry:', error);
      toast.error('Failed to delete knowledge entry');
    }
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'pdf':
        return <FileText size={20} className="text-red-500" />;
      case 'docx':
        return <FileText size={20} className="text-blue-500" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <Image size={20} className="text-green-500" />;
      case 'csv':
      case 'xlsx':
        return <FileSpreadsheet size={20} className="text-orange-500" />;
      case 'txt':
      case 'md':
        return <File size={20} className="text-gray-500" />;
      default:
        return <File size={20} className="text-gray-400" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const sortedEntries = [...knowledgeEntries].sort((a, b) => {
    let comparison = 0;
    switch (sortBy) {
      case 'date':
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        break;
      case 'title':
        comparison = a.title.localeCompare(b.title);
        break;
      case 'type':
        comparison = a.source.localeCompare(b.source);
        break;
    }
    return sortOrder === 'asc' ? comparison : -comparison;
  });

  const filteredEntries = filterTag 
    ? sortedEntries.filter(entry => entry.tags.includes(filterTag))
    : sortedEntries;

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            📚 Knowledge Base & Document Processing
          </h1>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('documents')}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                activeTab === 'documents'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              <Upload size={16} />
              <span>Documents</span>
            </button>
            <button
              onClick={() => setActiveTab('knowledge')}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                activeTab === 'knowledge'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              <BookOpen size={16} />
              <span>Knowledge</span>
            </button>
            <button
              onClick={() => setActiveTab('citations')}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                activeTab === 'citations'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              <FileText size={16} />
              <span>Citations</span>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'documents' && (
          <div className="h-full flex flex-col">
            {/* Document Upload */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Upload Document
                </h2>
                
                <div className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <input
                      ref={fileInputRef}
                      type="file"
                      onChange={handleFileSelect}
                      accept=".pdf,.docx,.txt,.md,.jpg,.jpeg,.png,.gif,.csv,.json"
                      className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                    />
                    <button
                      onClick={processDocument}
                      disabled={!selectedFile || isProcessing}
                      className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      {isProcessing ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Processing...</span>
                        </>
                      ) : (
                        <>
                          <Upload size={16} />
                          <span>Process</span>
                        </>
                      )}
                    </button>
                  </div>

                  {selectedFile && (
                    <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                      <File size={16} />
                      <span>Selected: {selectedFile.name} ({formatFileSize(selectedFile.size)})</span>
                    </div>
                  )}

                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    <p>Supported formats: PDF, DOCX, TXT, MD, Images (JPG, PNG, GIF), CSV, JSON</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Processed Documents */}
            <div className="flex-1 overflow-y-auto p-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Processed Documents
              </h3>
              
              {documents.length === 0 ? (
                <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                  <Upload size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No documents processed yet</p>
                  <p className="text-sm">Upload a document to get started</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {documents.map((doc, index) => (
                    <div key={index} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          {getFileIcon(doc.file_type)}
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">{doc.filename}</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {doc.file_type.toUpperCase()} • {formatFileSize(doc.file_size)} • {doc.pages} pages • {doc.word_count} words
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {doc.processing_time.toFixed(2)}s
                          </div>
                          <div className="text-xs text-gray-500">
                            {doc.confidence * 100}% confidence
                          </div>
                        </div>
                      </div>

                      {doc.summary && (
                        <div className="mb-3">
                          <h5 className="font-medium text-gray-900 dark:text-white mb-1">Summary</h5>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{doc.summary}</p>
                        </div>
                      )}

                      {doc.keywords && doc.keywords.length > 0 && (
                        <div className="mb-3">
                          <h5 className="font-medium text-gray-900 dark:text-white mb-1">Keywords</h5>
                          <div className="flex flex-wrap gap-1">
                            {doc.keywords.map((keyword, idx) => (
                              <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded text-xs">
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {doc.topics && doc.topics.length > 0 && (
                        <div>
                          <h5 className="font-medium text-gray-900 dark:text-white mb-1">Topics</h5>
                          <div className="flex flex-wrap gap-1">
                            {doc.topics.map((topic, idx) => (
                              <span key={idx} className="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded text-xs">
                                {topic}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'knowledge' && (
          <div className="h-full flex flex-col">
            {/* Search and Controls */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-4 mb-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && searchKnowledge()}
                    placeholder="Search knowledge base..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
                  />
                </div>
                <button
                  onClick={searchKnowledge}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  Search
                </button>
                <button
                  onClick={() => setShowAddEntry(true)}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center space-x-2"
                >
                  <Plus size={16} />
                  <span>Add Entry</span>
                </button>
              </div>

              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Filter size={16} className="text-gray-500" />
                  <select
                    value={filterTag}
                    onChange={(e) => setFilterTag(e.target.value)}
                    className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm dark:bg-gray-800 dark:text-white"
                  >
                    <option value="">All Tags</option>
                    {allTags.map(tag => (
                      <option key={tag} value={tag}>{tag}</option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center space-x-2">
                  <SortAsc size={16} className="text-gray-500" />
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm dark:bg-gray-800 dark:text-white"
                  >
                    <option value="date">Date</option>
                    <option value="title">Title</option>
                    <option value="type">Type</option>
                  </select>
                  <button
                    onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                    className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                  >
                    {sortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />}
                  </button>
                </div>
              </div>
            </div>

            {/* Knowledge Entries */}
            <div className="flex-1 overflow-y-auto p-4">
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p>Loading knowledge entries...</p>
                </div>
              ) : filteredEntries.length === 0 ? (
                <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                  <BookOpen size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No knowledge entries found</p>
                  <p className="text-sm">Add your first knowledge entry to get started</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredEntries.map((entry) => (
                    <div key={entry.id} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 dark:text-white mb-1">{entry.title}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{entry.source}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {entry.content.length > 200 ? entry.content.substring(0, 200) + '...' : entry.content}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <button
                            onClick={() => setSelectedEntry(entry)}
                            className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                          >
                            <Eye size={16} />
                          </button>
                          <button
                            onClick={() => deleteKnowledgeEntry(entry.id)}
                            className="p-2 text-red-500 hover:text-red-700"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </div>

                      {entry.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {entry.tags.map((tag, idx) => (
                            <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded text-xs">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}

                      <div className="text-xs text-gray-500 mt-2">
                        Created: {new Date(entry.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'citations' && (
          <div className="h-full flex items-center justify-center text-gray-500 dark:text-gray-400">
            <div className="text-center">
              <FileText size={48} className="mx-auto mb-4 opacity-50" />
              <p>Citation System</p>
              <p className="text-sm">Coming soon...</p>
            </div>
          </div>
        )}
      </div>

      {/* Add Knowledge Entry Modal */}
      {showAddEntry && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Add Knowledge Entry
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Title
                </label>
                <input
                  type="text"
                  value={newEntry.title}
                  onChange={(e) => setNewEntry({ ...newEntry, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter title..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Content
                </label>
                <textarea
                  value={newEntry.content}
                  onChange={(e) => setNewEntry({ ...newEntry, content: e.target.value })}
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter content..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Source
                </label>
                <input
                  type="text"
                  value={newEntry.source}
                  onChange={(e) => setNewEntry({ ...newEntry, source: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter source..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={newEntry.tags.join(', ')}
                  onChange={(e) => setNewEntry({ ...newEntry, tags: e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag) })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter tags..."
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowAddEntry(false)}
                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={addKnowledgeEntry}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                Add Entry
              </button>
            </div>
          </div>
        </div>
      )}

      {/* View Knowledge Entry Modal */}
      {selectedEntry && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {selectedEntry.title}
              </h3>
              <button
                onClick={() => setSelectedEntry(null)}
                className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Source</h4>
                <p className="text-gray-600 dark:text-gray-400">{selectedEntry.source}</p>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Content</h4>
                <p className="text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{selectedEntry.content}</p>
              </div>

              {selectedEntry.tags.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-1">
                    {selectedEntry.tags.map((tag, idx) => (
                      <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded text-xs">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="text-sm text-gray-500">
                <p>Created: {new Date(selectedEntry.created_at).toLocaleString()}</p>
                <p>Updated: {new Date(selectedEntry.updated_at).toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeBase; 