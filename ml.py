from flask import Flask, request, jsonify
from ultralytics import YOLO
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:5500'])

# Initialize the YOLO model
model = YOLO("yolov8n.pt")

# Function to convert a list into a dictionary with item counts
def list_to_dict_with_count(input_list):
    count_dict = {}
    for item in input_list:
        if item in count_dict:
            count_dict[item] += 1
        else:
            count_dict[item] = 1
    return count_dict

# Function to perform object detection and count food items
def detect_food(image_path):
    results = model(image_path)
    print(type(results))
    names = model.names
    food_list = []

    # Count food items
    for r in results.pred:
        for c in r[:, -1].unique():
            food_list.append(names[int(c)])

    food_dict = list_to_dict_with_count(food_list)
    return food_dict

# Function to make API requests and retrieve nutritional information
def get_nutritional_info(food_item):
    api_key = 'kyuAfQJYgTsgfiDveUEyPhPmKdDezTNrk2w6i1mw'
    base_url = 'https://api.nal.usda.gov/fdc/v1/foods/search'

    params = {
        'query': food_item,
        'api_key': api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if 'foods' in data and len(data['foods']) > 0:
        food = data['foods'][0]
        nutrients = food['foodNutrients']
        nutrient_dict = {}
        for nutrient in nutrients:
            nutrient_dict[nutrient['nutrientName']] = nutrient['value']
        return nutrient_dict
    else:
        return None



# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    # Save the uploaded file to disk
    file.save(file.filename)

    # Perform object detection on the uploaded image
    food_dict = detect_food(file.filename)

    # Get nutritional information for each food item
    nutrient_dict = {}
    for food_item in food_dict.keys():
        nutrient_info = get_nutritional_info(food_item)
        if nutrient_info is not None:
            nutrient_dict[food_item] = nutrient_info
    
    print("Result: ", {'food': food_dict, 'nutrients': nutrient_dict})

    # Return the results as JSON
    return jsonify({'food': food_dict, 'nutrients': nutrient_dict})

if __name__ == '__main__':
    app.run(port=5001)