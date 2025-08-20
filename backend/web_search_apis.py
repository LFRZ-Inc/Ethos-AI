"""
Web Search APIs and RAG System for Ethos AI
Integrates DuckDuckGo, News API, and Wikipedia for current information
"""

import requests
import json
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
from urllib.parse import quote_plus
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Structured search result"""
    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float = 0.0

@dataclass
class NewsArticle:
    """Structured news article"""
    title: str
    description: str
    url: str
    published_at: str
    source: str
    content: str = ""

@dataclass
class WikiPage:
    """Structured Wikipedia page"""
    title: str
    summary: str
    url: str
    categories: List[str]
    links: List[str] = None

class WebSearchAPIs:
    """Comprehensive web search and information retrieval system"""
    
    def __init__(self):
        self.news_api_key = None  # Will be set from environment
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Ethos-AI/1.0 (Educational AI Assistant)'
        })
        
    def set_news_api_key(self, api_key: str):
        """Set News API key"""
        self.news_api_key = api_key
        
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search using DuckDuckGo Instant Answer API
        Free, privacy-focused, no API key required
        """
        try:
            # DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Add instant answer if available
            if data.get('Abstract'):
                results.append(SearchResult(
                    title=data.get('Heading', 'Instant Answer'),
                    url=data.get('AbstractURL', ''),
                    snippet=data.get('Abstract', ''),
                    source='DuckDuckGo Instant Answer',
                    relevance_score=0.9
                ))
            
            # Add related topics
            for topic in data.get('RelatedTopics', [])[:max_results]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append(SearchResult(
                        title=topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', ''),
                        url=topic.get('FirstURL', ''),
                        snippet=topic.get('Text', ''),
                        source='DuckDuckGo Related Topics',
                        relevance_score=0.7
                    ))
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def search_news(self, query: str, max_results: int = 5) -> List[NewsArticle]:
        """
        Search current news using NewsAPI.org
        Requires free API key (100 requests/day)
        """
        if not self.news_api_key:
            logger.warning("News API key not set. Skipping news search.")
            return []
            
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': self.news_api_key,
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': max_results
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                articles.append(NewsArticle(
                    title=article.get('title', ''),
                    description=article.get('description', ''),
                    url=article.get('url', ''),
                    published_at=article.get('publishedAt', ''),
                    source=article.get('source', {}).get('name', ''),
                    content=article.get('content', '')
                ))
            
            return articles
            
        except Exception as e:
            logger.error(f"News API search error: {e}")
            return []
    
    def search_wikipedia(self, query: str, max_results: int = 3) -> List[WikiPage]:
        """
        Search Wikipedia using MediaWiki API
        Completely free, no API key required
        """
        try:
            # Search for pages
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': max_results
            }
            
            response = self.session.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            search_data = response.json()
            
            wiki_pages = []
            
            for page in search_data.get('query', {}).get('search', []):
                page_id = page.get('pageid')
                if not page_id:
                    continue
                
                # Get page details
                page_params = {
                    'action': 'query',
                    'format': 'json',
                    'prop': 'extracts|categories|links',
                    'pageids': page_id,
                    'exintro': '1',
                    'explaintext': '1',
                    'exsectionformat': 'plain',
                    'cllimit': 10,
                    'lllimit': 10
                }
                
                page_response = self.session.get(search_url, params=page_params, timeout=10)
                page_response.raise_for_status()
                page_data = page_response.json()
                
                page_info = page_data.get('query', {}).get('pages', {}).get(str(page_id), {})
                
                if page_info:
                    # Extract categories
                    categories = []
                    for cat in page_info.get('categories', []):
                        cat_title = cat.get('title', '')
                        if cat_title.startswith('Category:'):
                            categories.append(cat_title[9:])  # Remove 'Category:' prefix
                    
                    # Extract links
                    links = []
                    for link in page_info.get('links', []):
                        links.append(link.get('title', ''))
                    
                    wiki_pages.append(WikiPage(
                        title=page_info.get('title', ''),
                        summary=page_info.get('extract', ''),
                        url=f"https://en.wikipedia.org/wiki/{quote_plus(page_info.get('title', ''))}",
                        categories=categories,
                        links=links
                    ))
            
            return wiki_pages
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return []
    
    def search_all_sources(self, query: str) -> Dict[str, List]:
        """
        Search all available sources and return comprehensive results
        """
        results = {
            'web_search': [],
            'news': [],
            'wikipedia': [],
            'combined_context': ''
        }
        
        logger.info(f"Searching all sources for: {query}")
        
        # Search all sources in parallel (simplified sequential for now)
        results['web_search'] = self.search_duckduckgo(query, max_results=3)
        results['news'] = self.search_news(query, max_results=3)
        results['wikipedia'] = self.search_wikipedia(query, max_results=2)
        
        # Create combined context
        context_parts = []
        
        # Add web search results
        if results['web_search']:
            context_parts.append("Web Search Results:")
            for result in results['web_search']:
                context_parts.append(f"- {result.title}: {result.snippet}")
        
        # Add news results
        if results['news']:
            context_parts.append("\nRecent News:")
            for article in results['news']:
                context_parts.append(f"- {article.title}: {article.description}")
        
        # Add Wikipedia results
        if results['wikipedia']:
            context_parts.append("\nWikipedia Information:")
            for page in results['wikipedia']:
                context_parts.append(f"- {page.title}: {page.summary[:200]}...")
        
        results['combined_context'] = "\n".join(context_parts)
        
        return results

class RAGSystem:
    """Retrieval-Augmented Generation system"""
    
    def __init__(self):
        self.web_apis = WebSearchAPIs()
        self.cache = {}  # Simple cache for repeated queries
        self.cache_ttl = 3600  # 1 hour cache TTL
        
    def set_news_api_key(self, api_key: str):
        """Set News API key"""
        self.web_apis.set_news_api_key(api_key)
    
    def should_search(self, user_message: str) -> bool:
        """
        Determine if a message should trigger web search
        """
        # Keywords that suggest need for current information
        current_keywords = [
            'today', 'recent', 'latest', 'current', 'now', '2024', '2025',
            'news', 'update', 'happening', 'trending', 'breaking',
            'what is', 'who is', 'where is', 'when did', 'how to',
            'weather', 'stock', 'price', 'election', 'sports', 'movie'
        ]
        
        # Check for current events or factual queries
        message_lower = user_message.lower()
        
        # If message contains current keywords, search
        if any(keyword in message_lower for keyword in current_keywords):
            return True
        
        # If message asks for specific information
        if any(phrase in message_lower for phrase in ['what is', 'who is', 'tell me about']):
            return True
        
        return False
    
    def get_context_for_response(self, user_message: str) -> str:
        """
        Get relevant context for generating AI response
        """
        if not self.should_search(user_message):
            return ""
        
        # Check cache first
        cache_key = user_message.lower().strip()
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['context']
        
        # Perform search
        search_results = self.web_apis.search_all_sources(user_message)
        context = search_results['combined_context']
        
        # Cache the result
        self.cache[cache_key] = {
            'context': context,
            'timestamp': time.time()
        }
        
        return context
    
    def enhance_prompt(self, user_message: str, model_name: str = "general") -> str:
        """
        Enhance the user prompt with relevant context
        """
        context = self.get_context_for_response(user_message)
        
        if not context:
            return user_message
        
        # Create enhanced prompt
        enhanced_prompt = f"""Please provide a helpful response to the user's question. 
If relevant, use the following current information to provide accurate and up-to-date information:

{context}

User's question: {user_message}

Please respond naturally and incorporate the relevant information above if it helps answer the question. 
If the information above is not relevant to the user's question, simply answer based on your knowledge."""
        
        return enhanced_prompt

# Global instance
rag_system = RAGSystem()
web_apis = WebSearchAPIs()

def setup_news_api():
    """Setup News API key from environment or user input"""
    import os
    news_api_key = os.getenv('NEWS_API_KEY')
    if news_api_key:
        rag_system.set_news_api_key(news_api_key)
        web_apis.set_news_api_key(news_api_key)
        logger.info("News API key loaded from environment")
    else:
        logger.info("No News API key found. News search will be disabled.")
        logger.info("Get free API key at: https://newsapi.org/register")

# Initialize on import
setup_news_api()
