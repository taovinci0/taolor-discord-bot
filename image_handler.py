import base64
import io
import random

def decode_base64_image(base64_image):
    """
    Decodes base64 image data to a BytesIO object ready for Discord file upload
    
    Args:
        base64_image (str): Base64 encoded image string from API
        
    Returns:
        io.BytesIO: BytesIO object containing the decoded image
    """
    # Remove the "data:image/...;base64," prefix if present
    if base64_image.startswith("data:image"):
        # Split at the first comma; index [1] is the actual base64 string
        base64_part = base64_image.split(",", 1)[1]
    else:
        # If there's no prefix, assume the whole string is base64
        base64_part = base64_image

    # Decode the base64 string into raw bytes
    image_bytes = base64.b64decode(base64_part)
    
    # Return BytesIO object for Discord file upload
    return io.BytesIO(image_bytes)

def generate_random_seed():
    """
    Generates a random seed for the API requests
    
    Returns:
        int: A large random integer to be used as seed
    """
    # Generate a random 16-digit number
    return random.randint(1000000000000000, 9999999999999999) 