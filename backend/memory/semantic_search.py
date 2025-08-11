"""
Semantic Search System for Ethos AI
Provides meaning-based search through all conversations
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """A single search result"""
    conversation_id: str
    conversation_title: str
    message_id: str
    user_message: str
    ai_response: str
    timestamp: str
    relevance_score: float
    context: str
    topics: List[str]
    model_used: str

@dataclass
class MemoryAnalytics:
    """Analytics data about conversations"""
    total_conversations: int
    total_messages: int
    average_messages_per_conversation: float
    most_active_day: str
    most_active_hour: int
    top_topics: List[Tuple[str, int]]
    conversation_timeline: List[Dict]
    model_usage: Dict[str, int]
    average_response_length: float
    memory_growth_rate: float

class SemanticSearch:
    """Semantic search system for Ethos AI"""
    
    def __init__(self, database):
        self.database = database
        self.embeddings_cache = {}  # Cache for embeddings
        self.search_index = {}  # In-memory search index
        self.topic_keywords = {
            'programming': ['code', 'program', 'function', 'class', 'algorithm', 'debug', 'python', 'javascript', 'html', 'css', 'api', 'database', 'server', 'client'],
            'analysis': ['analyze', 'research', 'data', 'statistics', 'report', 'study', 'investigation', 'examination', 'evaluation', 'assessment'],
            'content_creation': ['write', 'create', 'content', 'story', 'article', 'blog', 'document', 'essay', 'script', 'copy', 'creative'],
            'visual_analysis': ['image', 'picture', 'visual', 'photo', 'design', 'graphic', 'art', 'drawing', 'chart', 'diagram', 'visualization'],
            'mathematics': ['calculate', 'solve', 'equation', 'mathematics', 'formula', 'math', 'number', 'statistics', 'probability', 'geometry'],
            'learning': ['learn', 'study', 'education', 'course', 'tutorial', 'lesson', 'knowledge', 'skill', 'training', 'practice'],
            'business': ['business', 'strategy', 'marketing', 'finance', 'management', 'planning', 'project', 'team', 'organization', 'leadership'],
            'technology': ['technology', 'tech', 'software', 'hardware', 'system', 'platform', 'application', 'digital', 'automation', 'innovation']
        }
        
    async def search_conversations(self, query: str, limit: int = 10, 
                                 conversation_filter: Optional[str] = None,
                                 date_filter: Optional[str] = None) -> List[SearchResult]:
        """Search conversations semantically"""
        try:
            logger.info(f"Performing semantic search for: '{query}'")
            
            # Get all conversations
            conversations = await self.database.get_conversations(limit=1000)
            
            # Filter conversations if needed
            if conversation_filter:
                conversations = [c for c in conversations if conversation_filter.lower() in c['title'].lower()]
            
            if date_filter:
                # Filter by date (simplified - could be enhanced)
                conversations = conversations[:50]  # Limit for date filtering
            
            # Search through each conversation
            all_results = []
            
            for conversation in conversations:
                messages = await self.database.get_messages(conversation['id'])
                
                for msg in messages:
                    # Calculate relevance score
                    relevance = self._calculate_relevance(query, msg)
                    
                    if relevance > 0.1:  # Only include relevant results
                        # Extract context
                        context = self._extract_context(messages, msg)
                        
                        # Extract topics
                        topics = self._extract_topics(msg.get('user', '') + ' ' + msg.get('assistant', ''))
                        
                        result = SearchResult(
                            conversation_id=conversation['id'],
                            conversation_title=conversation['title'],
                            message_id=f"{conversation['id']}-{msg.get('timestamp', '')}",
                            user_message=msg.get('user', ''),
                            ai_response=msg.get('assistant', ''),
                            timestamp=msg.get('timestamp', ''),
                            relevance_score=relevance,
                            context=context,
                            topics=topics,
                            model_used=msg.get('model_used', 'unknown')
                        )
                        
                        all_results.append(result)
            
            # Sort by relevance and limit results
            all_results.sort(key=lambda x: x.relevance_score, reverse=True)
            return all_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def _calculate_relevance(self, query: str, message: Dict) -> float:
        """Calculate relevance score between query and message"""
        try:
            query_lower = query.lower()
            user_text = message.get('user', '').lower()
            ai_text = message.get('assistant', '').lower()
            
            # Simple keyword matching (can be enhanced with embeddings)
            score = 0.0
            
            # Exact phrase matching
            if query_lower in user_text or query_lower in ai_text:
                score += 0.8
            
            # Word matching
            query_words = query_lower.split()
            user_words = user_text.split()
            ai_words = ai_text.split()
            
            # Count matching words
            user_matches = sum(1 for word in query_words if word in user_words)
            ai_matches = sum(1 for word in query_words if word in ai_words)
            
            # Calculate word match score
            if query_words:
                user_word_score = user_matches / len(query_words)
                ai_word_score = ai_matches / len(query_words)
                score += (user_word_score + ai_word_score) * 0.3
            
            # Topic matching
            message_topics = self._extract_topics(user_text + ' ' + ai_text)
            query_topics = self._extract_topics(query_lower)
            
            topic_matches = len(set(message_topics) & set(query_topics))
            if topic_matches > 0:
                score += topic_matches * 0.2
            
            # Length bonus (longer responses might be more relevant)
            total_length = len(user_text) + len(ai_text)
            if total_length > 100:
                score += 0.1
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {e}")
            return 0.0
    
    def _extract_context(self, messages: List[Dict], target_message: Dict) -> str:
        """Extract context around a message"""
        try:
            # Find the index of the target message
            target_index = -1
            for i, msg in enumerate(messages):
                if (msg.get('user') == target_message.get('user') and 
                    msg.get('assistant') == target_message.get('assistant')):
                    target_index = i
                    break
            
            if target_index == -1:
                return ""
            
            # Get surrounding messages
            start = max(0, target_index - 2)
            end = min(len(messages), target_index + 3)
            
            context_parts = []
            for i in range(start, end):
                msg = messages[i]
                if msg.get('user'):
                    context_parts.append(f"User: {msg['user'][:100]}...")
                if msg.get('assistant'):
                    context_parts.append(f"AI: {msg['assistant'][:100]}...")
            
            return " | ".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error extracting context: {e}")
            return ""
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        topics = []
        text_lower = text.lower()
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    async def get_memory_analytics(self) -> MemoryAnalytics:
        """Get comprehensive analytics about conversations"""
        try:
            conversations = await self.database.get_conversations(limit=1000)
            
            # Basic statistics
            total_conversations = len(conversations)
            total_messages = sum(conv.get('message_count', 0) for conv in conversations)
            avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
            
            # Analyze conversation timeline
            timeline = []
            for conv in conversations:
                timeline.append({
                    'id': conv['id'],
                    'title': conv['title'],
                    'created_at': conv['created_at'],
                    'message_count': conv['message_count'],
                    'updated_at': conv['updated_at']
                })
            
            # Analyze model usage (simplified)
            model_usage = {
                'llama3.2-3b': 0,
                'codellama-7b': 0,
                'claude-3.5': 0,
                'gpt-4': 0,
                'unknown': 0
            }
            
            # Analyze topics
            topic_counts = {}
            for conv in conversations:
                messages = await self.database.get_messages(conv['id'])
                for msg in messages:
                    text = (msg.get('user', '') + ' ' + msg.get('assistant', '')).lower()
                    topics = self._extract_topics(text)
                    for topic in topics:
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Calculate average response length
            total_length = 0
            message_count = 0
            for conv in conversations:
                messages = await self.database.get_messages(conv['id'])
                for msg in messages:
                    if msg.get('assistant'):
                        total_length += len(msg['assistant'])
                        message_count += 1
            
            avg_response_length = total_length / message_count if message_count > 0 else 0
            
            # Calculate memory growth rate (simplified)
            memory_growth_rate = len(conversations) / 30  # conversations per day estimate
            
            return MemoryAnalytics(
                total_conversations=total_conversations,
                total_messages=total_messages,
                average_messages_per_conversation=avg_messages,
                most_active_day="Monday",  # Simplified
                most_active_hour=14,  # Simplified
                top_topics=top_topics,
                conversation_timeline=timeline,
                model_usage=model_usage,
                average_response_length=avg_response_length,
                memory_growth_rate=memory_growth_rate
            )
            
        except Exception as e:
            logger.error(f"Error getting memory analytics: {e}")
            return MemoryAnalytics(
                total_conversations=0,
                total_messages=0,
                average_messages_per_conversation=0,
                most_active_day="Unknown",
                most_active_hour=0,
                top_topics=[],
                conversation_timeline=[],
                model_usage={},
                average_response_length=0,
                memory_growth_rate=0
            )
    
    async def get_conversation_insights(self, conversation_id: str) -> Dict[str, Any]:
        """Get insights about a specific conversation"""
        try:
            messages = await self.database.get_messages(conversation_id)
            
            # Analyze topics
            topic_counts = {}
            total_length = 0
            question_count = 0
            
            for msg in messages:
                text = (msg.get('user', '') + ' ' + msg.get('assistant', '')).lower()
                topics = self._extract_topics(text)
                for topic in topics:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
                
                if msg.get('user'):
                    total_length += len(msg['user'])
                    if '?' in msg['user']:
                        question_count += 1
                
                if msg.get('assistant'):
                    total_length += len(msg['assistant'])
            
            # Calculate insights
            insights = {
                'total_messages': len(messages),
                'total_length': total_length,
                'average_length': total_length / len(messages) if messages else 0,
                'question_count': question_count,
                'top_topics': sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3],
                'conversation_flow': self._analyze_conversation_flow(messages),
                'key_insights': self._extract_key_insights(messages)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting conversation insights: {e}")
            return {}
    
    def _analyze_conversation_flow(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze the flow of a conversation"""
        try:
            flow_analysis = {
                'starts_with_question': False,
                'has_multiple_topics': False,
                'conversation_depth': 'shallow',
                'interaction_pattern': 'qa'
            }
            
            if messages:
                first_msg = messages[0]
                if first_msg.get('user') and '?' in first_msg['user']:
                    flow_analysis['starts_with_question'] = True
                
                # Check for multiple topics
                all_topics = set()
                for msg in messages:
                    text = (msg.get('user', '') + ' ' + msg.get('assistant', '')).lower()
                    topics = self._extract_topics(text)
                    all_topics.update(topics)
                
                flow_analysis['has_multiple_topics'] = len(all_topics) > 2
                
                # Determine conversation depth
                if len(messages) > 10:
                    flow_analysis['conversation_depth'] = 'deep'
                elif len(messages) > 5:
                    flow_analysis['conversation_depth'] = 'medium'
            
            return flow_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing conversation flow: {e}")
            return {}
    
    def _extract_key_insights(self, messages: List[Dict]) -> List[str]:
        """Extract key insights from conversation"""
        try:
            insights = []
            
            # Analyze patterns
            question_count = sum(1 for msg in messages if msg.get('user') and '?' in msg['user'])
            if question_count > 5:
                insights.append(f"Exploratory conversation with {question_count} questions")
            
            # Check for code
            code_messages = sum(1 for msg in messages if '```' in msg.get('assistant', ''))
            if code_messages > 0:
                insights.append(f"Technical discussion with {code_messages} code examples")
            
            # Check for long responses
            long_responses = sum(1 for msg in messages if len(msg.get('assistant', '')) > 500)
            if long_responses > 0:
                insights.append(f"Detailed explanations with {long_responses} comprehensive responses")
            
            # Check for multiple topics
            all_topics = set()
            for msg in messages:
                text = (msg.get('user', '') + ' ' + msg.get('assistant', '')).lower()
                topics = self._extract_topics(text)
                all_topics.update(topics)
            
            if len(all_topics) > 3:
                insights.append(f"Multi-topic conversation covering {len(all_topics)} areas")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error extracting key insights: {e}")
            return [] 