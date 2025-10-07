import asyncio
import os
import json
import logging
from typing import Dict, AsyncIterator
from dotenv import load_dotenv

from llm_client import OpenRouterClient
from tools.nutrition import NutritionTools
from tools.exercise import ExerciseTools
from memory import UserMemory

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

class FitnessCoachAgent:
    """Production Fitness Coach Agent with comprehensive error handling"""
    
    def __init__(self):
        self.name = os.getenv("AGENT_NAME", "Fitness Coach")
        self.llm = OpenRouterClient()
        self.nutrition = NutritionTools()
        self.exercise = ExerciseTools()
        self.memory = UserMemory()
        
        self.system_prompt = """You are an expert fitness and nutrition coach named {name}.

Your capabilities:
- Create personalized workout plans based on fitness level and goals
- Provide evidence-based nutrition advice and meal planning
- Calculate calories and macronutrients for foods and recipes
- Track user progress over time and adjust recommendations
- Motivate and encourage users on their fitness journey

CRITICAL INSTRUCTION FOR NUTRITION QUERIES:
When you receive nutrition data from the API tools, you MUST use those EXACT numbers in your response.
DO NOT use your own knowledge or estimates when API data is provided.
The API data is always accurate and should be presented exactly as given.

Guidelines:
- Always prioritize safety and proper form
- Recommend consulting healthcare professionals for medical concerns
- Provide specific, actionable advice with clear instructions
- Be encouraging and positive while being realistic
- Ask clarifying questions when needed

When users ask about:
- Workouts: Use the exercise database to create structured plans
- Nutrition: ALWAYS use the exact numbers from API data when provided
- Progress: Reference their history and celebrate improvements

Be conversational, friendly, and professional.""".format(name=self.name)
        
        logger.info(f"{self.name} initialized successfully")
    
    async def process_message(self, user_id: str, message: str) -> AsyncIterator[str]:
        """Process user messages with comprehensive error handling"""
        try:
            logger.info(f"Processing message from user {user_id}: {message[:50]}...")
            
            user_context = await self.memory.get_user_context(user_id)
            
            message_lower = message.lower()
            tool_results = []
            
            # Nutrition detection
            if any(word in message_lower for word in [
                "calories", "nutrition", "food", "meal", "eat",
                "diet", "protein", "carbs", "fat", "macro"
            ]):
                try:
                    logger.info(f"🔍 Nutrition query detected: {message}")
                    
                    # Check for compound queries (multiple foods)
                    has_compound = False
                    compound_indicators = [" and ", " with ", ", ", " plus "]
                    for indicator in compound_indicators:
                        if indicator in message_lower:
                            has_compound = True
                            break
                    
                    # If compound query detected, show helpful tip first
                    if has_compound:
                        yield "\n💡 **Tip:** For the most accurate nutrition data, I recommend asking about each food separately. However, I'll do my best with your combined query!\n\n"
                    
                    # Extract just the food items from the question using LLM
                    food_query = await self.llm.extract_food_query(message)
                    logger.info(f"🍽️ Using food query: '{food_query}'")
                    
                    nutrition_data = await self.nutrition.analyze_food(food_query)
                    logger.info(f"📊 Nutrition API response: {nutrition_data}")
                    
                    if nutrition_data.get("success"):
                        foods = nutrition_data.get("foods", [])
                        
                        # Format nutrition data clearly for the LLM
                        nutrition_text = "===== NUTRITION DATA FROM NUTRITIONIX API =====\n"
                        nutrition_text += "YOU MUST USE THESE EXACT NUMBERS IN YOUR RESPONSE.\n"
                        nutrition_text += "DO NOT ESTIMATE OR USE YOUR OWN KNOWLEDGE.\n\n"
                        
                        for food in foods:
                            nutrition_text += f"Food: {food['name']}\n"
                            nutrition_text += f"Serving Size: {food['serving']}\n"
                            nutrition_text += f"Calories: {food['calories']} kcal\n"
                            nutrition_text += f"Protein: {food['protein']}g\n"
                            nutrition_text += f"Carbohydrates: {food['carbs']}g\n"
                            nutrition_text += f"Fat: {food['fat']}g\n"
                            if food.get('fiber', 0) > 0:
                                nutrition_text += f"Fiber: {food['fiber']}g\n"
                            if food.get('sugar', 0) > 0:
                                nutrition_text += f"Sugar: {food['sugar']}g\n"
                            nutrition_text += "\n"
                        
                        nutrition_text += "===== END OF API DATA =====\n"
                        nutrition_text += "Present these numbers EXACTLY as shown above in your response to the user.\n"
                        
                        tool_results.append(nutrition_text)
                        logger.info(f"✅ Added nutrition data to context")
                    else:
                        logger.warning(f"⚠️ Nutrition API returned error: {nutrition_data.get('error')}")
                        if has_compound:
                            yield "\n⚠️ I had trouble getting accurate data for multiple foods at once. Try asking about each food separately for better results!\n\n"
                        
                except Exception as e:
                    logger.error(f"❌ Nutrition API error: {str(e)}", exc_info=True)
            
            # Workout detection
            if any(word in message_lower for word in [
                "workout", "exercise", "training", "gym",
                "routine", "plan", "muscle", "strength"
            ]):
                try:
                    level = user_context.get("fitness_level", "beginner")
                    duration = user_context.get("preferences", {}).get("workout_duration", 30)
                    
                    focus = None
                    for muscle in ["chest", "legs", "back", "arms", "core", "shoulders", "abs", "cardio"]:
                        if muscle in message_lower:
                            focus = muscle
                            break
                    
                    workout_plan = self.exercise.create_workout_plan(level, duration, focus)
                    tool_results.append(
                        f"===== WORKOUT PLAN FROM EXERCISE DATABASE =====\n{json.dumps(workout_plan, indent=2)}\n===== END OF WORKOUT DATA ====="
                    )
                except Exception as e:
                    logger.error(f"Exercise generation error: {str(e)}")
            
            # Build messages for LLM
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # User context
            context_summary = f"""User Profile:
- Fitness Level: {user_context.get('fitness_level', 'Not set')}
- Goals: {', '.join(user_context.get('goals', [])) or 'Not set'}
- Restrictions: {', '.join(user_context.get('restrictions', [])) or 'None'}
- Interactions: {len(user_context.get('history', []))}"""
            
            messages.append({"role": "system", "content": context_summary})
            
            # Tool results - add as USER message for stronger emphasis
            if tool_results:
                tool_message = "\n\n".join(tool_results)
                messages.append({"role": "user", "content": f"[SYSTEM DATA - USE THESE EXACT NUMBERS]\n\n{tool_message}"})
            
            # Recent history
            for interaction in user_context.get("history", [])[-3:]:
                messages.append({"role": "user", "content": interaction["query"]})
                messages.append({"role": "assistant", "content": interaction["response"]})
            
            # Current message
            messages.append({"role": "user", "content": message})
            
            # Stream response
            full_response = ""
            async for chunk in self.llm.stream_completion(messages):
                full_response += chunk
                yield chunk
            
            # Save interaction
            await self.memory.save_interaction(
                user_id=user_id,
                query=message,
                response=full_response,
                metadata={"tools_used": len(tool_results) > 0}
            )
            
            logger.info(f"Successfully processed message for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            yield "\n[I'm experiencing technical difficulties. Please try again in a moment.]\n"
