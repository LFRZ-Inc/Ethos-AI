#!/usr/bin/env python3
"""
Ethos AI - Production AI Model System
Multi-model AI with intelligent routing and error handling
"""

import os
import logging
import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import Optional, Dict, Any, List
import gc
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class BaseAIModel:
    """Base class for all AI models"""
    
    def __init__(self, model_name: str, model_id: str, max_length: int = 2048):
        self.model_name = model_name
        self.model_id = model_id
        self.max_length = max_length
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_time = 0
        self.last_used = 0
        self.error_count = 0
        self.response_times = []
        
    def load_model(self) -> bool:
        """Load the model - to be implemented by subclasses"""
        raise NotImplementedError
        
    def generate_response(self, message: str, temperature: float = 0.7) -> str:
        """Generate response - to be implemented by subclasses"""
        raise NotImplementedError
        
    def unload_model(self):
        """Unload model to free memory"""
        try:
            if self.model is not None:
                del self.model
                self.model = None
                
            if self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None
                
            self.is_loaded = False
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()
                
            logger.info(f"Model {self.model_id} unloaded and memory freed")
            
        except Exception as e:
            logger.error(f"Error unloading model {self.model_id}: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "is_loaded": self.is_loaded,
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
            "load_time": self.load_time,
            "last_used": self.last_used,
            "error_count": self.error_count,
            "avg_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0
        }
    
    def is_healthy(self) -> bool:
        """Check if model is healthy"""
        return self.is_loaded and self.error_count < 3

class Ethos70BModel(BaseAIModel):
    """70B Parameter Model - High capability, slower responses"""
    
    def __init__(self):
        super().__init__(
            model_name="meta-llama/Llama-2-70b-chat-hf",
            model_id="ethos-70b",
            max_length=4096
        )
        
    def load_model(self) -> bool:
        """Load the 70B model with quantization"""
        try:
            start_time = time.time()
            logger.info(f"Loading 70B model: {self.model_name}")
            
            # Configure quantization for memory efficiency
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                use_fast=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            # Load model with quantization
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True
            )
            
            self.is_loaded = True
            self.load_time = time.time() - start_time
            logger.info(f"70B model loaded successfully in {self.load_time:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load 70B model: {e}")
            self.error_count += 1
            return False
    
    def generate_response(self, message: str, temperature: float = 0.7) -> str:
        """Generate response using 70B model"""
        if not self.is_loaded:
            return f"Error: 70B model not loaded. Please initialize the model first."
            
        try:
            start_time = time.time()
            
            # Create prompt in Llama-2 chat format
            prompt = f"""<s>[INST] You are Ethos AI, a local-first, privacy-focused AI assistant. 
You operate completely independently without any external dependencies or tracking.
You are helpful, honest, and direct in your responses.

User: {message} [/INST]"""
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1024,
                padding=True
            )
            
            # Move to device
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_length,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the assistant's response
            if "[/INST]" in response:
                response = response.split("[/INST]")[-1].strip()
            
            response = response.replace("<s>", "").replace("</s>", "").strip()
            
            # Update metrics
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.last_used = time.time()
            
            # Keep only last 10 response times
            if len(self.response_times) > 10:
                self.response_times = self.response_times[-10:]
            
            return response if response else "I apologize, but I couldn't generate a proper response. Please try again."
            
        except Exception as e:
            logger.error(f"Error generating 70B response: {e}")
            self.error_count += 1
            return f"Error: 70B model failed to generate response: {str(e)}"

class Ethos7BModel(BaseAIModel):
    """7B Parameter Model - Balanced capability and speed"""
    
    def __init__(self):
        super().__init__(
            model_name="meta-llama/Llama-2-7b-chat-hf",
            model_id="ethos-7b",
            max_length=2048
        )
        
    def load_model(self) -> bool:
        """Load the 7B model"""
        try:
            start_time = time.time()
            logger.info(f"Loading 7B model: {self.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                use_fast=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True
            )
            
            self.is_loaded = True
            self.load_time = time.time() - start_time
            logger.info(f"7B model loaded successfully in {self.load_time:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load 7B model: {e}")
            self.error_count += 1
            return False
    
    def generate_response(self, message: str, temperature: float = 0.7) -> str:
        """Generate response using 7B model"""
        if not self.is_loaded:
            return f"Error: 7B model not loaded. Please initialize the model first."
            
        try:
            start_time = time.time()
            
            # Create prompt
            prompt = f"""<s>[INST] You are Ethos AI, a local-first, privacy-focused AI assistant. 
You operate completely independently without any external dependencies or tracking.
You are helpful, honest, and direct in your responses.

User: {message} [/INST]"""
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Move to device
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_length,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the assistant's response
            if "[/INST]" in response:
                response = response.split("[/INST]")[-1].strip()
            
            response = response.replace("<s>", "").replace("</s>", "").strip()
            
            # Update metrics
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.last_used = time.time()
            
            if len(self.response_times) > 10:
                self.response_times = self.response_times[-10:]
            
            return response if response else "I apologize, but I couldn't generate a proper response. Please try again."
            
        except Exception as e:
            logger.error(f"Error generating 7B response: {e}")
            self.error_count += 1
            return f"Error: 7B model failed to generate response: {str(e)}"

class Ethos3BModel(BaseAIModel):
    """3B Parameter Model - Fast responses for simple tasks"""
    
    def __init__(self):
        super().__init__(
            model_name="meta-llama/Llama-2-3b-chat-hf",
            model_id="ethos-3b",
            max_length=1024
        )
        
    def load_model(self) -> bool:
        """Load the 3B model"""
        try:
            start_time = time.time()
            logger.info(f"Loading 3B model: {self.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                use_fast=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True
            )
            
            self.is_loaded = True
            self.load_time = time.time() - start_time
            logger.info(f"3B model loaded successfully in {self.load_time:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load 3B model: {e}")
            self.error_count += 1
            return False
    
    def generate_response(self, message: str, temperature: float = 0.7) -> str:
        """Generate response using 3B model"""
        if not self.is_loaded:
            return f"Error: 3B model not loaded. Please initialize the model first."
            
        try:
            start_time = time.time()
            
            # Create prompt
            prompt = f"""<s>[INST] You are Ethos AI, a local-first, privacy-focused AI assistant. 
You operate completely independently without any external dependencies or tracking.
You are helpful, honest, and direct in your responses.

User: {message} [/INST]"""
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=256,
                padding=True
            )
            
            # Move to device
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_length,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the assistant's response
            if "[/INST]" in response:
                response = response.split("[/INST]")[-1].strip()
            
            response = response.replace("<s>", "").replace("</s>", "").strip()
            
            # Update metrics
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.last_used = time.time()
            
            if len(self.response_times) > 10:
                self.response_times = self.response_times[-10:]
            
            return response if response else "I apologize, but I couldn't generate a proper response. Please try again."
            
        except Exception as e:
            logger.error(f"Error generating 3B response: {e}")
            self.error_count += 1
            return f"Error: 3B model failed to generate response: {str(e)}"

class ModelManager:
    """Manages multiple AI models with intelligent routing"""
    
    def __init__(self):
        self.models = {
            "ethos-70b": Ethos70BModel(),
            "ethos-7b": Ethos7BModel(),
            "ethos-3b": Ethos3BModel()
        }
        self.model_order = ["ethos-70b", "ethos-7b", "ethos-3b"]  # Fallback order
        self.executor = ThreadPoolExecutor(max_workers=3)
        
    def get_model(self, model_id: str) -> Optional[BaseAIModel]:
        """Get a specific model"""
        return self.models.get(model_id)
    
    def get_available_models(self) -> List[str]:
        """Get list of available model IDs"""
        return list(self.models.keys())
    
    def get_healthy_models(self) -> List[str]:
        """Get list of healthy model IDs"""
        return [model_id for model_id, model in self.models.items() if model.is_healthy()]
    
    def load_model(self, model_id: str) -> bool:
        """Load a specific model"""
        model = self.get_model(model_id)
        if not model:
            logger.error(f"Model {model_id} not found")
            return False
            
        if model.is_loaded:
            logger.info(f"Model {model_id} already loaded")
            return True
            
        return model.load_model()
    
    def unload_model(self, model_id: str):
        """Unload a specific model"""
        model = self.get_model(model_id)
        if model:
            model.unload_model()
    
    def generate_response(self, message: str, preferred_model: Optional[str] = None) -> str:
        """Generate response using the best available model"""
        
        # If preferred model is specified and healthy, use it
        if preferred_model:
            model = self.get_model(preferred_model)
            if model and model.is_healthy():
                response = model.generate_response(message)
                if not response.startswith("Error:"):
                    return response
                logger.warning(f"Preferred model {preferred_model} failed, trying fallback")
        
        # Try models in fallback order
        for model_id in self.model_order:
            model = self.get_model(model_id)
            if model and model.is_healthy():
                try:
                    response = model.generate_response(message)
                    if not response.startswith("Error:"):
                        return response
                except Exception as e:
                    logger.error(f"Model {model_id} failed: {e}")
                    model.error_count += 1
                    continue
        
        # All models failed
        return "Error: All AI models are currently unavailable. Please try again later."
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about all models"""
        return {
            model_id: model.get_model_info() 
            for model_id, model in self.models.items()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        healthy_models = self.get_healthy_models()
        total_models = len(self.models)
        
        return {
            "total_models": total_models,
            "healthy_models": len(healthy_models),
            "available_models": healthy_models,
            "system_status": "healthy" if healthy_models else "degraded",
            "models": self.get_model_info()
        }

# Global model manager instance
model_manager = ModelManager()

# Convenience functions
def initialize_model(model_id: str) -> bool:
    """Initialize a specific model"""
    return model_manager.load_model(model_id)

def generate_response(message: str, model_id: Optional[str] = None) -> str:
    """Generate response using the best available model"""
    return model_manager.generate_response(message, model_id)

def get_model_info() -> Dict[str, Any]:
    """Get information about all models"""
    return model_manager.get_model_info()

def get_system_status() -> Dict[str, Any]:
    """Get overall system status"""
    return model_manager.get_system_status()

def unload_model(model_id: str):
    """Unload a specific model"""
    model_manager.unload_model(model_id)
