import re
from .config import DIETARY_PREFENCES, ALLERGENS, MEAL_TYPE, CUISINE_TYPES

def clean_doubled_numbering(input_list):
    cleaned = []
    for item in input_list:
        cleaned_item = re.sub(r'^\d+\.\s*', '', item)
        cleaned.append(cleaned_item)
    return cleaned

def clean_additional_information_nutritions(data: dict) -> dict:
    cleaned = {}

    nutritions = data.get("total_nutritions", data)

    if isinstance(nutritions, dict):
        for key, value in nutritions.items():
            if isinstance(value, (int, float)):
                if key in ["protein", "fat", "carbs"]:
                    cleaned[key] = f"{value}g"
                else:
                    cleaned[key] = str(value)
            elif isinstance(value, str):
                match = re.search(r'\d+(?:\.\d+)?', value)
                if match:
                    number = match.group(0)
                    if key in ["protein", "fat", "carbs"]:
                        cleaned[key] = f"{number}g"
                    else:
                        cleaned[key] = number
                else:
                    cleaned[key] = value
            else:
                cleaned[key] = str(value)

    return cleaned

def validate_options_in_prompts(dietery, type_meal, allergens, cuisine):
    if dietery not in DIETARY_PREFENCES and dietery != " ":
        return {"error": f"Invalid dietary preference: {dietery}. Allowed values are: {DIETARY_PREFENCES}"}

    # Validate meal type
    if type_meal not in MEAL_TYPE and type_meal != " ":
        return {"error": f"Invalid meal type: {type_meal}. Allowed values are: {MEAL_TYPE}"}

    # Validate allergens (if not "None", ensure they're valid)
    valid_none_variants = ['None', 'N', 'o', 'n', 'e']
    
if not all(allergen in ALLERGENS or allergen in valid_none_variants for allergen in allergens):
        invalid_allergens = [allergen for allergen in allergens if allergen not in ALLERGENS and allergen not in valid_none_variants]
        return {"error": f"Invalid allergens: {invalid_allergens}. Allowed allergens are: {ALLERGENS}"}

    # Validate cuisine type
    if cuisine not in CUISINE_TYPES and cuisine != "Global":
        return {"error": f"Invalid cuisine type: {cuisine}. Allowed values are: {CUISINE_TYPES}"}

    # Return the validated data
    return {
        "message": "Validation passed!"
    }
