import httpx
import os
from typing import Dict
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class NutritionTools:
    """Handles nutrition API calls via Nutritionix"""
    
    def __init__(self):
        self.nutritionix_id = os.getenv('NUTRITIONIX_APP_ID')
        self.nutritionix_key = os.getenv('NUTRITIONIX_API_KEY')
    
    async def analyze_food(self, query: str) -> Dict:
        """
        Analyze nutrition for natural language food queries
        Uses Nutritionix API (200 free requests/day)
        """
        if not self.nutritionix_id or not self.nutritionix_key:
            return {"error": "Nutritionix API keys not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"🔍 Nutritionix API: '{query}'")
                
                response = await client.post(
                    "https://trackapi.nutritionix.com/v2/natural/nutrients",
                    headers={
                        "x-app-id": self.nutritionix_id,
                        "x-app-key": self.nutritionix_key,
                        "Content-Type": "application/json"
                    },
                    json={"query": query},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    foods = data.get("foods", [])
                    
                    if not foods:
                        return {"error": "No food data found"}
                    
                    result_foods = []
                    for food in foods:
                        food_data = {
                            "name": food.get("food_name", "Unknown"),
                            "serving": f"{food.get('serving_qty', 1)} {food.get('serving_unit', '')}".strip(),
                            "calories": round(float(food.get("nf_calories", 0)), 1),
                            "protein": round(float(food.get("nf_protein", 0)), 1),
                            "carbs": round(float(food.get("nf_total_carbohydrate", 0)), 1),
                            "fat": round(float(food.get("nf_total_fat", 0)), 1),
                            "fiber": round(float(food.get("nf_dietary_fiber", 0)), 1),
                            "sugar": round(float(food.get("nf_sugars", 0)), 1)
                        }
                        
                        logger.info(f"✅ {food_data['name']}: {food_data['calories']} kcal")
                        result_foods.append(food_data)
                    
                    return {"success": True, "foods": result_foods}
                    
                elif response.status_code == 404:
                    return {"error": "Food not found"}
                else:
                    logger.error(f"Nutritionix error: {response.status_code}")
                    return {"error": f"API error {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Nutritionix exception: {str(e)}", exc_info=True)
            return {"error": str(e)}
