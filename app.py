from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
import json
import os
import io
import base64
from dotenv import load_dotenv
import re
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional, Union


class NutriInfo(BaseModel):
    # Removed `None` from Field's default argument
    Protein: Optional[int] = Field(description="Protein content in grams (integer)")
    Total_Fat: Optional[int] = Field(alias="Total Fat", description="Total Fat content in grams (integer)")
    Carbohydrates: Optional[int] = Field(description="Carbohydrates content in grams (integer)")
    Calories: Optional[int] = Field(description="Calories in kcal (integer)")
    Sugars: Optional[int] = Field(description="Sugars content in grams (integer)")
    Sodium: Optional[int] = Field(description="Sodium content in mg (integer)")
    Per_Serving_Household_Measure: Optional[str] = Field(
        alias="Per Serving Household Measure", description="Per Serving Household Measure (string, e.g., '100g', '1 cup', or 'N/A')"
    )
    Iron: Optional[int] = Field(description="Iron content in mg (integer)")
    Vitamin_A: Optional[int] = Field(alias="Vitamin A", description="Vitamin A content in mcg (integer)")
    Vitamin_C: Optional[int] = Field(alias="Vitamin C", description="Vitamin C content in mg (integer)")
    Vitamin_D: Optional[int] = Field(alias="Vitamin D", description="Vitamin D content in IU (integer)")

class FoodDish(BaseModel):
    # dishName still uses `...` because it's required and has no default
    dishName: str = Field(..., description="The name of the food dish. If not a food item, set to 'Not a food item'.")
    # For list defaults, setting [] directly on the annotation is fine
    # or you can use Field(default_factory=list) if it's a mutable default.
    # The current `Field([], ...)` is generally fine.
    Ingredients: List[str] = Field(description="List of ingredients recalled; empty if not food")
    Nutrients: NutriInfo = Field(..., description="Nutritional information for the food dish")


load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Load nutrition data
def load_nutrition_data(nutrition_file_path: str) -> dict:
    """Load nutrition data from JSON file"""
    try:
        with open(nutrition_file_path, 'r', encoding='utf-8') as file:
            nutrition_data = json.load(file)

        numeric_fields = [
            'B-Carotene', 'Calcium', 'Carbohydrate', 'Cholesterol',
            'Dietary fibre', 'Energy', 'Iron', 'Monounsaturated fat',
            'Phosphorus', 'Polyunsaturated fat', 'Potassium', 'Protein',
            'Retinol', 'Riboflavin', 'Saturated fat', 'Selenium',
            'Sodium', 'Starch', 'Sugar', 'Thiamin', 'Total fat',
            'Vitamin A', 'Vitamin C', 'Vitamin D', 'Water',
            'Whole-grains', 'Zinc'
        ]

        nutrition_map = {}
        for dish, entry in nutrition_data.items():
            dish_data = entry.copy()
            for field in numeric_fields:
                val = dish_data.get(field, None)
                try:
                    dish_data[field] = float(val) if val not in [None, "", " "] else None
                except Exception:
                    dish_data[field] = None
            nutrition_map[dish.lower().replace(" ", "_")] = dish_data

        return nutrition_map
    except Exception as e:
        print(f"Error loading nutrition data: {e}")
        return {}

# Load nutrition data on startup
nutrition_map = load_nutrition_data("Final_key_value_pair.json")
# print(nutrition_map)

def predict_food_and_nutrition(image):
    """Predict food and nutrition from image using Gemini API"""
    try:
        with open("Final_key_value_pair.json", 'r', encoding='utf-8') as file:
            nutrition_data = json.load(file)
        class_names = list(nutrition_data.keys())
        prompt = f"""
        You are a culinary expert specializing in Singaporean cuisine. Given an image of a food item, first carefully examine its visual appearance, ingredients, and likely cooking techniques to infer how it was prepared. Based on this analysis, classify the dish into one of the following categories:
        Food classes: [{', '.join(class_names)}]
        If you are confident that the dish is not listed above, set dishName to your most promising guess based on its appearance and ingredients.
        After identifying the most promising dish, recall the ingredients used in making that dish and list them in the response accordingly.
        In case of Nutrition information use average values. Note that the nutrition information must be according to the portion size of the dish.

        Ensure all fields are populated:
        - `dishName`: The name of the food dish. If not a food item set to "Not a food item".
        - `Ingredients`: A list of recalled ingredients. If no ingredients are visible or identifiable, provide an empty list.
        - `Nutrients`: Provide detailed nutritional information. If specific nutrient values cannot be determined, use 0 for integers and "N/A" for 'Per Serving Household Measure'.
        **Strictly adhere to the provided schema and do not return any other text.**

        """

        response = model.generate_content(
            contents=[prompt, image], # Pass your prompt and the loaded image object here
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": FoodDish, # Use the Pydantic model for structured response
            }
        )

        # print("response:", response)  # Debugging output
        json_str = response.text.strip()
        if json_str.startswith("```"):
            json_str = re.sub(r"^```[a-zA-Z]*\n?", "", json_str)
            json_str = re.sub(r"\n?```$", "", json_str)

        # print("response:",response,"Raw Gemini response:", repr(json_str))

        # Check if the response is empty
        if not json_str:
            raise Exception("Gemini API returned an empty response.")

        try:
            food_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            # print("Raw Gemini response:", repr(json_str))  # For debugging
            raise Exception(f"Invalid JSON from Gemini API: {e}\nRaw response: {json_str}")

        # --- Nutrition map lookup ---
        dish_key = food_data.get("dishName", "").lower().replace(" ", "_")
        nutrition_info = nutrition_map.get(dish_key)

        # Map your nutrition fields to the required output keys
        field_map = {
            "Protein": ["Protein (g)", "Protein"],
            "Total Fat": ["Total fat (g)", "Total Fat"],
            "Carbohydrates": ["Carbohydrate (g)", "Carbohydrates"],
            "Calories": ["Energy (kcal)", "Calories"],
            "Sugars": ["Sugar (g)", "Sugars"],
            "Sodium": ["Sodium (mg)", "Sodium"],
            "Per Serving Household Measure": ["Per Serving Household Measure"],
            "Iron": ["Iron (mg)", "Iron"],
            "Vitamin A": ["Vitamin A (mcg)", "Vitamin A"],
            "Vitamin C": ["Vitamin C (mg)", "Vitamin C"],
            "Vitamin D": ["Vitamin D (IU)", "Vitamin D"]
        }

        # Initialize nutrients dictionary
        if nutrition_info:
            nutrients = {}
            for out_key, possible_keys in field_map.items():
                value = None
                for k in possible_keys:
                    if k in nutrition_info and nutrition_info[k] not in [None, "", " "]:
                        value = nutrition_info[k]
                        break
                # Try to convert to float and then int if possible, else keep as string
                if value is not None:
                    try:
                        value = float(value)
                        # Per Serving can be string (e.g., "Plate-23cm (400g)")
                        if out_key not in ["Per Serving Household Measure"]:
                            value = int(round(value))
                    except Exception:
                        pass
                # If not found in map, fallback to Gemini's value
                if value is None and "Nutrients" in food_data and out_key in food_data["Nutrients"]:
                    value = food_data["Nutrients"][out_key]
                nutrients[out_key] = value
            food_data["Nutrients"] = nutrients

            # Add per serving info to dish name if available
            per_serving = nutrients.get("Per Serving Household Measure")
            if per_serving:
                food_data["dishName"] = f'{food_data["dishName"]} ({per_serving})'

        return food_data

    except Exception as e:
        raise Exception(f"Error in food prediction: {str(e)}")


def process_image(image_data):
    """Process base64 image data"""
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Resize image
        target_size = (224, 224)
        image.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Create new image with white background
        new_image = Image.new("RGB", target_size, (255, 255, 255))
        offset = ((target_size[0] - image.size[0]) // 2,
                  (target_size[1] - image.size[1]) // 2)
        new_image.paste(image, offset)
        
        return new_image
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_food():
    """API endpoint to analyze food image"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Process the image
        processed_image = process_image(data['image'])
        
        # Get food prediction
        food_data = predict_food_and_nutrition(processed_image)
        # print("Food data:", food_data)  # Debugging output
    # Use food_data dictionary and return relevant information

    # return food_data
    
        return jsonify({
            'success': True,
            'data': food_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

if __name__ == '__main__':
    # Ensure the nutrition data is loaded before starting the app
    app.run(debug=True, host='0.0.0.0', port=5000)
