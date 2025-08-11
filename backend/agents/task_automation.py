"""
Task Automation System for Ethos AI
Enables multi-step workflows, scheduled tasks, and automated actions
"""

import asyncio
import logging
import time
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aioschedule
import os
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(Enum):
    WORKFLOW = "workflow"
    SCHEDULED = "scheduled"
    TRIGGERED = "triggered"
    FILE_PROCESSING = "file_processing"
    WEB_ACTION = "web_action"
    DATA_ANALYSIS = "data_analysis"

@dataclass
class TaskStep:
    """A single step in a task workflow"""
    id: str
    name: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str] = None
    timeout: int = 300  # 5 minutes default
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

@dataclass
class Task:
    """A complete task with multiple steps"""
    id: str
    name: str
    description: str
    task_type: TaskType
    steps: List[TaskStep]
    created_at: float
    scheduled_for: Optional[float] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5  # 1-10, higher is more important
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TaskAutomation:
    """Main task automation system"""
    
    def __init__(self, database, orchestrator):
        self.database = database
        self.orchestrator = orchestrator
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.scheduler = aioschedule.Scheduler()
        self.task_handlers = self._register_task_handlers()
        self.file_processor = FileProcessor(database, orchestrator)
        self.web_automation = WebAutomation(orchestrator)
        
    def _register_task_handlers(self) -> Dict[str, Callable]:
        """Register all available task handlers"""
        return {
            "send_message": self._handle_send_message,
            "process_file": self._handle_process_file,
            "web_search": self._handle_web_search,
            "data_analysis": self._handle_data_analysis,
            "file_operation": self._handle_file_operation,
            "schedule_reminder": self._handle_schedule_reminder,
            "send_notification": self._handle_send_notification,
            "code_execution": self._handle_code_execution,
            "api_call": self._handle_api_call,
            "data_extraction": self._handle_data_extraction,
            "content_generation": self._handle_content_generation,
            "system_command": self._handle_system_command
        }
    
    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        """Create a new task"""
        try:
            task_id = str(uuid.uuid4())
            steps = []
            
            for step_data in task_data.get('steps', []):
                step = TaskStep(
                    id=str(uuid.uuid4()),
                    name=step_data['name'],
                    action=step_data['action'],
                    parameters=step_data.get('parameters', {}),
                    dependencies=step_data.get('dependencies', []),
                    timeout=step_data.get('timeout', 300),
                    max_retries=step_data.get('max_retries', 3)
                )
                steps.append(step)
            
            task = Task(
                id=task_id,
                name=task_data['name'],
                description=task_data.get('description', ''),
                task_type=TaskType(task_data.get('type', 'workflow')),
                steps=steps,
                created_at=time.time(),
                scheduled_for=task_data.get('scheduled_for'),
                priority=task_data.get('priority', 5),
                tags=task_data.get('tags', []),
                metadata=task_data.get('metadata', {})
            )
            
            self.tasks[task_id] = task
            
            # Schedule if needed
            if task.scheduled_for:
                await self._schedule_task(task)
            
            # Store in database
            await self._store_task(task)
            
            logger.info(f"Created task: {task.name} (ID: {task_id})")
            return task
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise
    
    async def execute_task(self, task_id: str) -> Task:
        """Execute a task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        try:
            logger.info(f"Executing task: {task.name}")
            
            # Execute steps in order, respecting dependencies
            for step in task.steps:
                await self._execute_step(step, task)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            # Update database
            await self._update_task(task)
            
            logger.info(f"Task completed: {task.name}")
            return task
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = time.time()
            await self._update_task(task)
            logger.error(f"Task failed: {task.name} - {e}")
            raise
    
    async def _execute_step(self, step: TaskStep, task: Task) -> None:
        """Execute a single task step"""
        step.status = TaskStatus.RUNNING
        step.start_time = time.time()
        
        try:
            # Check dependencies
            if step.dependencies:
                for dep_id in step.dependencies:
                    dep_step = next((s for s in task.steps if s.id == dep_id), None)
                    if not dep_step or dep_step.status != TaskStatus.COMPLETED:
                        raise Exception(f"Dependency {dep_id} not completed")
            
            # Execute the step
            handler = self.task_handlers.get(step.action)
            if not handler:
                raise Exception(f"Unknown action: {step.action}")
            
            result = await handler(step.parameters, task)
            step.result = result
            step.status = TaskStatus.COMPLETED
            step.end_time = time.time()
            
        except Exception as e:
            step.error = str(e)
            step.status = TaskStatus.FAILED
            step.end_time = time.time()
            
            # Retry if possible
            if step.retry_count < step.max_retries:
                step.retry_count += 1
                step.status = TaskStatus.PENDING
                step.error = None
                step.start_time = None
                step.end_time = None
                logger.info(f"Retrying step {step.name} (attempt {step.retry_count})")
                await asyncio.sleep(2 ** step.retry_count)  # Exponential backoff
                await self._execute_step(step, task)
            else:
                raise
    
    async def _schedule_task(self, task: Task) -> None:
        """Schedule a task for later execution"""
        if not task.scheduled_for:
            return
        
        scheduled_time = datetime.fromtimestamp(task.scheduled_for)
        
        async def scheduled_execution():
            await asyncio.sleep(task.scheduled_for - time.time())
            await self.execute_task(task.id)
        
        # Schedule the task
        self.scheduler.every().day.at(scheduled_time.strftime("%H:%M")).do(scheduled_execution)
        logger.info(f"Scheduled task {task.name} for {scheduled_time}")
    
    # Task Handlers
    async def _handle_send_message(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Send a message using the orchestrator"""
        content = parameters.get('content', '')
        conversation_id = parameters.get('conversation_id')
        model_override = parameters.get('model_override')
        
        response = await self.orchestrator.process_message(
            content,
            conversation_id=conversation_id,
            model_override=model_override,
            use_tools=parameters.get('use_tools', True)
        )
        
        return {
            'response': response.content,
            'model_used': response.model_used,
            'tools_called': response.tools_called
        }
    
    async def _handle_process_file(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Process a file using the file processor"""
        file_path = parameters.get('file_path')
        operation = parameters.get('operation', 'analyze')
        
        return await self.file_processor.process_file(file_path, operation, parameters)
    
    async def _handle_web_search(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Perform web search"""
        query = parameters.get('query', '')
        max_results = parameters.get('max_results', 5)
        
        return await self.web_automation.search(query, max_results)
    
    async def _handle_data_analysis(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Perform data analysis"""
        data_source = parameters.get('data_source')
        analysis_type = parameters.get('analysis_type', 'summary')
        
        # Use the orchestrator to analyze data
        prompt = f"Please analyze the following data source: {data_source}. Analysis type: {analysis_type}"
        
        response = await self.orchestrator.process_message(
            prompt,
            model_override='claude-3.5',  # Good for analysis
            use_tools=True
        )
        
        return {
            'analysis': response.content,
            'model_used': response.model_used
        }
    
    async def _handle_file_operation(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Perform file operations"""
        operation = parameters.get('operation')
        source = parameters.get('source')
        destination = parameters.get('destination')
        
        if operation == 'copy':
            shutil.copy2(source, destination)
        elif operation == 'move':
            shutil.move(source, destination)
        elif operation == 'delete':
            os.remove(source)
        elif operation == 'create_directory':
            os.makedirs(source, exist_ok=True)
        
        return {'success': True, 'operation': operation}
    
    async def _handle_schedule_reminder(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Schedule a reminder"""
        reminder_time = parameters.get('time')
        message = parameters.get('message', '')
        
        # Create a reminder task
        reminder_task = {
            'name': f"Reminder: {message}",
            'description': f"Scheduled reminder for {reminder_time}",
            'type': 'scheduled',
            'scheduled_for': reminder_time,
            'steps': [{
                'name': 'Send Reminder',
                'action': 'send_notification',
                'parameters': {
                    'message': message,
                    'type': 'reminder'
                }
            }]
        }
        
        await self.create_task(reminder_task)
        return {'scheduled': True, 'reminder_time': reminder_time}
    
    async def _handle_send_notification(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Send a notification"""
        message = parameters.get('message', '')
        notification_type = parameters.get('type', 'info')
        
        # For now, just log the notification
        # In a real implementation, this could send emails, push notifications, etc.
        logger.info(f"NOTIFICATION ({notification_type}): {message}")
        
        return {'sent': True, 'message': message}
    
    async def _handle_code_execution(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Execute code safely"""
        code = parameters.get('code', '')
        language = parameters.get('language', 'python')
        
        # Use the orchestrator to execute code
        prompt = f"Please execute this {language} code and provide the result:\n\n{code}"
        
        response = await self.orchestrator.process_message(
            prompt,
            model_override='codellama-7b',  # Good for code
            use_tools=True
        )
        
        return {
            'result': response.content,
            'model_used': response.model_used
        }
    
    async def _handle_api_call(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Make an API call"""
        url = parameters.get('url')
        method = parameters.get('method', 'GET')
        headers = parameters.get('headers', {})
        data = parameters.get('data')
        
        import httpx
        
        async with httpx.AsyncClient() as client:
            if method.upper() == 'GET':
                response = await client.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = await client.post(url, headers=headers, json=data)
            else:
                raise Exception(f"Unsupported HTTP method: {method}")
        
        return {
            'status_code': response.status_code,
            'response': response.text,
            'headers': dict(response.headers)
        }
    
    async def _handle_data_extraction(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Extract data from various sources"""
        source = parameters.get('source')
        extraction_type = parameters.get('type', 'text')
        
        prompt = f"Please extract {extraction_type} data from: {source}"
        
        response = await self.orchestrator.process_message(
            prompt,
            model_override='claude-3.5',
            use_tools=True
        )
        
        return {
            'extracted_data': response.content,
            'type': extraction_type
        }
    
    async def _handle_content_generation(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Generate content"""
        content_type = parameters.get('type', 'text')
        topic = parameters.get('topic', '')
        length = parameters.get('length', 'medium')
        
        prompt = f"Please generate {content_type} content about: {topic}. Length: {length}"
        
        response = await self.orchestrator.process_message(
            prompt,
            model_override='gpt-4',  # Good for content generation
            use_tools=False
        )
        
        return {
            'generated_content': response.content,
            'type': content_type,
            'topic': topic
        }
    
    async def _handle_system_command(self, parameters: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Execute system commands (with safety checks)"""
        command = parameters.get('command', '')
        
        # Safety check - only allow safe commands
        safe_commands = ['ls', 'dir', 'pwd', 'echo', 'date', 'whoami']
        if command.split()[0] not in safe_commands:
            raise Exception(f"Unsafe command: {command}")
        
        import subprocess
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode
        }
    
    # Database operations
    async def _store_task(self, task: Task) -> None:
        """Store task in database"""
        # This would store the task in the database
        # For now, we'll just log it
        logger.info(f"Storing task: {task.id}")
    
    async def _update_task(self, task: Task) -> None:
        """Update task in database"""
        # This would update the task in the database
        # For now, we'll just log it
        logger.info(f"Updating task: {task.id} - Status: {task.status}")
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    async def get_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """Get all tasks, optionally filtered by status"""
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.CANCELLED
            await self._update_task(self.tasks[task_id])
            return True
        
        return False

class FileProcessor:
    """Handles file processing tasks"""
    
    def __init__(self, database, orchestrator):
        self.database = database
        self.orchestrator = orchestrator
        self.supported_formats = {
            'text': ['.txt', '.md', '.py', '.js', '.html', '.css', '.json'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            'document': ['.pdf', '.doc', '.docx'],
            'data': ['.csv', '.xlsx', '.json']
        }
    
    async def process_file(self, file_path: str, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process a file based on operation type"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if operation == 'analyze':
                return await self._analyze_file(file_path, file_ext)
            elif operation == 'extract_text':
                return await self._extract_text(file_path, file_ext)
            elif operation == 'summarize':
                return await self._summarize_file(file_path, file_ext)
            elif operation == 'convert':
                return await self._convert_file(file_path, parameters)
            else:
                raise Exception(f"Unknown operation: {operation}")
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    async def _analyze_file(self, file_path: str, file_ext: str) -> Dict[str, Any]:
        """Analyze file content"""
        if file_ext in self.supported_formats['text']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            prompt = f"Please analyze this file content and provide insights:\n\n{content[:2000]}..."
            
            response = await self.orchestrator.process_message(
                prompt,
                model_override='claude-3.5',
                use_tools=True
            )
            
            return {
                'analysis': response.content,
                'file_type': 'text',
                'size': len(content)
            }
        
        elif file_ext in self.supported_formats['image']:
            # For images, we'd use vision models
            prompt = f"Please analyze this image: {file_path}"
            
            response = await self.orchestrator.process_message(
                prompt,
                model_override='llava-7b',  # Vision model
                use_tools=True
            )
            
            return {
                'analysis': response.content,
                'file_type': 'image'
            }
        
        else:
            return {
                'analysis': f"File type {file_ext} not fully supported for analysis",
                'file_type': 'unknown'
            }
    
    async def _extract_text(self, file_path: str, file_ext: str) -> Dict[str, Any]:
        """Extract text from file"""
        if file_ext in self.supported_formats['text']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'text': content,
                'length': len(content)
            }
        else:
            raise Exception(f"Text extraction not supported for {file_ext}")
    
    async def _summarize_file(self, file_path: str, file_ext: str) -> Dict[str, Any]:
        """Summarize file content"""
        if file_ext in self.supported_formats['text']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            prompt = f"Please provide a concise summary of this content:\n\n{content[:3000]}..."
            
            response = await self.orchestrator.process_message(
                prompt,
                model_override='claude-3.5',
                use_tools=False
            )
            
            return {
                'summary': response.content,
                'original_length': len(content)
            }
        else:
            raise Exception(f"Summarization not supported for {file_ext}")
    
    async def _convert_file(self, file_path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Convert file format"""
        target_format = parameters.get('target_format')
        output_path = parameters.get('output_path')
        
        # This would implement file conversion logic
        # For now, just return a placeholder
        return {
            'converted': True,
            'output_path': output_path,
            'target_format': target_format
        }

class WebAutomation:
    """Handles web automation tasks"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    async def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Perform web search"""
        prompt = f"Please search the web for: {query}. Return {max_results} relevant results."
        
        response = await self.orchestrator.process_message(
            prompt,
            model_override='claude-3.5',
            use_tools=True
        )
        
        return {
            'query': query,
            'results': response.content,
            'model_used': response.model_used
        }
    
    async def scrape_website(self, url: str, selectors: List[str]) -> Dict[str, Any]:
        """Scrape website content"""
        prompt = f"Please scrape content from {url} using these selectors: {selectors}"
        
        response = await self.orchestrator.process_message(
            prompt,
            model_override='claude-3.5',
            use_tools=True
        )
        
        return {
            'url': url,
            'scraped_content': response.content
        } 