from ultralytics import YOLO
import requests

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
    names = model.names
    food_list = []

    # Count food items
    for r in results:
        for c in r.boxes.cls:
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

    if response.status_code == 200:
        data = response.json()
        if 'foods' in data and len(data['foods']) > 0:
            first_food = data['foods'][0]
            description = first_food['description']
            serving_size = first_food.get('servingSize', 0)
            nutritional_info = first_food['foodNutrients']

            print(f"Food: {description}")
            print(f"Serving Size: {serving_size}")
            print("Nutritional Information:")
            for nutrient in nutritional_info:
                print(f"{nutrient['nutrientName']}: {nutrient['value']} {nutrient['unitName']}")
        else:
            print(f"No results found for: {food_item}")
    else:
        print(f"Error in the API request for: {food_item}. Status Code: {response.status_code}")

# Main function
def main():
    image_path = "/content/1466490845071.jpg"
    food_dict = detect_food(image_path)

    for food_item, count in food_dict.items():
        
        print("__________________")
        print(f"Food Item: {food_item}, Count: {count}")
        print("Nutritional Information for", food_item)
        get_nutritional_info(food_item)

main()