import random

def transform_prompt(user_input):
    """
    Transform user input into a properly formatted prompt that includes:
    - Always starts with "A man with grey hair and beard"
    - Always includes a T Logo placed somewhere in the scene
    - Adds footwear description for full body requests
    
    Args:
        user_input (str): The raw user input from Discord
        
    Returns:
        str: Properly formatted prompt for the API
    """
    # Start with the standard opening
    transformed_prompt = "A man with grey hair and beard"
    
    # Add the user's scene description
    transformed_prompt += f" {user_input.strip()}"
    
    # Check if full body is mentioned, add footwear if so
    if "full body" in user_input.lower():
        footwear_options = [
            "He is wearing black boots.",
            "He is wearing leather shoes.",
            "He is wearing dark combat boots.",
            "He is wearing traditional sandals."
        ]
        transformed_prompt += f" {random.choice(footwear_options)}"
    
    # Add the T Logo placement if not already mentioned
    if "t logo" not in user_input.lower():
        logo_placements = [
            "with a T Logo glowing on the wall behind him",
            "with a T Logo visible on his chest",
            "with a T Logo engraved on the floor",
            "with a T Logo hanging from his necklace",
            "with a T Logo embroidered on his clothing",
            "with a T Logo projected on a nearby surface",
            "with a T Logo appearing in the background",
            "with a T Logo visible on a nearby object"
        ]
        transformed_prompt += f", {random.choice(logo_placements)}"
    
    return transformed_prompt 