"""
Model Orchestrator for Ethos AI
Handles intelligent routing between different AI models
"""

import asyncio
import logging
import re
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from .base_model import BaseModel, ModelResponse
from .ollama_model import OllamaModel
from .anthropic_model import AnthropicModel
from .openai_model import OpenAIModel
from .llava_model import LLaVAModel
from .flux_model import FluxModel
from memory.unified_memory import UnifiedMemory

logger = logging.getLogger(__name__)

class ModelOrchestrator:
    """Orchestrates multiple AI models for optimal response"""
    
    def __init__(self, config, vector_store=None, tool_manager=None):
        self.config = config
        self.vector_store = vector_store
        self.tool_manager = tool_manager
        self.models: Dict[str, BaseModel] = {}
        self.model_status: Dict[str, str] = {}  # available, unavailable, loading
        self.unified_memory = None  # Will be initialized after database is available
        
    async def initialize(self):
        """Initialize all models"""
        logger.info("Initializing model orchestrator...")
        
        # Initialize each model
        for model_id, model_config in self.config.models.items():
            if not model_config.enabled:
                continue
                
            try:
                model = await self._create_model(model_config)
                if model:
                    # Initialize the model
                    initialized = await model.initialize()
                    if initialized:
                        self.models[model_id] = model
                        self.model_status[model_id] = "available"
                        logger.info(f"Model {model_id} initialized successfully")
                    else:
                        self.model_status[model_id] = "unavailable"
                        logger.warning(f"Failed to initialize model {model_id}")
                else:
                    self.model_status[model_id] = "unavailable"
                    logger.warning(f"Failed to create model {model_id}")
                    
            except Exception as e:
                self.model_status[model_id] = "unavailable"
                logger.error(f"Error initializing model {model_id}: {e}")
        
        logger.info(f"Model orchestrator initialized with {len(self.models)} models")
        
        # Initialize unified memory if database is available
        if hasattr(self, 'database') and self.database:
            self.unified_memory = UnifiedMemory(self.database)
            logger.info("Unified memory system initialized")
    
    async def _create_model(self, model_config) -> Optional[BaseModel]:
        """Create a model instance based on configuration"""
        try:
            if model_config.provider == "ollama":
                return OllamaModel(model_config)
            elif model_config.provider == "anthropic":
                return AnthropicModel(model_config, self.config)
            elif model_config.provider == "openai":
                return OpenAIModel(model_config, self.config)
            elif model_config.provider == "llava":
                return LLaVAModel(model_config)
            elif model_config.provider == "flux":
                return FluxModel(model_config)
            else:
                logger.error(f"Unknown model provider: {model_config.provider}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating model {model_config.id}: {e}")
            return None
    
    async def process_message(
        self, 
        content: str, 
        conversation_id: Optional[str] = None,
        model_override: Optional[str] = None,
        use_tools: bool = True
    ) -> ModelResponse:
        """Process a message and return response"""
        start_time = time.time()
        
        try:
            # Determine which model to use
            if model_override and model_override in self.models:
                selected_model_id = model_override
            else:
                selected_model_id = await self._select_model(content)
            
            if not selected_model_id or selected_model_id not in self.models:
                # Fallback to first available model
                available_models = [mid for mid, status in self.model_status.items() if status == "available"]
                if not available_models:
                    raise Exception("No available models")
                selected_model_id = available_models[0]
            
            # Get the selected model
            model = self.models[selected_model_id]
            
            # Get unified context for all models
            context = await self._get_unified_context(conversation_id)
            
            # Process with the model
            response = await model.generate(content, context=context)
            
            # The response is already a ModelResponse object, just update the model_used
            response.model_used = selected_model_id
            
            # Calculate processing time
            processing_time = time.time() - start_time
            response.processing_time = processing_time
            
            # Store in unified memory
            if self.unified_memory:
                await self.unified_memory.add_memory_entry(
                    conversation_id, content, response.content, selected_model_id
                )
            
            # Also store in vector store if available
            if self.vector_store:
                await self._store_in_memory(content, response.content, conversation_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Return a fallback response
            return ModelResponse(
                content=f"I apologize, but I encountered an error: {str(e)}. Please try again or check your model configuration.",
                model_used="fallback",
                processing_time=time.time() - start_time,
                tools_called=[]
            )
    
    async def _select_model(self, content: str) -> Optional[str]:
        """Select the best model for the given content"""
        try:
            # Simple model selection logic
            query_type = self._analyze_query_type(content)
            
            # Map query types to model capabilities
            if query_type == "coding":
                # Look for coding-capable models
                for model_id, model in self.models.items():
                    if "coding" in model.model_config.capabilities:
                        return model_id
            elif query_type == "vision":
                # Look for vision-capable models
                for model_id, model in self.models.items():
                    if "vision" in model.model_config.capabilities:
                        return model_id
            elif query_type == "reasoning":
                # Look for reasoning-capable models
                for model_id, model in self.models.items():
                    if "reasoning" in model.model_config.capabilities:
                        return model_id
            
            # Default to first available model
            available_models = [mid for mid, status in self.model_status.items() if status == "available"]
            return available_models[0] if available_models else None
            
        except Exception as e:
            logger.error(f"Error selecting model: {e}")
            return None
    
    def _analyze_query_type(self, content: str) -> str:
        """Analyze the type of query"""
        content_lower = content.lower()
        
        # Check for coding-related keywords
        coding_keywords = ["code", "program", "function", "class", "algorithm", "bug", "error", "debug", "compile", "syntax"]
        if any(keyword in content_lower for keyword in coding_keywords):
            return "coding"
        
        # Check for vision-related keywords
        vision_keywords = ["image", "picture", "photo", "visual", "see", "look", "describe", "analyze image"]
        if any(keyword in content_lower for keyword in vision_keywords):
            return "vision"
        
        # Check for reasoning-related keywords
        reasoning_keywords = ["explain", "why", "how", "analyze", "compare", "evaluate", "think", "reason"]
        if any(keyword in content_lower for keyword in reasoning_keywords):
            return "reasoning"
        
        return "general"
    
    async def _get_unified_context(self, conversation_id: Optional[str]) -> List[Dict]:
        """Get unified context for all models"""
        if not conversation_id:
            return []
        
        try:
            # Use unified memory system if available
            if self.unified_memory:
                unified_context = await self.unified_memory.get_unified_context(conversation_id)
                
                # Format context for models
                formatted_context = []
                
                # Add conversation summary if available
                if unified_context.get('current_conversation', {}).get('summary'):
                    formatted_context.append({
                        'role': 'system',
                        'content': f"CONVERSATION SUMMARY: {unified_context['current_conversation']['summary']}"
                    })
                
                # Add recent messages
                messages = unified_context.get('current_conversation', {}).get('messages', [])
                for msg in messages:
                    if msg.get('user'):
                        formatted_context.append({
                            'role': 'user',
                            'content': msg['user']
                        })
                    if msg.get('assistant'):
                        formatted_context.append({
                            'role': 'assistant',
                            'content': msg['assistant']
                        })
                
                # Add related conversations context
                related = unified_context.get('related_conversations', [])
                if related:
                    related_context = "RELATED CONVERSATIONS:\n"
                    for conv in related[:2]:  # Limit to 2 related conversations
                        related_context += f"- {conv['title']} ({conv['message_count']} messages)\n"
                    formatted_context.append({
                        'role': 'system',
                        'content': related_context
                    })
                
                return formatted_context
            
            # Fallback to old method
            elif hasattr(self, 'database') and self.database:
                messages = await self.database.get_messages(conversation_id)
                return messages
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting unified context: {e}")
            return []
    
    async def _store_in_memory(self, user_message: str, ai_response: str, conversation_id: Optional[str]):
        """Store conversation in memory"""
        if self.vector_store:
            try:
                await self.vector_store.add_conversation(
                    user_message=user_message,
                    ai_response=ai_response,
                    conversation_id=conversation_id
                )
            except Exception as e:
                logger.error(f"Error storing in memory: {e}")
        # If no vector store, just log the conversation
        else:
            logger.info(f"Conversation stored (no vector store): {conversation_id}")
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        models = []
        for model_id, model in self.models.items():
            models.append({
                "id": model_id,
                "name": model.model_config.name,
                "type": model.model_config.type,
                "provider": model.model_config.provider,
                "capabilities": model.model_config.capabilities,
                "status": self.model_status.get(model_id, "unknown")
            })
        return models
    
    async def test_model(self, model_id: str) -> bool:
        """Test if a model is working"""
        if model_id not in self.models:
            return False
        
        try:
            model = self.models[model_id]
            response = await model.generate("Hello, this is a test message.")
            return bool(response and response.get("content"))
        except Exception as e:
            logger.error(f"Model test failed for {model_id}: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        for model in self.models.values():
            try:
                if hasattr(model, 'cleanup'):
                    await model.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up model: {e}") 