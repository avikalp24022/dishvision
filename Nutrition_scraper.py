from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import json
import re
import csv

# Initialize WebDriver (Ensure you have the correct driver for your browser)
driver = webdriver.Chrome()  # Replace with the path to your ChromeDriver if needed

# Open the website
url = "https://focos.hpb.gov.sg/eservices/ENCF/"
driver.get(url)

dishes = [
    "Hainanese Chicken Rice",
    # "Chilli Crab",
    # "Laksa",
    # "Char Kway Teow",
    # "Nasi Lemak",
    # "Bak Kut Teh",
    # "Fish Head Curry",
    # "Hokkien Mee",
    # "Sambal Stingray",
    # "Mee Goreng",
    # "Fried Carrot Cake",
    # "Kaya Toast",
    # "Roti Prata",
    # "Satay",
    # "Oyster Omelette",
    # "Prawn noodle",
    # # "Bak Chor Mee",
    # # "Wanton Mee",
    # "Popiah",
    # "Curry Puff",
    # "Dim Sum",
    # "Duck Rice",
    # # "Frog Porridge",
    # "rice Porridge",
    # "Lor Mee",
    # "Mee Rebus",
    # "Mee Siam",
    # "Apam balik",
    # # "Nasi Padang",
    # "Korean Bulgogi Beef",

    # "Ngoh Hiang",
    # "Kway Chap",
    # "Ice Kachang",
    # "Chendol",
    # "Pandan Chiffon Cake",
    # "Briyani",
    # "Beef Rendang",
    # "Ma la Xiang Guo",
    # # "Har Cheong Gai",
    # "Roast Duck Rice",
    # "Roti John",
    # "Thunder Tea Rice",
    # # "Economy Rice",
    # "Lontong",
    # "Sambal Stingray",
    # "Vadai",
    # "Durian",
    # "Chee Cheong Fun",
    # "Kueh Tutu",
    # # "Gulai Daun Ubi",
    # "Ayam Penyet",
    # "Ban Mian soup",
    # "Beef Kway Teow",
    # "Beef Noodle Soup",
    # "Chwee Kueh",
    # "Claypot Rice",
    # # "Crab Bee Hoon",
    # "Curry Chicken Noodles",
    # "Cereal Prawn",
    # "Drunken Prawn",

    # "Fish Soup Bee Hoon",
    # "Fish ball Noodles dry",
    # "Pulut hitam",
    # "Ondeh Ondeh",
    # "Hainanese Chicken Rice",
    # "Indian Rojak",
    # "Grilled Fish",
    # "Kopi",
    # "Mee Pok",
    # "Mee Soto",
    # "Otak Otak",
    # "Pig liver Soup",
    # # "pig",
    # "banana fritter",
    # "Paru Goreng",
    # "You Tiao",
    # "Satay Bee Hoon",
    # "Sayur Lodeh",
    # "Shredded Chicken Noodles",
    # "Soto Ayam",
    # "Sup Tulang",
    # "Turtle Soup",
    # "Vegetarian Bee Hoon",
    # "Kuih Sagu",
    # "Assam Pedas",
    # "Kuih apam balik",
    # "Braised pork ribs with black bean sauce",
    # "Chee pah",
    # "Beef Burger",
    # "Rendang Hati Ayam",
    # "Yong Tau Foo",

    # "Laksa Pasta",
    # # "Korean BBQ Dishes",
    # "bbq",
    # "Japanese Ramen",
    # "Mexican Tacos",
    # "Sushi Roll",
    # "Cold Brew Coffee",
    # # "Clarified Cocktails",
    # "cocktail",
    # "Double Cheeseburger, McDonalds",
    # "salad",
    # "fried Mushroom fritter"
]


# nutrients = [
#     "Carbohydrate", "Protein"
# ]  # Add all required nutrients here

nutrients = [
    # "B-Carotene",
    # "Calcium",
    "Carbohydrate",
    # "Cholesterol",
    # "Dietary fibre",
    # "Energy",
    # "Iron",
    # "Monounsaturated fat",
    # "Phosphorus",
    # "Polyunsaturated fat",
    # "Potassium",
    # "Protein",
    # "Retinol",
    # "Riboflavin",
    # "Saturated fat",
    # "Selenium",
    # "Sodium",
    # "Starch",
    # "Sugar",
    # "Thiamin",
    # "Total fat",
    # "Vitamin A",
    # # "Vitamin B1",
    # # "Vitamin B2",
    # # "Vitamin B3",
    # # "Vitamin B5",
    # "Vitamin C",
    # "Vitamin D",
    # "Water",
    # "Whole-grains",
    # "Zinc"
]
# Data storage
all_match_data = []
json_file_path = 'Final_all_nutrition_per_serving.json'

# Loop through each dish
for dish in dishes:
    row = {"Dish": dish}
    
    # Input the dish name
    food_name_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "txtFoodName"))
    )
    food_name_input.clear()
    food_name_input.send_keys(dish)
    
    # Loop through each nutrient
    for nutrient in nutrients:
        try:
            # Select the nutrient from the dropdown menu
            nutrient_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlNutrient"))
            )
            select_nutrient = Select(nutrient_dropdown)
            select_nutrient.select_by_visible_text(nutrient)
            
            # Wait for and select the radio button for Per serving edible portion
            per_100g_radio_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='rdPerServing_0']"))
            )
            per_100g_radio_button.click()
            
            # Click on the Search button
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btnSearch"))
            )
            search_button.click()
            
            time.sleep(2)  # Wait for results to load
            
            try:
                rows = driver.find_elements(By.XPATH, "//table[@class='gridviewlist']/tbody/tr")
                match_data = []

                for row in rows:
                    # Get all columns in the row
                    cols = row.find_elements(By.TAG_NAME, "td")
                    
                    # Initialize a list to store formatted column text for the current row
                    formatted_row = []
                    
                    # Loop through each column
                    for col in cols:
                        # Format the column text with curly braces and append to the list
                        formatted_row.append(f"{{ {col.text} }}")
                    
                    # Print the formatted row, with commas between columns
                    formatted_row_str = ", ".join(formatted_row)
                    
                    # Define a regex pattern to extract the 2nd, 3rd, 4th, and 5th values
                    pattern = r"\{([^}]+)\}, \{([^}]+)\}, \{([^}]+)\}, \{([^}]+)\}, \{([^}]+)\}, \{[^}]+\}"

                    # Use re.findall() to find all matches
                    matches = re.findall(pattern, formatted_row_str)

                    # Print the extracted values (2nd, 3rd, 4th, and 5th)
                    for match in matches:
                        second_value = match[1]  # 2nd value (Food Name)
                        third_value = match[2]   # 3rd value (Per Serving Household Measure)
                        fourth_value = match[3]  # 4th value (Nutrient Name)
                        fifth_value = match[4]   # 5th value (Nutrient Amount)

                        match_info = {
                            "Food Item": second_value,
                            "Per Serving Household Measure": third_value,
                            "Nutrient": fourth_value,
                            "Amount": fifth_value
                        }

                        # Append the dictionary to the list
                        match_data.append(match_info)
                
                # Add the match data for this dish to the overall data
                all_match_data.extend(match_data)
                
                # Continuously save the data to the JSON file
                with open(json_file_path, 'w') as json_file:
                    json.dump(all_match_data, json_file, indent=4)

            except Exception:
                print(f"No records found for {dish} - {nutrient}. Skipping...")
                continue  # Skip this nutrient if no records are found
        
        except Exception as e:
            print(f"Error processing {dish} - {nutrient}: {e}")
            continue
    
    print(f"Processed {dish}.")

# Close the browser
driver.quit()

print(f"Data extraction complete. Continuously saved to '{json_file_path}'.")


## ------------------------------------------------------------------------------------
## 2. Processing .json to convert it to .csv file

# Replace 'your_file.json' with your actual file path

# Load the JSON file
with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Convert JSON data into a DataFrame
df = pd.DataFrame(data)

# Pivot the data to arrange nutrients as columns and food items as rows
df_pivot = df.pivot_table(index=["Food Item", "Per Serving Household Measure"], columns="Nutrient", values="Amount", aggfunc="first")

# Reset index for proper formatting
df_pivot.reset_index(inplace=True)

# Rename "Food Item" to "Dish"
df_pivot.rename(columns={"Food Item": "Dish"}, inplace=True)

# Save the structured table as CSV
csv_filename = "Final_all_nutrition_per_serving.csv"
df_pivot.to_csv(csv_filename, index=False)

print(f"Data successfully saved as {csv_filename}")

## ----------------------------------------------------------------------------------
## 3. Convert this to json

# Path to your CSV file
csv_file_path = 'Final_all_nutrition_per_serving.csv'

# Path to save the output JSON file


# Read the CSV and convert to JSON
csv_data = []

# Open the CSV file
with open(csv_file_path, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    # Convert each row to a dictionary and append to the list
    for row in csv_reader:
        csv_data.append(row)

result = {}

for entry in csv_data:
    dish_name = entry["Dish"].strip()
    values = {k.strip(): v.strip() for k, v in entry.items() if k != "Dish"}
    result[dish_name] = values

# Save the new dict to a JSON file
with open(json_file_path, 'w', encoding='utf-8') as f_out:
    json.dump(result, f_out, indent=4)

print(f"Converted JSON saved to '{json_file_path}'")

