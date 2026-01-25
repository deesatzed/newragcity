"""
Developer-grade LLM wrapper with confidence tracking for Cognitron
Integrates OpenAI and Google Gemini APIs with logprobs analysis
"""

import asyncio
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import openai
import google.generativeai as genai
from openai import AsyncOpenAI

from .confidence import LLMCall


@dataclass
class LLMResponse:
    """LLM response with enterprise-grade confidence tracking"""
    text: str
    confidence: float
    tokens_used: int
    processing_time: float
    model_used: str
    logprobs: Optional[List[Dict[str, float]]] = None
    top_logprobs: Optional[List[Dict[str, float]]] = None
    uncertainty_indicators: List[str] = None
    
    def __post_init__(self):
        if self.uncertainty_indicators is None:
            self.uncertainty_indicators = []


class DeveloperGradeLLM:
    """
    Developer-grade LLM interface with confidence calibration
    Supports OpenAI GPT models and Google Gemini with logprobs analysis
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        primary_model: str = "gpt-4",
        fallback_model: str = "gemini-pro"
    ):
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        
        # Initialize OpenAI client
        if openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        else:
            try:
                self.openai_client = AsyncOpenAI()  # Uses OPENAI_API_KEY from env
            except Exception as e:
                print("⚠️  OpenAI API key not available - confidence tracking will be limited")
                self.openai_client = None
            
        # Initialize Gemini client
        try:
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
            else:
                genai.configure()  # Uses GOOGLE_API_KEY from env
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print("⚠️  Google API key not available - using fallback responses")
            self.gemini_model = None
        
        # Developer-grade configuration
        self.confidence_threshold = 0.85
        self.uncertainty_keywords = [
            "might", "could", "possibly", "perhaps", "maybe", "unclear",
            "uncertain", "ambiguous", "depends", "varies", "sometimes"
        ]
        
    async def generate_with_confidence(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.1,
        require_logprobs: bool = True
    ) -> LLMResponse:
        """
        Generate response with enterprise-grade confidence tracking
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature (lower = more deterministic)
            require_logprobs: Whether logprobs are required for confidence
            
        Returns:
            LLMResponse with confidence metrics
        """
        
        start_time = time.time()
        
        # Try primary model (OpenAI) first for logprobs
        if self.primary_model.startswith("gpt"):
            try:
                response = await self._generate_openai(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    include_logprobs=require_logprobs
                )
                
                if response:
                    return response
                    
            except Exception as e:
                print(f"⚠️  OpenAI generation failed: {e}")
                
        # Fallback to Gemini
        if self.gemini_model:
            try:
                response = await self._generate_gemini(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response
                
            except Exception as e:
                print(f"❌ Gemini generation failed: {e}")
        
        # Final fallback when no API keys available
        print("⚠️  No LLM APIs available - using test mode response")
        processing_time = time.time() - start_time
        return LLMResponse(
            text="TEST MODE: This is a test response from Cognitron's enterprise-grade system. In production, this would be a confident AI-generated answer with full confidence tracking.",
            confidence=0.8,  # Simulated confidence for testing
            tokens_used=20,
            processing_time=processing_time,
            model_used="test_mode",
            uncertainty_indicators=["test_mode_active"]
        )
            
    async def _generate_openai(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        include_logprobs: bool
    ) -> Optional[LLMResponse]:
        """Generate response using OpenAI API with logprobs"""
        
        start_time = time.time()
        
        try:
            # Create chat completion with logprobs for confidence tracking
            response = await self.openai_client.chat.completions.create(
                model=self.primary_model,
                messages=[
                    {"role": "system", "content": "You are a enterprise-grade AI assistant that provides highly accurate and reliable information. Always be precise and acknowledge uncertainty when appropriate."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                logprobs=include_logprobs,
                top_logprobs=5 if include_logprobs else None
            )
            
            processing_time = time.time() - start_time
            
            choice = response.choices[0]
            text = choice.message.content
            tokens_used = response.usage.total_tokens
            
            # Extract logprobs for confidence calculation
            logprobs_data = []
            top_logprobs_data = []
            
            if choice.logprobs and choice.logprobs.content:
                for token_logprob in choice.logprobs.content:
                    logprobs_data.append({token_logprob.token: token_logprob.logprob})
                    
                    if token_logprob.top_logprobs:
                        top_logprob_dict = {
                            tl.token: tl.logprob for tl in token_logprob.top_logprobs
                        }
                        top_logprobs_data.append(top_logprob_dict)
                        
            # Calculate confidence from logprobs and text analysis
            confidence = self._calculate_openai_confidence(text, logprobs_data, top_logprobs_data)
            
            # Detect uncertainty indicators
            uncertainty_indicators = self._detect_uncertainty_indicators(text)
            
            return LLMResponse(
                text=text,
                confidence=confidence,
                tokens_used=tokens_used,
                processing_time=processing_time,
                model_used=self.primary_model,
                logprobs=logprobs_data,
                top_logprobs=top_logprobs_data,
                uncertainty_indicators=uncertainty_indicators
            )
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
            
    async def _generate_gemini(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> LLMResponse:
        """Generate response using Google Gemini API"""
        
        start_time = time.time()
        
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            top_p=0.8,
            top_k=40
        )
        
        # Add enterprise-grade system instruction
        developer_prompt = f"""You are a enterprise-grade AI assistant that provides highly accurate and reliable information. 
Always be precise and acknowledge uncertainty when appropriate.

User Query: {prompt}

Response:"""
        
        response = await asyncio.to_thread(
            self.gemini_model.generate_content,
            developer_prompt,
            generation_config=generation_config
        )
        
        processing_time = time.time() - start_time
        
        text = response.text if response.text else ""
        tokens_used = len(text.split())  # Rough estimate for Gemini
        
        # Calculate confidence without logprobs (text-based analysis)
        confidence = self._calculate_gemini_confidence(text)
        
        # Detect uncertainty indicators
        uncertainty_indicators = self._detect_uncertainty_indicators(text)
        
        return LLMResponse(
            text=text,
            confidence=confidence,
            tokens_used=tokens_used,
            processing_time=processing_time,
            model_used="gemini-pro",
            uncertainty_indicators=uncertainty_indicators
        )
        
    def _calculate_openai_confidence(
        self,
        text: str,
        logprobs: List[Dict[str, float]],
        top_logprobs: List[Dict[str, float]]
    ) -> float:
        """
        Calculate confidence from OpenAI logprobs using enterprise-grade standards
        """
        
        # Start with text-based confidence
        text_confidence = self._calculate_text_confidence(text)
        
        if not logprobs:
            return text_confidence
            
        # Calculate token-level confidences
        token_confidences = []
        
        for token_logprob_dict in logprobs:
            for token, logprob in token_logprob_dict.items():
                # Convert logprob to probability
                prob = math.exp(logprob)
                
                # High probability tokens get high confidence
                if prob > 0.9:
                    token_confidence = 0.95
                elif prob > 0.7:
                    token_confidence = 0.8
                elif prob > 0.5:
                    token_confidence = 0.6
                else:
                    token_confidence = 0.3
                    
                token_confidences.append(token_confidence)
                
        if not token_confidences:
            return text_confidence
            
        # Use enterprise-grade confidence aggregation (conservative approach)
        logprob_confidence = min(token_confidences)  # Most conservative
        
        # Combine text and logprob confidence
        final_confidence = min(text_confidence, logprob_confidence)
        
        return max(0.0, min(1.0, final_confidence))
        
    def _calculate_gemini_confidence(self, text: str) -> float:
        """
        Calculate confidence for Gemini responses (text-based analysis only)
        """
        return self._calculate_text_confidence(text)
        
    def _calculate_text_confidence(self, text: str) -> float:
        """
        Calculate confidence based on text analysis using enterprise-grade criteria
        """
        if not text or len(text) < 10:
            return 0.2
            
        # Factors affecting confidence
        confidence_factors = []
        
        # Length factor (very short or very long responses may be less reliable)
        word_count = len(text.split())
        if 20 <= word_count <= 200:
            confidence_factors.append(0.9)
        elif 10 <= word_count < 20 or 200 < word_count <= 400:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
            
        # Uncertainty language factor
        uncertainty_count = sum(1 for keyword in self.uncertainty_keywords if keyword in text.lower())
        if uncertainty_count == 0:
            confidence_factors.append(0.95)
        elif uncertainty_count <= 2:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
            
        # Hedging phrases factor
        hedging_phrases = ["i think", "it seems", "it appears", "i believe", "i'm not sure"]
        hedging_count = sum(1 for phrase in hedging_phrases if phrase in text.lower())
        if hedging_count == 0:
            confidence_factors.append(0.9)
        elif hedging_count <= 1:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.4)
            
        # Definitiveness factor
        definitive_phrases = ["definitely", "certainly", "clearly", "obviously", "without doubt"]
        definitive_count = sum(1 for phrase in definitive_phrases if phrase in text.lower())
        if definitive_count > 0:
            confidence_factors.append(min(0.95, 0.8 + (definitive_count * 0.05)))
        else:
            confidence_factors.append(0.8)
            
        # Use enterprise-grade conservative aggregation (minimum confidence)
        final_confidence = min(confidence_factors) if confidence_factors else 0.5
        
        return max(0.0, min(1.0, final_confidence))
        
    def _detect_uncertainty_indicators(self, text: str) -> List[str]:
        """Detect uncertainty indicators in response text"""
        
        indicators = []
        text_lower = text.lower()
        
        # Check for uncertainty keywords
        found_keywords = [kw for kw in self.uncertainty_keywords if kw in text_lower]
        if found_keywords:
            indicators.append(f"uncertainty_language: {', '.join(found_keywords[:3])}")
            
        # Check for hedging phrases
        hedging_phrases = ["i think", "it seems", "it appears", "i believe", "i'm not sure"]
        found_hedging = [phrase for phrase in hedging_phrases if phrase in text_lower]
        if found_hedging:
            indicators.append(f"hedging_language: {', '.join(found_hedging[:2])}")
            
        # Check for question marks (indicating uncertainty)
        if "?" in text:
            indicators.append("contains_questions")
            
        # Check for conditional language
        conditional_words = ["if", "unless", "provided that", "assuming"]
        found_conditional = [word for word in conditional_words if word in text_lower]
        if found_conditional:
            indicators.append(f"conditional_language: {', '.join(found_conditional[:2])}")
            
        # Check response length (very short may indicate insufficient information)
        word_count = len(text.split())
        if word_count < 10:
            indicators.append("response_too_short")
        elif word_count > 300:
            indicators.append("response_very_long")
            
        return indicators
        
    async def create_llm_call_record(
        self,
        prompt: str,
        response: LLMResponse,
        call_id: Optional[str] = None
    ) -> LLMCall:
        """Create LLMCall record for confidence tracking"""
        
        if call_id is None:
            call_id = f"call_{int(time.time() * 1000)}"
            
        return LLMCall(
            call_id=call_id,
            prompt=prompt,
            response=response.text,
            logprobs=response.logprobs or [],
            top_logprobs=response.top_logprobs or [],
            processing_time=response.processing_time,
            token_count=response.tokens_used,
            timestamp=datetime.now()
        )
        
    async def batch_generate(
        self,
        prompts: List[str],
        max_tokens: int = 500,
        temperature: float = 0.1
    ) -> List[LLMResponse]:
        """
        Generate multiple responses in parallel with confidence tracking
        """
        
        tasks = [
            self.generate_with_confidence(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            for prompt in prompts
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid responses
        valid_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"❌ Batch generation failed for prompt {i}: {response}")
                # Create fallback response
                valid_responses.append(LLMResponse(
                    text="Unable to process this request due to technical difficulties.",
                    confidence=0.0,
                    tokens_used=0,
                    processing_time=0.0,
                    model_used="fallback",
                    uncertainty_indicators=["batch_generation_failure"]
                ))
            else:
                valid_responses.append(response)
                
        return valid_responses