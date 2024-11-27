import json
import os
from functools import lru_cache



path_dir = os.path.dirname(__file__)
# Function to save user settings


@lru_cache(maxsize=None)
def save_settings(background_color, font_size, button_color):
    settings = {
        'background_color': background_color,
        'font_size': font_size,
        'button_color': button_color
    }
    with open(f'{path_dir}/config.json', 'w') as f:
        json.dump(settings, f)

# Function to load saved settings

@lru_cache(maxsize=None)
def load_settings():
    try:
        if os.path.exists(f'{path_dir}/config.json'):
            with open(f'{path_dir}/config.json', 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading settings: {e}")
        return None