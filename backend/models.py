#!/usr/bin/env python3
"""
Ethos AI - 70B Model Integration
Local-first, privacy-focused AI with 70B parameter model
"""

import os
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import Optional, Dict, Any
import gc

logger = logging.getLogger(__name__)

class Ethos70BModel:
    """70B Parameter Language Model for Ethos AI"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = "meta-llama/Llama-2-70b-chat-hf"  # Default 70B model
        self.is_loaded = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self, model_name: Optional[str] = None) -> bool:
        """Load the 70B model with quantization for memory efficiency"""
        try:
            if model_name:
                self.model_name = model_name
                
            logger.info(f"Loading 70B model: {self.model_name}")
            logger.info(f"Device: {self.device}")
            logger.info(f"CUDA available: {torch.cuda.is_available()}")
            
            if torch.cuda.is_available():
                logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
            
            # Configure quantization for memory efficiency
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                use_fast=True
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            # Load model with quantization
            logger.info("Loading model with 4-bit quantization...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True
            )
            
            self.is_loaded = True
            logger.info("70B model loaded successfully!")
            
            # Log memory usage
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / 1e9
                reserved = torch.cuda.memory_reserved() / 1e9
                logger.info(f"GPU Memory - Allocated: {allocated:.2f} GB, Reserved: {reserved:.2f} GB")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load 70B model: {e}")
            self.is_loaded = False
            return False
    
    def generate_response(self, message: str, max_length: int = 2048, temperature: float = 0.7) -> str:
        """Generate response using the 70B model"""
        if not self.is_loaded or self.model is None or self.tokenizer is None:
            return "Model not loaded. Please wait for initialization."
            
        try:
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
                    max_new_tokens=max_length,
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
            
            # Extract only the assistant's response (after [/INST])
            if "[/INST]" in response:
                response = response.split("[/INST]")[-1].strip()
            
            # Clean up response
            response = response.replace("<s>", "").replace("</s>", "").strip()
            
            return response if response else "I apologize, but I couldn't generate a proper response. Please try again."
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
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
            
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()
                
            logger.info("70B model unloaded and memory freed")
            
        except Exception as e:
            logger.error(f"Error unloading model: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "is_loaded": self.is_loaded,
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
            "parameters": "70B" if self.is_loaded else "Not loaded",
            "quantization": "4-bit" if self.is_loaded else "None"
        }

# Global model instance
ethos_70b_model = Ethos70BModel()

def initialize_70b_model(model_name: Optional[str] = None) -> bool:
    """Initialize the 70B model"""
    return ethos_70b_model.load_model(model_name)

def generate_70b_response(message: str, max_length: int = 2048, temperature: float = 0.7) -> str:
    """Generate response using the 70B model"""
    return ethos_70b_model.generate_response(message, max_length, temperature)

def get_70b_model_info() -> Dict[str, Any]:
    """Get 70B model information"""
    return ethos_70b_model.get_model_info()

def unload_70b_model():
    """Unload the 70B model"""
    ethos_70b_model.unload_model()
