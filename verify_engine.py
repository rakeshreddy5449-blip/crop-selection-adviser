
import sys
import os

# Add src folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from recommendation_engine import RecommendationEngine

print("Initializing Crop Recommendation Engine...")

try:
    engine = RecommendationEngine()

    print("\nSUCCESS!")
    print("Recommendation Engine initialized.")
    print("ML models and agronomic rules are connected.")

except Exception as e:
    print("\nENGINE INITIALIZATION FAILED")
    print(type(e).__name__, "-", e)
