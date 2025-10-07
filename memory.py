import json
import os
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserMemory:
    """Stores user fitness data, preferences, and history"""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_user_file(self, user_id: str) -> str:
        """Get file path for user's data"""
        return os.path.join(self.storage_dir, f"user_{user_id}.json")
    
    async def get_user_context(self, user_id: str) -> Dict:
        """Load user's fitness profile and history"""
        file_path = self._get_user_file(user_id)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading user context: {str(e)}")
        
        return {
            "user_id": user_id,
            "fitness_level": "beginner",
            "goals": [],
            "restrictions": [],
            "preferences": {
                "workout_duration": 30,
                "workout_frequency": 3,
                "equipment": "bodyweight"
            },
            "history": [],
            "created_at": datetime.now().isoformat()
        }
    
    async def save_interaction(
        self, 
        user_id: str, 
        query: str, 
        response: str,
        metadata: Optional[Dict] = None
    ):
        """Save conversation and update user profile"""
        try:
            context = await self.get_user_context(user_id)
            
            context["history"].append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response,
                "metadata": metadata or {}
            })
            
            if len(context["history"]) > 50:
                context["history"] = context["history"][-50:]
            
            file_path = self._get_user_file(user_id)
            with open(file_path, 'w') as f:
                json.dump(context, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving interaction: {str(e)}")
    
    async def update_user_profile(self, user_id: str, updates: Dict):
        """Update user's fitness profile"""
        try:
            context = await self.get_user_context(user_id)
            context.update(updates)
            context["updated_at"] = datetime.now().isoformat()
            
            file_path = self._get_user_file(user_id)
            with open(file_path, 'w') as f:
                json.dump(context, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
