import requests
import numpy as np
from PIL import Image
from io import BytesIO
from collections import Counter


def get_average_color(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    image = image.resize((150, 150), resample=Image.BILINEAR)
    pixels = np.array(image)
    average_color = np.mean(pixels, axis=(0, 1)).astype(int)
    avg_packed = (int(x) for x in average_color)
    avg_packed = list(avg_packed)
    final_color_pack = if_dark_make_brighter(*avg_packed)
    # print(final_color_pack)
    return final_color_pack


def get_dominant_color(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    image = image.convert('RGB')  # Convert to RGB mode
    pixels = image.getcolors(image.size[0] * image.size[1])
    clean_pixels = []
    banned_colors: tuple = (255, 255, 255)
    for amount, color in pixels:
        if color != banned_colors:
            repack: tuple = (amount, color)
            clean_pixels.append(repack)
    dominant_color: list = (Counter(clean_pixels).most_common(1)[0][0])[1]
    # print(dominant_color)
    final_color_pack = if_dark_make_brighter(*dominant_color)
    # print(final_color_pack)
    return final_color_pack


def if_dark_make_brighter(*rgb):
    too_dark = 100  # число меньше этого - слишком тёмный цвет из RGB.
    brightness = 10
    saturation = 2.5
    packed_rgb: tuple = (rgb[0], rgb[1], rgb[2])
    if rgb[0] <= too_dark and rgb[1] <= too_dark and rgb[2] <= too_dark:
        red = int(rgb[0] * saturation) + brightness  # Red
        green = int(rgb[1] * saturation) + brightness  # Green
        blue = int(rgb[2] * saturation) + brightness  # Blue
        packed_rgb = (red, green, blue)
    return packed_rgb



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
