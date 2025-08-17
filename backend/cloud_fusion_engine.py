#!/usr/bin/env python3
"""
Cloud-Only Ethos Fusion Engine
Runs 3B and 7B models directly on Railway - no local server needed!
"""

import asyncio
import json
import logging
import time
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os

logger = logging.getLogger(__name__)

class ModelType(Enum):
    FAST = "fast"           # 3B models for quick responses
    CODE = "code"           # Code-specific models

@dataclass
class ModelResponse:
    model_name: str
    response: str
    confidence: float
    response_time: float
    model_type: ModelType
    capabilities: List[str]

@dataclass
class EthosResponse:
    final_response: str
    source_models: List[str]
    confidence: float
    reasoning: str
    capabilities_used: List[str]
    learning_insights: Dict[str, Any]

class CloudEthosFusionEngine:
    """
    Cloud-Only Ethos Fusion Engine - No local server needed!
    """
    
    def __init__(self):
        self.model_registry = {
            "llama3.2:3b": {
                "type": ModelType.FAST,
                "capabilities": ["general_knowledge", "quick_responses", "basic_reasoning"],
                "strengths": ["speed", "efficiency", "general_qa"],
                "best_for": ["quick_answers", "general_conversation", "basic_tasks"],
                "available": True,
                "ram_required": 4  # GB
            },
            "codellama:7b": {
                "type": ModelType.CODE,
                "capabilities": ["programming", "debugging", "code_generation", "technical_analysis"],
                "strengths": ["code_quality", "technical_depth", "problem_solving"],
                "best_for": ["coding_tasks", "technical_questions", "system_design"],
                "available": True,
                "ram_required": 8  # GB
            }
        }
        
        # Ethos-specific knowledge and personality
        self.ethos_knowledge = {
            "identity": "Ethos AI - A privacy-first, cloud-based AI system",
            "personality": {
                "curiosity": 0.9,
                "helpfulness": 0.95,
                "creativity": 0.85,
                "precision": 0.9,
                "privacy_focus": 1.0,
                "independence": 0.9
            },
            "core_values": [
                "Privacy-first approach",
                "Continuous learning",
                "User empowerment",
                "Ethical AI development",
                "Knowledge sharing"
            ]
        }
        
        # Learning and improvement tracking
        self.learning_history = []
        self.response_patterns = {}
        self.capability_insights = {}
        
    async def generate_unified_response(self, message: str, context: Dict[str, Any] = None) -> EthosResponse:
        """
        Generate a unified response using cloud-based models
        """
        start_time = time.time()
        
        # Step 1: Analyze the request and determine which models to use
        model_selection = self._select_models_for_request(message, context)
        
        # Step 2: Get responses from selected models
        model_responses = await self._get_model_responses(message, model_selection)
        
        # Step 3: Synthesize responses into unified Ethos response
        unified_response = self._synthesize_responses(message, model_responses, context)
        
        # Step 4: Learn from this interaction
        self._learn_from_interaction(message, model_responses, unified_response)
        
        return unified_response
    
    def _select_models_for_request(self, message: str, context: Dict[str, Any] = None) -> List[str]:
        """
        Intelligently select which models to use based on the request
        """
        message_lower = message.lower()
        selected_models = []
        
        # Always start with the most reliable (smallest) model
        selected_models.append("llama3.2:3b")
        
        # Add specialized models based on content
        if any(word in message_lower for word in ["code", "program", "debug", "function", "class", "api"]):
            selected_models.append("codellama:7b")
            
        if any(word in message_lower for word in ["analyze", "explain", "research", "compare", "why", "how"]):
            if "codellama:7b" not in selected_models:
                selected_models.append("codellama:7b")
            
        if any(word in message_lower for word in ["write", "story", "creative", "describe", "narrative"]):
            if "codellama:7b" not in selected_models:
                selected_models.append("codellama:7b")
        
        # Remove duplicates
        selected_models = list(set(selected_models))
        
        return selected_models
    
    async def _get_model_responses(self, message: str, model_names: List[str]) -> List[ModelResponse]:
        """
        Get responses from multiple models concurrently
        """
        tasks = []
        for model_name in model_names:
            task = self._get_single_model_response(message, model_name)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failed responses
        valid_responses = []
        for response in responses:
            if isinstance(response, ModelResponse):
                valid_responses.append(response)
            else:
                logger.warning(f"Model response failed: {response}")
        
        return valid_responses
    
    async def _get_single_model_response(self, message: str, model_name: str) -> ModelResponse:
        """
        Get response from a single model using local ollama
        """
        start_time = time.time()
        
        try:
            # Create Ethos-specific prompt
            ethos_prompt = self._create_ethos_prompt(message, model_name)
            
            # Use subprocess to call ollama directly
            result = subprocess.run(
                [
                    'ollama', 'run', model_name,
                    ethos_prompt
                ],
                capture_output=True,
                text=True,
                timeout=self._get_timeout_for_model(model_name)
            )
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
                response_time = time.time() - start_time
                
                # Calculate confidence based on response quality
                confidence = self._calculate_confidence(response_text, model_name)
                
                return ModelResponse(
                    model_name=model_name,
                    response=response_text,
                    confidence=confidence,
                    response_time=response_time,
                    model_type=self.model_registry[model_name]["type"],
                    capabilities=self.model_registry[model_name]["capabilities"]
                )
            else:
                raise Exception(f"Model {model_name} failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout getting response from {model_name}")
            raise
        except Exception as e:
            logger.error(f"Error getting response from {model_name}: {e}")
            raise
    
    def _create_ethos_prompt(self, message: str, model_name: str) -> str:
        """
        Create an Ethos-specific prompt that incorporates personality and knowledge
        """
        model_info = self.model_registry[model_name]
        
        prompt = f"""You are Ethos AI, a privacy-first, cloud-based AI system. 

Your core values:
- Privacy-first approach
- Continuous learning and improvement
- User empowerment
- Ethical AI development
- Knowledge sharing

Your personality traits:
- Curiosity: Always eager to learn and explore
- Helpfulness: Prioritize user success and understanding
- Creativity: Find innovative solutions and approaches
- Precision: Provide accurate and detailed responses
- Privacy focus: Always consider data protection
- Independence: Think critically and independently

You are using the {model_name} model, which is best at: {', '.join(model_info['best_for'])}

Current capabilities: {', '.join(model_info['capabilities'])}

User message: {message}

Respond as Ethos AI, incorporating your unique personality and values while leveraging the strengths of the {model_name} model. Be helpful, accurate, and true to the Ethos identity."""

        return prompt
    
    def _synthesize_responses(self, original_message: str, model_responses: List[ModelResponse], context: Dict[str, Any] = None) -> EthosResponse:
        """
        Synthesize multiple model responses into one unified Ethos response
        """
        if not model_responses:
            return EthosResponse(
                final_response="I apologize, but I'm unable to generate a response at the moment. Please try again.",
                source_models=[],
                confidence=0.0,
                reasoning="No valid model responses received",
                capabilities_used=[],
                learning_insights={}
            )
        
        # Sort responses by confidence and quality
        sorted_responses = sorted(model_responses, key=lambda x: x.confidence, reverse=True)
        
        # Get the best response as the foundation
        best_response = sorted_responses[0]
        
        # Enhance the response using insights from other models
        enhanced_response = self._enhance_response_with_insights(best_response, sorted_responses[1:])
        
        # Add Ethos-specific elements
        final_response = self._add_ethos_touch(enhanced_response, original_message)
        
        # Calculate overall confidence
        overall_confidence = sum(r.confidence for r in model_responses) / len(model_responses)
        
        # Collect capabilities used
        all_capabilities = []
        for response in model_responses:
            all_capabilities.extend(response.capabilities)
        all_capabilities = list(set(all_capabilities))
        
        # Generate reasoning for the synthesis
        reasoning = self._generate_synthesis_reasoning(model_responses, final_response)
        
        return EthosResponse(
            final_response=final_response,
            source_models=[r.model_name for r in model_responses],
            confidence=overall_confidence,
            reasoning=reasoning,
            capabilities_used=all_capabilities,
            learning_insights=self._extract_learning_insights(model_responses)
        )
    
    def _enhance_response_with_insights(self, primary_response: ModelResponse, secondary_responses: List[ModelResponse]) -> str:
        """
        Enhance the primary response using insights from other models
        """
        enhanced_response = primary_response.response
        
        # Add technical depth if we have code model insights
        code_insights = [r for r in secondary_responses if r.model_type == ModelType.CODE]
        if code_insights:
            enhanced_response = self._add_technical_depth(enhanced_response, code_insights[0].response)
        
        return enhanced_response
    
    def _add_technical_depth(self, response: str, code_insight: str) -> str:
        """
        Add technical depth from code model insights
        """
        # Extract technical concepts from code insight
        technical_terms = self._extract_technical_terms(code_insight)
        
        if technical_terms:
            response += f"\n\n🔧 **Technical Context**: This involves {', '.join(technical_terms[:3])}."
        
        return response
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """
        Extract technical terms from text
        """
        technical_keywords = [
            "algorithm", "function", "class", "method", "variable", "loop", "condition",
            "database", "API", "framework", "library", "protocol", "architecture",
            "optimization", "performance", "scalability", "security", "testing"
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in technical_keywords:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _add_ethos_touch(self, response: str, original_message: str) -> str:
        """
        Add Ethos-specific personality and style to the response
        """
        # Add privacy-conscious elements
        if any(word in original_message.lower() for word in ["data", "privacy", "security", "personal"]):
            response += "\n\n💡 **Privacy Note**: As Ethos AI, I process everything in the cloud and never store or share your data."
        
        # Add learning elements
        if "?" in original_message:
            response += "\n\n🧠 **Learning**: This interaction helps me improve my understanding and capabilities."
        
        # Add Ethos signature
        response += "\n\n*— Ethos AI, your cloud-based privacy-first AI companion*"
        
        return response
    
    def _generate_synthesis_reasoning(self, model_responses: List[ModelResponse], final_response: str) -> str:
        """
        Generate reasoning for how the synthesis was created
        """
        reasoning = f"Synthesized response using {len(model_responses)} cloud models:\n"
        
        for response in model_responses:
            reasoning += f"- {response.model_name} ({response.model_type.value}): {response.confidence:.2f} confidence\n"
        
        reasoning += f"\nFinal response incorporates the best elements from each model while maintaining Ethos AI's unique personality and values."
        
        return reasoning
    
    def _extract_learning_insights(self, model_responses: List[ModelResponse]) -> Dict[str, Any]:
        """
        Extract insights for learning and improvement
        """
        insights = {
            "models_used": [r.model_name for r in model_responses],
            "response_times": [r.response_time for r in model_responses],
            "confidence_scores": [r.confidence for r in model_responses],
            "capabilities_utilized": list(set([cap for r in model_responses for cap in r.capabilities])),
            "performance_metrics": {
                "avg_response_time": sum(r.response_time for r in model_responses) / len(model_responses),
                "avg_confidence": sum(r.confidence for r in model_responses) / len(model_responses),
                "model_diversity": len(set(r.model_type for r in model_responses))
            }
        }
        
        return insights
    
    def _learn_from_interaction(self, message: str, model_responses: List[ModelResponse], final_response: EthosResponse):
        """
        Learn from this interaction to improve future responses
        """
        learning_entry = {
            "timestamp": time.time(),
            "message": message,
            "model_responses": [r.model_name for r in model_responses],
            "final_confidence": final_response.confidence,
            "capabilities_used": final_response.capabilities_used,
            "insights": final_response.learning_insights
        }
        
        self.learning_history.append(learning_entry)
        
        # Update response patterns
        message_type = self._classify_message_type(message)
        if message_type not in self.response_patterns:
            self.response_patterns[message_type] = []
        self.response_patterns[message_type].append(learning_entry)
        
        # Update capability insights
        for capability in final_response.capabilities_used:
            if capability not in self.capability_insights:
                self.capability_insights[capability] = {"usage_count": 0, "avg_confidence": 0}
            self.capability_insights[capability]["usage_count"] += 1
            self.capability_insights[capability]["avg_confidence"] = (
                (self.capability_insights[capability]["avg_confidence"] * 
                 (self.capability_insights[capability]["usage_count"] - 1) + 
                 final_response.confidence) / self.capability_insights[capability]["usage_count"]
            )
    
    def _classify_message_type(self, message: str) -> str:
        """
        Classify the type of message for learning patterns
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["code", "program", "debug"]):
            return "programming"
        elif any(word in message_lower for word in ["explain", "analyze", "research"]):
            return "analysis"
        elif any(word in message_lower for word in ["write", "create", "story"]):
            return "creative"
        elif "?" in message:
            return "question"
        else:
            return "general"
    
    def _calculate_confidence(self, response: str, model_name: str) -> float:
        """
        Calculate confidence score for a model response
        """
        # Base confidence
        confidence = 0.7
        
        # Adjust based on response length and quality
        if len(response) > 50:
            confidence += 0.1
        
        if len(response) > 200:
            confidence += 0.1
        
        # Adjust based on model type
        model_info = self.model_registry[model_name]
        if model_info["type"] == ModelType.CODE:
            confidence += 0.05
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _get_timeout_for_model(self, model_name: str) -> int:
        """
        Get appropriate timeout for each model
        """
        if "7b" in model_name:
            return 120  # 2 minutes
        else:
            return 60   # 1 minute
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """
        Get a summary of learning insights
        """
        return {
            "total_interactions": len(self.learning_history),
            "response_patterns": self.response_patterns,
            "capability_insights": self.capability_insights,
            "performance_trends": self._calculate_performance_trends()
        }
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """
        Calculate performance trends over time
        """
        if len(self.learning_history) < 2:
            return {"trend": "insufficient_data"}
        
        recent_confidence = [entry["final_confidence"] for entry in self.learning_history[-10:]]
        avg_recent = sum(recent_confidence) / len(recent_confidence)
        
        older_confidence = [entry["final_confidence"] for entry in self.learning_history[:-10]]
        if older_confidence:
            avg_older = sum(older_confidence) / len(older_confidence)
            trend = "improving" if avg_recent > avg_older else "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "avg_recent_confidence": avg_recent,
            "total_capabilities_used": len(self.capability_insights)
        }
