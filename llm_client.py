import httpx
import os
import logging
from typing import AsyncIterator
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Handles all LLM interactions via OpenRouter API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "mistralai/mistral-small-3.2-24b-instruct:free"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": os.getenv("APP_URL", "http://localhost:8000"),
            "X-Title": os.getenv("AGENT_NAME", "Fitness Coach Agent"),
            "Content-Type": "application/json"
        }
        
        self.client = httpx.AsyncClient(timeout=120.0)
        logger.info(f"OpenRouter client initialized with model: {self.model}")
    
    async def extract_food_query(self, user_message: str) -> str:
        """
        Extract just the food items from a user's question
        Example: "How many calories in 3 eggs?" → "3 eggs"
        """
        messages = [
            {
                "role": "system",
                "content": """You are a food query extractor. Extract ONLY the food items and quantities from user questions.

Examples:
- "How many calories in 3 eggs?" → "3 eggs"
- "What's the nutrition for chicken breast and rice?" → "chicken breast and rice"
- "I ate 2 apples today" → "2 apples"
- "100g of salmon" → "100g salmon"
- "Tell me about 3 eggs and oatmeal" → "3 eggs and oatmeal"

Return ONLY the food items with quantities, nothing else. No questions, no extra words."""
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.1,
                    "max_tokens": 50
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                extracted = data["choices"][0]["message"]["content"].strip()
                logger.info(f"📝 Extracted food query: '{user_message}' → '{extracted}'")
                return extracted
            else:
                logger.warning(f"Failed to extract food query (status {response.status_code}), using original")
                return user_message
                
        except Exception as e:
            logger.error(f"Error extracting food query: {e}")
            return user_message
    
    async def stream_completion(self, messages: list) -> AsyncIterator[str]:
        """
        Stream chat completion responses from OpenRouter
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Yields:
            Content chunks as they arrive
        """
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"OpenRouter API error {response.status_code}: {error_text}")
                    yield "\n[Sorry, I'm having trouble connecting right now. Please try again.]\n"
                    return
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            import json
                            data = json.loads(data_str)
                            
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            logger.error(f"Error processing chunk: {e}")
                            continue
                            
        except httpx.TimeoutException:
            logger.error("OpenRouter request timeout")
            yield "\n[Request timed out. Please try again with a shorter message.]\n"
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}", exc_info=True)
            yield "\n[An error occurred. Please try again.]\n"
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
