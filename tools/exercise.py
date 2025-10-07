from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ExerciseTools:
    """Exercise database and workout plan generator"""
    
    def __init__(self):
        self.exercises_db = {
            "chest": [
                {
                    "name": "Push-ups",
                    "equipment": "bodyweight",
                    "difficulty": "beginner",
                    "instructions": "Start in plank position, lower body until chest nearly touches floor, push back up",
                    "reps": "3 sets of 10-15 reps"
                },
                {
                    "name": "Bench Press",
                    "equipment": "barbell",
                    "difficulty": "intermediate",
                    "instructions": "Lie on bench, lower bar to chest, press up until arms extended",
                    "reps": "3 sets of 8-12 reps"
                },
                {
                    "name": "Dumbbell Flyes",
                    "equipment": "dumbbells",
                    "difficulty": "intermediate",
                    "instructions": "Lie on bench with dumbbells above chest, lower arms out to sides, bring back up",
                    "reps": "3 sets of 10-12 reps"
                }
            ],
            "legs": [
                {
                    "name": "Bodyweight Squats",
                    "equipment": "bodyweight",
                    "difficulty": "beginner",
                    "instructions": "Stand with feet shoulder-width, lower hips back and down, stand back up",
                    "reps": "3 sets of 15-20 reps"
                },
                {
                    "name": "Lunges",
                    "equipment": "bodyweight",
                    "difficulty": "beginner",
                    "instructions": "Step forward, lower back knee toward ground, push back to start",
                    "reps": "3 sets of 10 reps per leg"
                },
                {
                    "name": "Barbell Squats",
                    "equipment": "barbell",
                    "difficulty": "intermediate",
                    "instructions": "Bar on upper back, squat down until thighs parallel, drive up through heels",
                    "reps": "3 sets of 8-12 reps"
                }
            ],
            "back": [
                {
                    "name": "Pull-ups",
                    "equipment": "pull-up bar",
                    "difficulty": "intermediate",
                    "instructions": "Hang from bar, pull body up until chin over bar, lower with control",
                    "reps": "3 sets of 5-10 reps"
                },
                {
                    "name": "Bent-over Rows",
                    "equipment": "barbell",
                    "difficulty": "intermediate",
                    "instructions": "Bend at hips with bar hanging, pull bar to lower chest, lower with control",
                    "reps": "3 sets of 8-12 reps"
                }
            ],
            "arms": [
                {
                    "name": "Bicep Curls",
                    "equipment": "dumbbells",
                    "difficulty": "beginner",
                    "instructions": "Hold dumbbells at sides, curl up to shoulders, lower with control",
                    "reps": "3 sets of 10-15 reps"
                },
                {
                    "name": "Tricep Dips",
                    "equipment": "parallel bars",
                    "difficulty": "beginner",
                    "instructions": "Support body on bars, lower until elbows at 90 degrees, push back up",
                    "reps": "3 sets of 8-12 reps"
                }
            ],
            "core": [
                {
                    "name": "Planks",
                    "equipment": "bodyweight",
                    "difficulty": "beginner",
                    "instructions": "Hold push-up position on forearms, keep body straight",
                    "reps": "3 sets of 30-60 seconds"
                },
                {
                    "name": "Crunches",
                    "equipment": "bodyweight",
                    "difficulty": "beginner",
                    "instructions": "Lie on back with knees bent, lift shoulders off ground, lower with control",
                    "reps": "3 sets of 15-20 reps"
                }
            ]
        }
    
    def get_exercises_by_muscle(self, muscle_group: str, difficulty: str = "beginner") -> List[Dict]:
        """Get exercises for specific muscle group"""
        muscle = muscle_group.lower()
        exercises = self.exercises_db.get(muscle, [])
        
        filtered = [e for e in exercises if e["difficulty"] == difficulty.lower()]
        return filtered if filtered else exercises
    
    def create_workout_plan(
        self, 
        level: str, 
        duration_minutes: int,
        focus: Optional[str] = None
    ) -> Dict:
        """Generate a complete workout plan"""
        plan = {
            "duration": f"{duration_minutes} minutes",
            "level": level,
            "warm_up": [
                "5 minutes light cardio (jogging, jumping jacks)",
                "Dynamic stretching (leg swings, arm circles)",
                "Joint mobility exercises"
            ],
            "main_workout": [],
            "cool_down": [
                "5 minutes light cardio (walking)",
                "Static stretching - hold each stretch 30 seconds",
                "Deep breathing exercises"
            ]
        }
        
        if focus:
            exercises = self.get_exercises_by_muscle(focus, level)
            plan["main_workout"] = exercises[:4]
        else:
            for muscle in ["chest", "legs", "back", "arms", "core"]:
                exercises = self.get_exercises_by_muscle(muscle, level)
                if exercises:
                    plan["main_workout"].append(exercises[0])
        
        return plan
