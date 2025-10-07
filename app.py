import logging
import os
import json
import re
from dotenv import load_dotenv
from sentient_agent_framework import (
    AbstractAgent,
    DefaultServer,
    Session,
    Query,
    ResponseHandler
)
import httpx
from collections import defaultdict

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class FitnessCoachAgent(AbstractAgent):
    """Fitness Coach Agent with AI-powered intent classification."""
    
    def __init__(self, name: str = "Fitness Coach AI"):
        super().__init__(name)
        
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.nutritionix_app_id = os.getenv('NUTRITIONIX_APP_ID')
        self.nutritionix_api_key = os.getenv('NUTRITIONIX_API_KEY')
        
        # Best free model: Mistral Small 3.2 24B
        self.model = "mistralai/mistral-small-3.2-24b-instruct:free"
        
        if not self.openrouter_api_key:
            raise ValueError("❌ OPENROUTER_API_KEY is not set")
        if not self.nutritionix_app_id or not self.nutritionix_api_key:
            raise ValueError("❌ Nutritionix API credentials not set")
        
        self.user_conversations = defaultdict(list)
        
        self.system_prompt = """You are an expert fitness and nutrition coach.

CRITICAL RULES FOR NUTRITION QUERIES:
1. When you receive nutrition data from the API (marked with "NUTRITION DATA FROM NUTRITIONIX API"), you MUST use those EXACT numbers.
2. NEVER estimate or calculate calories yourself - ONLY use API data provided.
3. If no API data is provided, ask for more specific information.
4. DO NOT say things like "1 large egg: approximately 70 calories" - Only use API numbers.

For workout and diet plans:
- Ask clarifying questions about goals, fitness level, equipment, dietary restrictions
- Provide detailed, structured plans with specific exercises, sets, reps
- For diet plans, include meal suggestions with general portions (but NOT specific calorie counts unless using API data)
- Be interactive, personal, and motivating
- Remember previous conversations and reference them"""
        
        logger.info(f"✅ Initialized {name} with {self.model}")
    
    async def assist(self, session: Session, query: Query, response_handler: ResponseHandler):
        """Main method with AI-powered intent classification."""
        user_message = query.prompt
        user_id = getattr(session, 'user_id', 'unknown')
        
        logger.info(f"📩 Query from {user_id}: {user_message}")
        
        stream = response_handler.create_text_stream("response")
        
        try:
            message_lower = user_message.lower()
            
            # AI-powered intent classification
            intent = await self._classify_intent(user_message)
            logger.info(f"🎯 Intent: {intent}")
            
            if intent == 'nutrition':
                # Check for compound queries
                has_compound = any(indicator in message_lower for indicator in [" and ", " with ", ", ", " plus "])
                
                if has_compound:
                    tip = "\n💡 **Tip:** For the most accurate nutrition data, I recommend asking about each food separately. However, I'll do my best with your combined query!\n\n"
                    await stream.emit_chunk(tip)
                
                # Extract food query and get nutrition data
                food_query = await self._extract_food_query(user_message)
                logger.info(f"🍽️ Using food query: '{food_query}'")
                
                nutrition_data = await self._get_nutrition_data_multiple(food_query)
                
                if nutrition_data:
                    nutrition_context = self._format_nutrition_for_llm(nutrition_data)
                    response_text = await self._get_llm_with_context(
                        user_message, user_id, nutrition_context, 'nutrition'
                    )
                else:
                    response_text = "❌ Sorry, couldn't find nutrition info. Try '2 eggs' or '100g chicken'."
            
            elif intent == 'workout':
                response_text = await self._get_llm_response(user_message, user_id, 'workout')
            
            elif intent == 'diet_plan':
                response_text = await self._get_llm_response(user_message, user_id, 'diet_plan')
            
            else:
                response_text = await self._get_llm_response(user_message, user_id, 'general')
            
            # Save to conversation memory
            self.user_conversations[user_id].append({"role": "user", "content": user_message})
            self.user_conversations[user_id].append({"role": "assistant", "content": response_text})
            
            # Keep only last 10 messages
            if len(self.user_conversations[user_id]) > 10:
                self.user_conversations[user_id] = self.user_conversations[user_id][-10:]
            
            logger.info(f"💾 Memory: {len(self.user_conversations[user_id])} messages for {user_id}")
            
            await stream.emit_chunk(response_text)
            logger.info("✅ Response emitted")
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}", exc_info=True)
            await stream.emit_chunk(f"❌ Error: {str(e)}")
        
        try:
            await stream.complete()
            logger.info("✅ Stream completed")
        except Exception as e:
            logger.error(f"❌ Stream completion error: {str(e)}")
    
    async def _classify_intent(self, message: str) -> str:
        """Use AI to classify intent - smart and scalable."""
        message_lower = message.lower()
        
        # Fast path: Obvious workout queries
        if any(kw in message_lower for kw in ['workout', 'exercise', 'training', 'routine', 'gym']):
            return 'workout'
        
        # Fast path: Diet/meal plan queries (NOT specific nutrition data)
        if any(phrase in message_lower for phrase in ['diet plan', 'meal plan', 'give me a plan', 'lose weight plan', 'gain weight plan']):
            return 'diet_plan'
        
        # Fast path: Obvious nutrition queries
        if any(kw in message_lower for kw in ['calories', 'calorie', 'colories', 'nutrition', 'macros']):
            # Use AI to determine if it's specific nutrition data or general advice
            return await self._ai_classify_nutrition(message)
        
        # Check for number + potential food query pattern
        if re.search(r'\d+', message):
            return await self._ai_classify_nutrition(message)
        
        return 'general'
    
    async def _ai_classify_nutrition(self, message: str) -> str:
        """Use AI to determine if this needs nutrition API or general advice."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{
                "role": "user",
                "content": f"""Is this question asking for SPECIFIC nutrition data about food items (calories, macros, etc.)?

Answer ONLY "yes" or "no".

Examples of YES (needs nutrition API):
- "How many calories in 3 eggs?"
- "What's in 100g chicken breast?"
- "3 eggs and toast nutrition"
- "Calories in pizza"

Examples of NO (general advice):
- "What should I eat before gym?"
- "Give me a diet plan"
- "How to lose weight?"
- "Healthy breakfast ideas"

Question: {message}
Answer:"""
            }],
            "temperature": 0.1,
            "max_tokens": 5
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result:
                        answer = result['choices'][0]['message']['content'].strip().lower()
                        if 'yes' in answer:
                            logger.info(f"🤖 AI: Specific nutrition query")
                            return 'nutrition'
                        else:
                            logger.info(f"🤖 AI: General nutrition advice")
                            return 'diet_plan'
        except Exception as e:
            logger.error(f"❌ AI classification error: {str(e)}")
        
        return 'general'
    
    async def _extract_food_query(self, user_message: str) -> str:
        """Extract food items using LLM."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{
                "role": "user",
                "content": f"""Extract ONLY the food items and quantities. Keep all foods mentioned.

Examples:
"How many calories in 3 eggs?" → "3 eggs"
"What's in 3 large eggs with 2 slices of whole wheat toast?" → "3 large eggs and 2 slices whole wheat toast"
"Calories in 100g chicken and rice?" → "100g chicken and rice"

Question: {user_message}
Answer (food items only):"""
            }],
            "temperature": 0.1,
            "max_tokens": 100
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result:
                        extracted = result['choices'][0]['message']['content'].strip()
                        return extracted
        except Exception as e:
            logger.error(f"❌ Extraction error: {str(e)}")
        
        return user_message
    
    async def _get_nutrition_data_multiple(self, query: str) -> dict:
        """Query Nutritionix API - handles multiple foods."""
        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers = {
            "x-app-id": self.nutritionix_app_id,
            "x-app-key": self.nutritionix_api_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={"query": query}, headers=headers, timeout=15.0)
                
                logger.info(f"📡 Nutritionix status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('foods'):
                        foods_data = []
                        for food in result['foods']:
                            foods_data.append({
                                "food_name": food.get('food_name', 'Unknown'),
                                "serving_qty": food.get('serving_qty', 0),
                                "serving_unit": food.get('serving_unit', ''),
                                "serving_weight_grams": food.get('serving_weight_grams', 0),
                                "calories": food.get('nf_calories', 0),
                                "protein": food.get('nf_protein', 0),
                                "carbs": food.get('nf_total_carbohydrate', 0),
                                "fat": food.get('nf_total_fat', 0),
                                "fiber": food.get('nf_dietary_fiber', 0),
                                "sugar": food.get('nf_sugars', 0)
                            })
                        logger.info(f"✅ Got {len(foods_data)} food items")
                        return {"foods": foods_data, "success": True}
        except Exception as e:
            logger.error(f"❌ Nutritionix error: {str(e)}")
        
        return None
    
    def _format_nutrition_for_llm(self, nutrition_data: dict) -> str:
        """Format nutrition data for LLM context."""
        if not nutrition_data or not nutrition_data.get('foods'):
            return ""
        
        context = "===== NUTRITION DATA FROM NUTRITIONIX API =====\n"
        context += "YOU MUST USE THESE EXACT NUMBERS.\n\n"
        
        foods = nutrition_data['foods']
        
        for food in foods:
            context += f"Food: {food['food_name']}\n"
            context += f"Serving: {food['serving_qty']} {food['serving_unit']} ({food['serving_weight_grams']:.0f}g)\n"
            context += f"Calories: {food['calories']:.1f} kcal\n"
            context += f"Protein: {food['protein']:.1f}g\n"
            context += f"Carbs: {food['carbs']:.1f}g\n"
            context += f"Fat: {food['fat']:.1f}g\n"
            context += f"Fiber: {food['fiber']:.1f}g\n"
            context += f"Sugar: {food['sugar']:.1f}g\n\n"
        
        if len(foods) > 1:
            total_cal = sum(f['calories'] for f in foods)
            total_pro = sum(f['protein'] for f in foods)
            total_car = sum(f['carbs'] for f in foods)
            total_fat = sum(f['fat'] for f in foods)
            
            context += f"TOTAL: {total_cal:.1f} kcal | Protein: {total_pro:.1f}g | Carbs: {total_car:.1f}g | Fat: {total_fat:.1f}g\n\n"
        
        context += "===== END OF API DATA =====\n"
        
        return context
    
    async def _get_llm_with_context(self, message: str, user_id: str, nutrition_context: str, context_type: str) -> str:
        """Get LLM response with nutrition data context."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if user_id in self.user_conversations:
            recent_conv = self.user_conversations[user_id][-4:]
            messages.extend(recent_conv)
        
        if nutrition_context:
            messages.append({"role": "user", "content": f"[SYSTEM DATA - USE EXACT NUMBERS]\n\n{nutrition_context}"})
        
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 600
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=60.0)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result:
                        return result['choices'][0]['message']['content']
                else:
                    return f"❌ AI error (status: {response.status_code})"
        except Exception as e:
            logger.error(f"❌ LLM error: {str(e)}")
            return f"❌ Error: {str(e)}"
    
    async def _get_llm_response(self, message: str, user_id: str, context: str = 'general') -> str:
        """Get LLM response with conversation memory."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = self.system_prompt
        
        if context == 'workout':
            system_prompt += "\n\nUser wants a workout plan. Ask about fitness level, goals, available equipment, and time before creating detailed plan."
        elif context == 'diet_plan':
            system_prompt += "\n\nUser wants a diet/meal plan. Ask about goals (weight loss/gain/maintain), dietary restrictions, meal preferences, and typical schedule. DO NOT provide specific calorie counts without using the API."
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if user_id in self.user_conversations:
            messages.extend(self.user_conversations[user_id])
        
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 700
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=60.0)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result:
                        return result['choices'][0]['message']['content']
                else:
                    return f"❌ AI error (status: {response.status_code})"
        except Exception as e:
            logger.error(f"❌ LLM error: {str(e)}")
            return f"❌ Error: {str(e)}"


if __name__ == "__main__":
    try:
        agent = FitnessCoachAgent(name="Fitness Coach AI")
        server = DefaultServer(agent)
        
        logger.info("🚀 Starting Fitness Coach with AI-powered classification...")
        server.run()
        
    except Exception as e:
        logger.error(f"❌ Failed to start: {str(e)}")
        raise
