"""
Vector store for Ethos AI
Handles semantic search and memory using ChromaDB
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for semantic search and memory"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.embeddings_dir = self.data_dir / "embeddings"
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self.collection = None
        self.embedding_model = None
        
    async def initialize(self):
        """Initialize the vector store"""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.embeddings_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="ethos_ai_memory",
                metadata={"description": "Ethos AI conversation memory"}
            )
            
            # Initialize embedding model
            await self._initialize_embedding_model()
            
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    async def _initialize_embedding_model(self):
        """Initialize the sentence transformer model"""
        try:
            # Use a lightweight model for better performance
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.embedding_model = SentenceTransformer(model_name)
            
            # Test the model
            test_embedding = self.embedding_model.encode("test")
            logger.info(f"Embedding model initialized: {model_name}")
            
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            raise
    
    async def add_conversation(
        self, 
        user_message: str, 
        ai_response: str, 
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Add a conversation to the vector store"""
        try:
            # Create combined text for embedding
            combined_text = f"User: {user_message}\nAssistant: {ai_response}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(combined_text).tolist()
            
            # Prepare metadata
            doc_metadata = {
                "conversation_id": conversation_id or "general",
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": time.time(),
                "type": "conversation"
            }
            
            if metadata:
                doc_metadata.update(metadata)
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[doc_metadata],
                ids=[f"conv_{int(time.time() * 1000)}"]
            )
            
            logger.debug(f"Added conversation to vector store: {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error adding conversation to vector store: {e}")
    
    async def search(self, query: str, limit: int = 10, threshold: float = 0.7) -> List[Dict]:
        """Search for similar conversations"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            processed_results = []
            for i in range(len(results["ids"][0])):
                distance = results["distances"][0][i]
                similarity = 1 - distance  # Convert distance to similarity
                
                if similarity >= threshold:
                    processed_results.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": similarity,
                        "distance": distance
                    })
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    async def get_conversation_messages(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """Get messages from a specific conversation"""
        try:
            # Search for messages in the conversation
            results = self.collection.get(
                where={"conversation_id": conversation_id},
                limit=limit
            )
            
            # Process results
            messages = []
            for i, metadata in enumerate(results["metadatas"]):
                if metadata:
                    messages.append({
                        "user": metadata.get("user_message", ""),
                        "assistant": metadata.get("ai_response", ""),
                        "timestamp": metadata.get("timestamp", 0)
                    })
            
            # Sort by timestamp
            messages.sort(key=lambda x: x["timestamp"])
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []
    
    async def add_document(self, content: str, metadata: Dict):
        """Add a document to the vector store"""
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata],
                ids=[f"doc_{int(time.time() * 1000)}"]
            )
            
            logger.debug(f"Added document to vector store: {metadata.get('title', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")
    
    async def search_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"type": "document"},
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            processed_results = []
            for i in range(len(results["ids"][0])):
                distance = results["distances"][0][i]
                similarity = 1 - distance
                
                processed_results.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": similarity
                })
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete all messages from a conversation"""
        try:
            # Get all documents for the conversation
            results = self.collection.get(
                where={"conversation_id": conversation_id}
            )
            
            if results["ids"]:
                # Delete the documents
                self.collection.delete(ids=results["ids"])
                logger.info(f"Deleted conversation: {conversation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            count = self.collection.count()
            
            # Get sample of conversations
            sample_results = self.collection.get(limit=100)
            
            # Count by conversation
            conversation_counts = {}
            for metadata in sample_results["metadatas"]:
                if metadata:
                    conv_id = metadata.get("conversation_id", "unknown")
                    conversation_counts[conv_id] = conversation_counts.get(conv_id, 0) + 1
            
            return {
                "total_documents": count,
                "conversation_count": len(conversation_counts),
                "sample_conversations": conversation_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting vector store statistics: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.client:
                self.client.reset()
            logger.info("Vector store cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up vector store: {e}") 