"""
Fitness Coach Agent - Built with Sentient Agent Framework
Compatible with Sentient Platform standards
"""

import os
import json
import logging
from typing import Dict, AsyncIterator
from dotenv import load_dotenv

from agent import FitnessCoachAgent

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SentientFitnessAgent:
    """
    Sentient-compatible Fitness Coach Agent
    Follows Sentient Agent Framework standards
    """
    
    # Agent metadata (Sentient standard)
    AGENT_INFO = {
        "name": "Fitness Coach AI",
        "version": "1.0.0",
        "description": "AI-powered fitness and nutrition coach",
        "author": "Your Name",
        "framework": "Sentient Agent Framework",
        "capabilities": [
            "nutrition_tracking",
            "workout_planning",
            "conversation_memory",
            "real_time_coaching"
        ],
        "apis": {
            "nutrition": "Nutritionix API",
            "llm": "OpenRouter (Mistral)"
        }
    }
    
    def __init__(self):
        """Initialize the Sentient-compatible agent"""
        self.agent = FitnessCoachAgent()
        logger.info(f"✅ {self.AGENT_INFO['name']} initialized with Sentient Framework")
    
    async def process_message(self, user_id: str, message: str, context: Dict = None) -> AsyncIterator[str]:
        """
        Process user messages (Sentient standard interface)
        
        Args:
            user_id: Unique user identifier
            message: User's message
            context: Optional context dictionary (Sentient standard)
            
        Yields:
            Response chunks for streaming
        """
        try:
            logger.info(f"📨 Processing message from user: {user_id}")
            
            # Use existing agent logic
            async for chunk in self.agent.process_message(user_id, message):
                yield chunk
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {str(e)}", exc_info=True)
            yield f"\n[Agent error: {str(e)}]\n"
    
    def get_info(self) -> Dict:
        """
        Return agent information (Sentient standard)
        """
        return self.AGENT_INFO
    
    def health_check(self) -> Dict:
        """
        Health check endpoint (Sentient standard)
        """
        return {
            "status": "healthy",
            "agent": self.AGENT_INFO['name'],
            "version": self.AGENT_INFO['version'],
            "framework": "Sentient Agent Framework"
        }

# Export singleton instance
sentient_fitness_agent = SentientFitnessAgent()
