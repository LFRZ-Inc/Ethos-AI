"""
Database system for Ethos AI
Handles SQLite database for conversations and user data
"""

import asyncio
import logging
import sqlite3
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
import aiosqlite

logger = logging.getLogger(__name__)

class Database:
    """SQLite database manager for Ethos AI"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "ethos_ai.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    async def initialize(self):
        """Initialize the database and create tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Create conversations table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL,
                        message_count INTEGER DEFAULT 0,
                        metadata TEXT
                    )
                """)
                
                # Create messages table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT NOT NULL,
                        user_message TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        model_used TEXT,
                        timestamp REAL NOT NULL,
                        metadata TEXT,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                    )
                """)
                
                # Create user_preferences table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at REAL NOT NULL
                    )
                """)
                
                # Create file_uploads table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS file_uploads (
                        id TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        file_type TEXT NOT NULL,
                        file_size INTEGER,
                        uploaded_at REAL NOT NULL,
                        metadata TEXT
                    )
                """)
                
                # Create indexes
                await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages (conversation_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations (updated_at)")
                
                await db.commit()
                
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def create_conversation(self, title: str = "New Conversation") -> str:
        """Create a new conversation"""
        try:
            conversation_id = f"conv_{int(time.time() * 1000)}"
            timestamp = time.time()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO conversations (id, title, created_at, updated_at, message_count)
                    VALUES (?, ?, ?, ?, 0)
                """, (conversation_id, title, timestamp, timestamp))
                await db.commit()
            
            logger.debug(f"Created conversation: {conversation_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise
    
    async def add_message(
        self, 
        conversation_id: str, 
        user_message: str, 
        ai_response: str, 
        model_used: str = None,
        metadata: Dict = None
    ):
        """Add a message to a conversation"""
        try:
            timestamp = time.time()
            metadata_json = json.dumps(metadata) if metadata else None
            
            async with aiosqlite.connect(self.db_path) as db:
                # Add message
                await db.execute("""
                    INSERT INTO messages (conversation_id, user_message, ai_response, model_used, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (conversation_id, user_message, ai_response, model_used, timestamp, metadata_json))
                
                # Update conversation
                await db.execute("""
                    UPDATE conversations 
                    SET message_count = message_count + 1, updated_at = ?
                    WHERE id = ?
                """, (timestamp, conversation_id))
                
                await db.commit()
            
            logger.debug(f"Added message to conversation: {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise
    
    async def get_conversations(self, limit: int = 50) -> List[Dict]:
        """Get all conversations"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute("""
                    SELECT id, title, created_at, updated_at, message_count, metadata
                    FROM conversations
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (limit,))
                
                rows = await cursor.fetchall()
                
                conversations = []
                for row in rows:
                    conversations.append({
                        "id": row["id"],
                        "title": row["title"],
                        "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row["created_at"])),
                        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row["updated_at"])),
                        "message_count": row["message_count"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    })
                
                return conversations
                
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation with its messages"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Get conversation details
                cursor = await db.execute("""
                    SELECT id, title, created_at, updated_at, message_count, metadata
                    FROM conversations
                    WHERE id = ?
                """, (conversation_id,))
                
                conv_row = await cursor.fetchone()
                if not conv_row:
                    return None
                
                # Get messages
                cursor = await db.execute("""
                    SELECT user_message, ai_response, model_used, timestamp, metadata
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY timestamp ASC
                """, (conversation_id,))
                
                message_rows = await cursor.fetchall()
                
                messages = []
                for row in message_rows:
                    messages.append({
                        "user": row["user_message"],
                        "assistant": row["ai_response"],
                        "model_used": row["model_used"],
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row["timestamp"])),
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    })
                
                return {
                    "id": conv_row["id"],
                    "title": conv_row["title"],
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(conv_row["created_at"])),
                    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(conv_row["updated_at"])),
                    "message_count": conv_row["message_count"],
                    "metadata": json.loads(conv_row["metadata"]) if conv_row["metadata"] else {},
                    "messages": messages
                }
                
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None
    
    async def get_messages(self, conversation_id: str) -> List[Dict]:
        """Get messages for a conversation in the format expected by the orchestrator"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute("""
                    SELECT user_message, ai_response, model_used, timestamp, metadata
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY timestamp ASC
                """, (conversation_id,))
                
                message_rows = await cursor.fetchall()
                
                messages = []
                for row in message_rows:
                    messages.append({
                        "user": row["user_message"],
                        "assistant": row["ai_response"],
                        "model_used": row["model_used"],
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row["timestamp"])),
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    })
                
                return messages
                
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    async def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE conversations 
                    SET title = ?, updated_at = ?
                    WHERE id = ?
                """, (title, time.time(), conversation_id))
                await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating conversation title: {e}")
            return False
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Delete messages first
                await db.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
                
                # Delete conversation
                await db.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
                
                await db.commit()
            
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
    
    async def set_preference(self, key: str, value: Any) -> bool:
        """Set a user preference"""
        try:
            value_json = json.dumps(value)
            timestamp = time.time()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
                    VALUES (?, ?, ?)
                """, (key, value_json, timestamp))
                await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting preference: {e}")
            return False
    
    async def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT value FROM user_preferences WHERE key = ?
                """, (key,))
                
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return default
                
        except Exception as e:
            logger.error(f"Error getting preference: {e}")
            return default
    
    async def add_file_upload(
        self, 
        file_id: str, 
        filename: str, 
        file_path: str, 
        file_type: str,
        file_size: int = None,
        metadata: Dict = None
    ):
        """Add a file upload record"""
        try:
            timestamp = time.time()
            metadata_json = json.dumps(metadata) if metadata else None
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO file_uploads (id, filename, file_path, file_type, file_size, uploaded_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (file_id, filename, file_path, file_type, file_size, timestamp, metadata_json))
                await db.commit()
            
            logger.debug(f"Added file upload: {file_id}")
            
        except Exception as e:
            logger.error(f"Error adding file upload: {e}")
            raise
    
    async def get_file_uploads(self, limit: int = 50) -> List[Dict]:
        """Get recent file uploads"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute("""
                    SELECT id, filename, file_path, file_type, file_size, uploaded_at, metadata
                    FROM file_uploads
                    ORDER BY uploaded_at DESC
                    LIMIT ?
                """, (limit,))
                
                rows = await cursor.fetchall()
                
                uploads = []
                for row in rows:
                    uploads.append({
                        "id": row["id"],
                        "filename": row["filename"],
                        "file_path": row["file_path"],
                        "file_type": row["file_type"],
                        "file_size": row["file_size"],
                        "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row["uploaded_at"])),
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    })
                
                return uploads
                
        except Exception as e:
            logger.error(f"Error getting file uploads: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Count conversations
                cursor = await db.execute("SELECT COUNT(*) FROM conversations")
                conversation_count = (await cursor.fetchone())[0]
                
                # Count messages
                cursor = await db.execute("SELECT COUNT(*) FROM messages")
                message_count = (await cursor.fetchone())[0]
                
                # Count file uploads
                cursor = await db.execute("SELECT COUNT(*) FROM file_uploads")
                upload_count = (await cursor.fetchone())[0]
                
                # Get total file size
                cursor = await db.execute("SELECT SUM(file_size) FROM file_uploads WHERE file_size IS NOT NULL")
                total_size = (await cursor.fetchone())[0] or 0
                
                return {
                    "conversation_count": conversation_count,
                    "message_count": message_count,
                    "upload_count": upload_count,
                    "total_file_size": total_size,
                    "database_size": self.db_path.stat().st_size if self.db_path.exists() else 0
                }
                
        except Exception as e:
            logger.error(f"Error getting database statistics: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup database connections"""
        # aiosqlite handles connection cleanup automatically
        logger.info("Database cleanup completed") 