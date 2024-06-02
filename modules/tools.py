import requests
import numpy as np
from PIL import Image
from io import BytesIO


def get_average_color(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    image = image.resize((150, 150), resample=Image.BILINEAR)
    pixels = np.array(image)
    average_color = np.mean(pixels, axis=(0, 1)).astype(int)
    reformatted_average_color = [int(x) for x in average_color]
    return reformatted_average_color


def is_unicode_emoji(emoji):
    try:
        codepoint = ord(emoji[0])
        if (0x1F600 <= codepoint <= 0x1F64F or  # Emoticons
                0x1F300 <= codepoint <= 0x1F5FF or  # Symbols, Pictographs
                0x1F680 <= codepoint <= 0x1F6FF or  # Transport and Map Symbols
                0x2600 <= codepoint <= 0x26FF or  # Miscellaneous Symbols
                0x2700 <= codepoint <= 0x27BF or  # Dingbats
                0xFE0F <= codepoint <= 0xFE0F or  # Variation Selector-16
                0x1F900 <= codepoint <= 0x1F9FF):  # Supplemental Symbols and Pictographs
            return True
    except:
        return False

    return False
