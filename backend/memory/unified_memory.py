"""
Unified Memory System for Ethos AI
Provides consistent memory access across all models
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """A single memory entry"""
    conversation_id: str
    user_message: str
    ai_response: str
    model_used: str
    timestamp: float
    metadata: Dict[str, Any]
    summary: Optional[str] = None
    topics: List[str] = None
    importance_score: float = 0.5

class UnifiedMemory:
    """Unified memory system for Ethos AI"""
    
    def __init__(self, database):
        self.database = database
        self.memory_cache = {}  # Cache for quick access
        self.conversation_summaries = {}  # Summaries for long conversations
        
    async def get_unified_context(self, conversation_id: str, max_messages: int = 20) -> Dict[str, Any]:
        """Get unified context for any model"""
        try:
            # Get conversation history
            messages = await self.database.get_messages(conversation_id)
            
            # Get conversation summary if available
            summary = await self.get_conversation_summary(conversation_id)
            
            # Get related conversations
            related_conversations = await self.get_related_conversations(conversation_id)
            
            # Create unified context
            context = {
                "current_conversation": {
                    "id": conversation_id,
                    "messages": messages[-max_messages:],  # Last N messages
                    "summary": summary,
                    "total_messages": len(messages)
                },
                "related_conversations": related_conversations,
                "ethos_identity": self.get_ethos_identity_context(),
                "memory_metadata": {
                    "total_conversations": await self.get_total_conversations(),
                    "total_messages": await self.get_total_messages(),
                    "last_updated": time.time()
                }
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting unified context: {e}")
            return self.get_fallback_context()
    
    async def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """Get or generate conversation summary"""
        try:
            # Check cache first
            if conversation_id in self.conversation_summaries:
                return self.conversation_summaries[conversation_id]
            
            # Get conversation messages
            messages = await self.database.get_messages(conversation_id)
            
            if len(messages) < 5:
                return None  # No summary needed for short conversations
            
            # Generate summary (simplified for now)
            summary = self.generate_conversation_summary(messages)
            
            # Cache the summary
            self.conversation_summaries[conversation_id] = summary
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return None
    
    def generate_conversation_summary(self, messages: List[Dict]) -> str:
        """Generate a summary of conversation messages"""
        try:
            # Extract key topics and themes
            topics = set()
            key_points = []
            
            for msg in messages:
                if msg.get('user'):
                    # Extract potential topics from user messages
                    content = msg['user'].lower()
                    if any(word in content for word in ['code', 'programming', 'debug']):
                        topics.add('programming')
                    if any(word in content for word in ['analyze', 'research', 'data']):
                        topics.add('analysis')
                    if any(word in content for word in ['write', 'create', 'content']):
                        topics.add('content_creation')
                    if any(word in content for word in ['image', 'visual', 'picture']):
                        topics.add('visual_analysis')
                
                # Extract key points from AI responses
                if msg.get('assistant'):
                    response = msg['assistant']
                    if len(response) > 100:  # Only summarize longer responses
                        key_points.append(response[:200] + "...")
            
            # Create summary
            summary_parts = []
            if topics:
                summary_parts.append(f"Topics discussed: {', '.join(topics)}")
            if key_points:
                summary_parts.append(f"Key insights: {len(key_points)} major points discussed")
            
            summary = f"Conversation summary: {len(messages)} messages exchanged. " + " ".join(summary_parts)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return f"Conversation with {len(messages)} messages"
    
    async def get_related_conversations(self, current_conversation_id: str, limit: int = 3) -> List[Dict]:
        """Get conversations related to the current one"""
        try:
            # Get all conversations
            all_conversations = await self.database.get_conversations(limit=50)
            
            # For now, return recent conversations (in a real implementation, 
            # this would use semantic similarity)
            related = []
            for conv in all_conversations:
                if conv['id'] != current_conversation_id:
                    related.append({
                        'id': conv['id'],
                        'title': conv['title'],
                        'message_count': conv['message_count'],
                        'updated_at': conv['updated_at']
                    })
                    if len(related) >= limit:
                        break
            
            return related
            
        except Exception as e:
            logger.error(f"Error getting related conversations: {e}")
            return []
    
    def get_ethos_identity_context(self) -> Dict[str, Any]:
        """Get Ethos AI identity context for all models"""
        return {
            "name": "Ethos from Ethos AI",
            "personality": "intelligent, helpful, warm, professional",
            "capabilities": [
                "natural_language_processing",
                "code_generation_and_analysis", 
                "data_analysis_and_research",
                "image_analysis_and_generation",
                "creative_writing_and_content",
                "mathematical_computation",
                "tool_integration_and_automation"
            ],
            "memory_system": "unified_memory_across_all_models",
            "conversation_style": "engaging, contextual, memory_aware",
            "specialization": "multi_modal_ai_assistant_with_unified_memory"
        }
    
    async def get_total_conversations(self) -> int:
        """Get total number of conversations"""
        try:
            conversations = await self.database.get_conversations(limit=1000)
            return len(conversations)
        except Exception as e:
            logger.error(f"Error getting total conversations: {e}")
            return 0
    
    async def get_total_messages(self) -> int:
        """Get total number of messages across all conversations"""
        try:
            conversations = await self.database.get_conversations(limit=1000)
            total = sum(conv.get('message_count', 0) for conv in conversations)
            return total
        except Exception as e:
            logger.error(f"Error getting total messages: {e}")
            return 0
    
    def get_fallback_context(self) -> Dict[str, Any]:
        """Get fallback context when database is unavailable"""
        return {
            "current_conversation": {
                "id": "unknown",
                "messages": [],
                "summary": "No conversation history available",
                "total_messages": 0
            },
            "related_conversations": [],
            "ethos_identity": self.get_ethos_identity_context(),
            "memory_metadata": {
                "total_conversations": 0,
                "total_messages": 0,
                "last_updated": time.time()
            }
        }
    
    async def add_memory_entry(self, conversation_id: str, user_message: str, 
                             ai_response: str, model_used: str, metadata: Dict = None):
        """Add a new memory entry"""
        try:
            entry = MemoryEntry(
                conversation_id=conversation_id,
                user_message=user_message,
                ai_response=ai_response,
                model_used=model_used,
                timestamp=time.time(),
                metadata=metadata or {},
                topics=self.extract_topics(user_message + " " + ai_response),
                importance_score=self.calculate_importance(user_message, ai_response)
            )
            
            # Store in database (already handled by database.add_message)
            # This is for future memory enhancements
            
            logger.debug(f"Added memory entry for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error adding memory entry: {e}")
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            'programming': ['code', 'program', 'function', 'class', 'algorithm', 'debug'],
            'analysis': ['analyze', 'research', 'data', 'statistics', 'report'],
            'content': ['write', 'create', 'content', 'story', 'article'],
            'visual': ['image', 'picture', 'visual', 'photo', 'design'],
            'math': ['calculate', 'solve', 'equation', 'mathematics', 'formula']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def calculate_importance(self, user_message: str, ai_response: str) -> float:
        """Calculate importance score for memory entry"""
        # Simple heuristic - longer, more detailed responses are more important
        length_score = min(len(ai_response) / 1000, 1.0)  # Normalize to 0-1
        
        # Questions with detailed answers are more important
        question_score = 0.5 if '?' in user_message else 0.0
        
        # Code-related content is more important
        code_score = 0.3 if any(word in user_message.lower() for word in ['code', 'program', 'function']) else 0.0
        
        return min(length_score + question_score + code_score, 1.0)
    
    async def search_memory(self, query: str, limit: int = 5) -> List[Dict]:
        """Search through memory for relevant information"""
        try:
            # Get all conversations
            conversations = await self.database.get_conversations(limit=50)
            
            results = []
            for conv in conversations:
                messages = await self.database.get_messages(conv['id'])
                
                for msg in messages:
                    # Simple keyword search (in a real implementation, this would use semantic search)
                    if query.lower() in msg.get('user', '').lower() or query.lower() in msg.get('assistant', '').lower():
                        results.append({
                            'conversation_id': conv['id'],
                            'conversation_title': conv['title'],
                            'user_message': msg.get('user', ''),
                            'ai_response': msg.get('assistant', ''),
                            'timestamp': msg.get('timestamp', ''),
                            'relevance_score': 0.8  # Simplified for now
                        })
                        
                        if len(results) >= limit:
                            break
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return [] 