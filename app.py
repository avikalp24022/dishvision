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

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

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
print(nutrition_map)

def predict_food_and_nutrition(image):
    """Predict food and nutrition from image using Gemini API"""
    try:
        with open("Final_key_value_pair.json", 'r', encoding='utf-8') as file:
            nutrition_data = json.load(file)
        class_names = list(nutrition_data.keys())
        # class_names = [
        #     "Ayam penyet with rice",
        #     "BBQ Turkey Bacon Double Cheeseburger, Burger King",
        #     "Bak kut teh",
        #     "Bak kut teh, soup only",
        #     "Baked durian mooncake",
        #     "Ban mian soup",
        #     "Banana fritter",
        #     "Beans broad, coated with satay powder, deep fried",
        #     "Beef ball kway teow soup",
        #     "Beef burger with cheese",
        #     "Beef noodles soup",
        #     "Beef rendang",
        #     "Beef satay, without satay sauce",
        #     "Beef, rendang with soya sauce, simmered (Malay)",
        #     "Biscuit, savoury, salada style",
        #     "Braised duck rice",
        #     "Braised duck with yam rice",
        #     "Braised pork ribs with black bean sauce",
        #     "Brown rice laksa noodles, cooked",
        #     "Brown rice porridge, plain",
        #     "Bulgogi Gimbap (Korean Rice Roll with Spicy Beef)",
        #     "Caesar salad",
        #     "Cafe 26 oriental salad dressing",
        #     "Cafe 26 tangy salad dressing",
        #     "Carrot cake with egg, plain, mashed & fried",
        #     "Cereal prawn",
        #     "Char kway teow",
        #     "Char siew chee cheong fun",
        #     "Chee cheong fun",
        #     "Chee pah",
        #     "Cheesy BBQ Meltz, KFC",
        #     "Chendol",
        #     "Chendol, durian",
        #     "Chendol, mango",
        #     "Chicken briyani",
        #     "Chicken curry noodles",
        #     "Chicken satay, without peanut sauce",
        #     "Chilli crab",
        #     "Chwee kueh",
        #     "Claypot rice with salted fish,chicken and chinese sausages",
        #     "Claypot rice, with mixed vegetable",
        #     "Claypot rice, with prawn",
        #     "Claypot rice, with stewed beef",
        #     "Coconut kueh tutu",
        #     "Curry fish head",
        #     "Curry puff, beef",
        #     "Curry puff, chicken",
        #     "Curry puff, frozen, deep fried",
        #     "Curry puff, potato and mutton filling, deep fried",
        #     "Curry puff, potato, and spices, deep fried",
        #     "Curry puff, twisted",
        #     "Deep fried carrot cake",
        #     "Deep fried fish bee hoon soup with milk",
        #     "Dim sum, beancurd roll",
        #     "Dim sum, chicken feet with dark sauce, stewed",
        #     "Dim sum, dumpling, chives with minced prawn, steamed",
        #     "Dim sum, dumpling, yam, deep fried",
        #     "Dim sum, pork ribs",
        #     "Dim sum, pork tart, BBQ",
        #     "Dim sum, sharkfin dumpling",
        #     "Dim sum, siew mai, steamed",
        #     "Dim sum, turnip cake, steamed",
        #     "Dim sum, you tiao",
        #     "Dodol berdurian",
        #     "Double Cheeseburger, McDonalds'",
        #     "Drunken prawn",
        #     "Dry prawn noodles",
        #     "Duck rice, with skin removed",
        #     "Durian",
        #     "Durian Pancake",
        #     "Durian cake",
        #     "Durian fermented",
        #     "Durian ice kacang",
        #     "Durian pudding",
        #     "Durian puff",
        #     "Durian wafer",
        #     "Durian, Malaysian, mid-range",
        #     "Durian, raw",
        #     "Fast foods, salad, vegetable, tossed, without dressing, with chicken",
        #     "Fish ball mee pok, dry",
        #     "Fish ball noodles dry",
        #     "Fish finger, grilled or baked",
        #     "Fish head ban mian soup",
        #     "Fish ngoh hiang",
        #     "Fish satay snack",
        #     "Fried mee siam",
        #     "Fried plain carrot cake",
        #     "Fried vegetarian bee hoon, plain",
        #     "Frog leg claypot rice",
        #     "Fruit salad, canned in heavy syrup",
        #     "Fruit salad, canned in heavy syrup, drained",
        #     "Fruit salad, canned in pear juice",
        #     "Fruit salad, canned in pear juice, drained",
        #     "Fruit salad, canned in pineapple juice",
        #     "Fruit salad, canned in pineapple juice, drained",
        #     "Fruit salad, canned in syrup",
        #     "Fruit salad, canned in syrup, drained",
        #     "Grains based salad with 3 vegetable toppings, no dressing",
        #     "Grains based salad with chicken and 3 vegetable toppings, no dressing",
        #     "Grains based salad with fish and 3 vegetable toppings, no dressing",
        #     "Gravy, assam pedas",
        #     "Gravy, for Indian rojak",
        #     "Gravy, laksa",
        #     "Gravy, mee rebus",
        #     "Gravy, mee siam",
        #     "Grilled stingray with sambal",
        #     "Ham Salad, Subway",
        #     "Hokkien mee",
        #     "Hot and spicy beef noodles soup",
        #     "Ice kachang",
        #     "Indian rojak, tempeh, battered, fried",
        #     "Japanese Pork Ramen",
        #     "Japanese shio ramen",
        #     "Japanese shoyu ramen",
        #     "Kaya Toast with Butter",
        #     "Kopi",
        #     "Kopi C",
        #     "Kopi C siu dai",
        #     "Kopi O",
        #     "Kopi O siu dai",
        #     "Kopi siu dai",
        #     "Korean bulgogi beef with rice",
        #     "Kuih apam balik",
        #     "Kuih bangkit sagu",
        #     "Kuih koci pulut hitam",
        #     "Kuih sagu",
        #     "Kway chap",
        #     "Kway chap, noodles only",
        #     "Kway teow soup, with beef balls",
        #     "Laksa",
        #     "Laksa lemak, without gravy",
        #     "Laksa noodles, cooked",
        #     "Laksa yong tauhu",
        #     "Laksa, leaf, fresh",
        #     "Liver roll ngoh hiang",
        #     "Lontong goreng",
        #     "Lor mee",
        #     "Lor mee (NEW)",
        #     "Ma La Xiang Guo",
        #     "Mee goreng",
        #     "Mee goreng, mamak style",
        #     "Mee rebus",
        #     "Mee rebus, without gravy",
        #     "Mee siam",
        #     "Mee siam, without gravy",
        #     "Mee soto",
        #     "Mushrooom Fritter (Fried Mushroom)",
        #     "Mutton briyani",
        #     "Mutton curry puff",
        #     "Mutton satay, without satay sauce",
        #     "Nasi Lemak with chicken wing",
        #     "Nasi briyani, rice only",
        #     "Nasi lemak with fried egg only",
        #     "Nasi lemak, rice only",
        #     "Ngoh hiang, meat roll",
        #     "Ngoh hiang, meat roll, bung bung",
        #     "Ngoh hiang, mixed items",
        #     "Ngoh hiang, prawn fritter, crispy",
        #     "Ngoh hiang, prawn fritter, dough",
        #     "Ngoh hiang, sausage",
        #     "Ngoh hiang, yam meat roll",
        #     "Noodles, instant, chicken curry, with seasoning, uncooked",
        #     "Noodles, laksa, thick, dried",
        #     "Noodles, laksa, thick, wet",
        #     "Noodles, with prawn, tofu and vegetables, soup",
        #     "Omelette, oyster",
        #     "Otak",
        #     "Otak, shrimp",
        #     "Otak, sotong",
        #     "Oven Roasted Chicken Breast Salad, Subway",
        #     "Pandan chiffon cake",
        #     "Paru goreng",
        #     "Paste, hainanese chicken rice",
        #     "Paste, laksa, commercial",
        #     "Paste, mee rebus",
        #     "Paste, mee siam, commercial",
        #     "Peanut kueh tutu",
        #     "Penang laksa",
        #     "Penang prawn noodle",
        #     "Pig's liver soup",
        #     "Plain roti prata",
        #     "Pop corn, durian flavoured",
        #     "Popiah",
        #     "Popiah circular shape, skin only",
        #     "Popiah skin",
        #     "Pork satay, with satay sauce",
        #     "Potato curry puff",
        #     "Prawn cocktail",
        #     "Prawn noodles soup",
        #     "Pulut hitam with coconut milk",
        #     "Pulut hitam, served with coconut milk",
        #     "Red rice porridge, plain",
        #     "Rendang hati ayam",
        #     "Rice porridge, fish, dry",
        #     "Roast Beef Salad, Subway",
        #     "Roasted duck rice",
        #     "Roti john",
        #     "Salad with 3 vegetable toppings, no dressing",
        #     "Salad with chicken and 3 vegetable toppings, no dressing",
        #     "Salad with chicken and 4 vegetable toppings, no dressing",
        #     "Salad with fish and 3 vegetable toppings, no dressing",
        #     "Salad, ocean chef, Long John Silver's",
        #     "Salad, seafood, Long John Silver's",
        #     "Salad, vegetable, tossed, without dressing",
        #     "Sandwiches and burgers, roast beef sandwich with cheese",
        #     "Sardine curry puff",
        #     "Satay bee hoon",
        #     "Satay sauce",
        #     "Satay, beef, frozen",
        #     "Satay, chicken, canned",
        #     "Satay, chicken, frozen",
        #     "Satay, mutton, frozen",
        #     "Sauce, BBQ, McDonalds'",
        #     "Sauce, chee cheong fun",
        #     "Sausage, cocktail, chicken, boiled",
        #     "Sayur lodeh",
        #     "Shrimp chee cheong fun",
        #     "Soto ayam",
        #     "Soup, pig's liver , chinese spinach",
        #     "Spicy cucumber salad with coconut milk",
        #     "Subway Club Salad, Subway",
        #     "Sup tulang",
        #     "Sushi roll",
        #     "Sushi, california roll",
        #     "Sushi, raw tuna, roll",
        #     "Sushi, roll, cucumber",
        #     "Sushi, roll, futomaki",
        #     "Sushi, tuna salad",
        #     "Sweet Onion Chicken Teriyaki Salad, Subway",
        #     "Sweet potato ondeh ondeh",
        #     "Thai chicken feet salad",
        #     "Thai mango salad",
        #     "Thunder Tea Rice with Soup",
        #     "Traditional ondeh ondeh",
        #     "Tuna, salad, with thousand island dressing, canned",
        #     "Turkey Breast Salad, Subway",
        #     "Turtle soup",
        #     "Vadai with kacang hitam",
        #     "Vadai, kacang dal kuning",
        #     "Vegetable briyani",
        #     "Vegetarian brown rice porridge",
        #     "Vegetarian fried bee hoon",
        #     "Veggie Delite Salad, Subway",
        #     "Yong tau foo, beancurd skin, deep fried",
        #     "Yong tau foo, bittergourd with fish paste, boiled",
        #     "Yong tau foo, chilli sauce",
        #     "Yong tau foo, eggplant with fish paste",
        #     "Yong tau foo, fishmeat wrapped with taukee",
        #     "Yong tau foo, mixed items, noodles not included",
        #     "Yong tau foo, okra with fish paste",
        #     "Yong tau foo, pork skin, deep fried",
        #     "Yong tau foo, red chilli with fish",
        #     "Yong tau foo, red sauce",
        #     "Yong tau foo, squid roll",
        #     "Yong tau foo, taupok with fish paste",
        #     "Yong tau foo, tofu with fish paste",
        #     "You tiao",
        #     "Chicken murtabak",
        #     "Coleslaw, KFC",
        #     "Coleslaw, Long John Silver's",
        #     "Cucur badak",
        #     "Cucur udang",
        #     "Dressing, coleslaw, reduced fat, commercial",
        #     "Dressing, coleslaw, regular, commercial",
        #     "Dry minced pork and mushroom noodles",
        #     "Green wanton noodles dry",
        #     "Hong Kong wanton noodles, dry",
        #     "Kuih lompang",
        #     "Mushroom and minced pork noodles soup",
        #     "Paper thosai",
        #     "Rawa thosai",
        #     "Roasted duck",
        #     "Roasted duck rice",
        #     "Roasted duck without skin",
        #     "Roasted mock duck",
        #     "Thosai",
        #     "Thosai masala",
        #     "Vegetable murtabak",
        #     "Wanton noodles dry",
        #     "Wanton noodles soup",
        #     "gulai duan ubi",
        #     "Har cheong gai",
        #     "Nasi padang",
        #     "Economy rice (mixed rice)",
        #     "Taco"
        # ]
        prompt = f"""
        You are a culinary expert specializing in Singaporean cuisine. Given an image of a food item, first carefully examine its visual appearance, ingredients, and likely cooking techniques to infer how it was prepared. Based on this analysis, classify the dish into one of the following categories:
        Food classes: [{', '.join(class_names)}]
        If you are confident that the dish is not listed above, set dishName to your most promising guess based on its appearance and ingredients.
        After identifying the most promising dish, recall the ingredients used in making that dish and list them in the response accordingly.
        In case of Nutrition information use average values. Note that the nutrition information must be according to the portion size of the dish.
        """

        prompt+="""Respond as a JSON String in the following format and nothing else:
        {
            "dishName": "the food dish name",
            "Ingredients": [ /* list of ingredients recalled; empty if not food */ ],
            "Nutrients": {
                "Protein": x,        // in grams (integer)
                "Total Fat": y,            // in grams (integer)
                "Carbohydrates": z,   // in grams (integer)
                "Calories": a, // in kcal (integer)
                "Sugars": b, // in grams (integer)
                "Sodium": c, // in mg (integer)
                "Per Serving Household Measure" : d // in grams (integer)
            }
        }
        Do not include any additional text or explanation.
        """

        response = model.generate_content([prompt, image])
        json_str = response.text.strip()
        # Remove Markdown code block markers if present
        if json_str.startswith("```"):
            json_str = re.sub(r"^```[a-zA-Z]*\n?", "", json_str)
            json_str = re.sub(r"\n?```$", "", json_str)

        print("Gemini raw response:", repr(json_str))

        if not json_str:
            raise Exception("Gemini API returned an empty response.")

        try:
            food_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print("Raw Gemini response:", repr(json_str))  # For debugging
            raise Exception(f"Invalid JSON from Gemini API: {e}\nRaw response: {json_str}")

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
    app.run(debug=True, host='0.0.0.0', port=5000)
