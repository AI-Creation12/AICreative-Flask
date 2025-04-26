from flask import request, jsonify
# from PIL import Image
# from .image_utils import compress_image, encode_image, validate_image_size
from .gemini_api import analize_image_with_prompt, generate_image_based_on_prompt
from .validation import clean_doubled_numbering, clean_additional_information_nutritions, validate_options_in_prompts
from .api_keys import get_remaining_time_in_hour
from .config import MAX_IMAGE_SIZE_MB
from io import BytesIO
import json, re
import base64

def setup_routes(app):
    @app.route("/upload", methods=["POST"])
    def upload_image():

        if request.method == "OPTIONS":
            return '', 200
        
        data = request.get_json()

        prompt_dietary_preference = data.get("dietary")
        prompt_type_meal = data.get("meal_type")
        prompt_allergens = data.get("allergens")
        prompt_cuisene_type = data.get("cuisine_type")
        print("DIETERY:", prompt_dietary_preference)
        print("TYPE MEAL:", prompt_type_meal)
        print("ALLERGENS:", prompt_allergens)
        print("CUISENE TYPE:", prompt_cuisene_type)

        if not prompt_dietary_preference:
            prompt_dietary_preference = " "
        if not prompt_type_meal:
            prompt_type_meal = " "
        if prompt_allergens == []:
            prompt_allergens = "None"
        if not prompt_cuisene_type:
            prompt_cuisene_type = "Global"

        validation = validate_options_in_prompts(prompt_dietary_preference,prompt_type_meal,prompt_allergens,prompt_cuisene_type)
        
        if "message" not in validation or validation["message"] != "Validation passed!":
            return jsonify({"error": "Not valid prompts"}), 404

        image_base64_string = data.get("image")
        image_base64 = base64.b64decode(image_base64_string)
        
        if not image_base64:
            return jsonify({"error": "No image provided"}), 422
        
        prompt_text = f"""
        Write all ingredients in JSON format.
        The response must always contain an 'ingredients' attribute as a list of objects.
        Each object should have 'name' (the recognized ingredient) and 'quantity' (either by count or weight, e.g., '100g').
        If no ingredients are recognized, return an list for 'ingredients' that has one string in it with text "Error".
        If there are ingriedents generate and wrap into one json response with details about a dish based on the recognition ingredients and cuisine type). 
            The response must include the following attributes:
            - "title": The title of the dish.
            - "title-prompt": Safe prompt to generate image of dish
            - "description": A brief description of the dish.
            - "ingredients_additional": A list of additional ingredients needed to prepare the dish, formatted as objects with "name" and "quantity".
            - "recipe": Step-by-step instructions on how to make the dish.
            - "nutritions": A list of calculated nutritional values for each ingredient along with additional ingriedeints, with objects containing "name" and "nutrition" details (e.g., calories [number], protein [number], fat [number], carbs [number]) for specific quantity of ingredient use in dish.
            - "total_nutritions": The total nutritional values for the entire dish, summarizing all ingredients.
            - "estimated_time": The estimated time required to prepare the dish. (only total time)
            The JSON structure must be well-formed and contain all the specified attributes. If no ingredients are recognized or you cant process image in order to generate recipie, the list for 'ingredients' must still be returned with a single string: `"Error"`, as mentioned.
            The cuisine type is: {prompt_cuisene_type}.
            Dietary preference is: {prompt_dietary_preference}.
            Allergens to avoid: {', '.join(prompt_allergens)}.
            Meal type: {prompt_type_meal}.
        """
        # print(prompt_text)
        try:
            # Send to Gemini API
            response_analize = analize_image_with_prompt(prompt_text, image_base64)
        except Exception as e:
            if "Rate limit exceeded" in str(e):
                countdown=get_remaining_time_in_hour()
                # print(countdown)
                return jsonify({"error": "Rate limit exceeded", "countdown": countdown}), 429
        #DEBUG
        # Print the actual API response in the console
        # print("Received API Response:", response_analize.text)
        # print("Received API Response TEST:", response_analize_test.text)
        # Correcting resposnse text
        # re.sub(r'^.*?json', '', response_analize, flags=re.DOTALL).replace("", "").strip()
        # print(response_analize)
        try:
            # Validation of coorect image 
            match = re.search(r'\{.*?\}', response_analize.text, re.DOTALL)
            json_block_str = match.group(0)    
            # print("ONE RESPONSE: ",json_block_str)
            parsed_response = json.loads(json_block_str)
            ingredients_list = parsed_response.get("ingredients", [])
            # CODE 422 for not valid image
            if (isinstance(ingredients_list, list) and len(ingredients_list) == 1 and (ingredients_list[0] == "Error" or (isinstance(ingredients_list[0], dict) and ingredients_list[0].get("name") == "Error"))):
                return jsonify({"error": "No ingredients found in the image"}), 422

        except:
            #If the response and image are correct
            response_json_analize_fix = response_analize.text.replace("```json", "").replace("```","").strip()        
            # print("ONE RESPONSE: ",response_json_analize_fix)
            # Extract title, ingredients, and recipe from the response text (JSON parsing)
            try:
                response_json_analize = json.loads(response_json_analize_fix)
                ingredients = response_json_analize.get("ingredients", [])
                response_json_recipe=json.loads(response_json_analize_fix)
                dish_title = response_json_recipe.get("title",[])
                prompt_image_dish = response_json_recipe.get("title-prompt",[])
                dish_description = response_json_recipe.get("description",[])
                additional_ingredients = response_json_recipe.get("ingredients_additional",[])
                ### DEBUG
                dish_steps = response_json_recipe.get("recipe",[])
                dish_steps_fixed = clean_doubled_numbering(dish_steps)
                # print(dish_steps, dish_steps_fixed)
                dish_nutritions = response_json_recipe.get("nutritions",[])
                dish_total_nutritions = response_json_recipe.get("total_nutritions",[])
                dish_total_nutritions_fix = clean_additional_information_nutritions(dish_total_nutritions)
                # print(dish_total_nutritions, dish_total_nutritions_fix)
                # print(type(dish_total_nutritions),type(dish_total_nutritions_fix))
                dish_time = response_json_recipe.get("estimated_time",[])

                ### DEBUG
                # Printing recived api response
                # print('PROPOSED DISH IS ', dish_title, 'WHICH IS', dish_description)
                try:
                    image_of_dish = generate_image_based_on_prompt(prompt_image_dish)
                except Exception as e:
                    if "Rate limit exceeded" in str(e):
                        countdown = get_remaining_time_in_hour()
                        return jsonify({"error": "Rate limit exceeded", "countdown": countdown}), 429

                recipie_data = {
                    "title": response_json_recipe.get("title",[]),
                    "description": response_json_recipe.get("description",[]),
                    "ingredients": ingredients,
                    "ingredients_additional" : response_json_recipe.get("ingredients_additional",[]),
                    "recipe": clean_doubled_numbering(response_json_recipe.get("recipe",[])),
                    "nutritions": response_json_recipe.get("nutritions",[]),
                    "total_nutritions": clean_additional_information_nutritions(response_json_recipe.get("total_nutritions",[])),
                    "estimated_time": response_json_recipe.get("estimated_time",[]),
                    "image_64encode": image_of_dish
                }



            except json.JSONDecodeError:
                return jsonify({"error": "Failed to parse Gemini API response"}), 500

        
        return jsonify(recipie_data)
