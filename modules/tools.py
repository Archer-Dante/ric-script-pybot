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
