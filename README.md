# DishVision

DishVision is an AI-powered web application that analyzes images of food dishes to predict the dish name and provide comprehensive nutritional information. Leveraging machine learning and a robust nutrition database, DishVision aims to assist users in understanding what they eat, supporting healthier dietary choices.

---

## Features

- **Food Recognition**: Upload an image of a dish and receive an AI-powered prediction of the food item.
- **Nutritional Analysis**: Automatically retrieve nutrition facts for recognized dishes, including macronutrients (protein, fat, carbohydrates), vitamins, and minerals.
- **Interactive Web Interface**: User-friendly interface for uploading images and viewing results.
- **API Access**: Uses Gemini API for Food Recognition and Ingredients task.
- **Extensible Dataset**: Nutrition information is sourced, cleaned, and processed from reputable sources.

---

## Demo

> ![DishVision UI Example]
> <img width="1599" height="808" alt="image" src="https://github.com/user-attachments/assets/f7da27ba-4846-4781-b1bc-4c61f35c8d80" />

---

## Getting Started

### Prerequisites

- Python 3.8+
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) (for nutrition scraping, if updating the nutrition database)
- [pip](https://pip.pypa.io/en/stable/)
- API Key for Gemini (Google Generative AI model)  
- (Optional) `virtualenv` for environment isolation

### Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/avikalp24022/dishvision.git
    cd dishvision
    ```

2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up Environment Variables**
    - Create a `.env` file in the project root:
      ```
      GEMINI_API_KEY=your_gemini_api_key_here
      ```
    - Replace `your_gemini_api_key_here` with your Google Gemini API key.

4. **Prepare Nutrition Data (optional: only if updating/expanding the nutrition dataset)**
    - The script `Nutrition_scraper.py` scrapes nutritional information for a list of dishes and nutrients, saving data to JSON/CSV.
    - Requires ChromeDriver and access to the Singapore HPB nutrition site.

5. **Run the Application**
    ```bash
    python app.py
    ```
    - The web server will be available at `http://localhost:5000`.

---

## Usage

### Web App

1. Open your browser and navigate to `http://localhost:5000`.
2. Click "Choose Image" to upload a food dish photo.
3. Click "Analyze" to let DishVision predict the dish and show its nutritional breakdown.

## Project Structure

```
dishvision/
│
├── app.py                    # Main Flask web app and API
├── Nutrition_scraper.py      # Script for scraping nutrition data
├── requirements.txt          # Python dependencies
├── static/                   # Static files (CSS, demo images)
├── templates/                # HTML templates
├── .env                      # API keys and environment variables
├── Final_key_value_pair.json # Nutrition data (used by app)
└── Final_all_nutrition_per_serving.csv # Processed nutrition data
```

---

## Data Collection & Processing

- **Nutrition_scraper.py**: Uses Selenium to scrape nutritional information for various dishes and nutrients.
- Data is cleaned, transformed to JSON, and then to CSV for efficient lookups.
- Nutrition data is mapped to dish names for quick API responses.

---

## Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a new branch (`git checkout -b my-feature`).
3. Commit your changes (`git commit -am 'Add feature'`).
4. Push to the branch (`git push origin my-feature`).
5. Open a Pull Request.

---

## License

This project currently does not specify a license. Please contact the repository owner for usage permissions.

---

## Acknowledgements

- [Singapore Health Promotion Board (HPB)](https://focos.hpb.gov.sg/eservices/ENCF/) for nutrition data source.
- Google Gemini API for AI food recognition and ingredients.
- Open-source libraries: Flask, Selenium, Pandas, etc.

---

## Contact

For questions or suggestions, open an issue or contact [avikalp24022](https://github.com/avikalp24022).
